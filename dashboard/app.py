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
    .suggested-question-btn {
        margin: 0.25rem 0;
        text-align: left;
        font-size: 0.9rem;
    }
    .stButton > button {
        border-radius: 0.5rem;
        transition: all 0.3s ease;
    }
    .stButton > button:hover {
        transform: translateY(-2px);
        box-shadow: 0 4px 8px rgba(0,0,0,0.1);
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


@st.cache_data(ttl=300)  # Cache for 5 minutes since questions are based on content
def fetch_suggested_questions(num_questions: int = 15):
    """Fetch suggested questions from API"""
    try:
        response = requests.get(f"{API_BASE_URL}/suggested-questions", params={"num_questions": num_questions})
        if response.status_code == 200:
            return response.json()
        return []
    except Exception as e:
        st.warning(f"Could not fetch suggested questions: {e}")
        # Return fallback questions
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
        
        # Suggested Questions Section
        st.subheader("💡 Suggested Questions")
        st.markdown("Questions generated based on your knowledge base content. Click any question to use it.")
        
        # Fetch suggested questions from API (based on actual content)
        with st.spinner("Loading suggested questions from your knowledge base..."):
            suggested_questions = fetch_suggested_questions(num_questions=15)
        
        if not suggested_questions:
            st.info("No content found in knowledge base. Please ingest some documents or Confluence pages first.")
            suggested_questions = [
                "How do we handle deployment rollbacks?",
                "What is our incident response procedure?",
                "How do we troubleshoot service failures?"
            ]
        
        # Display suggested questions as clickable buttons
        # Use a grid layout for better organization
        num_cols = 3
        cols = st.columns(num_cols)
        
        # Initialize session state for selected question if not exists
        if 'selected_question' not in st.session_state:
            st.session_state['selected_question'] = ""
        
        for idx, suggested_q in enumerate(suggested_questions):
            col_idx = idx % num_cols
            with cols[col_idx]:
                # Truncate long questions for button text
                button_text = suggested_q if len(suggested_q) <= 50 else suggested_q[:47] + "..."
                if st.button(button_text, key=f"suggest_{idx}", use_container_width=True):
                    st.session_state['selected_question'] = suggested_q
        
        st.divider()
        
        # Question input with pre-filled value if a suggestion was clicked
        question = st.text_input(
            "Ask a question:", 
            value=st.session_state.get('selected_question', ''),
            placeholder="e.g., How do we roll back service X?",
            key="question_input"
        )
        
        # Clear session state after displaying (so it doesn't persist)
        if st.session_state.get('selected_question'):
            # Only clear if user hasn't modified the question
            if question == st.session_state['selected_question']:
                pass  # Keep it for now, will be cleared after query
            else:
                st.session_state['selected_question'] = ""
        
        if st.button("Query", type="primary", use_container_width=True) and question:
            # Clear selected question after query
            if 'selected_question' in st.session_state:
                st.session_state['selected_question'] = ""
            
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
        
        # Enhanced Filters Section
        with st.expander("🔧 Filters & Search", expanded=True):
            col1, col2, col3 = st.columns(3)
            with col1:
                severity_filter = st.selectbox(
                    "Filter by Severity",
                    ["All", "high", "medium", "low"],
                    index=0
                )
            with col2:
                gap_type_filter = st.selectbox(
                    "Filter by Gap Type",
                    ["All", "low_similarity", "repeated_query", "uncertainty", "empty_retrieval"],
                    index=0
                )
            with col3:
                limit = st.slider("Number of gaps to show", 5, 100, 20)
            
            # Search functionality
            search_query = st.text_input("🔍 Search gaps by query text:", placeholder="Type to search...")
        
        # Fetch gaps
        all_gaps = fetch_gaps(limit=1000)  # Fetch more for filtering
        
        if all_gaps:
            # Convert to DataFrame
            df = pd.DataFrame(all_gaps)
            
            # Apply filters
            if severity_filter != "All":
                df = df[df["severity"] == severity_filter]
            
            if gap_type_filter != "All":
                df = df[df["gap_type"] == gap_type_filter]
            
            # Apply search filter
            if search_query:
                df = df[df["query"].str.contains(search_query, case=False, na=False)]
            
            # Limit results
            df = df.head(limit)
            
            # Calculate priority score (combination of severity and occurrence)
            def calculate_priority(row):
                severity_scores = {"high": 3, "medium": 2, "low": 1}
                return severity_scores.get(row["severity"], 0) * row["occurrence_count"]
            
            df["priority_score"] = df.apply(calculate_priority, axis=1)
            df = df.sort_values("priority_score", ascending=False)
            
            # Summary Metrics
            st.subheader("📊 Summary Metrics")
            col1, col2, col3, col4 = st.columns(4)
            with col1:
                st.metric("Total Gaps", len(df))
            with col2:
                high_priority = len(df[df["priority_score"] >= 6])
                st.metric("High Priority", high_priority)
            with col3:
                avg_occurrences = df["occurrence_count"].mean() if len(df) > 0 else 0
                st.metric("Avg Occurrences", f"{avg_occurrences:.1f}")
            with col4:
                total_affected = df["occurrence_count"].sum() if len(df) > 0 else 0
                st.metric("Total Affected Queries", total_affected)
            
            st.divider()
            
            # Export functionality
            col1, col2 = st.columns([3, 1])
            with col1:
                st.subheader("📋 Gap Details")
            with col2:
                # Export buttons
                csv = df.to_csv(index=False).encode('utf-8')
                st.download_button(
                    "📥 Export CSV",
                    csv,
                    "knowledge_gaps.csv",
                    "text/csv",
                    key="download-csv"
                )
            
            # Enhanced table with priority
            display_df = df[["query", "gap_type", "severity", "occurrence_count", "priority_score", "suggested_topic"]].copy()
            display_df = display_df.rename(columns={
                "query": "Query",
                "gap_type": "Gap Type",
                "severity": "Severity",
                "occurrence_count": "Occurrences",
                "priority_score": "Priority",
                "suggested_topic": "Suggested Topic"
            })
            
            st.dataframe(
                display_df,
                use_container_width=True,
                height=400
            )
            
            st.divider()
            
            # Enhanced Visualizations
            col1, col2 = st.columns(2)
            
            with col1:
                st.subheader("📈 Gaps by Type")
                gap_type_counts = df["gap_type"].value_counts()
                if len(gap_type_counts) > 0:
                    fig = px.pie(
                        values=gap_type_counts.values,
                        names=gap_type_counts.index,
                        title="Distribution of Gap Types",
                        color_discrete_map={
                            "low_similarity": "#ff6b6b",
                            "repeated_query": "#ffa500",
                            "uncertainty": "#ffd93d",
                            "empty_retrieval": "#6bcf7f"
                        }
                    )
                    st.plotly_chart(fig, use_container_width=True)
                else:
                    st.info("No data to display")
            
            with col2:
                st.subheader("📊 Top Queries by Priority")
                top_queries = df.nlargest(10, "priority_score")
                if len(top_queries) > 0:
                    fig = px.bar(
                        x=top_queries["priority_score"],
                        y=top_queries["query"],
                        orientation='h',
                        labels={"x": "Priority Score", "y": "Query"},
                        color=top_queries["severity"],
                        color_discrete_map={"high": "#ff6b6b", "medium": "#ffa500", "low": "#6bcf7f"},
                        title="Top 10 Gaps by Priority"
                    )
                    fig.update_layout(showlegend=False)
                    st.plotly_chart(fig, use_container_width=True)
                else:
                    st.info("No data to display")
            
            # Additional visualizations
            col1, col2 = st.columns(2)
            
            with col1:
                st.subheader("📉 Occurrences Distribution")
                if len(df) > 0:
                    fig = px.histogram(
                        df,
                        x="occurrence_count",
                        nbins=20,
                        labels={"occurrence_count": "Number of Occurrences", "count": "Number of Gaps"},
                        title="Distribution of Gap Occurrences"
                    )
                    st.plotly_chart(fig, use_container_width=True)
                else:
                    st.info("No data to display")
            
            with col2:
                st.subheader("🎯 Severity vs Occurrences")
                if len(df) > 0:
                    fig = px.scatter(
                        df,
                        x="occurrence_count",
                        y="priority_score",
                        color="severity",
                        size="occurrence_count",
                        hover_data=["query"],
                        labels={"occurrence_count": "Occurrences", "priority_score": "Priority Score"},
                        color_discrete_map={"high": "#ff6b6b", "medium": "#ffa500", "low": "#6bcf7f"},
                        title="Gap Priority Analysis"
                    )
                    st.plotly_chart(fig, use_container_width=True)
                else:
                    st.info("No data to display")
            
            st.divider()
            
            # Action Items Section
            st.subheader("🎯 Recommended Action Items")
            
            # Generate action items based on gaps
            high_priority_gaps = df[df["priority_score"] >= 6].head(5)
            
            if len(high_priority_gaps) > 0:
                for idx, gap in high_priority_gaps.iterrows():
                    with st.expander(f"🔴 Priority {int(gap['priority_score'])}: {gap['query'][:60]}..."):
                        col1, col2 = st.columns(2)
                        with col1:
                            st.write(f"**Gap Type:** {gap['gap_type']}")
                            st.write(f"**Severity:** {gap['severity'].upper()}")
                            st.write(f"**Occurrences:** {gap['occurrence_count']}")
                        with col2:
                            st.write(f"**Suggested Topic:** {gap.get('suggested_topic', 'N/A')}")
                            if gap.get('users_affected'):
                                st.write(f"**Users Affected:** {len(gap['users_affected'])}")
                        
                        st.write("**Recommended Action:**")
                        if gap['gap_type'] == 'empty_retrieval':
                            st.info(f"📝 Create documentation for: {gap.get('suggested_topic', gap['query'])}")
                        elif gap['gap_type'] == 'repeated_query':
                            st.warning(f"⚠️ This question has been asked {gap['occurrence_count']} times. Create a FAQ or detailed guide.")
                        elif gap['gap_type'] == 'low_similarity':
                            st.warning(f"⚠️ Improve existing documentation on: {gap.get('suggested_topic', 'this topic')}")
                        else:
                            st.info(f"📚 Review and enhance documentation related to: {gap.get('suggested_topic', gap['query'])}")
            else:
                st.success("✅ No high-priority gaps requiring immediate attention!")
            
            # Gap Trends (if we have date information)
            if len(df) > 0 and 'first_detected' in df.columns:
                st.divider()
                st.subheader("📅 Gap Detection Timeline")
                try:
                    df['first_detected'] = pd.to_datetime(df['first_detected'])
                    df['date'] = df['first_detected'].dt.date
                    daily_gaps = df.groupby('date').size().reset_index(name='count')
                    
                    if len(daily_gaps) > 0:
                        fig = px.line(
                            daily_gaps,
                            x='date',
                            y='count',
                            labels={'date': 'Date', 'count': 'Gaps Detected'},
                            title='Gaps Detected Over Time',
                            markers=True
                        )
                        st.plotly_chart(fig, use_container_width=True)
                except:
                    st.info("Date information not available for trend analysis")
        else:
            st.info("No gaps found with the selected filters. Try adjusting your filters or ask more questions to generate gap data.")


if __name__ == "__main__":
    main()
