import re
from typing import Dict, Any

class AIAssistantRouter:
    """
    A modular intent router for the Local AI Assistant.
    Parses natural language requests and maps them to CRM filter actions.
    Future-proofed for Ollama/OpenAI integration by acting as an intent parser.
    """
    
    def __init__(self):
        self.intents = [
            {
                "pattern": r"(?i)show\s+(hot|warm|cold)\s+leads",
                "action": "filter_priority",
                "extract": lambda m: {"priority": "High Opportunity" if m.group(1).lower() == "hot" else "Medium" if m.group(1).lower() == "warm" else "Low"}
            },
            {
                "pattern": r"(?i)find\s+businesses\s+needing\s+redesign",
                "action": "filter_redesign",
                "extract": lambda m: {"is_mobile_responsive": "No", "has_ssl": "No"}
            },
            {
                "pattern": r"(?i)show\s+(\w+)\s+without\s+ssl",
                "action": "filter_category_no_ssl",
                "extract": lambda m: {"category": m.group(1).capitalize(), "has_ssl": "No"}
            },
            {
                "pattern": r"(?i)(\w+)\s+without\s+instagram",
                "action": "filter_category_no_instagram",
                "extract": lambda m: {"category": m.group(1).capitalize(), "missing_social": "instagram.com"}
            },
            {
                "pattern": r"(?i)generate\s+proposal\s+for\s+(.*)",
                "action": "generate_proposal",
                "extract": lambda m: {"business_name": m.group(1).strip()}
            }
        ]

    def parse_query(self, query: str) -> Dict[str, Any]:
        """
        Takes a natural language string and returns an intent dictionary.
        """
        for intent in self.intents:
            match = re.search(intent["pattern"], query)
            if match:
                return {
                    "action": intent["action"],
                    "params": intent["extract"](match),
                    "raw_query": query
                }
                
        return {
            "action": "unknown",
            "params": {},
            "raw_query": query
        }

ai_router = AIAssistantRouter()
