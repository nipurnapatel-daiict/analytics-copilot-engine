# tests/test_temp.py
from app.services.rag_service import RagService

def run_test():
    print("Initializing RagService...")
    service = RagService()

    query = "What is the refund policy for pending orders?"
    existing_thread_id = "9417a506-b961-45ac-8f96-6cd02d0e6c29"
    
    print(f"Sending query with Thread ID: {existing_thread_id}")
    
    response = service.retrieve_response(
        query=query, 
        thread_id=existing_thread_id
    )
    
    print("\n--- RAG Response Received ---")
    print(response)
    print("----------------------------")

if __name__ == "__main__":
    run_test()
