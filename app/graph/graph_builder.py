"""
Purpose: Build a robust, fault-tolerant LangGraph workflow for the analytics copilot.
"""
from langgraph.graph import StateGraph, END
from app.graph.graph_state import GraphState
from app.graph.graph_nodes import (
    classifier_node, sql_node, rag_node, 
    hybrid_node, error_node, summarize_node 
)
from app.core.constants import ApplicationConstants

class GraphBuilder:
    @staticmethod
    def build_graph():
        workflow = StateGraph(GraphState)

        workflow.add_node("classifier", classifier_node)
        workflow.add_node("sql", sql_node)
        workflow.add_node("rag", rag_node)
        workflow.add_node("hybrid", hybrid_node)
        workflow.add_node("summarize", summarize_node) 
        workflow.add_node("error", error_node)

        workflow.set_entry_point("classifier")

        workflow.add_conditional_edges(
            "classifier",
            lambda state: state["route"],
            {
                ApplicationConstants.SQL_ROUTE: "sql",
                ApplicationConstants.RAG_ROUTE: "rag",
                ApplicationConstants.HYBRID_ROUTE: "hybrid",
                ApplicationConstants.ERROR_ROUTE: "error"  
            }
        )

        def route_after_node(state: dict) -> str:
            if state.get("error"):
                return "error"
            return "summarize" 

        workflow.add_conditional_edges("sql", route_after_node, {"error": "error", "summarize": "summarize"})
        workflow.add_conditional_edges("rag", route_after_node, {"error": "error", "summarize": "summarize"})
        workflow.add_conditional_edges("hybrid", route_after_node, {"error": "error", "summarize": "summarize"})

        workflow.add_edge("summarize", END) 
        workflow.add_edge("error", END)

        return workflow.compile()
