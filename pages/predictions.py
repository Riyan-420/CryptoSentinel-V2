"""Predictions Page - View and analyze predictions"""
import streamlit as st
import plotly.graph_objects as go
import pandas as pd
from datetime import datetime


def render():
    """Render predictions page"""
    st.markdown('<h1 class="main-header">Predictions</h1>', unsafe_allow_html=True)
    st.markdown('<p class="sub-header">Historical predictions and performance tracking</p>', unsafe_allow_html=True)
    
    # Explanation dropdown
    with st.expander("How Predictions Work", expanded=False):
        st.markdown("""
            **Prediction Methodology:**
            
            Our ML pipeline uses ensemble learning with multiple models:
            
            1. **XGBoost** - Gradient boosting for price regression
            2. **Random Forest** - Ensemble of decision trees
            3. **Gradient Boosting** - Sequential error correction
            4. **Ridge Regression** - Regularized linear model
            
            The best model is selected based on validation RMSE. Additionally:
            
            - **Direction Classifier** - Predicts up/down movement
            - **K-Means Clustering** - Identifies market regimes
            
            **Validation Rules:**
            
            Predictions are validated after 30 minutes. A prediction is marked correct if:
            - The price moved at least 0.1% (to filter noise)
            - The actual direction matches the predicted direction
        """)
    
    # Current prediction
    st.subheader("Current Prediction")
    
    try:
        from app.data_fetcher import fetch_current_price, fetch_price_history
        from app.feature_engineering import engineer_features
        from app.predictor import generate_prediction, model_loader
        
        current = fetch_current_price()
        history = fetch_price_history(hours=6)
        features = engineer_features(history)
        prediction = generate_prediction(features, current['current_price'])
        
        if prediction:
            col1, col2, col3 = st.columns(3)
            
            with col1:
                st.metric(
                    "Predicted Price",
                    f"${prediction['predicted_price']:,.2f}",
                    f"{prediction['price_change_pct']:+.2f}%"
                )
            
            with col2:
                direction_color = "positive" if prediction['predicted_direction'] == 'up' else "negative"
                st.markdown(f"""
                    <div class="metric-card">
                        <p style="color: #94a3b8;">Direction</p>
                        <p class="{direction_color}" style="font-size: 1.5rem; text-transform: uppercase;">
                            {prediction['predicted_direction']}
                        </p>
                        <p style="color: #64748b;">{prediction['confidence']:.1f}% confidence</p>
                    </div>
                """, unsafe_allow_html=True)
            
            with col3:
                st.markdown(f"""
                    <div class="metric-card">
                        <p style="color: #94a3b8;">Model Used</p>
                        <p style="font-size: 1.2rem; color: #a855f7;">{prediction['model_used']}</p>
                        <p style="color: #64748b;">Horizon: {prediction['prediction_horizon_minutes']} min</p>
                    </div>
                """, unsafe_allow_html=True)
            
            # All model predictions
            st.markdown("---")
            st.subheader("All Model Predictions")
            
            all_preds = prediction.get('all_predictions', {})
            if all_preds:
                pred_df = pd.DataFrame([
                    {"Model": k, "Predicted Price": f"${v:,.2f}", 
                     "Change": f"{((v - current['current_price']) / current['current_price'] * 100):+.2f}%"}
                    for k, v in all_preds.items()
                ])
                st.dataframe(pred_df, use_container_width=True, hide_index=True)
        else:
            st.warning("No prediction available. Models may not be loaded.")
            
    except Exception as e:
        st.error(f"Error generating prediction: {e}")
    
    # Prediction history
    st.markdown("---")
    st.subheader("Prediction History")
    
    try:
        from app.predictor import get_prediction_history, get_prediction_accuracy, validate_predictions
        from app.data_fetcher import fetch_current_price
        
        # Validate predictions before displaying
        try:
            current = fetch_current_price()
            validate_predictions(current['current_price'])
        except Exception as e:
            st.warning(f"Could not validate predictions: {e}")
        
        history = get_prediction_history()
        
        if history:
            # Filter options
            col1, col2 = st.columns(2)
            with col1:
                show_validated = st.checkbox("Show only validated", value=False)
            with col2:
                show_correct = st.selectbox(
                    "Filter by result",
                    ["All", "Correct", "Incorrect"],
                    index=0
                )
            
            # Filter history
            filtered = history
            if show_validated:
                filtered = [p for p in filtered if p.get('was_correct') is not None]
            if show_correct == "Correct":
                filtered = [p for p in filtered if p.get('was_correct') == True]
            elif show_correct == "Incorrect":
                filtered = [p for p in filtered if p.get('was_correct') == False]
            
            # Display as table
            if filtered:
                display_data = []
                for p in reversed(filtered):
                    status = ""
                    if p.get('was_correct') is None:
                        status = "Pending"
                    elif p.get('was_correct'):
                        status = "Correct"
                    else:
                        status = "Incorrect"
                    
                    display_data.append({
                        "Time": p.get('timestamp', '')[:19],
                        "Current": f"${p.get('current_price', 0):,.2f}",
                        "Predicted": f"${p.get('predicted_price', 0):,.2f}",
                        "Direction": p.get('predicted_direction', '').upper(),
                        "Actual": f"${p.get('actual_price', 0):,.2f}" if p.get('actual_price') else "-",
                        "Error": f"${p.get('error_amount', 0):,.2f}" if p.get('error_amount') else "-",
                        "Status": status
                    })
                
                df = pd.DataFrame(display_data)
                
                # Style the dataframe
                def color_status(val):
                    if val == "Correct":
                        return 'color: #22c55e'
                    elif val == "Incorrect":
                        return 'color: #ef4444'
                    return 'color: #f59e0b'
                
                styled = df.style.applymap(color_status, subset=['Status'])
                st.dataframe(styled, use_container_width=True, hide_index=True)
            else:
                st.info("No predictions match the current filter.")
            
            # Accuracy stats
            st.markdown("---")
            st.subheader("Performance Statistics")
            
            accuracy = get_prediction_accuracy()
            
            col1, col2, col3, col4 = st.columns(4)
            
            with col1:
                st.metric("Accuracy", f"{accuracy.get('accuracy', 0):.1f}%")
            with col2:
                st.metric("Validated", accuracy.get('validated_count', 0))
            with col3:
                st.metric("Correct", accuracy.get('correct_count', 0))
            with col4:
                st.metric("Avg Error", f"${accuracy.get('avg_error', 0):,.2f}")
            
        else:
            st.info("No prediction history yet. Predictions will appear here after the model makes them.")
            
    except Exception as e:
        st.error(f"Error loading prediction history: {e}")

