import streamlit as st
import requests
import pandas as pd
import plotly.express as px
import plotly.graph_objects as go
from datetime import datetime
from typing import List, Dict

# Configuration
API_BASE_URL = "http://localhost:8000"

st.set_page_config(
    page_title="AI Knowledge Gap Detector",
    page_icon="🧠",
    layout="wide",
    initial_sidebar_state="expanded"
)

# Initialize theme in session state
if 'theme' not in st.session_state:
    st.session_state.theme = 'light'

# Theme CSS function
def get_theme_css(theme):
    """Generate CSS based on selected theme"""
    if theme == 'dark':
        return """
        <style>
        /* Dark Theme */
        :root {
            --bg-primary: #0f172a;
            --bg-secondary: #1e293b;
            --bg-card: #1e293b;
            --bg-input: #1e293b;
            --text-primary: #f1f5f9;
            --text-secondary: #cbd5e1;
            --border-color: #334155;
            --accent: #3b82f6;
        }
        
        /* Hide Streamlit default elements */
        #MainMenu {visibility: hidden !important;}
        footer {visibility: hidden !important;}
        header {visibility: hidden !important;}
        .stDeployButton {display: none !important;}
        [data-testid="stHeader"] {display: none !important;}
        [data-testid="stToolbar"] {display: none !important;}
        [data-testid="stDecoration"] {display: none !important;}
        
        /* Main background */
        .stApp {
            background-color: var(--bg-primary) !important;
        }
        
        .main .block-container {
            padding-top: 2rem;
            padding-bottom: 2rem;
            max-width: 1400px;
            background-color: var(--bg-primary);
        }
        
        /* Sidebar */
        [data-testid="stSidebar"] {
            background-color: var(--bg-secondary) !important;
        }
        
        [data-testid="stSidebar"] > div:first-child {
            background-color: var(--bg-secondary) !important;
        }
        
        [data-testid="stSidebar"] * {
            color: var(--text-primary) !important;
        }
        
        /* Text colors */
        .main *,
        p, span, div, label, h1, h2, h3, h4, h5, h6,
        .stMarkdown,
        .element-container {
            color: var(--text-primary) !important;
        }
        
        /* Header */
        .main-header {
            font-size: 2.5rem;
            font-weight: 700;
            color: var(--text-primary);
            margin-bottom: 0.5rem;
            letter-spacing: -0.03em;
            line-height: 1.2;
        }
        
        .sub-header {
            font-size: 1rem;
            color: var(--text-secondary);
            margin-bottom: 2.5rem;
            font-weight: 400;
        }
        
        /* Section headers */
        h2 {
            color: var(--text-primary) !important;
            border-bottom: 2px solid var(--border-color);
        }
        
        h3 {
            color: var(--text-primary) !important;
        }
        
        /* Cards */
        .gap-card {
            background: var(--bg-card) !important;
            border: 1px solid var(--border-color) !important;
        }
        
        .answer-container {
            background: var(--bg-card) !important;
            border-left: 5px solid var(--accent) !important;
        }
        
        /* Input fields */
        .stTextInput > div > div > input {
            background-color: var(--bg-input) !important;
            color: var(--text-primary) !important;
            border: 1.5px solid var(--border-color) !important;
        }
        
        .stTextInput > div > div > input:focus {
            border-color: var(--accent) !important;
        }
        
        /* Select boxes */
        .stSelectbox > div > div > select {
            background-color: var(--bg-input) !important;
            color: var(--text-primary) !important;
            border: 1.5px solid var(--border-color) !important;
        }
        
        /* Sliders */
        .stSlider > div > div {
            background-color: var(--bg-input) !important;
        }
        
        /* Buttons */
        .stButton > button {
            background-color: var(--accent) !important;
            color: #ffffff !important;
        }
        
        /* Radio buttons */
        [data-testid="stRadio"] label {
            color: var(--text-primary) !important;
        }
        
        /* Expander */
        .streamlit-expanderHeader {
            background-color: var(--bg-card) !important;
            color: var(--text-primary) !important;
        }
        
        /* Metrics */
        [data-testid="stMetricValue"] {
            color: var(--text-primary) !important;
        }
        
        [data-testid="stMetricLabel"] {
            color: var(--text-secondary) !important;
        }
        
        /* Dataframe */
        .dataframe {
            background-color: var(--bg-card) !important;
        }
        
        /* Tech badge */
        .tech-badge {
            background: var(--bg-secondary) !important;
            color: var(--text-secondary) !important;
            border: 1px solid var(--border-color) !important;
        }
        </style>
        """
    else:
        return """
        <style>
        /* Light Theme */
        :root {
            --bg-primary: #ffffff;
            --bg-secondary: #f8fafc;
            --bg-card: #ffffff;
            --bg-input: #ffffff;
            --text-primary: #1e293b;
            --text-secondary: #64748b;
            --border-color: #e2e8f0;
            --accent: #667eea;
        }
        
        /* Hide Streamlit default elements */
        #MainMenu {visibility: hidden !important;}
        footer {visibility: hidden !important;}
        header {visibility: hidden !important;}
        .stDeployButton {display: none !important;}
        [data-testid="stHeader"] {display: none !important;}
        [data-testid="stToolbar"] {display: none !important;}
        [data-testid="stDecoration"] {display: none !important;}
        
        /* Main background */
        .stApp {
            background-color: var(--bg-primary) !important;
        }
        
        .main .block-container {
            padding-top: 2rem;
            padding-bottom: 2rem;
            max-width: 1400px;
        }
        
        /* Sidebar */
        [data-testid="stSidebar"] {
            background-color: #ffffff !important;
        }
        
        [data-testid="stSidebar"] > div:first-child {
            background-color: #ffffff !important;
        }
        
        [data-testid="stSidebar"] * {
            color: #1e293b !important;
        }
        
        /* Text colors */
        .main *,
        p, span, div, label, h1, h2, h3, h4, h5, h6,
        .stMarkdown,
        .element-container {
            color: #1e293b !important;
        }
        
        /* Header */
        .main-header {
            font-size: 2.5rem;
            font-weight: 700;
            color: #1e293b;
            margin-bottom: 0.5rem;
            letter-spacing: -0.03em;
            line-height: 1.2;
        }
        
        .sub-header {
            font-size: 1rem;
            color: #64748b;
            margin-bottom: 2.5rem;
            font-weight: 400;
        }
        
        /* Section headers */
        h2 {
            color: #1e293b !important;
            border-bottom: 2px solid #e2e8f0;
        }
        
        h3 {
            color: #1e293b !important;
        }
        
        /* Cards */
        .gap-card {
            background: #ffffff !important;
            border: 1px solid #e2e8f0 !important;
        }
        
        .answer-container {
            background: #f8fafc !important;
            border-left: 5px solid #667eea !important;
        }
        
        /* Input fields - Light theme specific */
        .stTextInput > div > div > input {
            background-color: #ffffff !important;
            color: #1e293b !important;
            border: 1.5px solid #e2e8f0 !important;
        }
        
        .stTextInput > div > div > input::placeholder {
            color: #94a3b8 !important;
        }
        
        .stTextInput > div > div > input:focus {
            border-color: #667eea !important;
            box-shadow: 0 0 0 3px rgba(102, 126, 234, 0.1) !important;
            color: #1e293b !important;
        }
        
        /* Select boxes - Light theme specific - More specific selectors */
        div[data-baseweb="select"] {
            background-color: #ffffff !important;
        }
        
        div[data-baseweb="select"] > div {
            background-color: #ffffff !important;
            color: #1e293b !important;
        }
        
        .stSelectbox > div > div > div {
            background-color: #ffffff !important;
            color: #1e293b !important;
        }
        
        .stSelectbox > div > div > select {
            background-color: #ffffff !important;
            color: #1e293b !important;
            border: 1.5px solid #e2e8f0 !important;
        }
        
        .stSelectbox > div > div > select option {
            background-color: #ffffff !important;
            color: #1e293b !important;
        }
        
        /* BaseWeb select styling */
        [data-baseweb="select"] {
            background-color: #ffffff !important;
        }
        
        [data-baseweb="select"] > div {
            background-color: #ffffff !important;
            color: #1e293b !important;
        }
        
        [data-baseweb="select"] input {
            background-color: #ffffff !important;
            color: #1e293b !important;
        }
        
        /* Select box text visibility */
        .stSelectbox label {
            color: #1e293b !important;
        }
        
        .stSelectbox [data-baseweb="select"] {
            background-color: #ffffff !important;
        }
        
        .stSelectbox [data-baseweb="select"] > div {
            background-color: #ffffff !important;
            color: #1e293b !important;
        }
        
        /* Sliders - Light theme specific */
        .stSlider > div > div {
            background-color: #ffffff !important;
        }
        
        .stSlider > div > div > div {
            background-color: #ffffff !important;
        }
        
        /* Buttons - Light theme specific */
        .stButton > button {
            background-color: #667eea !important;
            color: #ffffff !important;
        }
        
        .stButton > button:hover {
            background-color: #5568d3 !important;
        }
        
        /* Radio buttons - Light theme specific */
        [data-testid="stRadio"] label {
            color: #1e293b !important;
        }
        
        /* Expander - Light theme specific */
        .streamlit-expanderHeader {
            background-color: #ffffff !important;
            color: #1e293b !important;
        }
        
        .streamlit-expanderContent {
            background-color: #ffffff !important;
        }
        
        [data-testid="stExpander"] {
            background-color: #ffffff !important;
        }
        
        /* Sidebar buttons - Light theme specific */
        [data-testid="stSidebar"] .stButton > button {
            background-color: #667eea !important;
            color: #ffffff !important;
        }
        
        [data-testid="stSidebar"] .stButton > button:hover {
            background-color: #5568d3 !important;
        }
        
        /* Question suggestion buttons in Query Interface */
        [data-testid="stButton"] > button {
            background-color: #667eea !important;
            color: #ffffff !important;
        }
        
        [data-testid="stButton"] > button:hover {
            background-color: #5568d3 !important;
        }
        
        /* Ensure all input text is visible - More specific */
        input[type="text"],
        input[type="search"],
        input[type="text"]:focus,
        textarea {
            color: #1e293b !important;
            background-color: #ffffff !important;
        }
        
        /* BaseWeb Select Component - More aggressive targeting */
        [data-baseweb="select"] {
            background-color: #ffffff !important;
        }
        
        [data-baseweb="select"] > div {
            background-color: #ffffff !important;
            color: #1e293b !important;
        }
        
        [data-baseweb="select"] > div > div {
            background-color: #ffffff !important;
            color: #1e293b !important;
        }
        
        [data-baseweb="select"] input {
            background-color: #ffffff !important;
            color: #1e293b !important;
        }
        
        [data-baseweb="select"] span {
            color: #1e293b !important;
        }
        
        /* Select box dropdown menu */
        [role="listbox"] {
            background-color: #ffffff !important;
        }
        
        [role="option"] {
            background-color: #ffffff !important;
            color: #1e293b !important;
        }
        
        [role="option"]:hover {
            background-color: #f1f5f9 !important;
            color: #1e293b !important;
        }
        
        /* Additional BaseWeb overrides */
        .stSelectbox [data-baseweb="select"] > div[aria-selected="true"] {
            background-color: #ffffff !important;
            color: #1e293b !important;
        }
        
        .stSelectbox [data-baseweb="select"] > div[aria-selected="false"] {
            background-color: #ffffff !important;
            color: #1e293b !important;
        }
        
        /* Metrics */
        [data-testid="stMetricValue"] {
            color: var(--text-primary) !important;
        }
        
        [data-testid="stMetricLabel"] {
            color: var(--text-secondary) !important;
        }
        
        /* Dataframe */
        .dataframe {
            background-color: var(--bg-card) !important;
        }
        
        /* Tech badge */
        .tech-badge {
            background: #f1f5f9 !important;
            color: #475569 !important;
            border: 1px solid var(--border-color) !important;
        }
        </style>
        """

