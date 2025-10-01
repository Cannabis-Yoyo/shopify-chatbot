import streamlit as st
import time
import json
import os
from datetime import datetime
from pathlib import Path
from chatbot import Chatbot
from config import GROQ_API_KEY, PDF_FOLDER, DATA_FOLDER

st.set_page_config(
    page_title="Shopify Customer Support",
    page_icon="🛍️",
    layout="wide",
    initial_sidebar_state="expanded"
)

# Custom CSS with professional color scheme
st.markdown("""
    <style>
    /* Main background */
    .main {
        background-color: #f8f9fa;
    }
    
    /* Sidebar styling */
    [data-testid="stSidebar"] {
        background-color: #ffffff !important;
        border-right: 1px solid #e0e0e0;
    }
    
    [data-testid="stSidebar"] * {
        color: #2d3748 !important;
    }
    
    [data-testid="stSidebar"] .element-container {
        color: #2d3748 !important;
    }
    
    [data-testid="stSidebar"] [data-testid="stMarkdownContainer"] {
        color: #2d3748 !important;
    }
    
    [data-testid="stSidebar"] [data-testid="stMarkdownContainer"] * {
        color: #2d3748 !important;
    }
    
    /* Button styling */
    .stButton>button {
        width: 100%;
        border-radius: 8px;
        height: 50px;
        font-weight: 500;
        transition: all 0.3s;
        border: none;
        color: white !important;
        background-color: #667eea !important;
    }
    
    .stButton>button:hover {
        transform: translateY(-2px);
        box-shadow: 0 4px 12px rgba(0,0,0,0.1);
        background-color: #5568d3 !important;
    }
    
    .stButton>button[kind="secondary"] {
        background-color: #e2e8f0 !important;
        color: #2d3748 !important;
    }
    
    .stButton>button[kind="secondary"]:hover {
        background-color: #cbd5e0 !important;
    }
    
    .stButton>button[kind="primary"] {
        background-color: #667eea !important;
        color: white !important;
    }
    
    /* Chat message styling */
    .chat-message {
        padding: 1.2rem 1.5rem;
        border-radius: 12px;
        margin-bottom: 1rem;
        animation: fadeIn 0.4s;
        max-width: 75%;
        word-wrap: break-word;
    }
    
    .user-message {
        background: linear-gradient(135deg, #667eea 0%, #764ba2 100%);
        color: white;
        margin-left: auto;
        margin-right: 0;
    }
    
    .bot-message {
        background-color: #ffffff;
        color: #2d3748;
        margin-right: auto;
        margin-left: 0;
        border: 1px solid #e2e8f0;
        box-shadow: 0 1px 3px rgba(0,0,0,0.05);
    }
    
    @keyframes fadeIn {
        from { 
            opacity: 0; 
            transform: translateY(10px); 
        }
        to { 
            opacity: 1; 
            transform: translateY(0); 
        }
    }
    
    /* Typing indicator */
    .typing-indicator {
        display: flex;
        align-items: center;
        padding: 1rem 1.5rem;
        background-color: #ffffff;
        border-radius: 12px;
        width: fit-content;
        border: 1px solid #e2e8f0;
        box-shadow: 0 1px 3px rgba(0,0,0,0.05);
    }
    
    .typing-indicator span {
        height: 8px;
        width: 8px;
        background-color: #667eea;
        border-radius: 50%;
        display: inline-block;
        margin: 0 3px;
        animation: typing 1.4s infinite;
    }
    
    .typing-indicator span:nth-child(2) {
        animation-delay: 0.2s;
    }
    
    .typing-indicator span:nth-child(3) {
        animation-delay: 0.4s;
    }
    
    @keyframes typing {
        0%, 60%, 100% { 
            transform: translateY(0); 
            opacity: 0.7;
        }
        30% { 
            transform: translateY(-10px); 
            opacity: 1;
        }
    }
    
    /* Header container */
    .header-container {
        background: linear-gradient(135deg, #667eea 0%, #764ba2 100%);
        padding: 2.5rem;
        border-radius: 12px;
        color: white;
        margin-bottom: 2rem;
        text-align: center;
        box-shadow: 0 4px 12px rgba(102, 126, 234, 0.3);
    }
    
    .header-container h1 {
        margin: 0;
        font-size: 2.5rem;
        font-weight: 700;
    }
    
    .header-container p {
        margin: 0.5rem 0 0 0;
        font-size: 1.1rem;
        opacity: 0.95;
    }
    
    .header-container h2 {
        margin: 0;
        font-size: 2rem;
        font-weight: 600;
    }
    
    /* Option card */
    .option-card {
        background: white;
        padding: 2rem;
        border-radius: 12px;
        box-shadow: 0 2px 8px rgba(0,0,0,0.08);
        margin: 1rem 0;
        transition: all 0.3s;
        border: 2px solid transparent;
        height: 100%;
    }
    
    .option-card:hover {
        transform: translateY(-5px);
        box-shadow: 0 8px 20px rgba(0,0,0,0.12);
        border-color: #667eea;
    }
    
    .option-card h3 {
        color: #2d3748;
        margin-top: 0;
        font-size: 1.5rem;
        margin-bottom: 1rem;
    }
    
    .option-card p {
        color: #4a5568;
        line-height: 1.6;
    }
    
    .option-card ul {
        color: #4a5568;
        line-height: 1.8;
    }
    
    .option-card em {
        color: #667eea;
        font-weight: 500;
    }
    
    /* Input styling */
    .stTextInput>div>div>input {
        border-radius: 8px;
        border: 2px solid #e2e8f0;
        padding: 0.75rem;
    }
    
    .stTextInput>div>div>input:focus {
        border-color: #667eea;
        box-shadow: 0 0 0 3px rgba(102, 126, 234, 0.1);
    }
    
    /* Chat input */
    .stChatInput>div>div>textarea {
        border-radius: 8px;
        border: 2px solid #e2e8f0;
    }
    
    .stChatInput>div>div>textarea:focus {
        border-color: #667eea;
        box-shadow: 0 0 0 3px rgba(102, 126, 234, 0.1);
    }
    
    /* Sidebar text */
    [data-testid="stSidebar"] h3 {
        color: #2d3748 !important;
        font-size: 1.2rem;
        font-weight: 600;
    }
    
    [data-testid="stSidebar"] h3,
    [data-testid="stSidebar"] p,
    [data-testid="stSidebar"] strong {
        color: #2d3748 !important;
    }
    
    [data-testid="stSidebar"] .stMarkdown {
        color: #2d3748 !important;
    }
    
    /* Divider */
    hr {
        margin: 1.5rem 0;
        border: none;
        border-top: 1px solid #e2e8f0;
    }
    
    /* Alert messages */
    .stAlert {
        border-radius: 8px;
        padding: 1rem;
        margin: 1rem 0;
    }
    
    /* Error messages */
    .stAlert[data-baseweb="notification"] {
        background-color: #fee !important;
        border-left: 4px solid #f56565 !important;
    }
    
    [data-testid="stNotification"][kind="error"] {
        background-color: #fee2e2 !important;
        border-left: 4px solid #ef4444 !important;
        color: #991b1b !important;
    }
    
    [data-testid="stNotification"][kind="error"] * {
        color: #991b1b !important;
    }
    
    /* Success messages */
    .stSuccess {
        background-color: #d1fae5 !important;
        border-left: 4px solid #10b981 !important;
        color: #065f46 !important;
        padding: 1rem !important;
        border-radius: 8px !important;
        margin: 1rem 0 !important;
    }
    
    .stSuccess * {
        color: #065f46 !important;
    }
    
    [data-testid="stNotification"][kind="success"] {
        background-color: #d1fae5 !important;
        border-left: 4px solid #10b981 !important;
        color: #065f46 !important;
    }
    
    [data-testid="stNotification"][kind="success"] * {
        color: #065f46 !important;
    }
    
    /* Warning messages */
    .stWarning {
        background-color: #fef3c7 !important;
        border-left: 4px solid #f59e0b !important;
        color: #92400e !important;
        padding: 1rem !important;
        border-radius: 8px !important;
        margin: 1rem 0 !important;
    }
    
    .stWarning * {
        color: #92400e !important;
    }
    
    [data-testid="stAlert"][data-baseweb="notification"]:has(.stWarning),
    [data-testid="stNotification"][kind="warning"] {
        background-color: #fef3c7 !important;
        border-left: 4px solid #f59e0b !important;
        color: #92400e !important;
    }
    
    [data-testid="stNotification"][kind="warning"] * {
        color: #92400e !important;
    }
    
    /* Info messages */
    .stInfo {
        background-color: #dbeafe !important;
        border-left: 4px solid #3b82f6 !important;
        color: #1e40af !important;
        padding: 1rem !important;
        border-radius: 8px !important;
        margin: 1rem 0 !important;
    }
    
    .stInfo * {
        color: #1e40af !important;
    }
    
    [data-testid="stNotification"][kind="info"] {
        background-color: #dbeafe !important;
        border-left: 4px solid #3b82f6 !important;
        color: #1e40af !important;
    }
    
    [data-testid="stNotification"][kind="info"] * {
        color: #1e40af !important;
    }
    
    /* Ensure error text is visible */
    .element-container .stAlert p,
    .element-container .stSuccess p,
    .element-container .stWarning p,
    .element-container .stInfo p {
        color: inherit !important;
        margin: 0;
        font-weight: 500;
    }
    </style>
    """, unsafe_allow_html=True)

