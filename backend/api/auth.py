"""
Production-quality Authentication API.
- Real JWT (PyJWT) with HS256, access token 15 min, refresh token 7 days
- bcrypt password hashing via passlib
- SQLAlchemy-backed SQLite users table (persistent across restarts)
- Endpoints: register, login, forgot-password, reset-password, refresh, me, logout,
             profile update, password change
"""

import os
import uuid
import secrets
from datetime import datetime, timedelta, timezone
from functools import wraps
from pathlib import Path

import bcrypt
import jwt
from flask import request, g
from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker

from backend.api.auth_models import AuthBase, User, PasswordResetToken, RefreshTokenBlacklist

# ── Configuration ────────────────────────────────────────────────────────────
BASE_DIR = Path(__file__).resolve().parent.parent.parent
DATA_DIR = BASE_DIR / "data"
DATA_DIR.mkdir(parents=True, exist_ok=True)
DB_PATH = DATA_DIR / "leadforge.db"

# Secrets — in production load from environment variables
ACCESS_SECRET = os.environ.get("FORGE_ACCESS_SECRET", "forge-access-secret-change-in-prod-2024")
REFRESH_SECRET = os.environ.get("FORGE_REFRESH_SECRET", "forge-refresh-secret-change-in-prod-2024")
ACCESS_TOKEN_EXPIRE_MINUTES = 15
REFRESH_TOKEN_EXPIRE_DAYS = 7
RESET_TOKEN_EXPIRE_MINUTES = 30

# ── Password hashing ─────────────────────────────────────────────────────────
def _hash_password(password: str) -> str:
    return bcrypt.hashpw(password.encode("utf-8"), bcrypt.gensalt(rounds=12)).decode("utf-8")

def _verify_password(password: str, hashed: str) -> bool:
    try:
        return bcrypt.checkpw(password.encode("utf-8"), hashed.encode("utf-8"))
    except Exception:
        return False

# ── Database ──────────────────────────────────────────────────────────────────
_engine = create_engine(
    f"sqlite:///{DB_PATH}",
    echo=False,
    connect_args={"timeout": 30, "check_same_thread": False},
)
AuthBase.metadata.create_all(bind=_engine)
_Session = sessionmaker(bind=_engine, autocommit=False, autoflush=False)


def _get_db():
    if not hasattr(g, "_auth_db"):
        g._auth_db = _Session()
    return g._auth_db


def _close_db(app):
    """Register teardown on the Flask app to close the session."""
    @app.teardown_appcontext
    def teardown(exc):
        db = g.pop("_auth_db", None)
        if db is not None:
            db.close()


# ── Seed default admin user ───────────────────────────────────────────────────
def _seed_admin():
    """Create the default admin account if no users exist."""
    db = _Session()
    try:
        if db.query(User).count() == 0:
            admin = User(
                name="LeadForge Agency Admin",
                email="admin@leadforge.ai",
                password_hash=_hash_password("Admin123!"),
                role="Owner",
                company="LeadForge Agency",
                subscription="Enterprise Unlimited",
                linked_providers="email,google,github,microsoft,apple",
            )
            db.add(admin)
            db.commit()
    finally:
        db.close()


# ── JWT helpers ───────────────────────────────────────────────────────────────
def _make_access_token(user_id: int) -> str:
    now = datetime.now(timezone.utc)
    payload = {
        "sub": str(user_id),
        "iat": now,
        "exp": now + timedelta(minutes=ACCESS_TOKEN_EXPIRE_MINUTES),
        "type": "access",
        "jti": str(uuid.uuid4()),
    }
    return jwt.encode(payload, ACCESS_SECRET, algorithm="HS256")


def _make_refresh_token(user_id: int) -> str:
    now = datetime.now(timezone.utc)
    payload = {
        "sub": str(user_id),
        "iat": now,
        "exp": now + timedelta(days=REFRESH_TOKEN_EXPIRE_DAYS),
        "type": "refresh",
        "jti": str(uuid.uuid4()),
    }
    return jwt.encode(payload, REFRESH_SECRET, algorithm="HS256")


def _decode_access_token(token: str) -> dict:
    return jwt.decode(token, ACCESS_SECRET, algorithms=["HS256"])


def _decode_refresh_token(token: str) -> dict:
    return jwt.decode(token, REFRESH_SECRET, algorithms=["HS256"])


