from core.logger import logger
from core.forge_os.registry import registry

class PlanningEngine:
    """
    The FORGE OS Planning Engine.
    Executes the 7-step decision framework before formulating a response.
    """
    def __init__(self):
        self.registry = registry

    def _determine_intent(self, query: str) -> dict:
        """Step 1 & 2: Understand objective and problem."""
        query = query.lower()
        if "metrics" in query or "dashboard" in query or "summary" in query or "briefing" in query:
            return {"intent": "get_metrics", "problem": "User needs pipeline overview"}
        if "hot" in query or "best" in query or "top" in query or "contact" in query:
            return {"intent": "get_top_opportunities", "problem": "User needs high-ROI prospects"}
        return {"intent": "unknown", "problem": "Unclear"}

    def _select_tool(self, intent_data: dict) -> str:
        """Step 3 & 4: Determine data needed and select tool."""
        if intent_data["intent"] == "get_metrics":
            return "get_crm_metrics"
        if intent_data["intent"] == "get_top_opportunities":
            return "get_top_opportunities"
        return None

    def execute_query(self, query: str) -> dict:
        """
        Executes the full planning pipeline:
        1. Determine Objective
        2. Identify Problem
        3. Determine Data needed
        4. Select Internal Tool
        5. Calculate ROI / Extract Data
        6. Check Automation Potential (Future LLM hooks)
        7. Recommend Action
        """
        logger.info(f"FORGE OS Planning Engine evaluating query: '{query}'")
        
        intent_data = self._determine_intent(query)
        tool_name = self._select_tool(intent_data)
        
        if not tool_name:
            return {
                "success": False,
                "message": "I could not determine the appropriate tool for this request. Please specify if you want metrics, top opportunities, or specific lead details.",
                "data": None
            }
            
        logger.info(f"FORGE OS Planning Engine selected tool: {tool_name}")
        
        data = None
        recommendation = ""
        
        if tool_name == "get_crm_metrics":
            data = self.registry.get_crm_metrics()
            recommendation = "Review the top-ranked leads in your pipeline to capitalize on the estimated pipeline value."
        elif tool_name == "get_top_opportunities":
            data = self.registry.get_top_opportunities(limit=3)
            recommendation = "I recommend contacting the #1 ranked lead immediately. I can generate a personalized proposal if you'd like."
            
        return {
            "success": True,
            "tool_used": tool_name,
            "intent": intent_data["intent"],
            "data": data,
            "recommendation": recommendation
        }

planner = PlanningEngine()
