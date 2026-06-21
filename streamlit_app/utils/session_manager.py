"""
Purpose: Manage Streamlit session state and chat threads with nested dictionaries.
Locks the thread title to the absolute first query regardless of backend title values.
"""
import streamlit as st

class SessionManager:

    @staticmethod
    def initialize_session():
        """Initializes tracking dictionaries using the backend's sorted chronological sequence."""
        if "threads" not in st.session_state:
            st.session_state.threads = {}
            
            from services.api_service import APIService
            try:
                db_threads = APIService.fetch_all_threads()
                
                for thread in db_threads:
                    t_id = thread["thread_id"]
                    
                    st.session_state.threads[t_id] = {
                        "title": thread.get("title", f"Session...{t_id[-4:]}"),
                        "messages": [] 
                    }
                    
                    try:
                        formatted_messages = APIService.fetch_thread_history(t_id)
                        if formatted_messages:
                            st.session_state.threads[t_id]["messages"] = formatted_messages
                            user_queries = [m["message"] for m in formatted_messages if m.get("role") == "user"]
                            if user_queries:
                                first_msg = user_queries[0].strip()
                                st.session_state.threads[t_id]["title"] = first_msg[:27] + "..." if len(first_msg) > 30 else first_msg
                    except Exception:
                        pass 
                        
            except Exception as e:
                st.error(f"Could not load previous conversations: {str(e)}")

        if "current_thread_id" not in st.session_state:
            st.session_state.current_thread_id = None

    @staticmethod
    def create_new_thread():
        """Unsets the current thread ID to prepare the UI for a fresh chat session."""
        st.session_state.current_thread_id = None

    @staticmethod
    def get_current_messages():
        """Safe retrieval of messages tied to the active chat thread selection."""
        thread_id = st.session_state.current_thread_id
        if not thread_id or thread_id not in st.session_state.threads:
            return []
        return st.session_state.threads[thread_id].get("messages", [])
    
    @staticmethod
    def store_message(thread_id: str, role: str, message: str, route: str = None, raw_payload: dict = None):
        """Appends a chat turn and promotes the active thread without modifying an established title."""
        if thread_id not in st.session_state.threads:
            st.session_state.threads[thread_id] = {"title": "New Chat", "messages": []}
            
        st.session_state.threads[thread_id]["messages"].append({
            "role": role,
            "message": message,
            "route": route,
            "raw_payload": raw_payload
        })
        
        current_title = st.session_state.threads[thread_id].get("title", "").strip()
        

        if role == "user" and (not current_title or current_title in ["New Chat", "temp_holding_id"]):
            clean_title = message.strip()
            if len(clean_title) > 30:
                clean_title = clean_title[:27] + "..."
            st.session_state.threads[thread_id]["title"] = clean_title

        if thread_id in st.session_state.threads:
            thread_data = st.session_state.threads.pop(thread_id)
            st.session_state.threads = {thread_id: thread_data, **st.session_state.threads}

    @staticmethod
    def load_thread_history(thread_id: str):
        """Loads historic log items safely without overwriting the original conversation title."""
        if thread_id not in st.session_state.threads:
            st.session_state.threads[thread_id] = {"title": f"Session...{thread_id[-4:]}", "messages": []}

        if st.session_state.threads[thread_id].get("messages"):
            active_thread_data = st.session_state.threads.pop(thread_id)
            st.session_state.threads = {thread_id: active_thread_data, **st.session_state.threads}
            return

        from services.api_service import APIService
        try:
            formatted_messages = APIService.fetch_thread_history(thread_id)
            st.session_state.threads[thread_id]["messages"] = formatted_messages
            
            user_queries = [m["message"] for m in formatted_messages if m.get("role") == "user"]
            if user_queries:
                first_question = user_queries[0].strip()
                if len(first_question) > 30:
                    first_question = first_question[:27] + "..."
                st.session_state.threads[thread_id]["title"] = first_question
        
            active_thread_data = st.session_state.threads.pop(thread_id)
            st.session_state.threads = {thread_id: active_thread_data, **st.session_state.threads}
                
        except Exception as e:
            st.sidebar.warning(f"Could not load conversation history logs: {str(e)}")


