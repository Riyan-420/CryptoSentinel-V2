"""Dashboard Page - Main overview"""
import streamlit as st
import plotly.graph_objects as go
import plotly.express as px
from datetime import datetime
import pandas as pd


def render():
    """Render dashboard page"""
    st.markdown('<h1 class="main-header">Bitcoin Dashboard</h1>', unsafe_allow_html=True)
    st.markdown('<p class="sub-header">Real-time market data and ML predictions</p>', unsafe_allow_html=True)
    
    # Fetch current data
    try:
        from app.data_fetcher import fetch_current_price, fetch_price_history
        current = fetch_current_price()
        history = fetch_price_history(hours=24)
    except Exception as e:
        st.error(f"Failed to fetch data: {e}")
        return
    
    # Top metrics row
    col1, col2, col3, col4 = st.columns(4)
    
    with col1:
        st.metric(
            label="Bitcoin Price",
            value=f"${current['current_price']:,.2f}",
            delta=f"{current['change_percent_24h']:+.2f}%"
        )
    
    with col2:
        # Get prediction if available
        try:
            from app.feature_engineering import engineer_features
            from app.predictor import generate_prediction
            
            features = engineer_features(history)
            prediction = generate_prediction(features, current['current_price'])
            
            if prediction:
                pred_price = prediction['predicted_price']
                delta = prediction['price_change_pct']
                st.metric(
                    label="Predicted Price (30m)",
                    value=f"${pred_price:,.2f}",
                    delta=f"{delta:+.2f}%"
                )
            else:
                st.metric(label="Predicted Price", value="N/A", delta=None)
        except:
            st.metric(label="Predicted Price", value="N/A", delta=None)
    
    with col3:
        # Direction
        try:
            direction = prediction.get('predicted_direction', 'N/A') if prediction else 'N/A'
            confidence = prediction.get('confidence', 0) if prediction else 0
            color = "positive" if direction == "up" else "negative"
            st.markdown(f"""
                <div class="metric-card">
                    <p style="color: #94a3b8; margin-bottom: 0.5rem;">Predicted Direction</p>
                    <p class="{color}" style="font-size: 1.5rem; font-weight: 600;">
                        {"Bullish" if direction == "up" else "Bearish"}
                    </p>
                    <p style="color: #64748b;">{confidence:.1f}% confidence</p>
                </div>
            """, unsafe_allow_html=True)
        except:
            st.metric(label="Direction", value="N/A")
    
    with col4:
        # Market regime
        try:
            regime = prediction.get('market_regime', 'N/A') if prediction else 'N/A'
            st.markdown(f"""
                <div class="metric-card">
                    <p style="color: #94a3b8; margin-bottom: 0.5rem;">Market Regime</p>
                    <p class="neutral" style="font-size: 1.5rem; font-weight: 600; text-transform: capitalize;">
                        {regime}
                    </p>
                </div>
            """, unsafe_allow_html=True)
        except:
            st.metric(label="Market Regime", value="N/A")
    
    st.markdown("---")
    
    # Price chart
    st.subheader("Price History (24h)")
    
    if history:
        df = pd.DataFrame(history)
        df['datetime'] = pd.to_datetime(df['timestamp'], unit='ms')
        
        fig = go.Figure()
        
        fig.add_trace(go.Scatter(
            x=df['datetime'],
            y=df['price'],
            mode='lines',
            name='BTC Price',
            line=dict(color='#a855f7', width=2),
            fill='tozeroy',
            fillcolor='rgba(168, 85, 247, 0.1)'
        ))
        
        # Add prediction line if available
        try:
            if prediction:
                last_time = df['datetime'].iloc[-1]
                pred_time = last_time + pd.Timedelta(minutes=30)
                
                fig.add_trace(go.Scatter(
                    x=[last_time, pred_time],
                    y=[current['current_price'], prediction['predicted_price']],
                    mode='lines+markers',
                    name='Prediction',
                    line=dict(color='#22c55e' if prediction['predicted_direction'] == 'up' else '#ef4444', 
                             width=2, dash='dash'),
                    marker=dict(size=10)
                ))
        except:
            pass
        
        fig.update_layout(
            plot_bgcolor='rgba(0,0,0,0)',
            paper_bgcolor='rgba(0,0,0,0)',
            font=dict(color='#e2e8f0'),
            xaxis=dict(
                showgrid=True,
                gridcolor='rgba(100,100,100,0.2)',
                title=None
            ),
            yaxis=dict(
                showgrid=True,
                gridcolor='rgba(100,100,100,0.2)',
                title='Price (USD)',
                tickprefix='$'
            ),
            legend=dict(
                orientation='h',
                yanchor='bottom',
                y=1.02,
                xanchor='right',
                x=1
            ),
            margin=dict(l=0, r=0, t=30, b=0),
            height=400
        )
        
        st.plotly_chart(fig, use_container_width=True)
    
    # Model info section
    st.markdown("---")
    
    col1, col2 = st.columns(2)
    
    with col1:
        st.subheader("Model Information")
        
        try:
            from app.predictor import model_loader
            if model_loader.is_loaded:
                st.markdown(f"""
                    <div class="info-box">
                        <p><strong>Active Model:</strong> {model_loader.best_model_name}</p>
                        <p><strong>Version:</strong> {model_loader.metadata.get('version', 'N/A')}</p>
                        <p><strong>Models Loaded:</strong> {', '.join(model_loader.models.keys())}</p>
                    </div>
                """, unsafe_allow_html=True)
            else:
                st.warning("No models loaded. Run training pipeline first.")
        except Exception as e:
            st.warning(f"Could not load model info: {e}")
    
    with col2:
        st.subheader("Quick Stats")
        
        try:
            from app.predictor import get_prediction_accuracy
            accuracy = get_prediction_accuracy()
            
            st.markdown(f"""
                <div class="info-box">
                    <p><strong>Prediction Accuracy:</strong> {accuracy.get('accuracy', 0):.1f}%</p>
                    <p><strong>Validated Predictions:</strong> {accuracy.get('validated_count', 0)}</p>
                    <p><strong>Average Error:</strong> ${accuracy.get('avg_error', 0):,.2f}</p>
                </div>
            """, unsafe_allow_html=True)
        except:
            st.info("No prediction history available yet.")