# Apply theme CSS
st.markdown(get_theme_css(st.session_state.theme), unsafe_allow_html=True)

# Additional shared CSS
st.markdown("""
    <style>
    /* Professional gap cards */
    .gap-card {
        padding: 1.5rem;
        border-radius: 10px;
        border-left: 5px solid;
        margin: 1rem 0;
        box-shadow: 0 2px 8px rgba(0, 0, 0, 0.08);
        transition: all 0.3s ease;
    }
    
    .gap-card:hover {
        box-shadow: 0 4px 16px rgba(0, 0, 0, 0.12);
        transform: translateY(-2px);
    }
    
    .gap-high {
        border-left-color: #ef4444;
        background: linear-gradient(90deg, rgba(239, 68, 68, 0.05) 0%, var(--bg-card) 100%);
    }
    
    .gap-medium {
        border-left-color: #f59e0b;
        background: linear-gradient(90deg, rgba(245, 158, 11, 0.05) 0%, var(--bg-card) 100%);
    }
    
    .gap-low {
        border-left-color: #10b981;
        background: linear-gradient(90deg, rgba(16, 185, 129, 0.05) 0%, var(--bg-card) 100%);
    }
    
    /* Tech badge styling */
    .tech-badge {
        display: inline-block;
        padding: 0.35rem 0.85rem;
        border-radius: 6px;
        font-family: 'SF Mono', 'Monaco', 'Courier New', monospace;
        font-size: 0.8rem;
        font-weight: 500;
    }
    
    /* Status indicators */
    .status-online {
        display: inline-block;
        width: 10px;
        height: 10px;
        background: #10b981;
        border-radius: 50%;
        margin-right: 0.5rem;
        box-shadow: 0 0 0 2px rgba(16, 185, 129, 0.2);
    }
    
    .status-offline {
        display: inline-block;
        width: 10px;
        height: 10px;
        background: #ef4444;
        border-radius: 50%;
        margin-right: 0.5rem;
        box-shadow: 0 0 0 2px rgba(239, 68, 68, 0.2);
    }
    
    /* Answer container */
    .answer-container {
        padding: 1.75rem;
        border-radius: 10px;
        margin: 1.5rem 0;
        box-shadow: 0 2px 8px rgba(0, 0, 0, 0.06);
        line-height: 1.7;
    }
    
    /* Professional buttons */
    .stButton > button {
        border-radius: 8px;
        border: none;
        padding: 0.6rem 1.75rem;
        font-weight: 500;
        transition: all 0.2s ease;
        box-shadow: 0 2px 4px rgba(0, 0, 0, 0.1);
    }
    
    .stButton > button:hover {
        transform: translateY(-1px);
        box-shadow: 0 4px 8px rgba(0, 0, 0, 0.15);
    }
    
    /* Input fields */
    .stTextInput > div > div > input {
        border-radius: 8px;
        padding: 0.75rem 1rem;
        font-size: 0.95rem;
    }
    
    .stTextInput > div > div > input:focus {
        box-shadow: 0 0 0 3px rgba(102, 126, 234, 0.1);
    }
    
    /* Metrics styling */
    [data-testid="stMetricValue"] {
        font-size: 2rem;
        font-weight: 700;
    }
    
    [data-testid="stMetricLabel"] {
        font-size: 0.9rem;
        font-weight: 500;
    }
    
    /* Divider styling */
    hr {
        margin: 2rem 0;
        border: none;
        border-top: 1px solid var(--border-color);
    }
    
    /* Theme toggle button positioning */
    .theme-toggle-container {
        position: fixed;
        top: 20px;
        right: 20px;
        z-index: 999;
    }
    </style>
""", unsafe_allow_html=True)