CHAT_HISTORY_DIR = Path("chat_history")
CHAT_HISTORY_DIR.mkdir(exist_ok=True)

def load_chat_history():
    """Load all chat sessions from files"""
    chat_files = sorted(CHAT_HISTORY_DIR.glob("*.json"), key=os.path.getmtime, reverse=True)
    chats = []
    for file in chat_files:
        try:
            with open(file, 'r') as f:
                chat_data = json.load(f)
                chats.append(chat_data)
        except Exception as e:
            st.error(f"Error loading chat {file.name}: {e}")
    return chats

def save_chat_session(session_id, messages, mode, context_data=None):
    """Save chat session to file with context"""
    file_path = CHAT_HISTORY_DIR / f"{session_id}.json"
    chat_data = {
        "session_id": session_id,
        "timestamp": datetime.now().isoformat(),
        "mode": mode,
        "messages": messages,
        "context": context_data
    }
    with open(file_path, 'w') as f:
        json.dump(chat_data, f, indent=2)

def initialize_session_state():
    """Initialize session state variables"""
    if 'chatbot' not in st.session_state:
        with st.spinner("Initializing AI Assistant..."):
            st.session_state.chatbot = Chatbot(GROQ_API_KEY, PDF_FOLDER, DATA_FOLDER)
    
    if 'current_session_id' not in st.session_state:
        st.session_state.current_session_id = datetime.now().strftime("%Y%m%d_%H%M%S")
    
    if 'messages' not in st.session_state:
        st.session_state.messages = []
    
    if 'mode' not in st.session_state:
        st.session_state.mode = None
    
    if 'typing' not in st.session_state:
        st.session_state.typing = False
    
    if 'pending_input' not in st.session_state:
        st.session_state.pending_input = None
    
    if 'order_submenu' not in st.session_state:
        st.session_state.order_submenu = None

