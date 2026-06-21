"""
Purpose: Independent utility script to completely purge all chat threads and histories from OpenSearch.
Usage: python wipe_history.py
"""
import sys
import os

sys.path.append(os.path.dirname(os.path.abspath(__file__)))

from opensearchpy import OpenSearch, RequestsHttpConnection
from core.config import settings
from core.constants import ApplicationConstants

def wipe_all_conversations():
    print("=" * 60)
    print("WARNING: You are about to completely wipe all chat thread logs!")
    print(f"Targeting OpenSearch Index: '{ApplicationConstants.CHAT_HISTORY_INDEX}'")
    print("=" * 60)
    
    confirm = input("Are you absolutely sure you want to proceed? (yes/no): ").strip().lower()
    if confirm != "yes":
        print("Operation cancelled safely. No indices were modified.")
        sys.exit(0)

    print(f"\nConnecting to OpenSearch cluster at {settings.OPENSEARCH_HOST}:{settings.OPENSEARCH_PORT}...")
    try:
        client = OpenSearch(
            hosts=[{"host": settings.OPENSEARCH_HOST, "port": settings.OPENSEARCH_PORT}],
            use_ssl=False,
            verify_certs=False,
            ssl_assert_hostname=False,
            ssl_show_warn=False,
            connection_class=RequestsHttpConnection
        )
        
        if not client.ping():
            print(f"ERROR: Could not communicate with OpenSearch cluster on port {settings.OPENSEARCH_PORT}.")
            sys.exit(1)
            
        target_index = ApplicationConstants.CHAT_HISTORY_INDEX
        
        if client.indices.exists(index=target_index):
            print(f"-> Index found: '{target_index}'. Issuing global deletion query...")
            
            purge_query = {"query": {"match_all": {}}}
            response = client.delete_by_query(
                index=target_index,
                body=purge_query,
                refresh=True,
                wait_for_completion=True
            )
            
            deleted_count = response.get("deleted", 0)
            print(f"   SUCCESS: Permanently purged {deleted_count} message documents from '{target_index}'.")
        else:
            print(f"-> Index '{target_index}' does not exist yet. There is nothing to clear.")

        print("\n" + "=" * 60)
        print("COMPLETE: Your open conversations index has been completely wiped clean.")
        print("Run your FastAPI app and Streamlit interface to enjoy a professional sandbox!")
        print("=" * 60)

    except Exception as error:
        print(f"\nCRITICAL CRASH: Failed to clear OpenSearch records: {str(error)}")
        sys.exit(1)

if __name__ == "__main__":
    wipe_all_conversations()