@st.cache_data(ttl=60)
def fetch_gaps(severity: str = None, limit: int = 20):
    """Fetch knowledge gaps from API"""
    try:
        params = {"limit": limit}
        if severity:
            params["severity"] = severity
        response = requests.get(f"{API_BASE_URL}/gaps", params=params, timeout=5)
        if response.status_code == 200:
            return response.json()
        return []
    except:
        return []


@st.cache_data(ttl=60)
def fetch_statistics():
    """Fetch gap statistics from API"""
    try:
        response = requests.get(f"{API_BASE_URL}/gaps/stats", timeout=5)
        if response.status_code == 200:
            return response.json()
        return {}
    except:
        return {}


@st.cache_data(ttl=300)
def fetch_suggested_questions(num_questions: int = 15):
    """Fetch suggested questions from API"""
    try:
        response = requests.get(f"{API_BASE_URL}/suggested-questions", params={"num_questions": num_questions}, timeout=5)
        if response.status_code == 200:
            return response.json()
        return []
    except:
        return [
            "How do we handle deployment rollbacks?",
            "What is our incident response procedure?",
            "How do we troubleshoot service failures?",
            "What are the steps for database migrations?",
            "How do we handle payment gateway failures?"
        ]


def query_knowledge_base(question: str, user_id: str = None):
    """Query the knowledge base"""
    try:
        payload = {"question": question}
        if user_id:
            payload["user_id"] = user_id
        
        response = requests.post(f"{API_BASE_URL}/query", json=payload, timeout=30)
        if response.status_code == 200:
            return response.json()
        return None
    except Exception as e:
        return None