def new_chat():
    """Start a new chat session"""
    st.session_state.current_session_id = datetime.now().strftime("%Y%m%d_%H%M%S")
    st.session_state.messages = []
    st.session_state.mode = None
    st.session_state.typing = False
    st.session_state.pending_input = None
    st.session_state.order_submenu = None
    st.session_state.chatbot.clear_context()

def load_chat_session(session_id, messages, mode, context_data=None):
    """Load a specific chat session with context"""
    st.session_state.current_session_id = session_id
    st.session_state.messages = messages
    st.session_state.mode = mode
    st.session_state.typing = False
    st.session_state.pending_input = None
    st.session_state.order_submenu = None
    
    if context_data:
        st.session_state.chatbot.import_context(context_data)
    else:
        st.session_state.chatbot.clear_context()

def delete_chat_session(session_id):
    """Delete a chat session"""
    file_path = CHAT_HISTORY_DIR / f"{session_id}.json"
    try:
        if file_path.exists():
            file_path.unlink()
            if st.session_state.current_session_id == session_id:
                new_chat()
            return True
    except Exception as e:
        st.error(f"Error deleting chat: {e}")
    return False

def display_typing_indicator():
    """Display typing indicator animation"""
    return """
    <div class="typing-indicator">
        <span></span>
        <span></span>
        <span></span>
    </div>
    """

