"""Run All Pipelines - Single Command Execution"""
import sys
from datetime import datetime

print("\n" + "="*70)
print("CRYPTOSENTINEL - FULL PIPELINE EXECUTION")
print("="*70)
print(f"Started at: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}")
print("="*70 + "\n")

try:
    # Step 1: Feature Pipeline
    print("\n" + "="*70)
    print("STEP 1/3: FEATURE PIPELINE")
    print("="*70)
    print("Fetching price data and engineering features...\n")
    
    from pipelines.feature_pipeline import feature_pipeline
    feature_result = feature_pipeline()
    
    if not feature_result.get('success'):
        print("\nFeature pipeline failed!")
        sys.exit(1)
    
    print(f"\nFeature pipeline complete!")
    print(f"   - Rows processed: {feature_result.get('rows_processed', 0)}")
    print(f"   - Duration: {feature_result.get('duration_seconds', 0):.2f}s")
    
    # Step 2: Training Pipeline
    print("\n" + "="*70)
    print("STEP 2/3: TRAINING PIPELINE")
    print("="*70)
    print("Training models and detecting drift...\n")
    
    from pipelines.training_pipeline import training_pipeline
    training_result = training_pipeline()
    
    print(f"\nTraining pipeline complete!")
    print(f"   - Best model: {training_result.get('best_model', 'N/A')}")
    print(f"   - Samples trained: {training_result.get('samples_trained', 0)}")
    print(f"   - Duration: {training_result.get('duration_seconds', 0):.2f}s")
    
    metrics = training_result.get('metrics', {})
    if metrics:
        best = training_result.get('best_model', '')
        if best in metrics:
            print(f"   - RMSE: {metrics[best].get('rmse', 0):.6f}")
            print(f"   - MAE: {metrics[best].get('mae', 0):.6f}")
            print(f"   - R²: {metrics[best].get('r2', 0):.4f}")
    
    # Step 3: Inference Pipeline
    print("\n" + "="*70)
    print("STEP 3/3: INFERENCE PIPELINE")
    print("="*70)
    print("Generating predictions and checking alerts...\n")
    
    from pipelines.inference_pipeline import inference_pipeline
    inference_result = inference_pipeline()
    
    print(f"\nInference pipeline complete!")
    print(f"   - Current price: ${inference_result.get('current_price', 0):,.2f}")
    
    prediction = inference_result.get('prediction', {})
    if prediction:
        print(f"   - Predicted price: ${prediction.get('predicted_price', 0):,.2f}")
        print(f"   - Direction: {prediction.get('predicted_direction', 'N/A').upper()}")
        print(f"   - Confidence: {prediction.get('confidence', 0):.1f}%")
    
    alerts = inference_result.get('alerts', [])
    if alerts:
        print(f"   - Alerts generated: {len(alerts)}")
    
    print(f"   - Duration: {inference_result.get('duration_seconds', 0):.2f}s")
    
    # Summary
    total_duration = (
        feature_result.get('duration_seconds', 0) +
        training_result.get('duration_seconds', 0) +
        inference_result.get('duration_seconds', 0)
    )
    
    print("\n" + "="*70)
    print("ALL PIPELINES COMPLETED SUCCESSFULLY")
    print("="*70)
    print(f"Total execution time: {total_duration:.2f}s")
    print(f"Completed at: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}")
    print("="*70 + "\n")
    
    print("CryptoSentinel is ready!")
    print("   Run: streamlit run dashboard.py")
    print()

except KeyboardInterrupt:
    print("\n\nPipeline execution interrupted by user")
    sys.exit(130)
    
except Exception as e:
    print(f"\n\nPipeline execution failed!")
    print(f"Error: {e}")
    import traceback
    traceback.print_exc()
    sys.exit(1)


