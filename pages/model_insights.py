"""Model Insights Page - SHAP and Feature Importance"""
import streamlit as st
import plotly.graph_objects as go
import plotly.express as px
import pandas as pd


def render():
    """Render model insights page"""
    st.markdown('<h1 class="main-header">Model Insights</h1>', unsafe_allow_html=True)
    st.markdown('<p class="sub-header">Understanding how the model makes predictions</p>', unsafe_allow_html=True)
    
    # Explanation
    with st.expander("About Model Explainability", expanded=False):
        st.markdown("""
            **Why Explainability Matters:**
            
            Understanding why a model makes certain predictions is crucial for:
            - Building trust in the model's decisions
            - Identifying potential issues or biases
            - Improving model performance
            - Regulatory compliance
            
            **SHAP (SHapley Additive exPlanations):**
            
            SHAP values show how each feature contributes to a prediction.
            - Positive values push the prediction higher
            - Negative values push it lower
            - The magnitude indicates the strength of the contribution
            
            **Feature Importance:**
            
            Shows which features the model relies on most heavily for making decisions.
        """)
    
    # Model selection
    try:
        from app.predictor import model_loader
        
        if not model_loader.is_loaded:
            st.warning("Models not loaded. Please run the training pipeline first.")
            return
        
        available_models = [m for m in model_loader.models.keys() 
                          if m not in ['classifier', 'kmeans', 'pca']]
        
        col1, col2 = st.columns([2, 1])
        with col1:
            selected_model = st.selectbox(
                "Select Model for Analysis",
                available_models,
                index=available_models.index(model_loader.best_model_name) 
                    if model_loader.best_model_name in available_models else 0,
                help="Choose which model to analyze"
            )
        with col2:
            st.markdown(f"""
                <div class="info-box">
                    <p><strong>Best Model:</strong> {model_loader.best_model_name}</p>
                </div>
            """, unsafe_allow_html=True)
        
    except Exception as e:
        st.error(f"Error loading models: {e}")
        return
    
    st.markdown("---")
    
    # Tabs for different insights
    tab1, tab2, tab3 = st.tabs(["SHAP Analysis", "Feature Importance", "Model Comparison"])
    
    with tab1:
        st.subheader("SHAP Values")
        
        try:
            from app.data_fetcher import fetch_price_history
            from app.feature_engineering import engineer_features
            from app.explainer import get_shap_values
            
            with st.spinner("Calculating SHAP values..."):
                history = fetch_price_history(hours=6)
                features = engineer_features(history)
                shap_data = get_shap_values(features, selected_model)
            
            if shap_data:
                # Top features bar chart
                top_features = shap_data.get('top_features', [])
                
                if top_features:
                    df = pd.DataFrame(top_features)
                    
                    # Color based on positive/negative impact
                    colors = ['#22c55e' if v > 0 else '#ef4444' for v in df['importance']]
                    
                    fig = go.Figure(go.Bar(
                        x=df['importance'],
                        y=df['feature'],
                        orientation='h',
                        marker_color=colors
                    ))
                    
                    fig.update_layout(
                        title="Top Feature Contributions (SHAP)",
                        plot_bgcolor='rgba(0,0,0,0)',
                        paper_bgcolor='rgba(0,0,0,0)',
                        font=dict(color='#e2e8f0'),
                        xaxis_title="SHAP Value (Impact on Prediction)",
                        yaxis_title=None,
                        height=400,
                        margin=dict(l=0, r=0, t=40, b=0)
                    )
                    fig.update_yaxes(autorange="reversed")
                    
                    st.plotly_chart(fig, use_container_width=True)
                    
                    # Interpretation
                    st.markdown("**Interpretation:**")
                    positive_features = [f for f in top_features if f['importance'] > 0]
                    negative_features = [f for f in top_features if f['importance'] < 0]
                    
                    if positive_features:
                        st.markdown(f"- Features pushing price **higher**: {', '.join([f['feature'] for f in positive_features[:3]])}")
                    if negative_features:
                        st.markdown(f"- Features pushing price **lower**: {', '.join([f['feature'] for f in negative_features[:3]])}")
                else:
                    st.info("No SHAP values available for this model.")
            else:
                st.warning("Could not calculate SHAP values.")
                
        except Exception as e:
            st.error(f"Error calculating SHAP values: {e}")
    
    with tab2:
        st.subheader("Feature Importance")
        
        try:
            from app.explainer import get_feature_importance
            
            importance = get_feature_importance(selected_model)
            
            if importance:
                # Take top 15 features
                top_n = 15
                sorted_imp = dict(list(importance.items())[:top_n])
                
                fig = go.Figure(go.Bar(
                    x=list(sorted_imp.values()),
                    y=list(sorted_imp.keys()),
                    orientation='h',
                    marker_color='#a855f7'
                ))
                
                fig.update_layout(
                    title=f"Top {top_n} Most Important Features",
                    plot_bgcolor='rgba(0,0,0,0)',
                    paper_bgcolor='rgba(0,0,0,0)',
                    font=dict(color='#e2e8f0'),
                    xaxis_title="Importance Score",
                    yaxis_title=None,
                    height=500,
                    margin=dict(l=0, r=0, t=40, b=0)
                )
                fig.update_yaxes(autorange="reversed")
                
                st.plotly_chart(fig, use_container_width=True)
                
                # Feature categories
                st.markdown("---")
                st.subheader("Feature Categories")
                
                categories = {
                    "Technical Indicators": ['rsi', 'macd', 'macd_signal', 'macd_histogram', 
                                            'bb_width', 'bb_position'],
                    "Moving Averages": ['sma_5', 'sma_10', 'sma_20', 'ema_5', 'ema_10', 'ema_20',
                                       'price_to_sma_20', 'sma_5_to_sma_20'],
                    "Volatility & Momentum": ['volatility', 'momentum_10', 'roc_10'],
                    "Returns": ['returns', 'log_returns'] + [f'returns_lag_{i}' for i in [1,2,3,5,10]],
                    "Lag Features": [f'price_lag_{i}' for i in [1,2,3,5,10]],
                    "Time Features": ['hour', 'day_of_week', 'is_weekend']
                }
                
                cat_importance = {}
                for cat, features in categories.items():
                    total = sum(importance.get(f, 0) for f in features)
                    cat_importance[cat] = total
                
                fig2 = px.pie(
                    values=list(cat_importance.values()),
                    names=list(cat_importance.keys()),
                    title="Importance by Feature Category",
                    color_discrete_sequence=px.colors.sequential.Purples_r
                )
                fig2.update_layout(
                    plot_bgcolor='rgba(0,0,0,0)',
                    paper_bgcolor='rgba(0,0,0,0)',
                    font=dict(color='#e2e8f0')
                )
                
                st.plotly_chart(fig2, use_container_width=True)
            else:
                st.warning("Feature importance not available for this model type.")
                
        except Exception as e:
            st.error(f"Error getting feature importance: {e}")
    
    with tab3:
        st.subheader("Model Comparison")
        
        try:
            metadata = model_loader.metadata
            
            if metadata:
                st.markdown(f"""
                    <div class="info-box">
                        <p><strong>Model Version:</strong> {metadata.get('version', 'N/A')}</p>
                        <p><strong>Created:</strong> {metadata.get('created_at', 'N/A')}</p>
                        <p><strong>Best Model:</strong> {metadata.get('best_model', 'N/A')}</p>
                        <p><strong>Training Samples:</strong> {metadata.get('training_samples', 'N/A')}</p>
                    </div>
                """, unsafe_allow_html=True)
                
                st.markdown("---")
                
                # Model metrics comparison
                metrics = metadata.get('metrics', {})
                
                if metrics:
                    st.markdown("### Model Performance Metrics")
                    st.markdown("*Lower RMSE and MAE are better. Higher R² is better.*")
                    
                    # Create comparison DataFrame
                    comparison_data = []
                    regression_models = ['xgboost', 'random_forest', 'gradient_boosting', 'ridge']
                    
                    for model_name in regression_models:
                        if model_name in metrics:
                            model_metrics = metrics[model_name]
                            comparison_data.append({
                                'Model': model_name.replace('_', ' ').title(),
                                'RMSE': f"{model_metrics.get('rmse', 0):.2f}",
                                'MAE': f"{model_metrics.get('mae', 0):.2f}",
                                'R²': f"{model_metrics.get('r2', 0):.4f}",
                                'Best': 'YES' if model_name == model_loader.best_model_name else ''
                            })
                    
                    if comparison_data:
                        df_comparison = pd.DataFrame(comparison_data)
                        
                        # Display as table with styling
                        st.dataframe(
                            df_comparison,
                            use_container_width=True,
                            hide_index=True
                        )
                        
                        # Visual comparison - RMSE
                        st.markdown("---")
                        st.markdown("### RMSE Comparison (Lower is Better)")
                        
                        rmse_data = []
                        for model_name in regression_models:
                            if model_name in metrics:
                                rmse_data.append({
                                    'Model': model_name.replace('_', ' ').title(),
                                    'RMSE': metrics[model_name].get('rmse', 0),
                                    'is_best': model_name == model_loader.best_model_name
                                })
                        
                        if rmse_data:
                            df_rmse = pd.DataFrame(rmse_data)
                            colors = ['#22c55e' if row['is_best'] else '#6366f1' 
                                     for _, row in df_rmse.iterrows()]
                            
                            fig_rmse = go.Figure(go.Bar(
                                x=df_rmse['Model'],
                                y=df_rmse['RMSE'],
                                marker_color=colors,
                                text=df_rmse['RMSE'].round(2),
                                textposition='auto'
                            ))
                            
                            fig_rmse.update_layout(
                                plot_bgcolor='rgba(0,0,0,0)',
                                paper_bgcolor='rgba(0,0,0,0)',
                                font=dict(color='#e2e8f0'),
                                yaxis_title="RMSE (Root Mean Squared Error)",
                                xaxis_title=None,
                                height=400,
                                showlegend=False
                            )
                            
                            st.plotly_chart(fig_rmse, use_container_width=True)
                            
                            best_model_metrics = metrics.get(model_loader.best_model_name, {})
                            st.success(f"""
                                **{model_loader.best_model_name.replace('_', ' ').title()}** was selected as the best model with:
                                - RMSE: ${best_model_metrics.get('rmse', 0):,.2f}
                                - MAE: ${best_model_metrics.get('mae', 0):,.2f}
                                - R²: {best_model_metrics.get('r2', 0):.4f}
                            """)
                    else:
                        st.info("No regression model metrics available.")
                else:
                    st.info("No metrics available. Please run training pipeline.")
                
                st.markdown("---")
                
                # Model list
                st.markdown("### Loaded Models")
                for name in model_loader.models.keys():
                    model_type = type(model_loader.models[name]).__name__
                    is_best = " 🏆" if name == model_loader.best_model_name else ""
                    st.markdown(f"- **{name}**: {model_type}{is_best}")
            
        except Exception as e:
            st.error(f"Error loading model comparison: {e}")