def render_message(message, is_user=True):
    """Render a chat message with styling"""
    css_class = "user-message" if is_user else "bot-message"
    role_label = "You" if is_user else "AI Assistant"
    
    # Preprocess newlines outside the f-string
    safe_message = message.replace("\n", "<br/>")
    
    # Determine alignment
    style = "margin-left: auto; display: block;" if is_user else "margin-right: auto; display: block;"
    
    st.markdown(
        f"""
        <div class="chat-message {css_class}" style="{style}">
            <strong>{role_label}:</strong><br/>
            {safe_message}
        </div>
        """,
        unsafe_allow_html=True
    )

def main():
    initialize_session_state()
    
    # Sidebar
    with st.sidebar:
        st.markdown("### Shopify Support")
        st.markdown("---")
        
        # New Chat Button
        if st.button("+ New Chat", use_container_width=True):
            new_chat()
            st.rerun()
        
        st.markdown("---")
        st.markdown("### Chat History")
        
        # Load and display chat history
        all_chats = load_chat_history()
        
        if all_chats:
            if st.button("Delete All Chats", use_container_width=True, type="secondary"):
                if st.session_state.get('confirm_delete_all', False):
                    for chat_file in CHAT_HISTORY_DIR.glob("*.json"):
                        try:
                            chat_file.unlink()
                        except Exception as e:
                            st.error(f"Error deleting {chat_file.name}: {e}")
                    new_chat()
                    st.session_state.confirm_delete_all = False
                    st.rerun()
                else:
                    st.session_state.confirm_delete_all = True
                    st.rerun()
            
            if st.session_state.get('confirm_delete_all', False):
                st.warning("Click again to confirm")
                if st.button("Cancel", use_container_width=True):
                    st.session_state.confirm_delete_all = False
                    st.rerun()
            
            st.markdown("---")
            
            for chat in all_chats:
                session_id = chat['session_id']
                timestamp = datetime.fromisoformat(chat['timestamp'])
                message_count = len(chat['messages'])
                
                preview_text = f"{timestamp.strftime('%b %d, %I:%M %p')}"
                is_active = session_id == st.session_state.current_session_id
                
                col1, col2 = st.columns([5, 1])
                
                with col1:
                    if st.button(
                        f"{preview_text}\n{message_count} messages",
                        key=f"load_{session_id}",
                        use_container_width=True,
                        type="primary" if is_active else "secondary"
                    ):
                        load_chat_session(
                            session_id, 
                            chat['messages'], 
                            chat.get('mode'),
                            chat.get('context')
                        )
                        st.rerun()
                
                with col2:
                    if st.button("X", key=f"delete_{session_id}", help="Delete", use_container_width=True):
                        if delete_chat_session(session_id):
                            st.rerun()
        else:
            st.info("No chat history yet")
        
        st.markdown("---")
        st.markdown("### About")
        st.markdown("**Version:** 2.0.0")
        st.markdown("**Feature:** Chat & Order Management")

    # Main content area
    if st.session_state.mode is None:
        # Home screen
        st.markdown("""
            <div class="header-container">
                <h1>Shopify Customer Support</h1>
                <p>Your 24/7 AI-powered assistant with conversation memory</p>
            </div>
        """, unsafe_allow_html=True)
        
        st.markdown("### How can we help you today?")
        
        col1, col2 = st.columns(2)
        
        with col1:
            st.markdown("""
                <div class="option-card">
                    <h3>Chat with AI Assistant</h3>
                    <p>Get instant answers about:</p>
                    <ul>
                        <li>Privacy Policy</li>
                        <li>Terms of Service</li>
                        <li>General Inquiries</li>
                        <li>Store Information</li>
                    </ul>
                    <p><em>Now with conversation memory!</em></p>
                </div>
            """, unsafe_allow_html=True)
            
            if st.button("Start Chat", key="start_chat", use_container_width=True):
                st.session_state.mode = "chat"
                st.session_state.messages.append({
                    "role": "assistant",
                    "content": "Hello! I'm your Shopify AI assistant. I'll remember our conversation to provide better help. How can I assist you today?"
                })
                save_chat_session(
                    st.session_state.current_session_id,
                    st.session_state.messages,
                    st.session_state.mode,
                    st.session_state.chatbot.export_context()
                )
                st.rerun()
        
        with col2:
            st.markdown("""
                <div class="option-card">
                    <h3>Order Management</h3>
                    <p>Manage your orders:</p>
                    <ul>
                        <li>Track Order Status</li>
                        <li>View Order Details</li>
                        <li>Request Refunds</li>
                        <li>Update Information</li>
                    </ul>
                </div>
            """, unsafe_allow_html=True)
            
            if st.button("Order Management", key="order_mgmt", use_container_width=True):
                st.session_state.mode = "order"
                st.rerun()
    
    elif st.session_state.mode == "order":
        # Order Management submenu
        if st.session_state.order_submenu is None:
            st.markdown("""
                <div class="header-container">
                    <h2>Order Management</h2>
                </div>
            """, unsafe_allow_html=True)
            
            col1, col2 = st.columns([1, 5])
            with col1:
                if st.button("Back", use_container_width=True):
                    st.session_state.mode = None
                    st.rerun()
            
            st.markdown("### Select an option:")
            
            col1, col2 = st.columns(2)
            
            with col1:
                st.markdown("""
                    <div class="option-card">
                        <h3>View Order Details</h3>
                        <p>Check your order status and information</p>
                    </div>
                """, unsafe_allow_html=True)
                
                if st.button("View Order", key="view_order", use_container_width=True):
                    st.session_state.order_submenu = "view"
                    st.rerun()
            
            with col2:
                st.markdown("""
                    <div class="option-card">
                        <h3>Process Refund</h3>
                        <p>Request a refund for your order</p>
                    </div>
                """, unsafe_allow_html=True)
                
                if st.button("Process Refund", key="process_refund", use_container_width=True):
                    st.session_state.order_submenu = "refund"
                    st.rerun()
        
        elif st.session_state.order_submenu == "view":
            st.markdown("""
                <div class="header-container">
                    <h2>View Order Details</h2>
                </div>
            """, unsafe_allow_html=True)
            
            col1, col2 = st.columns([1, 5])
            with col1:
                if st.button("Back", use_container_width=True):
                    st.session_state.order_submenu = None
                    st.rerun()
            
            st.markdown("### Enter your order ID:")
            order_id = st.text_input("Order ID", placeholder="e.g., 1234", key="view_order_id")
            
            if st.button("View Details", use_container_width=True):
                if order_id.strip():
                    order_id = order_id.strip().lstrip('#')
                    
                    if order_id.isdigit():
                        result = st.session_state.chatbot.orders.format_order_response(order_id)
                        result_html = result.replace('\n', '<br/>')
                        st.markdown(
                            f"""
                            <div class="chat-message bot-message" style="max-width: 100%; margin: 1rem 0;">
                                {result_html}
                            </div>
                            """,
                            unsafe_allow_html=True
                        )
                    else:
                        st.markdown(
                            """
                            <div style="background-color: #fee2e2; border-left: 4px solid #ef4444; 
                                        color: #991b1b; padding: 1rem; border-radius: 8px; margin: 1rem 0;">
                                <strong>Error:</strong> Please enter a valid order ID (numbers only)
                            </div>
                            """,
                            unsafe_allow_html=True
                        )
                else:
                    st.markdown(
                        """
                        <div style="background-color: #fee2e2; border-left: 4px solid #ef4444; 
                                    color: #991b1b; padding: 1rem; border-radius: 8px; margin: 1rem 0;">
                            <strong>Error:</strong> Order ID cannot be empty
                        </div>
                        """,
                        unsafe_allow_html=True
                    )
        
        elif st.session_state.order_submenu == "refund":
            st.markdown("""
                <div class="header-container">
                    <h2>Process Refund</h2>
                </div>
            """, unsafe_allow_html=True)
            
            col1, col2 = st.columns([1, 5])
            with col1:
                if st.button("Back", use_container_width=True):
                    st.session_state.order_submenu = None
                    if 'refund_confirmation' in st.session_state:
                        del st.session_state.refund_confirmation
                    if 'refund_order_id_confirmed' in st.session_state:
                        del st.session_state.refund_order_id_confirmed
                    st.rerun()
            
            if st.session_state.get('refund_confirmation', False):
                order_id = st.session_state.get('refund_order_id_confirmed', '')
                st.warning(f"You are about to process a refund for order #{order_id}")
                
                col1, col2 = st.columns(2)
                with col1:
                    if st.button("Confirm Refund", use_container_width=True):
                        result = st.session_state.chatbot.orders.process_refund(order_id)
                        result_html = result.replace('\n', '<br/>')
                        st.markdown(
                            f"""
                            <div class="chat-message bot-message" style="max-width: 100%; margin: 1rem 0;">
                                {result_html}
                            </div>
                            """,
                            unsafe_allow_html=True
                        )
                        st.session_state.refund_confirmation = False
                        del st.session_state.refund_order_id_confirmed
                with col2:
                    if st.button("Cancel", use_container_width=True):
                        st.info("Refund cancelled")
                        st.session_state.refund_confirmation = False
                        if 'refund_order_id_confirmed' in st.session_state:
                            del st.session_state.refund_order_id_confirmed
                        st.rerun()
            else:
                st.markdown("### Enter your order ID for refund:")
                order_id = st.text_input("Order ID", placeholder="e.g., 1234", key="refund_order_id")
                
                if st.button("Request Refund", use_container_width=True):
                    if order_id.strip():
                        order_id = order_id.strip().lstrip('#')
                        
                        if order_id.isdigit():
                            st.session_state.refund_confirmation = True
                            st.session_state.refund_order_id_confirmed = order_id
                            st.rerun()
                        else:
                            st.markdown(
                                """
                                <div style="background-color: #fee2e2; border-left: 4px solid #ef4444; 
                                            color: #991b1b; padding: 1rem; border-radius: 8px; margin: 1rem 0;">
                                    <strong>Error:</strong> Please enter a valid order ID (numbers only)
                                </div>
                                """,
                                unsafe_allow_html=True
                            )
                    else:
                        st.markdown(
                            """
                            <div style="background-color: #fee2e2; border-left: 4px solid #ef4444; 
                                        color: #991b1b; padding: 1rem; border-radius: 8px; margin: 1rem 0;">
                                <strong>Error:</strong> Order ID cannot be empty
                            </div>
                            """,
                            unsafe_allow_html=True
                        )
    
    else:
        # Chat interface
        st.markdown("""
            <div class="header-container">
                <h2>Chat with AI Assistant</h2>
            </div>
        """, unsafe_allow_html=True)
        
        # Back button
        col1, col2 = st.columns([1, 5])
        with col1:
            if st.button("Back", use_container_width=True):
                st.session_state.mode = None
                st.rerun()
        
        # Display chat messages
        chat_container = st.container()
        with chat_container:
            for message in st.session_state.messages:
                is_user = message["role"] == "user"
                render_message(message["content"], is_user)
            
            if st.session_state.typing:
                st.markdown(display_typing_indicator(), unsafe_allow_html=True)
        
        # Chat input
        user_input = st.chat_input("Type your message here...")
        
        if user_input:
            st.session_state.messages.append({
                "role": "user",
                "content": user_input
            })
            
            st.session_state.pending_input = user_input
            st.session_state.typing = True
            st.rerun()
        
        # Process bot response
        if st.session_state.typing:
            if st.session_state.pending_input:
                with st.spinner(""):
                    time.sleep(0.5)
                    
                    bot_response = st.session_state.chatbot.chat(st.session_state.pending_input)
                    
                    st.session_state.messages.append({
                        "role": "assistant",
                        "content": bot_response
                    })
                    
                    # Save with context
                    save_chat_session(
                        st.session_state.current_session_id,
                        st.session_state.messages,
                        st.session_state.mode,
                        st.session_state.chatbot.export_context()
                    )
                    
                    st.session_state.typing = False
                    st.session_state.pending_input = None
                    st.rerun()
            else:
                st.session_state.typing = False
                st.rerun()

if __name__ == "__main__":
    main()