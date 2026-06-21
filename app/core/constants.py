"""
Purpose: Store reusable application constants.
"""

class ApplicationConstants:

    APPLICATION_JSON = "application/json"

    SQL_ROUTE = "sql"
    RAG_ROUTE = "rag"
    HYBRID_ROUTE = "hybrid"
    ERROR_ROUTE = "error"

    MAX_SQL_RESULT_ROWS = 50
    SELECT_KEYWORD = "select"

    FORBIDDEN_SQL_KEYWORDS = [
        "insert",
        "update",
        "delete",
        "drop",
        "alter",
        "truncate",
        "create",
        "grant", 
        "revoke"
    ]

    VECTOR_FIELD = "embedding_vector"
    KNN_VECTOR_TYPE = "knn_vector"
    OPENSEARCH_SPACE_TYPE = "cosinesimil"
    OPENSEARCH_ENGINE = "nmslib"
    VECTOR_DIMENSION = 384
    DEFAULT_TOP_K = 5
    CHAT_HISTORY_LIMIT = 10
    REQUEST_TIMEOUT = 30
    RAG_ROUTE = "rag"
    HYBRID_ROUTE = "hybrid"
    SQL_ROUTE = "sql"
    ERROR_ROUTE = "error"

    CHAT_HISTORY_INDEX = "chat-history-index"
    THREAD_ID_PREFIX = "thread"
    DEFAULT_THREAD_LIMIT = 20