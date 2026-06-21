"""
Purpose: Manage conversation history storage using OpenSearch.
"""
from datetime import datetime, timezone
from opensearchpy import OpenSearch, RequestsHttpConnection
from app.core.config import settings
from app.core.constants import ApplicationConstants
from app.core.logger import logger

class ChatHistoryService:
    def __init__(self):
        self.client = OpenSearch(
            hosts=[{"host": settings.OPENSEARCH_HOST, "port": settings.OPENSEARCH_PORT}],
            use_ssl=False,
            verify_certs=False,
            ssl_assert_hostname=False,
            ssl_show_warn=False,
            connection_class=RequestsHttpConnection
        )
        self.index_name = ApplicationConstants.CHAT_HISTORY_INDEX

    def create_chat_index(self):
        """Builds a dedicated conversation index if it does not already exist."""
        if self.client.indices.exists(index=self.index_name):
            return

        mapping = {
            "mappings": {
                "properties": {
                    "thread_id": {"type": "keyword"},
                    "query": {"type": "text"},
                    "response": {"type": "text"},
                    "route": {"type": "keyword"},
                    "timestamp": {"type": "date"}
                }
            }
        }
        self.client.indices.create(index=self.index_name, body=mapping)
        logger.info(f"OpenSearch index '{self.index_name}' initialized successfully.")

    def save_message(self, thread_id: str, query: str, response: any, route: str):
        """Persists a single conversational transaction log statement."""
        document = {
            "thread_id": thread_id,
            "query": query,
            "response": str(response),
            "route": route,
            "timestamp": datetime.now(timezone.utc).isoformat()
        }
        self.client.index(
            index=self.index_name,
            body=document,
            refresh=True
        )
        logger.info(f"Chat history stored for thread: {thread_id}")

    def get_thread_history(self, thread_id: str) -> list[dict]:
        """Retrieves chronologically sorted message histories matching a session thread ID."""
        search_query = {
            "size": ApplicationConstants.DEFAULT_THREAD_LIMIT,
            "sort": [{"timestamp": {"order": "asc"}}],
            "query": {"term": {"thread_id": thread_id}}
        }
        try:
            response = self.client.search(index=self.index_name, body=search_query)
            return [hit["_source"] for hit in response["hits"]["hits"]]
        except Exception as error:
            logger.error(f"Failed to fetch thread history: {error}")
            return []
        
    def get_all_threads(self) -> list:
        """Retrieves a unique list of all historical conversational thread profiles."""
        search_query = {
            "size": 0,  
            "aggs": {
                "distinct_threads": {
                    "terms": {
                        "field": "thread_id", 
                        "size": 100           
                    },
                    "aggs": {
                        "latest_message": {
                            "top_hits": {
                                "size": 1,
                                "_source": {"includes": ["query", "timestamp"]},
                                "sort": [{"timestamp": {"order": "desc"}}]
                            }
                        }
                    }
                }
            }
        }
        try:
            response = self.client.search(index=self.index_name, body=search_query)
            buckets = response["aggregations"]["distinct_threads"]["buckets"]

            threads = []
            for bucket in buckets:
                top_hits = bucket["latest_message"]["hits"]["hits"]
                title = "New Chat Session"
                if top_hits:
                    raw_query = top_hits[0]["_source"].get("query", "")
                    title = raw_query[:25] + "..." if len(raw_query) > 25 else raw_query

                threads.append({
                    "thread_id": bucket["key"],
                    "title": title or "Analytics Query Session",
                    "timestamp": top_hits[0]["_source"].get("timestamp") if top_hits else None,
                })
            
            return threads
        except Exception as error:
            logger.error(f"Failed to fetch historical unique threads from OpenSearch: {error}")
            return []
