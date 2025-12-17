"""Alerts Page - View and manage alerts"""
import streamlit as st
import plotly.graph_objects as go
import pandas as pd
from datetime import datetime


def render():
    """Render alerts page"""
    st.markdown('<h1 class="main-header">Alerts</h1>', unsafe_allow_html=True)
    st.markdown('<p class="sub-header">Price movements and prediction alerts</p>', unsafe_allow_html=True)
    
    # Explanation
    with st.expander("About Alerts", expanded=False):
        st.markdown("""
            **CryptoSentinel monitors for several types of alerts:**
            
            1. **Price Change Alerts**
               - Triggered when price moves >5% from previous reading
               - Severity increases at >10% movement
            
            2. **High Volatility Alerts**
               - Triggered when volatility exceeds 50%
               - Indicates unstable market conditions
            
            3. **Prediction Deviation Alerts**
               - Triggered when actual price deviates >3% from prediction
               - May indicate model drift or unusual market conditions
            
            4. **Drawdown Alerts**
               - Triggered when price drops >10% from recent peak
               - Important for risk management
        """)
    
    try:
        from app.alerts import get_alert_history, get_alert_summary
        
        # Summary metrics
        summary = get_alert_summary()
        
        col1, col2, col3 = st.columns(3)
        
        with col1:
            st.metric("Total Alerts", summary.get('total_alerts', 0))
        with col2:
            st.metric("High Severity", summary.get('high_severity', 0))
        with col3:
            by_type = summary.get('by_type', {})
            most_common = max(by_type.items(), key=lambda x: x[1])[0] if by_type else "None"
            st.metric("Most Common", most_common.replace('_', ' ').title())
        
        # Alerts by type chart
        if summary.get('by_type'):
            st.markdown("---")
            st.subheader("Alerts by Type")
            
            by_type = summary['by_type']
            
            fig = go.Figure(go.Bar(
                x=list(by_type.keys()),
                y=list(by_type.values()),
                marker_color=['#a855f7', '#6366f1', '#22c55e', '#ef4444'][:len(by_type)]
            ))
            
            fig.update_layout(
                plot_bgcolor='rgba(0,0,0,0)',
                paper_bgcolor='rgba(0,0,0,0)',
                font=dict(color='#e2e8f0'),
                xaxis_title=None,
                yaxis_title="Count",
                height=300,
                margin=dict(l=0, r=0, t=20, b=0)
            )
            
            st.plotly_chart(fig, use_container_width=True)
        
        # Alert history
        st.markdown("---")
        st.subheader("Alert History")
        
        # Filters
        col1, col2 = st.columns(2)
        with col1:
            filter_type = st.selectbox(
                "Filter by Type",
                ["All", "price_change", "high_volatility", "prediction_deviation", "drawdown"],
                index=0
            )
        with col2:
            filter_severity = st.selectbox(
                "Filter by Severity",
                ["All", "high", "medium"],
                index=0
            )
        
        alerts = get_alert_history(limit=50)
        
        # Apply filters
        if filter_type != "All":
            alerts = [a for a in alerts if a.get('type') == filter_type]
        if filter_severity != "All":
            alerts = [a for a in alerts if a.get('severity') == filter_severity]
        
        if alerts:
            for alert in reversed(alerts):
                severity = alert.get('severity', 'medium')
                severity_color = '#ef4444' if severity == 'high' else '#f59e0b'
                alert_type = alert.get('type', 'unknown').replace('_', ' ').title()
                
                with st.expander(f"{alert_type} - {alert.get('timestamp', '')[:19]}", expanded=False):
                    st.markdown(f"""
                        <div style="border-left: 4px solid {severity_color}; padding-left: 1rem;">
                            <p><strong>Message:</strong> {alert.get('message', 'N/A')}</p>
                            <p><strong>Severity:</strong> <span style="color: {severity_color}; text-transform: uppercase;">{severity}</span></p>
                        </div>
                    """, unsafe_allow_html=True)
                    
                    # Show additional details based on type
                    alert_type_raw = alert.get('type', '')
                    
                    if alert_type_raw == 'price_change':
                        col1, col2, col3 = st.columns(3)
                        with col1:
                            st.metric("Current", f"${alert.get('current_price', 0):,.2f}")
                        with col2:
                            st.metric("Previous", f"${alert.get('previous_price', 0):,.2f}")
                        with col3:
                            st.metric("Change", f"{alert.get('change_percent', 0):+.2f}%")
                    
                    elif alert_type_raw == 'high_volatility':
                        st.metric("Volatility", f"{alert.get('volatility', 0)*100:.2f}%")
                    
                    elif alert_type_raw == 'prediction_deviation':
                        col1, col2, col3 = st.columns(3)
                        with col1:
                            st.metric("Current", f"${alert.get('current_price', 0):,.2f}")
                        with col2:
                            st.metric("Predicted", f"${alert.get('predicted_price', 0):,.2f}")
                        with col3:
                            st.metric("Deviation", f"{alert.get('deviation_percent', 0):.2f}%")
                    
                    elif alert_type_raw == 'drawdown':
                        col1, col2, col3 = st.columns(3)
                        with col1:
                            st.metric("Current", f"${alert.get('current_price', 0):,.2f}")
                        with col2:
                            st.metric("Peak", f"${alert.get('peak_price', 0):,.2f}")
                        with col3:
                            st.metric("Drawdown", f"{alert.get('drawdown_percent', 0):.2f}%")
        else:
            st.info("No alerts match the current filters.")
        
        # Clear alerts button
        st.markdown("---")
        col1, col2 = st.columns([1, 3])
        with col1:
            if st.button("Clear All Alerts"):
                from app.alerts import clear_alerts
                clear_alerts()
                st.success("Alerts cleared!")
                st.rerun()
        
    except Exception as e:
        st.error(f"Error loading alerts: {e}")

