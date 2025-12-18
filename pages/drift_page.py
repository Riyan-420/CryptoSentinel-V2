"""Data Drift Detection Page"""
import streamlit as st
import plotly.graph_objects as go
import pandas as pd
from datetime import datetime


def render():
    """Render data drift detection page"""
    st.markdown('<h1 class="main-header">Data Drift Detection</h1>', unsafe_allow_html=True)
    st.markdown('<p class="sub-header">Monitor data distribution changes for model retraining</p>', unsafe_allow_html=True)
    
    # Explanation
    with st.expander("Understanding Data Drift", expanded=True):
        st.markdown("""
            ### What is Data Drift?
            
            **Data drift** occurs when the statistical properties of input data change over time compared to the baseline data used for training.
            
            ### How It Works Here
            
            1. **Training Time**: When models are trained, current data becomes the **reference baseline**
            2. **Next Pipeline Run**: New data is compared against this baseline
            3. **Drift Detection**: If distributions differ significantly, drift is detected
            4. **Action**: Drift triggers model retraining to adapt to new patterns
            
            ### Why It Matters for Crypto
            
            Cryptocurrency markets undergo regime changes:
            - Bull markets → Bear markets
            - Low volatility → High volatility
            - Normal trading → Black swan events
            
            When drift is detected, it signals that the model's understanding of the market is outdated.
            
            ### Detection Methods
            
            **1. DeepChecks (Primary)**
            - Uses domain classifier approach
            - Comprehensive multi-feature analysis
            - Score >0.3 indicates significant drift
            
            **2. Kolmogorov-Smirnov Test (Fallback)**
            - Statistical test comparing distributions
            - Per-feature p-value analysis
            - Average score >0.3 triggers retraining
        """)
    
    st.markdown("---")
    
    # Get current drift report
    try:
        from app.drift_detection import get_drift_report, check_data_quality
        
        report = get_drift_report()
        
        # Main drift status
        st.subheader("Current Drift Status")
        
        drift_detected = report.get('drift_detected', False)
        drift_score = report.get('drift_score', 0.0)
        threshold = report.get('threshold', 0.3)
        timestamp = report.get('timestamp', 'N/A')
        method = report.get('method', 'unknown')
        
        col1, col2, col3, col4 = st.columns(4)
        
        with col1:
            status_emoji = "🔴" if drift_detected else "🟢"
            status_text = "DRIFT DETECTED" if drift_detected else "NO DRIFT"
            st.markdown(f"""
                <div class="metric-card">
                    <p style="color: #94a3b8;">Status</p>
                    <p style="font-size: 1.5rem;">{status_emoji} {status_text}</p>
                </div>
            """, unsafe_allow_html=True)
        
        with col2:
            score_color = "negative" if drift_detected else "positive"
            st.markdown(f"""
                <div class="metric-card">
                    <p style="color: #94a3b8;">Drift Score</p>
                    <p class="{score_color}" style="font-size: 1.5rem;">{drift_score:.4f}</p>
                    <p style="color: #64748b; font-size: 0.85rem;">Threshold: {threshold}</p>
                </div>
            """, unsafe_allow_html=True)
        
        with col3:
            st.markdown(f"""
                <div class="metric-card">
                    <p style="color: #94a3b8;">Method</p>
                    <p style="font-size: 1.2rem; color: #a855f7;">{method.upper()}</p>
                </div>
            """, unsafe_allow_html=True)
        
        with col4:
            st.markdown(f"""
                <div class="metric-card">
                    <p style="color: #94a3b8;">Last Check</p>
                    <p style="font-size: 1rem;">{timestamp[:19] if timestamp != 'N/A' else 'N/A'}</p>
                </div>
            """, unsafe_allow_html=True)
        
        # Visualization
        st.markdown("---")
        st.subheader("Drift Score Visualization")
        
        # Gauge chart
        fig = go.Figure(go.Indicator(
            mode="gauge+number+delta",
            value=drift_score,
            domain={'x': [0, 1], 'y': [0, 1]},
            title={'text': "Drift Score", 'font': {'color': '#e2e8f0'}},
            delta={'reference': threshold},
            gauge={
                'axis': {'range': [None, 1], 'tickcolor': "#e2e8f0"},
                'bar': {'color': "#ef4444" if drift_detected else "#22c55e"},
                'bgcolor': "rgba(0,0,0,0)",
                'borderwidth': 2,
                'bordercolor': "#334155",
                'steps': [
                    {'range': [0, threshold], 'color': 'rgba(34, 197, 94, 0.2)'},
                    {'range': [threshold, 1], 'color': 'rgba(239, 68, 68, 0.2)'}
                ],
                'threshold': {
                    'line': {'color': "#f59e0b", 'width': 4},
                    'thickness': 0.75,
                    'value': threshold
                }
            }
        ))
        
        fig.update_layout(
            plot_bgcolor='rgba(0,0,0,0)',
            paper_bgcolor='rgba(0,0,0,0)',
            font=dict(color='#e2e8f0'),
            height=300
        )
        
        st.plotly_chart(fig, use_container_width=True)
        
        # Feature-level drift
        st.markdown("---")
        st.subheader("Feature-Level Drift Analysis")
        
        feature_drifts = report.get('feature_drifts', {})
        
        if feature_drifts:
            # Show top drifting features
            drift_items = []
            for feature, data in feature_drifts.items():
                if isinstance(data, dict):
                    drift_items.append({
                        "Feature": feature,
                        "Statistic": f"{data.get('statistic', 0):.4f}",
                        "P-Value": f"{data.get('p_value', 1):.4f}",
                        "Drifted": "✓" if data.get('drifted', False) else "✗"
                    })
            
            if drift_items:
                df_drift = pd.DataFrame(drift_items)
                df_drift = df_drift.sort_values('Statistic', ascending=False)
                
                # Show top 15
                st.dataframe(df_drift.head(15), use_container_width=True, hide_index=True)
                
                # Count drifted features
                drifted_count = sum(1 for item in drift_items if item["Drifted"] == "✓")
                total_count = len(drift_items)
                drift_pct = (drifted_count / total_count * 100) if total_count > 0 else 0
                
                col1, col2, col3 = st.columns(3)
                with col1:
                    st.metric("Total Features", total_count)
                with col2:
                    st.metric("Drifted Features", drifted_count)
                with col3:
                    st.metric("Drift Percentage", f"{drift_pct:.1f}%")
            else:
                st.info("No feature-level drift data available.")
        else:
            st.info("No feature-level drift data available. Run the training pipeline to generate drift analysis.")
        
        # Interpretation
        st.markdown("---")
        st.subheader("Interpretation & Actions")
        
        if report.get('message'):
            st.info(report['message'])
        elif drift_detected:
            st.error(f"""
                **DRIFT DETECTED - Action Required**
                
                The current data distribution has significantly deviated from the training baseline.
                
                **Drift Score:** {drift_score:.4f} (threshold: {threshold})
                
                **Recommended Actions:**
                1. Model retraining will be triggered automatically on next cycle
                2. Review recent market conditions for regime changes
                3. Monitor prediction accuracy closely
                4. Consider adding new features if drift persists
                
                **What This Means:**
                - Market patterns have shifted since training
                - Model predictions may be less reliable
                - Retraining with fresh data will adapt to new patterns
            """)
        else:
            st.success(f"""
                **NO DRIFT DETECTED - System Healthy**
                
                The current data distribution is consistent with the training baseline.
                
                **Drift Score:** {drift_score:.4f} (threshold: {threshold})
                
                **Status:**
                - Model is operating within expected parameters
                - No immediate retraining required
                - Continue monitoring on schedule
                - Predictions should remain reliable
            """)
        
        # Manual check buttons
        st.markdown("---")
        st.subheader("Manual Actions")
        
        # Quick drift check (no retraining)
        st.markdown("### Quick Drift Check")
        col1, col2 = st.columns([2, 1])
        
        with col1:
            st.markdown("""
                Check current market data for drift **without retraining**.
                Fast check (~30 seconds) to see if data has changed since training.
            """)
        
        with col2:
            if st.button("🔍 Check Drift Only", type="secondary"):
                with st.spinner("Checking for drift..."):
                    try:
                        from app.data_fetcher import fetch_price_history
                        from app.feature_engineering import engineer_features, get_feature_names
                        from app.drift_detection import detect_drift
                        
                        # Fetch recent data
                        st.info("Fetching recent market data...")
                        history = fetch_price_history(hours=24)
                        
                        # Engineer features
                        st.info("Engineering features...")
                        features_df = engineer_features(history)
                        
                        # Get feature columns
                        feature_cols = get_feature_names()
                        available_cols = [c for c in feature_cols if c in features_df.columns]
                        
                        # Check drift
                        st.info("Comparing against baseline...")
                        drift_result = detect_drift(features_df, available_cols)
                        
                        # Display results
                        st.markdown("---")
                        if drift_result.get('drift_detected'):
                            st.error(f"""
                                **DRIFT DETECTED!**
                                
                                **Score:** {drift_result.get('drift_score', 0):.4f} (threshold: {drift_result.get('threshold', 0.3)})
                                
                                **Method:** {drift_result.get('method', 'N/A').upper()}
                                
                                **Recommendation:** Consider running the training pipeline to retrain with fresh data.
                            """)
                        else:
                            st.success(f"""
                                **NO DRIFT DETECTED**
                                
                                **Score:** {drift_result.get('drift_score', 0):.4f} (threshold: {drift_result.get('threshold', 0.3)})
                                
                                **Status:** Model is operating within expected parameters. No retraining needed.
                            """)
                        
                        # Show feature-level details if available
                        feature_drifts = drift_result.get('feature_drifts', {})
                        if feature_drifts:
                            with st.expander("Feature-Level Details"):
                                drift_items = []
                                for feature, data in feature_drifts.items():
                                    if isinstance(data, dict):
                                        drift_items.append({
                                            "Feature": feature,
                                            "Drifted": "✓" if data.get('drifted', False) else "✗"
                                        })
                                if drift_items:
                                    drifted_count = sum(1 for item in drift_items if item["Drifted"] == "✓")
                                    st.markdown(f"**{drifted_count} of {len(drift_items)} features showing drift**")
                        
                        st.rerun()
                        
                    except Exception as e:
                        st.error(f"Drift check failed: {e}")
        
        # Full training pipeline (with retraining)
        st.markdown("---")
        st.markdown("### Full Training Pipeline")
        col1, col2 = st.columns([2, 1])
        
        with col1:
            st.markdown("""
                Run the complete training pipeline: check drift, retrain models, and update baseline.
                This takes longer (~2-3 minutes) but ensures models are up-to-date.
            """)
        
        with col2:
            if st.button("🔄 Train & Update Baseline", type="primary"):
                with st.spinner("Running training pipeline..."):
                    try:
                        from pipelines.training_pipeline import training_pipeline
                        result = training_pipeline()
                        st.success(f"Pipeline complete! Best model: {result.get('best_model', 'N/A')}")
                        st.rerun()
                    except Exception as e:
                        st.error(f"Pipeline failed: {e}")
        
    except Exception as e:
        st.error(f"Error loading drift data: {e}")
