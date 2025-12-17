"""Data Analysis Page - EDA and Drift Detection"""
import streamlit as st
import plotly.graph_objects as go
import plotly.express as px
import pandas as pd


def render():
    """Render data analysis page"""
    st.markdown('<h1 class="main-header">Data Analysis</h1>', unsafe_allow_html=True)
    st.markdown('<p class="sub-header">Exploratory data analysis and data quality monitoring</p>', unsafe_allow_html=True)
    
    # Tabs
    tab1, tab2 = st.tabs(["EDA Report", "Correlations"])
    
    with tab1:
        render_eda()
    
    with tab2:
        render_correlations()


def render_eda():
    """Render EDA section"""
    st.subheader("Exploratory Data Analysis")
    
    with st.expander("About EDA", expanded=False):
        st.markdown("""
            **Exploratory Data Analysis** helps understand the underlying patterns in our data:
            
            - **Trend Analysis**: Identifies bullish/bearish trends using moving averages
            - **Statistical Summary**: Key statistics like mean, std, skewness
            - **Anomaly Detection**: Identifies unusual price movements using z-scores
        """)
    
    try:
        from app.data_fetcher import fetch_price_history
        from app.feature_engineering import engineer_features
        from app.eda import generate_eda_report
        
        # Time range selector
        hours = st.selectbox(
            "Select Time Range",
            [6, 12, 24, 48, 72],
            index=2,
            format_func=lambda x: f"{x} hours"
        )
        
        with st.spinner("Generating EDA report..."):
            history = fetch_price_history(hours=hours)
            features = engineer_features(history)
            report = generate_eda_report(features)
        
        if report.get('error'):
            st.error(report['error'])
            return
        
        # Trend
        col1, col2 = st.columns(2)
        
        with col1:
            trend = report.get('trend', {})
            trend_type = trend.get('trend', 'neutral')
            trend_color = 'positive' if trend_type == 'bullish' else ('negative' if trend_type == 'bearish' else 'neutral')
            
            st.markdown(f"""
                <div class="metric-card">
                    <h4 style="color: #94a3b8;">Market Trend</h4>
                    <p class="{trend_color}" style="font-size: 1.5rem; text-transform: capitalize;">
                        {trend_type}
                    </p>
                    <p style="color: #64748b;">Strength: {trend.get('strength', 0)*100:.0f}%</p>
                    <p style="color: #64748b; font-size: 0.85rem;">{trend.get('description', '')}</p>
                </div>
            """, unsafe_allow_html=True)
        
        with col2:
            stats = report.get('statistics', {})
            st.markdown(f"""
                <div class="metric-card">
                    <h4 style="color: #94a3b8;">Price Statistics</h4>
                    <p>Mean: <strong>${stats.get('mean', 0):,.2f}</strong></p>
                    <p>Std Dev: <strong>${stats.get('std', 0):,.2f}</strong></p>
                    <p>Range: <strong>${stats.get('range', 0):,.2f}</strong></p>
                </div>
            """, unsafe_allow_html=True)
        
        # Statistics table
        st.markdown("---")
        st.subheader("Detailed Statistics")
        
        stats_df = pd.DataFrame([
            {"Metric": "Count", "Value": stats.get('count', 0)},
            {"Metric": "Mean", "Value": f"${stats.get('mean', 0):,.2f}"},
            {"Metric": "Median", "Value": f"${stats.get('median', 0):,.2f}"},
            {"Metric": "Std Dev", "Value": f"${stats.get('std', 0):,.2f}"},
            {"Metric": "Min", "Value": f"${stats.get('min', 0):,.2f}"},
            {"Metric": "Max", "Value": f"${stats.get('max', 0):,.2f}"},
            {"Metric": "Skewness", "Value": f"{stats.get('skewness', 0):.4f}"},
            {"Metric": "Kurtosis", "Value": f"{stats.get('kurtosis', 0):.4f}"},
        ])
        
        if stats.get('sharpe_ratio'):
            stats_df = pd.concat([stats_df, pd.DataFrame([
                {"Metric": "Sharpe Ratio", "Value": f"{stats.get('sharpe_ratio', 0):.4f}"}
            ])], ignore_index=True)
        
        st.dataframe(stats_df, use_container_width=True, hide_index=True)
        
        # Anomalies
        anomalies = report.get('anomalies', [])
        if anomalies:
            st.markdown("---")
            st.subheader("Detected Anomalies")
            
            anomaly_df = pd.DataFrame(anomalies)
            st.dataframe(anomaly_df, use_container_width=True, hide_index=True)
        
    except Exception as e:
        st.error(f"Error generating EDA report: {e}")


def render_correlations():
    """Render correlation matrix section"""
    st.subheader("Feature Correlations")
    
    with st.expander("About Correlations", expanded=False):
        st.markdown("""
            **Correlation Analysis** shows how features relate to each other:
            
            - Values close to **1** indicate strong positive correlation
            - Values close to **-1** indicate strong negative correlation
            - Values close to **0** indicate no linear relationship
            
            Understanding correlations helps identify:
            - Redundant features
            - Feature interactions
            - Potential multicollinearity issues
        """)
    
    try:
        from app.data_fetcher import fetch_price_history
        from app.feature_engineering import engineer_features
        from app.eda import calculate_correlation_matrix
        
        with st.spinner("Calculating correlations..."):
            history = fetch_price_history(hours=24)
            features = engineer_features(history)
        
        # Feature selection
        available_features = ['price', 'rsi', 'macd', 'volatility', 'momentum_10', 
                             'sma_5', 'sma_20', 'bb_width', 'returns']
        available_features = [f for f in available_features if f in features.columns]
        
        selected_features = st.multiselect(
            "Select features for correlation",
            available_features,
            default=available_features[:6]
        )
        
        if len(selected_features) >= 2:
            corr_data = calculate_correlation_matrix(features, selected_features)
            
            if 'error' not in corr_data:
                matrix = pd.DataFrame(corr_data['matrix'])
                
                # Heatmap
                fig = px.imshow(
                    matrix,
                    labels=dict(x="Feature", y="Feature", color="Correlation"),
                    x=selected_features,
                    y=selected_features,
                    color_continuous_scale='RdBu_r',
                    zmin=-1, zmax=1
                )
                
                fig.update_layout(
                    plot_bgcolor='rgba(0,0,0,0)',
                    paper_bgcolor='rgba(0,0,0,0)',
                    font=dict(color='#e2e8f0'),
                    height=500
                )
                
                st.plotly_chart(fig, use_container_width=True)
                
                # Top correlations
                st.markdown("**Strongest Correlations:**")
                top_corrs = corr_data.get('top_correlations', [])
                for corr in top_corrs:
                    st.markdown(f"- {corr['feature_1']} vs {corr['feature_2']}: **{corr['correlation']:.4f}**")
            else:
                st.warning(corr_data['error'])
        else:
            st.info("Select at least 2 features to see correlations.")
            
    except Exception as e:
        st.error(f"Error calculating correlations: {e}")

