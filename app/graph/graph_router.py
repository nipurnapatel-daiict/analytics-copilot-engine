"""
Purpose: Route queries to appropriate workflow paths using semantic LLM classification.
"""
from app.core.constants import ApplicationConstants
from app.core.logger import logger
from app.llm.bedrock_client import get_bedrock_llm

class GraphRouter:
    @staticmethod
    def classify_query(query: str) -> str:
        """Analyzes natural language queries semantically using an LLM to assign routing tokens."""
        try:
            llm = get_bedrock_llm()
            
            system_prompt = (
                "You are an expert intent classification router for an enterprise analytics system.\n"
                "Your job is to classify the user's input query into exactly one of four valid route strings:\n\n"
                
                f"- '{ApplicationConstants.SQL_ROUTE}': Used strictly for fetching numbers, totals, lists of records, quantities, or current trends from a database where NO EXPLANATION OR REASON IS ASKED. (e.g., 'What are our sales?', 'Show total orders').\n\n"
                
                f"- '{ApplicationConstants.RAG_ROUTE}': Used strictly for company policy documents, logistics hub explanations, compliance manuals, text guidelines, or general greetings.\n\n"
                
                f"- '{ApplicationConstants.HYBRID_ROUTE}': CRITICAL: Used when a query asks for the REASON, CAUSE, HOW or WHY behind a numerical metric or trend. If a user asks 'Why are sales decreasing?' or 'What caused the drop in revenue?', this is ALWAYS HYBRID because you must fetch the data metrics (SQL) AND cross-reference the policy/logistics logs (RAG) to explain the reason.\n\n"
                
                f"- '{ApplicationConstants.ERROR_ROUTE}': Used only if the prompt is complete gibberish or entirely unrelated to corporate business.\n\n"
                
                "CRITICAL: Output ONLY the plain string token itself (e.g., sql, rag, hybrid, error) in lowercase. Do not include markdown headers, quotes, punctuation, or explanations."
            )
            
            prompt = f"### System Prompt\n{system_prompt}\n\n### User Query\n{query}\n\n### Route Selected:"
            response = llm.invoke(prompt)
            predicted_route = str(response.content).strip().lower()
            
            if "hybrid" in predicted_route:
                return ApplicationConstants.HYBRID_ROUTE
            if "sql" in predicted_route:
                return ApplicationConstants.SQL_ROUTE
            if "error" in predicted_route:
                return ApplicationConstants.ERROR_ROUTE
            if "rag" in predicted_route:
                return ApplicationConstants.RAG_ROUTE
                
        except Exception as err:
            logger.error(f"Semantic routing model exception triggered: {err}")
            
        return ApplicationConstants.RAG_ROUTE



