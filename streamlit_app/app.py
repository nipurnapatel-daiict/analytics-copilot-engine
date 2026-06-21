"""
Purpose: Streamlined Streamlit UI view layer for Analytics Copilot interactions.
"""
import streamlit as st
import uuid
from services.api_service import APIService
from utils.session_manager import SessionManager
from utils.visualizer import UIVisualizer

st.set_page_config(
    page_title="Analytics Copilot",
    layout="wide"
)

@st.cache_resource
def initialize_backend():
    """Ensure backend services are initialized on first app load."""
    try:
        APIService.health_check()
    except Exception as e:
        st.warning(f"Backend initialization notice: {e}")

initialize_backend()
SessionManager.initialize_session()

st.sidebar.title("Analytics Copilot")

if st.sidebar.button("New Chat", use_container_width=True):
    SessionManager.create_new_thread()
    st.rerun()

st.sidebar.markdown("---")
st.sidebar.subheader("Conversation Threads")

threads_dict = st.session_state.threads

for t_id in list(threads_dict.keys()):
    display_title = threads_dict[t_id].get("title") or f"Session...{t_id[-4:]}"
    is_active = (st.session_state.current_thread_id == t_id)
    
    if len(display_title) > 28:
        display_title = display_title[:25] + "..."
        
    if st.sidebar.button(
        display_title, 
        key=f"sidebar_btn_{t_id}", 
        use_container_width=True, 
        type="primary" if is_active else "secondary"
    ):
        st.session_state.current_thread_id = t_id
        SessionManager.load_thread_history(t_id)
        st.rerun()

st.title("Analytics Copilot")
st.caption("SQL Warehouse Extraction and Document Compliance RAG")

messages = SessionManager.get_current_messages()

if len(messages) == 0:
    st.markdown("""
    <div style="padding: 2rem 0; text-align: center;">
        <h3>How can I help you analyze today?</h3>
        <p style="color: #94a3b8; font-size: 1.1rem;">
            Ask questions about sales revenue, order statistics, company policy compliance, or hybrid warehouse insights.
        </p>
    </div>
    """, unsafe_allow_html=True)
    
    cols = st.columns(3)
    suggestions = [
        {"title": "Sales Revenue", "text": "What is the total revenue?"},
        {"title": "Refund Policy", "text": "What is the refund policy?"},
        {"title": "Laptop Sales Analysis", "text": "Why are laptop sales decreasing?"}
    ]
    for i, card in enumerate(suggestions):
        with cols[i]:
            st.markdown(f"""
            <div style="border: 1px solid rgba(255, 255, 255, 0.1); padding: 1.25rem; border-radius: 8px; height: 120px;">
                <h4 style="margin-top: 0; font-size: 1.1rem; margin-bottom: 0.5rem;">{card['title']}</h4>
                <p style="color: #94a3b8; font-size: 0.95rem; margin-bottom: 0;">"{card['text']}"</p>
            </div>
            """, unsafe_allow_html=True)
            if st.button("Try Query", key=f"suggest_btn_{i}", use_container_width=True):
                st.session_state.suggested_query = card['text']
                st.rerun()

for message in messages:
    with st.chat_message(message["role"]):
        if message.get("route"):
            UIVisualizer.render_route_badge(message["route"])
        
        st.markdown(message["message"])
        
        if message.get("raw_payload") and message.get("route"):
            UIVisualizer.render_data_visualizations(message, message["route"])

user_query = st.chat_input("Ask analytics or document compliance related questions...")

if "suggested_query" in st.session_state and st.session_state.suggested_query:
    user_query = st.session_state.suggested_query
    del st.session_state.suggested_query

# Handle input event cycle submissions
if user_query:
    with st.chat_message("user"):
        st.markdown(user_query)

    active_thread_id = st.session_state.current_thread_id

    if not active_thread_id or active_thread_id not in st.session_state.threads:
        temporary_id = "temp_holding_id"
        st.session_state.current_thread_id = temporary_id
        
        SessionManager.store_message(
            thread_id=temporary_id, role="user", message=user_query
        )
        send_thread_payload = None  # PASS NULL TO BACKEND SO IT CREATES A NEW THREAD
    else:
        SessionManager.store_message(
            thread_id=active_thread_id, role="user", message=user_query
        )
        send_thread_payload = active_thread_id  # PASS ACTIVE ID TO CONTINUE CHAT

    try:
        with st.spinner("Executing analytical graph routing..."):
            response = APIService.send_message(
                query=user_query,
                thread_id=send_thread_payload
            )

        backend_thread_id = response.get("thread_id")
        
        if not backend_thread_id:
            st.error("Backend communication error: Missing valid thread tracking ID.")
            st.stop()

        if st.session_state.current_thread_id == "temp_holding_id":
            if "temp_holding_id" in st.session_state.threads:
                st.session_state.threads[backend_thread_id] = st.session_state.threads.pop("temp_holding_id")
            
        st.session_state.current_thread_id = backend_thread_id

        route_selected = response.get("route", "unknown")
        text_content = response.get("response") or response.get("message") or ""

        SessionManager.store_message(
            thread_id=backend_thread_id, 
            role="assistant", 
            message=text_content, 
            route=route_selected,
            raw_payload=response
        )

        st.rerun()

    except Exception as error:
        with st.chat_message("assistant"):
            st.error(f"Execution boundary tracking error: {error}")
