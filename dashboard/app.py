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
    layout="wide"
)

# Custom CSS
st.markdown("""
    <style>
    .main-header {
        font-size: 2.5rem;
        font-weight: bold;
        color: #1f77b4;
        margin-bottom: 1rem;
    }
    .gap-card {
        padding: 1rem;
        border-radius: 0.5rem;
        border-left: 4px solid;
        margin: 0.5rem 0;
    }
    .gap-high {
        background-color: #fee;
        border-color: #f44;
    }
    .gap-medium {
        background-color: #ffe;
        border-color: #fa4;
    }
    .gap-low {
        background-color: #efe;
        border-color: #4a4;
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
        response = requests.get(f"{API_BASE_URL}/gaps", params=params)
        if response.status_code == 200:
            return response.json()
        return []
    except Exception as e:
        st.error(f"Error fetching gaps: {e}")
        return []


@st.cache_data(ttl=60)
def fetch_statistics():
    """Fetch gap statistics from API"""
    try:
        response = requests.get(f"{API_BASE_URL}/gaps/stats")
        if response.status_code == 200:
            return response.json()
        return {}
    except Exception as e:
        st.error(f"Error fetching statistics: {e}")
        return {}


def query_knowledge_base(question: str, user_id: str = None):
    """Query the knowledge base"""
    try:
        payload = {"question": question}
        if user_id:
            payload["user_id"] = user_id
        
        response = requests.post(f"{API_BASE_URL}/query", json=payload)
        if response.status_code == 200:
            return response.json()
        return None
    except Exception as e:
        st.error(f"Error querying knowledge base: {e}")
        return None


def main():
    st.markdown('<div class="main-header">🧠 AI Knowledge Gap Detector</div>', unsafe_allow_html=True)
    st.markdown("**Your company doesn't know what it doesn't know — until now.**")
    
    # Sidebar
    with st.sidebar:
        st.header("Navigation")
        page = st.radio(
            "Select Page",
            ["Dashboard", "Query Interface", "Gap Analysis"],
            index=0
        )
        
        st.divider()
        st.header("API Status")
        try:
            response = requests.get(f"{API_BASE_URL}/health")
            if response.status_code == 200:
                st.success("✅ API Connected")
                health_data = response.json()
                st.json(health_data)
            else:
                st.error("❌ API Error")
        except:
            st.error("❌ Cannot connect to API")
            st.info("Make sure the FastAPI server is running on port 8000")
    
    # Dashboard Page
    if page == "Dashboard":
        st.header("📊 Knowledge Gap Dashboard")
        
        # Fetch statistics
        stats = fetch_statistics()
        
        if stats:
            col1, col2, col3, col4 = st.columns(4)
            
            with col1:
                st.metric("Total Queries", stats.get("total_queries", 0))
            
            with col2:
                st.metric("Knowledge Gaps", stats.get("total_gaps", 0))
            
            with col3:
                gap_rate = stats.get("gap_rate", 0)
                st.metric("Gap Rate", f"{gap_rate:.1%}")
            
            with col4:
                high_severity = stats.get("severity_breakdown", {}).get("high", 0)
                st.metric("High Severity Gaps", high_severity, delta=None)
            
            st.divider()
            
            # Gap type breakdown
            col1, col2 = st.columns(2)
            
            with col1:
                st.subheader("Gap Types")
                gap_types = stats.get("gap_types", {})
                if gap_types:
                    fig = px.pie(
                        values=list(gap_types.values()),
                        names=list(gap_types.keys()),
                        title="Distribution of Gap Types"
                    )
                    st.plotly_chart(fig, use_container_width=True)
                else:
                    st.info("No gap data available")
            
            with col2:
                st.subheader("Severity Breakdown")
                severity = stats.get("severity_breakdown", {})
                if severity:
                    fig = px.bar(
                        x=list(severity.keys()),
                        y=list(severity.values()),
                        title="Gaps by Severity",
                        labels={"x": "Severity", "y": "Count"}
                    )
                    st.plotly_chart(fig, use_container_width=True)
                else:
                    st.info("No severity data available")
        
        # Top Gaps
        st.divider()
        st.subheader("🔴 Top Knowledge Gaps")
        
        gaps = fetch_gaps(limit=10)
        
        if gaps:
            for gap in gaps:
                severity_class = f"gap-{gap['severity']}"
                st.markdown(f"""
                    <div class="gap-card {severity_class}">
                        <strong>{gap['query']}</strong><br>
                        <small>Type: {gap['gap_type']} | Occurrences: {gap['occurrence_count']} | 
                        Severity: {gap['severity'].upper()}</small><br>
                        <small>Suggested Topic: {gap.get('suggested_topic', 'N/A')}</small>
                    </div>
                """, unsafe_allow_html=True)
        else:
            st.info("No knowledge gaps detected yet. Try asking some questions!")
    
    # Query Interface
    elif page == "Query Interface":
        st.header("💬 Query Knowledge Base")
        
        question = st.text_input("Ask a question:", placeholder="e.g., How do we roll back service X?")
        
        if st.button("Query", type="primary") and question:
            with st.spinner("Searching knowledge base..."):
                result = query_knowledge_base(question)
                
                if result:
                    st.subheader("Answer")
                    st.write(result["answer"])
                    
                    # Show sources
                    if result.get("sources"):
                        with st.expander("Sources"):
                            for source in result["sources"]:
                                st.write(f"📄 {source}")
                    
                    # Show confidence
                    confidence = result.get("confidence_score", 0)
                    st.progress(confidence, text=f"Confidence: {confidence:.1%}")
                    
                    # Gap detection indicator
                    if result.get("is_gap"):
                        st.error(f"⚠️ Knowledge Gap Detected: {result.get('gap_reason', 'Unknown reason')}")
                    else:
                        st.success("✅ Answer found in knowledge base")
                    
                    # Similarity scores
                    if result.get("similarity_scores"):
                        with st.expander("Retrieval Details"):
                            st.write("Similarity Scores:")
                            for i, score in enumerate(result["similarity_scores"], 1):
                                st.write(f"Document {i}: {score:.3f}")
    
    # Gap Analysis
    elif page == "Gap Analysis":
        st.header("🔍 Detailed Gap Analysis")
        
        # Filters
        col1, col2 = st.columns(2)
        with col1:
            severity_filter = st.selectbox(
                "Filter by Severity",
                ["All", "high", "medium", "low"],
                index=0
            )
        with col2:
            limit = st.slider("Number of gaps to show", 5, 50, 20)
        
        # Fetch gaps
        gaps = fetch_gaps(
            severity=severity_filter if severity_filter != "All" else None,
            limit=limit
        )
        
        if gaps:
            # Convert to DataFrame
            df = pd.DataFrame(gaps)
            
            # Display table
            st.subheader("Gap Details")
            st.dataframe(
                df[["query", "gap_type", "severity", "occurrence_count", "suggested_topic"]],
                use_container_width=True
            )
            
            # Charts
            col1, col2 = st.columns(2)
            
            with col1:
                st.subheader("Gaps by Type")
                gap_type_counts = df["gap_type"].value_counts()
                fig = px.bar(
                    x=gap_type_counts.index,
                    y=gap_type_counts.values,
                    labels={"x": "Gap Type", "y": "Count"}
                )
                st.plotly_chart(fig, use_container_width=True)
            
            with col2:
                st.subheader("Top Queries (by occurrence)")
                top_queries = df.nlargest(10, "occurrence_count")
                fig = px.bar(
                    x=top_queries["occurrence_count"],
                    y=top_queries["query"],
                    orientation='h',
                    labels={"x": "Occurrences", "y": "Query"}
                )
                st.plotly_chart(fig, use_container_width=True)
        else:
            st.info("No gaps found with the selected filters.")


if __name__ == "__main__":
    main()
