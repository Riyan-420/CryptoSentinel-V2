"""CryptoSentinel - Streamlit Dashboard"""
import streamlit as st
from datetime import datetime

# Page config
st.set_page_config(
    page_title="CryptoSentinel",
    page_icon="",
    layout="wide",
    initial_sidebar_state="expanded"
)

# Custom CSS
st.markdown("""
<style>
    /* Main background */
    .stApp {
        background: linear-gradient(135deg, #0f172a 0%, #1e1b4b 50%, #0f172a 100%);
    }
    
    /* Sidebar */
    [data-testid="stSidebar"] {
        background: linear-gradient(180deg, #1e293b 0%, #0f172a 100%);
        border-right: 1px solid #334155;
    }
    
    /* Cards */
    .metric-card {
        background: linear-gradient(145deg, #1e293b, #0f172a);
        border: 1px solid #334155;
        border-radius: 12px;
        padding: 20px;
        margin: 10px 0;
        box-shadow: 0 4px 20px rgba(0, 0, 0, 0.3);
    }
    
    /* Headers */
    .main-header {
        font-size: 2.5rem;
        font-weight: 700;
        background: linear-gradient(90deg, #a855f7, #6366f1);
        -webkit-background-clip: text;
        -webkit-text-fill-color: transparent;
        margin-bottom: 0.5rem;
    }
    
    .sub-header {
        color: #94a3b8;
        font-size: 1.1rem;
        margin-bottom: 2rem;
    }
    
    /* Metrics */
    [data-testid="stMetricValue"] {
        font-size: 2rem;
        font-weight: 600;
    }
    
    /* Positive/Negative colors */
    .positive { color: #22c55e; }
    .negative { color: #ef4444; }
    .neutral { color: #f59e0b; }
    
    /* Buttons */
    .stButton > button {
        background: linear-gradient(90deg, #a855f7, #6366f1);
        color: white;
        border: none;
        border-radius: 8px;
        padding: 0.5rem 1.5rem;
        font-weight: 600;
        transition: all 0.3s ease;
    }
    
    .stButton > button:hover {
        transform: translateY(-2px);
        box-shadow: 0 4px 15px rgba(168, 85, 247, 0.4);
    }
    
    /* Tabs */
    .stTabs [data-baseweb="tab-list"] {
        gap: 8px;
        background: transparent;
    }
    
    .stTabs [data-baseweb="tab"] {
        background: #1e293b;
        border-radius: 8px;
        border: 1px solid #334155;
        color: #94a3b8;
        padding: 0.5rem 1rem;
    }
    
    .stTabs [aria-selected="true"] {
        background: linear-gradient(90deg, #a855f7, #6366f1);
        color: white;
        border: none;
    }
    
    /* Expander */
    .streamlit-expanderHeader {
        background: #1e293b;
        border-radius: 8px;
        border: 1px solid #334155;
    }
    
    /* Dataframe */
    .stDataFrame {
        border-radius: 8px;
        overflow: hidden;
    }
    
    /* Info boxes */
    .info-box {
        background: rgba(99, 102, 241, 0.1);
        border-left: 4px solid #6366f1;
        padding: 1rem;
        border-radius: 0 8px 8px 0;
        margin: 1rem 0;
    }
    
    /* Success indicator */
    .status-dot {
        display: inline-block;
        width: 8px;
        height: 8px;
        border-radius: 50%;
        margin-right: 8px;
    }
    .status-online { background: #22c55e; }
    .status-offline { background: #ef4444; }
    
    /* Hide Streamlit branding */
    #MainMenu {visibility: hidden;}
    footer {visibility: hidden;}
</style>
""", unsafe_allow_html=True)


def main():
    """Main dashboard entry point"""
    # Sidebar navigation
    with st.sidebar:
        st.markdown('<h2 style="color: #a855f7;">CryptoSentinel</h2>', unsafe_allow_html=True)
        st.markdown('<p style="color: #64748b; font-size: 0.85rem;">Bitcoin Price Intelligence</p>', unsafe_allow_html=True)
        st.markdown("---")
        
        page = st.radio(
            "Navigation",
            [
                "Dashboard",
                "Predictions",
                "Model Insights",
                "Data Analysis",
                "Data Drift",
                "Alerts",
                "Pipeline Control",
                "About"
            ],
            label_visibility="collapsed"
        )
        
        st.markdown("---")
        
        # Status indicator
        try:
            from app.predictor import model_loader
            is_loaded = model_loader.is_loaded
        except:
            is_loaded = False
        
        status_class = "status-online" if is_loaded else "status-offline"
        status_text = "Models Active" if is_loaded else "Models Offline"
        st.markdown(
            f'<p><span class="status-dot {status_class}"></span>{status_text}</p>',
            unsafe_allow_html=True
        )
        
        st.markdown(f'<p style="color: #64748b; font-size: 0.75rem;">Last update: {datetime.now().strftime("%H:%M:%S")}</p>', unsafe_allow_html=True)
    
    # Page routing
    if page == "Dashboard":
        from pages import home
        home.render()
    elif page == "Predictions":
        from pages import predictions
        predictions.render()
    elif page == "Model Insights":
        from pages import model_insights
        model_insights.render()
    elif page == "Data Analysis":
        from pages import data_analysis
        data_analysis.render()
    elif page == "Data Drift":
        from pages import drift_page
        drift_page.render()
    elif page == "Alerts":
        from pages import alerts_page
        alerts_page.render()
    elif page == "Pipeline Control":
        from pages import pipeline_control
        pipeline_control.render()
    elif page == "About":
        from pages import about
        about.render()


if __name__ == "__main__":
    main()

