"""Pipeline Control Page - Manage ML pipelines"""
import streamlit as st
import pandas as pd
from datetime import datetime


def render():
    """Render pipeline control page"""
    st.markdown('<h1 class="main-header">Pipeline Control</h1>', unsafe_allow_html=True)
    st.markdown('<p class="sub-header">Manage feature, training, and inference pipelines</p>', unsafe_allow_html=True)
    
    # Explanation
    with st.expander("About Pipelines", expanded=False):
        st.markdown("""
            **CryptoSentinel uses three main pipelines:**
            
            1. **Feature Pipeline**
               - Fetches price data from CoinGecko API
               - Engineers technical indicators (RSI, MACD, Bollinger Bands, etc.)
               - Stores features in Hopsworks Feature Store
               - *Runs every 5 minutes via GitHub Actions*
            
            2. **Training Pipeline**
               - Loads features from Feature Store
               - Trains multiple ML models (XGBoost, RF, GB, Ridge)
               - Selects best model based on RMSE
               - Registers models in Hopsworks Model Registry
               - *Runs every 30 minutes via GitHub Actions*
            
            3. **Inference Pipeline**
               - Generates real-time predictions
               - Validates past predictions
               - Checks for alerts
               - *Runs every 5 minutes via FastAPI scheduler (local) or Streamlit scheduler (Hugging Face)*
        """)
    
    # Background scheduler status
    try:
        from app.scheduler import get_scheduler_status
        scheduler_status = get_scheduler_status()
        
        st.subheader("Background Scheduler")
        if scheduler_status["running"]:
            st.success("Background scheduler is running")
            col1, col2 = st.columns(2)
            with col1:
                if scheduler_status["last_feature_run"]:
                    st.info(f"Last feature run: {scheduler_status['last_feature_run']}")
                else:
                    st.info("Feature pipeline: Not run yet")
            with col2:
                if scheduler_status["last_training_run"]:
                    st.info(f"Last training run: {scheduler_status['last_training_run']}")
                else:
                    st.info("Training pipeline: Not run yet")
        else:
            st.warning("Background scheduler is not running")
    except ImportError:
        st.info("Background scheduler not available")
    
    st.markdown("---")
    
    # Pipeline status
    st.subheader("Pipeline Status")
    
    try:
        from app.predictor import model_loader, get_prediction_history
        from app.drift_detection import get_drift_report
        from app.alerts import get_alert_summary
        
        col1, col2, col3 = st.columns(3)
        
        with col1:
            status = "Online" if model_loader.is_loaded else "Offline"
            status_color = "positive" if model_loader.is_loaded else "negative"
            st.markdown(f"""
                <div class="metric-card">
                    <h4 style="color: #94a3b8;">Model Status</h4>
                    <p class="{status_color}" style="font-size: 1.3rem;">{status}</p>
                    <p style="color: #64748b;">Best: {model_loader.best_model_name if model_loader.is_loaded else 'N/A'}</p>
                </div>
            """, unsafe_allow_html=True)
        
        with col2:
            pred_count = len(get_prediction_history())
            st.markdown(f"""
                <div class="metric-card">
                    <h4 style="color: #94a3b8;">Predictions</h4>
                    <p style="font-size: 1.3rem; color: #a855f7;">{pred_count}</p>
                    <p style="color: #64748b;">In history buffer</p>
                </div>
            """, unsafe_allow_html=True)
        
        with col3:
            drift_report = get_drift_report()
            drift_detected = drift_report.get('drift_detected', False)
            drift_score = drift_report.get('drift_score', 0)
            drift_color = "negative" if drift_detected else "positive"
            status = "DRIFT" if drift_detected else "OK"
            st.markdown(f"""
                <div class="metric-card">
                    <h4 style="color: #94a3b8;">Drift Status</h4>
                    <p class="{drift_color}" style="font-size: 1.3rem;">{status}</p>
                    <p style="color: #64748b;">Score: {drift_score:.3f}</p>
                </div>
            """, unsafe_allow_html=True)
        
    except Exception as e:
        st.error(f"Error loading status: {e}")
    
    # Manual pipeline triggers
    st.markdown("---")
    st.subheader("Manual Pipeline Triggers")
    
    st.warning("Running pipelines manually may take several minutes.")
    
    col1, col2, col3 = st.columns(3)
    
    with col1:
        st.markdown("### Feature Pipeline")
        st.markdown("Fetch data and engineer features")
        if st.button("Run Feature Pipeline", key="feature"):
            with st.spinner("Running feature pipeline..."):
                try:
                    from pipelines.feature_pipeline import feature_pipeline
                    result = feature_pipeline()
                    st.success(f"Complete! Processed {result.get('rows_processed', 0)} rows in {result.get('duration_seconds', 0):.1f}s")
                except Exception as e:
                    st.error(f"Pipeline failed: {e}")
    
    with col2:
        st.markdown("### Training Pipeline")
        st.markdown("Train models and register")
        if st.button("Run Training Pipeline", key="training"):
            with st.spinner("Running training pipeline... (this may take a while)"):
                try:
                    from pipelines.training_pipeline import training_pipeline
                    result = training_pipeline()
                    st.success(f"Complete! Best model: {result.get('best_model', 'N/A')}")
                    st.info(f"Trained on {result.get('samples_trained', 0)} samples in {result.get('duration_seconds', 0):.1f}s")
                except Exception as e:
                    st.error(f"Pipeline failed: {e}")
    
    with col3:
        st.markdown("### Inference Pipeline")
        st.markdown("Generate predictions")
        if st.button("Run Inference Pipeline", key="inference"):
            with st.spinner("Running inference pipeline..."):
                try:
                    from pipelines.inference_pipeline import inference_pipeline
                    result = inference_pipeline()
                    pred = result.get('prediction', {})
                    if pred:
                        st.success(f"Prediction: ${pred.get('predicted_price', 0):,.2f} ({pred.get('predicted_direction', 'N/A')})")
                    else:
                        st.warning("No prediction generated. Models may not be loaded.")
                except Exception as e:
                    st.error(f"Pipeline failed: {e}")
    
    # Model management
    st.markdown("---")
    st.subheader("Model Management")
    
    col1, col2 = st.columns(2)
    
    with col1:
        st.markdown("### Reload Models")
        st.markdown("Reload models from disk")
        if st.button("Reload Models"):
            try:
                from app.predictor import model_loader
                success = model_loader.load()
                if success:
                    st.success(f"Models reloaded! Best: {model_loader.best_model_name}")
                else:
                    st.warning("No models found. Run training pipeline first.")
            except Exception as e:
                st.error(f"Reload failed: {e}")
    
    with col2:
        st.markdown("### Model Info")
        try:
            if model_loader.is_loaded:
                metadata = model_loader.metadata
                st.markdown(f"""
                    - **Version**: {metadata.get('version', 'N/A')}
                    - **Created**: {metadata.get('created_at', 'N/A')}
                    - **Models**: {', '.join(model_loader.models.keys())}
                """)
            else:
                st.info("No models loaded.")
        except:
            st.info("Model info unavailable.")
    
    # Configuration info
    st.markdown("---")
    st.subheader("Configuration")
    
    try:
        from app.config import settings
        
        config_df = pd.DataFrame([
            {"Setting": "Prediction Refresh", "Value": f"{settings.PREDICTION_REFRESH_MINUTES} min"},
            {"Setting": "Training Interval", "Value": f"{settings.TRAINING_INTERVAL_MINUTES} min"},
            {"Setting": "Direction Tolerance", "Value": f"{settings.DIRECTION_TOLERANCE_PCT}%"},
            {"Setting": "RSI Period", "Value": str(settings.RSI_PERIOD)},
            {"Setting": "N Clusters", "Value": str(settings.N_CLUSTERS)},
            {"Setting": "Drift Threshold", "Value": f"{settings.DRIFT_THRESHOLD}"},
            {"Setting": "Hopsworks Project", "Value": settings.HOPSWORKS_PROJECT_NAME},
        ])
        
        st.dataframe(config_df, use_container_width=True, hide_index=True)
        
    except Exception as e:
        st.error(f"Error loading config: {e}")

