"""About Page - Project information"""
import streamlit as st


def render():
    """Render about page"""
    st.markdown('<h1 class="main-header">About CryptoSentinel</h1>', unsafe_allow_html=True)
    st.markdown('<p class="sub-header">Bitcoin Price Prediction with Machine Learning</p>', unsafe_allow_html=True)
    
    # Project overview
    st.subheader("Project Overview")
    
    st.markdown("""
        CryptoSentinel is a comprehensive machine learning system for Bitcoin price prediction,
        built with modern MLOps practices including feature stores, model registries, and 
        automated CI/CD pipelines.
        
        This project demonstrates the full ML lifecycle from data ingestion to production deployment.
    """)
    
    # Architecture
    st.markdown("---")
    st.subheader("System Architecture")
    
    with st.expander("Data Pipeline", expanded=True):
        st.markdown("""
            **Data Ingestion:**
            - Real-time price data from CoinGecko API
            - Historical price, OHLCV, and market data
            - 24-hour rolling window for feature engineering
            
            **Feature Engineering:**
            - Technical indicators: RSI, MACD, Bollinger Bands
            - Moving averages: SMA, EMA (5, 10, 20 periods)
            - Volatility and momentum indicators
            - Time-based features (hour, day of week)
            - Lag features for temporal patterns
            
            **Feature Store:**
            - Hopsworks Feature Store for centralized feature management
            - Local parquet fallback for offline development
        """)
    
    with st.expander("ML Models", expanded=True):
        st.markdown("""
            **Regression Models (Price Prediction):**
            - XGBoost Regressor (primary)
            - Random Forest Regressor
            - Gradient Boosting Regressor
            - Ridge Regression
            
            **Classification Model (Direction):**
            - Gradient Boosting Classifier
            - Predicts up/down movement with confidence
            
            **Clustering (Market Regime):**
            - K-Means with PCA dimensionality reduction
            - Identifies: accumulation, uptrend, distribution, downtrend
            
            **Model Selection:**
            - Automatic selection based on validation RMSE
            - All models saved for comparison
        """)
    
    with st.expander("MLOps Infrastructure", expanded=True):
        st.markdown("""
            **Model Registry:**
            - Hopsworks Model Registry for versioning
            - Local joblib storage for deployment
            - Automatic model promotion
            
            **CI/CD Pipelines:**
            - GitHub Actions workflows
            - Feature pipeline: every 30 minutes
            - Training pipeline: every 30 minutes (offset)
            - Automated retraining on drift detection
            
            **Monitoring:**
            - Data drift detection (DeepChecks/KS-test)
            - Prediction accuracy tracking
            - Alert system for anomalies
        """)
    
    with st.expander("Explainability", expanded=True):
        st.markdown("""
            **SHAP (SHapley Additive exPlanations):**
            - Feature contribution to individual predictions
            - Identifies which features drive the model
            
            **Feature Importance:**
            - Global importance from tree-based models
            - Helps understand model behavior
            
            **Prediction Validation:**
            - 30-minute validation window
            - Tolerance-based correctness (0.1% threshold)
            - Prevents false positives from market noise
        """)
    
    # Tech stack
    st.markdown("---")
    st.subheader("Technology Stack")
    
    col1, col2, col3 = st.columns(3)
    
    with col1:
        st.markdown("**Frontend**")
        st.markdown("""
            - Streamlit
            - Plotly
            - Custom CSS
        """)
    
    with col2:
        st.markdown("**Backend**")
        st.markdown("""
            - FastAPI
            - Prefect
            - APScheduler
        """)
    
    with col3:
        st.markdown("**ML/Data**")
        st.markdown("""
            - scikit-learn
            - XGBoost
            - SHAP
            - Pandas/NumPy
        """)
    
    col1, col2, col3 = st.columns(3)
    
    with col1:
        st.markdown("**MLOps**")
        st.markdown("""
            - Hopsworks
            - GitHub Actions
            - Docker
        """)
    
    with col2:
        st.markdown("**Data Quality**")
        st.markdown("""
            - DeepChecks
            - SciPy (KS-test)
        """)
    
    with col3:
        st.markdown("**API**")
        st.markdown("""
            - CoinGecko
            - RESTful endpoints
        """)
    
    # Credits
    st.markdown("---")
    st.subheader("Project Information")
    
    st.markdown("""
        **Course:** Machine Learning (SEM 5)
        
        **Key Features:**
        - Real-time Bitcoin price prediction
        - Multiple ML model comparison
        - Automated 30-minute update cycle
        - Comprehensive explainability
        - Data drift monitoring
        - Production-ready deployment
        
        **Python Version:** 3.11.9
    """)
    
    # Links
    st.markdown("---")
    
    col1, col2, col3 = st.columns(3)
    
    with col1:
        st.markdown("**API Endpoints**")
        st.code("""
GET  /api/price/current
GET  /api/prediction/current
GET  /api/model/metrics
POST /api/pipeline/training
        """)
    
    with col2:
        st.markdown("**Quick Start**")
        st.code("""
# Install dependencies
pip install -r requirements.txt

# Run Streamlit
streamlit run dashboard.py

# Run FastAPI
python -m api.main
        """)
    
    with col3:
        st.markdown("**Configuration**")
        st.code("""
# env.example
HOPSWORKS_API_KEY=xxx
HOPSWORKS_PROJECT_NAME=CryptoSentinel
TRAINING_INTERVAL_MINUTES=30
        """)

