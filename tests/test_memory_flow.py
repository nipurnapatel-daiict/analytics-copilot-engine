"""
Purpose: Run automated integration validation checks against OpenSearch history indices.
"""
from app.services.opensearch_service import ChatHistoryService
from app.graph.memory import MemoryManager

def run_memory_verification():
    print(" Initializing Phase 6 Memory Storage Verification...")
    
    history_service = ChatHistoryService()
    
    history_service.create_chat_index()
    
    test_thread = MemoryManager.generate_thread_id()
    print(f"Generated test isolation reference -> {test_thread}")
    
    print("Saving mock analytical turn record logs...")
    history_service.save_message(
        thread_id=test_thread,
        query="What is the total revenue?",
        response="[{'total_revenue': Decimal('600000.00')}]",
        route="sql"
    )
    
    print("Querying storage indexes metrics data...")
    history_records = history_service.get_thread_history(test_thread)
    
    if history_records:
        print(" Verification Successful! Conversational logs matched:")
        print(f"   Stored Dataset -> {history_records}")
    else:
        print("Verification Failed: Dataset cluster returned an empty log statement matrix.")

if __name__ == "__main__":
    run_memory_verification()
