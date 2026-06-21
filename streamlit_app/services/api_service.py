"""
Purpose: Manage API communication with Analytics Copilot backend.
"""
import requests

class APIService:
    # BASE_URL = "http://localhost:8050/api/v1/copilot"
    BASE_URL = "http://milestone3-api:8050/api/v1/copilot"

    @classmethod
    def health_check(cls) -> dict:
        try:
            response = requests.get(f"{cls.BASE_URL}/health", timeout=5)
            if response.status_code == 200:
                return response.json()
            return {"status": "unhealthy"}
        except Exception as e:
            raise Exception(f"Backend health check failed: {e}")

    @classmethod
    def fetch_all_threads(cls) -> list:
        try:
            response = requests.get(f"{cls.BASE_URL}/threads", timeout=5)
            if response.status_code == 200:
                return response.json().get("threads", [])
            return []
        except Exception as e:
            raise Exception(f"Failed to fetch conversation history: {e}")

    @classmethod
    def fetch_thread_history(cls, thread_id: str) -> list:
        """Fetches and normalizes historical arrays containing pairs of queries and responses."""
        try:
            response = requests.get(f"{cls.BASE_URL}/history/{thread_id}", timeout=10)
            if response.status_code != 200:
                return []
            
            history_items = response.json().get("history", [])
            formatted_messages = []
            
            for item in history_items:
                formatted_messages.append({
                    "role": "user",
                    "message": item.get("query", "")
                })
                formatted_messages.append({
                    "role": "assistant",
                    "message": item.get("response") or item.get("message") or "",
                    "route": item.get("route", "unknown"),
                    "raw_payload": item
                })
            return formatted_messages
        except Exception as e:
            raise Exception(f"Error loading thread history: {e}")

    @classmethod
    def send_message(cls, query: str, thread_id: str = None) -> dict:
        payload = {"query": query}
        if thread_id:
            payload["thread_id"] = thread_id

        try:
            response = requests.post(
                f"{cls.BASE_URL}/chat",
                json=payload,
                timeout=60 
            )
            response.raise_for_status()
            return response.json()
        except requests.exceptions.RequestException as e:
            raise Exception(f"Chat communication failure: {e}")
