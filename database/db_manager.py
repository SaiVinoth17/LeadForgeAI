import os
import shutil
from datetime import datetime
from sqlalchemy import create_engine, inspect, text
from sqlalchemy.orm import sessionmaker
from core.config import DB_PATH
from core.logger import logger
from models.lead import Base

class DatabaseManager:
    def __init__(self):
        self._ensure_schema_up_to_date()
        self.engine = create_engine(f"sqlite:///{DB_PATH}", echo=False, connect_args={"timeout": 30})
        self.SessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=self.engine)
        self.init_db()
        
    def _ensure_schema_up_to_date(self):
        """Migrate schema dynamically by adding missing columns to preserve data."""
        if not DB_PATH.exists():
            return
            
        temp_engine = create_engine(f"sqlite:///{DB_PATH}", echo=False)
        inspector = inspect(temp_engine)
        
        if inspector.has_table("leads"):
            columns = [col['name'] for col in inspector.get_columns("leads")]
            
            # Missing columns logic
            required_columns = {
                "priority": "VARCHAR(50) DEFAULT 'Cold'",
                "proposal": "TEXT",
                "email_draft": "TEXT",
                "whatsapp_draft": "TEXT",
                "meeting_date": "DATETIME",
                "followup_date": "DATETIME",
                "estimated_value": "FLOAT DEFAULT 0.0",
                "screenshot_path": "VARCHAR(500)",
                "last_contacted": "DATETIME",
                "detected_frameworks": "TEXT",
                "analytics_tags": "TEXT"
            }
            
            missing_cols = {k: v for k, v in required_columns.items() if k not in columns}
            
            if missing_cols:
                backup_path = DB_PATH.parent / f"leadforge_backup_{datetime.now().strftime('%Y%m%d_%H%M%S')}.db"
                shutil.copy(DB_PATH, backup_path)
                logger.info(f"Schema missing V2 columns. Backup created at {backup_path}.")
                
                with temp_engine.begin() as conn:
                    for col_name, col_type in missing_cols.items():
                        logger.info(f"Migrating DB: Adding column {col_name}")
                        try:
                            conn.execute(text(f"ALTER TABLE leads ADD COLUMN {col_name} {col_type}"))
                        except Exception as e:
                            logger.error(f"Failed to add column {col_name}: {e}")
                            
        temp_engine.dispose()

    def init_db(self):
        try:
            Base.metadata.create_all(bind=self.engine)
            logger.info("Database initialized successfully.")
        except Exception as e:
            logger.error(f"Error initializing database: {e}")
            
    def get_session(self):
        return self.SessionLocal()

db_manager = DatabaseManager()
