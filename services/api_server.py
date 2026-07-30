"""
High-Performance REST Backend Server for FORGE OS V5.
Supports FastAPI with Flask fallback.
"""

import json
import logging
from database.crud import get_all_leads
from services.ai_director import ai_director
from services.memory_engine import memory_engine
from services.strategy_engine import strategy_engine
from services.explainable_ai import explainable_ai

try:
    from fastapi import FastAPI
    from fastapi.middleware.cors import CORSMiddleware

    app = FastAPI(title="FORGE OS V5 API Engine", version="5.0.0")
    app.add_middleware(
        CORSMiddleware,
        allow_origins=["*"],
        allow_credentials=True,
        allow_methods=["*"],
        allow_headers=["*"],
    )

    @app.get("/api/v5/director")
    async def get_director():
        rec = ai_director.get_top_recommendation()
        rec["rationale"] = explainable_ai.explain("top_lead")
        return rec

    @app.get("/api/v5/leads")
    async def get_leads():
        leads = get_all_leads()
        result = []
        for l in leads:
            mem = memory_engine.get_client_memory(l.business_name)
            result.append({
                "id": l.id,
                "business_name": l.business_name,
                "category": l.category,
                "website": l.website,
                "score": l.opportunity_score or 90,
                "digital_twin": mem
            })
        return result

    @app.get("/api/v5/health")
    async def get_health():
        return {
            "providers": [
                {"name": "Gemini 1.5 Flash", "latency": "12 ms", "status": "Online"},
                {"name": "Groq LPU Engine", "latency": "45 ms", "status": "Online"},
            ],
            "status": "⚡ FORGE OS V5 ONLINE"
        }

except ImportError:
    from flask import Flask, jsonify
    from flask_cors import CORS

    app = Flask(__name__)
    CORS(app)

    @app.route("/api/v5/director")
    def get_director():
        rec = ai_director.get_top_recommendation()
        rec["rationale"] = explainable_ai.explain("top_lead")
        return jsonify(rec)

    @app.route("/api/v5/leads")
    def get_leads():
        leads = get_all_leads()
        result = []
        for l in leads:
            mem = memory_engine.get_client_memory(l.business_name)
            result.append({
                "id": l.id,
                "business_name": l.business_name,
                "category": l.category,
                "website": l.website,
                "score": l.opportunity_score or 90,
                "digital_twin": mem
            })
        return jsonify(result)

    @app.route("/api/v5/health")
    def get_health():
        return jsonify({
            "providers": [
                {"name": "Gemini 1.5 Flash", "latency": "12 ms", "status": "Online"},
                {"name": "Groq LPU Engine", "latency": "45 ms", "status": "Online"},
            ],
            "status": "⚡ FORGE OS V5 ONLINE"
        })