def check_api_health():
    """Check API health status"""
    try:
        response = requests.get(f"{API_BASE_URL}/health", timeout=5)
        if response.status_code == 200:
            return True, response.json()
        return False, None
    except:
        return False, None


def main():
    # Theme Toggle Button - Upper Right Corner
    # Use a container approach with proper column weights
    header_col1, header_col2 = st.columns([20, 1])
    
    with header_col1:
        # Professional Header
        st.markdown('<div class="main-header">Sentinel Knowledge</div>', unsafe_allow_html=True)
    
    with header_col2:
        # Theme toggle button
        current_theme = st.session_state.theme
        if current_theme == 'light':
            if st.button("🌙", key="theme_toggle", help="Switch to dark theme", use_container_width=True):
                st.session_state.theme = 'dark'
                st.rerun()
        else:
            if st.button("☀️", key="theme_toggle", help="Switch to light theme", use_container_width=True):
                st.session_state.theme = 'light'
                st.rerun()
    
    # Sub-header
    st.markdown('<div class="sub-header">Intelligent RAG system with automated knowledge gap detection and analysis</div>', unsafe_allow_html=True)
    
    st.markdown("<br>", unsafe_allow_html=True)  # Add spacing
    
    # Sidebar
    with st.sidebar:
        st.markdown("### Navigation")
        page = st.radio(
            "Select Page",
            ["Dashboard", "Query Interface", "Gap Analysis", "Confluence"],
            index=0,
            label_visibility="collapsed"
        )
        
        st.divider()
        
        st.markdown("### System Status")
        api_healthy, health_data = check_api_health()
        
        if api_healthy:
            st.markdown('<span class="status-online"></span><strong style="color: #10b981;">API Online</strong>', unsafe_allow_html=True)
            if health_data:
                vector_count = health_data.get("vector_store", {}).get("total_documents", 0)
                st.caption(f"Vector Store: **{vector_count}** documents")
        else:
            st.markdown('<span class="status-offline"></span><strong style="color: #ef4444;">API Offline</strong>', unsafe_allow_html=True)
            st.caption("Start the API server to enable features")
        
        st.divider()
        
        st.markdown("### Quick Actions")
        if st.button("Refresh Data", use_container_width=True):
            st.cache_data.clear()
            st.rerun()
        
        if st.button("API Documentation", use_container_width=True):
            st.markdown(f"[Open API Docs]({API_BASE_URL}/docs)")
    
    # Dashboard Page
    if page == "Dashboard":
        st.markdown("## Dashboard Overview")
        st.caption("Real-time insights into your knowledge base and detected gaps")
        
        # Fetch statistics
        stats = fetch_statistics()
        
        # Key Metrics
        st.markdown("### Key Metrics")
        col1, col2, col3, col4 = st.columns(4)
        
        with col1:
            total_queries = stats.get("total_queries", 0) if stats else 0
            st.metric("Total Queries", f"{total_queries:,}")
        
        with col2:
            total_gaps = stats.get("total_gaps", 0) if stats else 0
            st.metric("Knowledge Gaps", f"{total_gaps:,}")
        
        with col3:
            gap_rate = stats.get("gap_rate", 0) if stats else 0
            st.metric("Gap Rate", f"{gap_rate:.1%}" if gap_rate > 0 else "0%")
        
        with col4:
            high_severity = stats.get("severity_breakdown", {}).get("high", 0) if stats else 0
            st.metric("High Severity", f"{high_severity:,}")
        
        st.divider()
        
        # Visualizations
        st.markdown("### Analytics")
        col1, col2 = st.columns(2)
        
        with col1:
            st.markdown("#### Gap Type Distribution")
            if stats and stats.get("gap_types"):
                gap_types = stats.get("gap_types", {})
                fig = px.pie(
                    values=list(gap_types.values()),
                    names=list(gap_types.keys()),
                    color_discrete_sequence=['#667eea', '#764ba2', '#f093fb', '#4facfe', '#00f2fe']
                )
                fig.update_layout(
                    showlegend=True,
                    margin=dict(l=20, r=20, t=20, b=20),
                    font=dict(size=12),
                    height=350
                )
                st.plotly_chart(fig, use_container_width=True)
            else:
                st.info("No gap type data available. Start querying to generate insights.")
        
        with col2:
            st.markdown("#### Severity Breakdown")
            if stats and stats.get("severity_breakdown"):
                severity = stats.get("severity_breakdown", {})
                fig = px.bar(
                    x=list(severity.keys()),
                    y=list(severity.values()),
                    labels={"x": "Severity Level", "y": "Count"},
                    color=list(severity.keys()),
                    color_discrete_map={"high": "#ef4444", "medium": "#f59e0b", "low": "#10b981"}
                )
                fig.update_layout(
                    showlegend=False,
                    margin=dict(l=20, r=20, t=20, b=20),
                    font=dict(size=12),
                    height=350
                )
                st.plotly_chart(fig, use_container_width=True)
            else:
                st.info("No severity data available. Start querying to generate insights.")
        
        # Top Gaps Section
        st.divider()
        st.markdown("### Top Knowledge Gaps")
        st.caption("Most critical knowledge gaps requiring attention")
        
        gaps = fetch_gaps(limit=10)
        
        if gaps:
            for gap in gaps:
                # Use Streamlit components with proper formatting
                gap_type_display = gap['gap_type'].replace('_', ' ')
                severity_display = gap['severity'].upper()
                
                # Create a card-like container
                with st.container():
                    # Query
                    st.markdown(f"**{gap['query']}**")
                    
                    # Gap type, occurrences, severity
                    st.text(f"{gap_type_display} • Occurrences: {gap['occurrence_count']} • Severity: {severity_display}")
                    
                    # Source page/document
                    if gap.get('source_page_title'):
                        st.text(f"📄 Source Page: {gap.get('source_page_title')}")
                    elif gap.get('source_document'):
                        st.text(f"📄 Source: {gap.get('source_document')}")
                    
                    # Suggested topic
                    st.text(f"Suggested Topic: {gap.get('suggested_topic', 'N/A')}")
                    
                    st.divider()
        else:
            st.info("**No knowledge gaps detected yet.**")
            st.markdown("""
            **Getting Started:**
            1. Ingest documents or Confluence pages via the API
            2. Ask questions via the Query Interface
            3. Gaps will be automatically detected and displayed here
            """)
    
    # Query Interface
    elif page == "Query Interface":
        st.markdown("## Query Knowledge Base")
        st.caption("Ask questions about your documentation. The system will automatically detect knowledge gaps.")
        
        # Suggested Questions Section
        with st.expander("Suggested Questions", expanded=True):
            st.caption("Questions generated from your knowledge base content. Click any question to use it.")
            
            with st.spinner("Loading suggested questions..."):
                suggested_questions = fetch_suggested_questions(num_questions=15)
            
            if not suggested_questions:
                st.info("No content in knowledge base. Please ingest documents first.")
                suggested_questions = [
                    "How do we handle deployment rollbacks?",
                    "What is our incident response procedure?",
                    "How do we troubleshoot service failures?"
                ]
            
            num_cols = 3
            cols = st.columns(num_cols)
            
            if 'selected_question' not in st.session_state:
                st.session_state['selected_question'] = ""
            
            for idx, suggested_q in enumerate(suggested_questions):
                col_idx = idx % num_cols
                with cols[col_idx]:
                    button_text = suggested_q if len(suggested_q) <= 50 else suggested_q[:47] + "..."
                    if st.button(button_text, key=f"suggest_{idx}", use_container_width=True):
                        st.session_state['selected_question'] = suggested_q
                        st.rerun()
        
        st.divider()
        
        # Query Input
        st.markdown("### Ask a Question")
        question = st.text_input(
            "Enter your question:",
            value=st.session_state.get('selected_question', ''),
            placeholder="e.g., How do we handle deployment rollbacks?",
            key="question_input",
            label_visibility="collapsed"
        )
        
        col1, col2 = st.columns([1, 5])
        with col1:
            query_clicked = st.button("Query", type="primary", use_container_width=True)
        
        if query_clicked and question:
            if 'selected_question' in st.session_state:
                st.session_state['selected_question'] = ""
            
            with st.spinner("Analyzing knowledge base..."):
                result = query_knowledge_base(question)
                
                if result:
                    st.divider()
                    st.markdown("### Answer")
                    
                    st.markdown(f"""
                    <div class="answer-container">
                        {result["answer"]}
                    </div>
                    """, unsafe_allow_html=True)
                    
                    # Sources
                    if result.get("sources"):
                        with st.expander("Source Documents", expanded=False):
                            for source in result["sources"]:
                                st.markdown(f"• `{source}`")
                    
                    # Confidence and Status
                    col1, col2 = st.columns(2)
                    with col1:
                        confidence = result.get("confidence_score", 0)
                        st.metric("Confidence Score", f"{confidence:.1%}")
                        st.progress(confidence)
                    
                    with col2:
                        if result.get("is_gap"):
                            st.error(f"**Knowledge Gap Detected**\n\n**Type:** `{result.get('gap_reason', 'Unknown')}`")
                        else:
                            st.success("**Answer Found**\n\nAnswer retrieved from knowledge base")
                    
                    # Technical Details
                    if result.get("similarity_scores"):
                        with st.expander("Retrieval Metrics", expanded=False):
                            st.markdown("**Similarity Scores:**")
                            for i, score in enumerate(result["similarity_scores"], 1):
                                st.code(f"Document {i}: {score:.3f}")
                else:
                    st.error("**Failed to query knowledge base.**\n\nPlease check:\n- API server is running\n- Network connection\n- API endpoint is accessible")
        elif query_clicked and not question:
            st.warning("Please enter a question first.")
    
    # Gap Analysis
    elif page == "Gap Analysis":
        st.markdown("## Detailed Gap Analysis")
        st.caption("Comprehensive analysis of detected knowledge gaps across your entire document collection")
        
        # Info box explaining collection-wide analysis
        st.info("""
        **📊 Collection-Wide Gap Analysis**
        
        This section analyzes knowledge gaps across your **entire document collection**, including:
        - All ingested Confluence pages
        - All uploaded documents (PDF, DOCX, TXT, Markdown)
        - Questions asked through the Query Interface
        
        Gaps are automatically detected when queries cannot be answered well from your knowledge base.
        Each gap shows which document or page it originated from (if available).
        """)
        
        # Button to analyze all Confluence data
        st.markdown("---")
        st.markdown("### Analyze All Confluence Data")
        col1, col2 = st.columns([3, 1])
        with col1:
            st.markdown("""
            **Analyze your entire Confluence collection for knowledge gaps.**
            
            This will generate questions based on all your Confluence content, query them through the knowledge base,
            and automatically detect gaps. Results will appear below.
            """)
        with col2:
            if st.button("🔍 Analyze Confluence Data", type="primary", use_container_width=True):
                st.session_state["analyze_confluence"] = True
        
        if st.session_state.get("analyze_confluence", False):
            with st.spinner("Analyzing all Confluence data... This may take a few minutes."):
                try:
                    analysis_response = requests.post(
                        f"{API_BASE_URL}/analyze/confluence/all",
                        json={"num_questions": 10},  # Reduced to 10 for faster processing
                        timeout=900  # 15 minutes timeout
                    )
                    if analysis_response.status_code == 200:
                        analysis_data = analysis_response.json()
                        st.success(f"✅ Analysis completed!")
                        
                        # Show summary
                        col1, col2, col3, col4 = st.columns(4)
                        with col1:
                            st.metric("Confluence Pages", analysis_data.get("total_confluence_pages", 0))
                        with col2:
                            st.metric("Total Chunks", analysis_data.get("total_confluence_chunks", 0))
                        with col3:
                            st.metric("Questions Analyzed", analysis_data.get("questions_analyzed", 0))
                        with col4:
                            st.metric("Gaps Detected", analysis_data.get("gaps_detected", 0))
                        
                        st.info("💡 **Scroll down to see all detected gaps below!**")
                        st.session_state["analyze_confluence"] = False
                    else:
                        st.error(f"Analysis failed: {analysis_response.text}")
                        st.session_state["analyze_confluence"] = False
                except Exception as e:
                    st.error(f"Error during analysis: {str(e)}")
                    st.session_state["analyze_confluence"] = False
        
        st.markdown("---")
        
        # Filters
        with st.expander("Filters & Search", expanded=True):
            col1, col2, col3 = st.columns(3)
            with col1:
                severity_filter = st.selectbox("Filter by Severity", ["All", "high", "medium", "low"], index=0)
            with col2:
                gap_type_filter = st.selectbox(
                    "Filter by Gap Type",
                    ["All", "low_similarity", "repeated_query", "uncertainty", "empty_retrieval"],
                    index=0
                )
            with col3:
                limit = st.slider("Results Limit", 5, 100, 20)
            
            search_query = st.text_input("Search", placeholder="Search gaps by query text...", label_visibility="collapsed")
        
        # Fetch and filter gaps from entire collection
        all_gaps = fetch_gaps(limit=1000)
        
        if all_gaps and len(all_gaps) > 0:
            df = pd.DataFrame(all_gaps)
            
            # Apply filters
            if severity_filter != "All":
                df = df[df["severity"] == severity_filter]
            if gap_type_filter != "All":
                df = df[df["gap_type"] == gap_type_filter]
            if search_query:
                df = df[df["query"].str.contains(search_query, case=False, na=False)]
            
            df = df.head(limit)
            
            # Calculate priority
            def calculate_priority(row):
                severity_scores = {"high": 3, "medium": 2, "low": 1}
                return severity_scores.get(row["severity"], 0) * row["occurrence_count"]
            
            df["priority_score"] = df.apply(calculate_priority, axis=1)
            df = df.sort_values("priority_score", ascending=False)
            
            # Summary Metrics
            st.markdown("### Summary Metrics")
            col1, col2, col3, col4 = st.columns(4)
            with col1:
                st.metric("Total Gaps", f"{len(df):,}")
            with col2:
                high_priority = len(df[df["priority_score"] >= 6])
                st.metric("High Priority", f"{high_priority:,}")
            with col3:
                avg_occ = df["occurrence_count"].mean() if len(df) > 0 else 0
                st.metric("Avg Occurrences", f"{avg_occ:.1f}")
            with col4:
                total_affected = df["occurrence_count"].sum() if len(df) > 0 else 0
                st.metric("Total Affected", f"{total_affected:,}")
            
            st.divider()
            
            # Export and Table
            col1, col2 = st.columns([4, 1])
            with col1:
                st.markdown("### Gap Details")
            with col2:
                csv = df.to_csv(index=False).encode('utf-8')
                st.download_button("Export CSV", csv, "knowledge_gaps.csv", "text/csv", use_container_width=True)
            
            # Add source file/page column
            def get_source_info(row):
                if row.get('source_page_title'):
                    return row['source_page_title']
                elif row.get('source_document'):
                    return row['source_document']
                else:
                    return "Unknown"
            
            df["source_file"] = df.apply(get_source_info, axis=1)
            
            display_df = df[["query", "gap_type", "severity", "occurrence_count", "priority_score", "suggested_topic", "source_file"]].copy()
            display_df.columns = ["Query", "Type", "Severity", "Occurrences", "Priority", "Suggested Topic", "Source File/Page"]
            
            st.dataframe(
                display_df,
                use_container_width=True,
                height=400,
                hide_index=True
            )
            
            st.divider()
            
            # Visualizations
            st.markdown("### Visualizations")
            col1, col2 = st.columns(2)
            
            with col1:
                st.markdown("#### Gap Type Distribution")
                if len(df) > 0:
                    gap_type_counts = df["gap_type"].value_counts()
                    fig = px.pie(
                        values=gap_type_counts.values,
                        names=gap_type_counts.index,
                        color_discrete_sequence=px.colors.qualitative.Set3
                    )
                    fig.update_layout(showlegend=True, margin=dict(l=20, r=20, t=20, b=20), height=350)
                    st.plotly_chart(fig, use_container_width=True)
                else:
                    st.info("No gap type data available")
            
            with col2:
                st.markdown("#### Top Queries by Priority")
                if len(df) > 0:
                    top_queries = df.nlargest(10, "priority_score")
                    fig = px.bar(
                        x=top_queries["priority_score"],
                        y=top_queries["query"],
                        orientation='h',
                        color=top_queries["severity"],
                        color_discrete_map={"high": "#ef4444", "medium": "#f59e0b", "low": "#10b981"},
                        labels={"x": "Priority Score", "y": ""}
                    )
                    fig.update_layout(showlegend=False, margin=dict(l=20, r=20, t=20, b=20), height=350)
                    st.plotly_chart(fig, use_container_width=True)
            
            # Action Items
            st.divider()
            st.markdown("### Recommended Action Items")
            
            high_priority_gaps = df[df["priority_score"] >= 6].head(5)
            if len(high_priority_gaps) > 0:
                for idx, gap in high_priority_gaps.iterrows():
                    with st.expander(f"Priority {int(gap['priority_score'])}: {gap['query'][:70]}..."):
                        col1, col2 = st.columns(2)
                        with col1:
                            st.markdown(f"**Type:** `{gap['gap_type']}`")
                            st.markdown(f"**Severity:** {gap['severity'].upper()}")
                            st.markdown(f"**Occurrences:** {gap['occurrence_count']}")
                        with col2:
                            st.markdown(f"**Suggested Topic:** {gap.get('suggested_topic', 'N/A')}")
                        
                        # Show source file/page information
                        source_info = gap.get('source_page_title') or gap.get('source_document') or 'Unknown'
                        st.markdown(f"**📄 Source File/Page:** {source_info}")
                        
                        st.markdown("**Recommended Action:**")
                        if gap['gap_type'] == 'empty_retrieval':
                            st.info(f"**Create documentation** for: {gap.get('suggested_topic', gap['query'])}")
                        elif gap['gap_type'] == 'repeated_query':
                            st.warning(f"**Create FAQ** - This question has been asked {gap['occurrence_count']} times")
                        else:
                            st.info(f"**Enhance documentation** related to: {gap.get('suggested_topic', 'this topic')}")
            else:
                st.success("**No high-priority gaps** requiring immediate attention!")
        else:
            st.warning("**No knowledge gaps detected yet.**")
            st.markdown("""
            **To generate gap analysis for your Confluence data:**
            
            1. **Go to Confluence section** - Click "Confluence" in the sidebar
            2. **Click "Analyze All Confluence Data for Gaps"** - This will analyze your entire Confluence collection
            3. **View results here** - All detected gaps will appear in this section
            
            **Or generate gaps by querying:**
            - Use the Query Interface to ask questions
            - Gaps are detected automatically when:
              - Questions can't be answered well (low similarity scores)
              - No relevant documents are found
              - Answers contain uncertainty phrases
              - Same questions are asked repeatedly
            
            **Once you have gaps, they will appear here with:**
            - Query that revealed the gap
            - Gap type and severity
            - Source document/page (if available)
            - Suggested documentation topics
            """)
            
            # Show statistics even if no gaps
            try:
                stats_response = requests.get(f"{API_BASE_URL}/gaps/stats", timeout=5)
                if stats_response.status_code == 200:
                    stats = stats_response.json()
                    st.markdown("### Current Statistics")
                    col1, col2, col3 = st.columns(3)
                    with col1:
                        st.metric("Total Queries", stats.get("total_queries", 0))
                    with col2:
                        st.metric("Total Gaps", stats.get("total_gaps", 0))
                    with col3:
                        gap_rate = stats.get("gap_rate", 0) * 100
                        st.metric("Gap Rate", f"{gap_rate:.1f}%")
            except:
                pass
    
    # Confluence Integration Page
    elif page == "Confluence":
        st.markdown("## Confluence Integration")
        st.caption("View and manage your Confluence spaces and pages")
        
        # Fetch Confluence spaces
        @st.cache_data(ttl=300)
        def fetch_confluence_spaces():
            """Fetch Confluence spaces from API"""
            try:
                response = requests.get(f"{API_BASE_URL}/confluence/spaces", timeout=10)
                if response.status_code == 200:
                    return response.json()
                return None
            except Exception as e:
                return None
        
        with st.spinner("Loading Confluence spaces..."):
            confluence_data = fetch_confluence_spaces()
        
        if confluence_data:
            spaces = confluence_data.get("spaces", [])
            count = confluence_data.get("count", 0)
            
            st.markdown("### Available Spaces")
            st.caption(f"Found {count} accessible Confluence space(s)")
            
            if spaces:
                # Display spaces in cards
                for space in spaces:
                    space_type = space.get("type", "unknown")
                    space_key = space.get("key", "")
                    space_name = space.get("name", "Unnamed Space")
                    
                    with st.expander(f"📁 {space_name} ({space_type})", expanded=False):
                        col1, col2 = st.columns(2)
                        with col1:
                            st.markdown(f"**Space Key:** `{space_key}`")
                            st.markdown(f"**Type:** {space_type}")
                        with col2:
                            # Button to view pages
                            if st.button(f"View Pages", key=f"view_{space_key}", use_container_width=True):
                                st.session_state[f"selected_space_{space_key}"] = True
                        
                        # Fetch and display pages if button clicked
                        if st.session_state.get(f"selected_space_{space_key}", False):
                            with st.spinner(f"Loading pages from {space_name}..."):
                                try:
                                    pages_response = requests.get(
                                        f"{API_BASE_URL}/confluence/spaces/{space_key}/pages",
                                        params={"limit": 50},
                                        timeout=10
                                    )
                                    if pages_response.status_code == 200:
                                        pages_data = pages_response.json()
                                        pages = pages_data.get("pages", [])
                                        st.markdown(f"**Pages in this space:** {len(pages)}")
                                        
                                        if pages:
                                            # Create a selectbox for page selection
                                            page_options = {f"{p.get('title', 'Untitled')} (ID: {p.get('id')})": p.get('id') for p in pages}
                                            selected_page_label = st.selectbox(
                                                "Select a page to view full content:",
                                                options=list(page_options.keys()),
                                                key=f"page_select_{space_key}",
                                                index=0 if pages else None
                                            )
                                            
                                            if selected_page_label:
                                                selected_page_id = page_options[selected_page_label]
                                                
                                                # Button to fetch and display full content
                                                if st.button(f"View Full Content", key=f"view_content_{space_key}_{selected_page_id}"):
                                                    st.session_state[f"viewing_page_{selected_page_id}"] = True
                                                
                                                # Display full content if button clicked
                                                if st.session_state.get(f"viewing_page_{selected_page_id}", False):
                                                    with st.spinner("Loading page content..."):
                                                        try:
                                                            page_response = requests.get(
                                                                f"{API_BASE_URL}/confluence/pages/{selected_page_id}",
                                                                timeout=15
                                                            )
                                                            if page_response.status_code == 200:
                                                                page_data = page_response.json()
                                                                
                                                                # Display page metadata
                                                                st.markdown("---")
                                                                st.markdown(f"### {page_data.get('title', 'Untitled')}")
                                                                
                                                                col1, col2, col3 = st.columns(3)
                                                                with col1:
                                                                    st.caption(f"**Space:** {page_data.get('space_name', 'Unknown')}")
                                                                with col2:
                                                                    st.caption(f"**Author:** {page_data.get('author', 'Unknown')}")
                                                                with col3:
                                                                    st.caption(f"**Version:** {page_data.get('version', 'N/A')}")
                                                                
                                                                if page_data.get('last_modified'):
                                                                    st.caption(f"**Last Modified:** {page_data.get('last_modified')}")
                                                                
                                                                if page_data.get('url'):
                                                                    st.markdown(f"[🔗 Open in Confluence]({page_data.get('url')})")
                                                                
                                                                st.markdown("---")
                                                                
                                                                # Display full content
                                                                st.markdown("### Full Content")
                                                                content = page_data.get('content', '')
                                                                if content:
                                                                    # Display content in a scrollable container (not an expander to avoid nesting)
                                                                    # Use markdown with proper escaping
                                                                    import html
                                                                    escaped_content = html.escape(content)
                                                                    st.markdown(
                                                                        f"""
                                                                        <div style="
                                                                            max-height: 500px;
                                                                            overflow-y: auto;
                                                                            padding: 1rem;
                                                                            background-color: {'#ffffff' if st.session_state.theme == 'light' else '#1e293b'};
                                                                            border: 1px solid {'#e2e8f0' if st.session_state.theme == 'light' else '#334155'};
                                                                            border-radius: 8px;
                                                                            margin: 1rem 0;
                                                                        ">
                                                                            <div style="white-space: pre-wrap; line-height: 1.6; color: {'#1e293b' if st.session_state.theme == 'light' else '#f1f5f9'};">
                                                                                {escaped_content}
                                                                            </div>
                                                                        </div>
                                                                        """,
                                                                        unsafe_allow_html=True
                                                                    )
                                                                    
                                                                    # Show content stats
                                                                    word_count = len(content.split())
                                                                    char_count = len(content)
                                                                    st.caption(f"Content: {word_count} words, {char_count} characters")
                                                                else:
                                                                    st.info("This page has no content.")
                                                            else:
                                                                st.error(f"Could not load page content: {page_response.status_code}")
                                                                st.text(page_response.text[:500])
                                                        except Exception as e:
                                                            st.error(f"Error loading page content: {str(e)}")
                                            
                                            # Also show list of all pages
                                            st.markdown("---")
                                            st.markdown(f"**All Pages ({len(pages)}):**")
                                            for page in pages[:20]:  # Show first 20
                                                st.markdown(f"• **{page.get('title', 'Untitled')}** (ID: `{page.get('id')}`)")
                                                if page.get('url'):
                                                    st.caption(f"   [View in Confluence]({page.get('url')})")
                                        else:
                                            st.info("No pages found in this space.")
                                    else:
                                        st.warning(f"Could not load pages: {pages_response.status_code}")
                                except Exception as e:
                                    st.error(f"Error loading pages: {str(e)}")
            else:
                st.info("No spaces found. Make sure Confluence is configured correctly.")
        else:
            st.error("**Could not connect to Confluence**")
            st.markdown("""
            **Troubleshooting:**
            1. Check that Confluence credentials are configured in `.env`
            2. Verify the API server is running
            3. Check API endpoint: `/confluence/spaces`
            4. Ensure your IP is in the Confluence allowlist
            """)


if __name__ == "__main__":
    main()
