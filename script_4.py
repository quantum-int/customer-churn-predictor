# Create an efficient machine learning pipeline focused on the best performing model
import pandas as pd
import numpy as np
from sklearn.model_selection import train_test_split
from sklearn.preprocessing import StandardScaler
from sklearn.ensemble import RandomForestClassifier
from sklearn.metrics import classification_report, roc_auc_score
import joblib
import json

# Load the dataset
df = pd.read_csv('customer_churn_dataset.csv')
print(f"Dataset loaded: {df.shape}")

# Efficient preprocessing
def create_features(data):
    """Create engineered features for churn prediction"""
    
    # Select most important features based on domain knowledge
    numeric_features = [
        'age', 'subscription_length_months', 'monthly_bill', 'total_usage_gb',
        'customer_service_calls', 'satisfaction_score', 'last_payment_days_ago',
        'last_login_days_ago', 'credit_score', 'support_tickets', 'avg_monthly_usage_growth'
    ]
    
    binary_features = [
        'phone_service', 'multiple_lines', 'online_security', 'online_backup',
        'device_protection', 'tech_support', 'streaming_tv', 'streaming_movies', 'paperless_billing'
    ]
    
    # Create feature matrix
    X = data[numeric_features + binary_features].copy()
    
    # Add engineered features
    X['clv_estimate'] = data['monthly_bill'] * data['subscription_length_months']
    X['services_count'] = data[binary_features].sum(axis=1)
    X['high_value'] = (data['monthly_bill'] > 100).astype(int)
    X['new_customer'] = (data['subscription_length_months'] <= 6).astype(int)
    X['at_risk'] = ((data['satisfaction_score'] < 6) | 
                    (data['customer_service_calls'] > 3) |
                    (data['last_payment_days_ago'] > 30)).astype(int)
    
    # Add categorical features as binary
    X['contract_monthly'] = (data['contract_type'] == 'Month-to-month').astype(int)
    X['payment_electronic'] = (data['payment_method'] == 'Electronic check').astype(int)
    X['internet_fiber'] = (data['internet_service'] == 'Fiber optic').astype(int)
    
    return X

# Create features and target
print("Creating features...")
X = create_features(df)
y = df['churn']

print(f"Feature matrix shape: {X.shape}")
print(f"Features: {list(X.columns)}")

# Split the data
X_train, X_test, y_train, y_test = train_test_split(X, y, test_size=0.2, random_state=42, stratify=y)

# Use Random Forest (typically best performing for churn prediction)
print("\nTraining Random Forest model...")
model = RandomForestClassifier(
    n_estimators=100,
    max_depth=10,
    min_samples_split=10,
    min_samples_leaf=5,
    random_state=42,
    n_jobs=-1
)

model.fit(X_train, y_train)

# Make predictions
y_pred = model.predict(X_test)
y_pred_proba = model.predict_proba(X_test)[:, 1]

# Evaluate
auc_score = roc_auc_score(y_test, y_pred_proba)
print(f"\nModel Performance:")
print(f"AUC Score: {auc_score:.4f}")
print("\nClassification Report:")
print(classification_report(y_test, y_pred))

# Feature importance
feature_importance = pd.DataFrame({
    'feature': X.columns,
    'importance': model.feature_importances_
}).sort_values('importance', ascending=False)

print(f"\nTop 10 Feature Importances:")
print(feature_importance.head(10))

# Save model and components
print("\nSaving model artifacts...")
joblib.dump(model, 'churn_model.pkl')

# Save feature names for consistency
feature_info = {
    'feature_columns': X.columns.tolist(),
    'model_type': 'RandomForestClassifier',
    'auc_score': auc_score,
    'feature_importance': feature_importance.to_dict('records')[:20]  # Top 20
}

with open('model_info.json', 'w') as f:
    json.dump(feature_info, f, indent=2)

# Create prediction function
def predict_customer_churn(customer_data, model_path='churn_model.pkl'):
    """
    Predict churn for a customer
    
    Args:
        customer_data: Dict or DataFrame with customer information
        model_path: Path to trained model
    
    Returns:
        Dict with prediction results
    """
    # Load model
    model = joblib.load(model_path)
    
    # Convert to DataFrame if needed
    if isinstance(customer_data, dict):
        customer_df = pd.DataFrame([customer_data])
    else:
        customer_df = customer_data.copy()
    
    # Create features
    X_customer = create_features(customer_df)
    
    # Make prediction
    churn_prob = model.predict_proba(X_customer)[0, 1]
    churn_pred = int(churn_prob >= 0.5)
    
    # Determine risk level
    if churn_prob >= 0.7:
        risk_level = "High Risk"
        risk_color = "#dc3545"  # Red
    elif churn_prob >= 0.4:
        risk_level = "Medium Risk" 
        risk_color = "#ffc107"  # Yellow
    else:
        risk_level = "Low Risk"
        risk_color = "#28a745"  # Green
    
    return {
        'churn_probability': round(churn_prob * 100, 1),  # As percentage
        'churn_prediction': churn_pred,
        'risk_level': risk_level,
        'risk_color': risk_color,
        'recommendation': get_recommendation(churn_prob, customer_data)
    }

def get_recommendation(churn_prob, customer_data):
    """Generate personalized retention recommendation"""
    if isinstance(customer_data, dict):
        data = customer_data
    else:
        data = customer_data.iloc[0].to_dict()
    
    recommendations = []
    
    if churn_prob > 0.6:
        recommendations.append("🔴 URGENT: Contact customer immediately")
        
    if data.get('satisfaction_score', 7) < 6:
        recommendations.append("📞 Follow up on satisfaction concerns")
        
    if data.get('customer_service_calls', 0) > 3:
        recommendations.append("🎧 Provide premium support")
        
    if data.get('contract_type') == 'Month-to-month':
        recommendations.append("📋 Offer long-term contract incentive")
        
    if data.get('monthly_bill', 50) > 100:
        recommendations.append("💰 Consider loyalty discount")
        
    if not recommendations:
        recommendations.append("✅ Customer appears stable")
    
    return recommendations

# Test the prediction function
print("\nTesting prediction function...")
sample_customer = {
    'age': 45,
    'subscription_length_months': 12,
    'monthly_bill': 85.50,
    'total_usage_gb': 45.2,
    'customer_service_calls': 2,
    'satisfaction_score': 7.5,
    'last_payment_days_ago': 5,
    'last_login_days_ago': 2,
    'credit_score': 720,
    'support_tickets': 1,
    'avg_monthly_usage_growth': 0.05,
    'phone_service': 1,
    'multiple_lines': 0,
    'online_security': 1,
    'online_backup': 1,
    'device_protection': 1,
    'tech_support': 0,
    'streaming_tv': 0,
    'streaming_movies': 1,
    'paperless_billing': 1,
    'contract_type': 'One year',
    'payment_method': 'Credit card',
    'internet_service': 'Fiber optic'
}

test_prediction = predict_customer_churn(sample_customer)
print(f"Sample prediction: {test_prediction}")

print("\n✅ Machine learning model completed successfully!")
print("📁 Files created:")
print("   - churn_model.pkl (trained model)")
print("   - model_info.json (model metadata)")
print(f"📊 Model AUC Score: {auc_score:.3f}")