# ── Auth guard decorator ──────────────────────────────────────────────────────
def require_auth(f):
    """Decorator: validates Bearer access token, sets g.current_user."""
    @wraps(f)
    def decorated(*args, **kwargs):
        auth_header = request.headers.get("Authorization", "")
        if not auth_header.startswith("Bearer "):
            return {"error": "Missing or invalid Authorization header"}, 401
        token = auth_header.split(" ", 1)[1]
        try:
            payload = _decode_access_token(token)
        except jwt.ExpiredSignatureError:
            return {"error": "Access token expired"}, 401
        except jwt.InvalidTokenError:
            return {"error": "Invalid access token"}, 401

        db = _get_db()
        user = db.query(User).filter_by(id=int(payload["sub"]), is_active=True).first()
        if not user:
            return {"error": "User not found"}, 401
        g.current_user = user
        return f(*args, **kwargs)
    return decorated


# ── Route registration ────────────────────────────────────────────────────────
def register_auth_routes(app):
    _seed_admin()
    _close_db(app)

    # ── Register ─────────────────────────────────────────────────────────────
    @app.route("/api/v5/auth/register", methods=["POST"])
    def register():
        data = request.json or {}
        name = (data.get("name") or "").strip()
        email = (data.get("email") or "").lower().strip()
        password = data.get("password") or ""

        if not name or not email or not password:
            return {"error": "name, email, and password are required"}, 400
        if len(password) < 8:
            return {"error": "Password must be at least 8 characters"}, 400
        if "@" not in email:
            return {"error": "Invalid email address"}, 400

        db = _get_db()
        if db.query(User).filter_by(email=email).first():
            return {"error": "An account with this email already exists"}, 409

        user = User(
            name=name,
            email=email,
            password_hash=_hash_password(password),
            role="Agency Owner",
            company=data.get("company", "My Agency").strip() or "My Agency",
            subscription="Starter",
            linked_providers="email",
        )
        db.add(user)
        db.commit()
        db.refresh(user)

        access_token = _make_access_token(user.id)
        refresh_token = _make_refresh_token(user.id)
        return {"access_token": access_token, "refresh_token": refresh_token, "user": user.to_dict()}, 201

    # ── Login ─────────────────────────────────────────────────────────────────
    @app.route("/api/v5/auth/login", methods=["POST"])
    def login():
        data = request.json or {}
        email = (data.get("email") or "").lower().strip()
        password = data.get("password") or ""

        if not email or not password:
            return {"error": "Email and password are required"}, 400

        db = _get_db()
        user = db.query(User).filter_by(email=email, is_active=True).first()
        if not user or not _verify_password(password, user.password_hash):
            return {"error": "Invalid email or password"}, 401

        access_token = _make_access_token(user.id)
        refresh_token = _make_refresh_token(user.id)
        return {"access_token": access_token, "refresh_token": refresh_token, "user": user.to_dict()}

    # ── Refresh ───────────────────────────────────────────────────────────────
    @app.route("/api/v5/auth/refresh", methods=["POST"])
    def refresh():
        data = request.json or {}
        ref_token = data.get("refresh_token") or ""
        try:
            payload = _decode_refresh_token(ref_token)
            if payload.get("type") != "refresh":
                raise jwt.InvalidTokenError("Not a refresh token")
        except jwt.ExpiredSignatureError:
            return {"error": "Refresh token expired, please log in again"}, 401
        except jwt.InvalidTokenError:
            return {"error": "Invalid refresh token"}, 401

        # Check blacklist
        db = _get_db()
        jti = payload.get("jti", "")
        if db.query(RefreshTokenBlacklist).filter_by(jti=jti).first():
            return {"error": "Refresh token has been revoked"}, 401

        user = db.query(User).filter_by(id=int(payload["sub"]), is_active=True).first()
        if not user:
            return {"error": "User not found"}, 401

        new_access = _make_access_token(user.id)
        return {"access_token": new_access, "user": user.to_dict()}

    # ── Me (guarded) ──────────────────────────────────────────────────────────
    @app.route("/api/v5/auth/me", methods=["GET"])
    @require_auth
    def me():
        return g.current_user.to_dict()

    # ── Logout ────────────────────────────────────────────────────────────────
    @app.route("/api/v5/auth/logout", methods=["POST"])
    def logout():
        data = request.json or {}
        ref_token = data.get("refresh_token") or ""
        if ref_token:
            try:
                payload = _decode_refresh_token(ref_token)
                jti = payload.get("jti", "")
                if jti:
                    db = _get_db()
                    if not db.query(RefreshTokenBlacklist).filter_by(jti=jti).first():
                        db.add(RefreshTokenBlacklist(jti=jti))
                        db.commit()
            except Exception:
                pass  # Even if token is invalid, we treat logout as successful
        return {"message": "Logged out successfully"}

    # ── Forgot Password ───────────────────────────────────────────────────────
    @app.route("/api/v5/auth/forgot-password", methods=["POST"])
    def forgot_password():
        data = request.json or {}
        email = (data.get("email") or "").lower().strip()
        if not email:
            return {"error": "Email is required"}, 400

        db = _get_db()
        user = db.query(User).filter_by(email=email, is_active=True).first()
        # Always return success to prevent email enumeration
        if not user:
            return {"message": "If this email exists, a reset token has been generated.", "reset_token": None}

        # Invalidate old tokens
        db.query(PasswordResetToken).filter_by(user_id=user.id, used=False).update({"used": True})
        db.commit()

        token_value = secrets.token_urlsafe(32)
        expires_at = datetime.utcnow() + timedelta(minutes=RESET_TOKEN_EXPIRE_MINUTES)
        reset_token = PasswordResetToken(user_id=user.id, token=token_value, expires_at=expires_at)
        db.add(reset_token)
        db.commit()

        # In a production app this would be emailed. For local dev, return in response.
        return {
            "message": "Password reset token generated. Copy the token below and use it to reset your password.",
            "reset_token": token_value,
            "expires_in_minutes": RESET_TOKEN_EXPIRE_MINUTES,
        }

    # ── Reset Password ────────────────────────────────────────────────────────
    @app.route("/api/v5/auth/reset-password", methods=["POST"])
    def reset_password():
        data = request.json or {}
        token_value = (data.get("token") or "").strip()
        new_password = data.get("new_password") or ""

        if not token_value or not new_password:
            return {"error": "token and new_password are required"}, 400
        if len(new_password) < 8:
            return {"error": "Password must be at least 8 characters"}, 400

        db = _get_db()
        reset_token = db.query(PasswordResetToken).filter_by(token=token_value, used=False).first()
        if not reset_token:
            return {"error": "Invalid or already-used reset token"}, 400
        if reset_token.expires_at < datetime.utcnow():
            return {"error": "Reset token has expired"}, 400

        user = db.query(User).filter_by(id=reset_token.user_id, is_active=True).first()
        if not user:
            return {"error": "User not found"}, 404

        user.password_hash = _hash_password(new_password)
        user.updated_at = datetime.utcnow()
        reset_token.used = True
        db.commit()

        return {"message": "Password reset successfully. You can now log in with your new password."}

    # ── Update Profile (guarded) ──────────────────────────────────────────────
    @app.route("/api/v5/auth/profile", methods=["PUT"])
    @require_auth
    def update_profile():
        data = request.json or {}
        user = g.current_user
        db = _get_db()

        if "name" in data and data["name"].strip():
            user.name = data["name"].strip()
        if "company" in data and data["company"].strip():
            user.company = data["company"].strip()
        user.updated_at = datetime.utcnow()
        db.commit()
        db.refresh(user)

        return user.to_dict()

    # ── Change Password (guarded) ─────────────────────────────────────────────
    @app.route("/api/v5/auth/password", methods=["PUT"])
    @require_auth
    def change_password():
        data = request.json or {}
        current_password = data.get("current_password") or ""
        new_password = data.get("new_password") or ""

        if not current_password or not new_password:
            return {"error": "current_password and new_password are required"}, 400
        if len(new_password) < 8:
            return {"error": "New password must be at least 8 characters"}, 400

        user = g.current_user
        if not _verify_password(current_password, user.password_hash):
            return {"error": "Current password is incorrect"}, 401

        db = _get_db()
        user.password_hash = _hash_password(new_password)
        user.updated_at = datetime.utcnow()
        db.commit()

        return {"message": "Password changed successfully"}

    # ── OAuth (stub — local app doesn't have real OAuth) ──────────────────────
    @app.route("/api/v5/auth/oauth/<provider>", methods=["POST"])
    def oauth_login(provider: str):
        if provider not in ["google", "github", "microsoft", "apple"]:
            return {"error": "Unsupported provider"}, 400

        data = request.json or {}
        email = (data.get("email") or f"user@{provider}.com").lower().strip()
        name = data.get("name") or f"User ({provider.capitalize()})"

        db = _get_db()
        user = db.query(User).filter_by(email=email).first()
        if not user:
            user = User(
                name=name,
                email=email,
                password_hash="",
                role="Agency Member",
                company="My Agency",
                subscription="Pro Tier",
                linked_providers=provider,
            )
            db.add(user)
            db.commit()
            db.refresh(user)
        else:
            providers = [p.strip() for p in user.linked_providers.split(",") if p.strip()]
            if provider not in providers:
                providers.append(provider)
                user.linked_providers = ",".join(providers)
                db.commit()

        access_token = _make_access_token(user.id)
        refresh_token = _make_refresh_token(user.id)
        return {"access_token": access_token, "refresh_token": refresh_token, "provider": provider, "user": user.to_dict()}
