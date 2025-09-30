# Now let's build comprehensive machine learning models for churn prediction
import pandas as pd
import numpy as np
from sklearn.model_selection import train_test_split, cross_val_score, GridSearchCV
from sklearn.preprocessing import StandardScaler, LabelEncoder, OneHotEncoder
from sklearn.ensemble import RandomForestClassifier, GradientBoostingClassifier
from sklearn.linear_model import LogisticRegression
from sklearn.svm import SVC
from sklearn.metrics import classification_report, confusion_matrix, roc_auc_score, roc_curve
from sklearn.pipeline import Pipeline
import joblib
import warnings
warnings.filterwarnings('ignore')

# Load the dataset
df = pd.read_csv('customer_churn_dataset.csv')
print(f"Dataset loaded: {df.shape}")
print(f"Churn distribution: {df['churn'].value_counts()}")

# Preprocessing pipeline
def preprocess_data(df):
    """Comprehensive preprocessing for churn prediction"""
    
    # Create a copy
    data = df.copy()
    
    # Feature engineering
    # Create customer lifetime value estimate
    data['estimated_clv'] = data['monthly_bill'] * data['subscription_length_months']
    
    # Create service intensity score
    service_features = ['phone_service', 'multiple_lines', 'online_security', 'online_backup', 
                       'device_protection', 'tech_support', 'streaming_tv', 'streaming_movies']
    data['service_count'] = data[service_features].sum(axis=1)
    
    # Create engagement score
    data['engagement_score'] = (
        10 - data['last_login_days_ago'] + 
        10 - data['last_payment_days_ago'] + 
        data['satisfaction_score'] - 
        data['customer_service_calls']
    )
    
    # Create risk indicators
    data['high_bill'] = (data['monthly_bill'] > data['monthly_bill'].quantile(0.8)).astype(int)
    data['new_customer'] = (data['subscription_length_months'] <= 6).astype(int)
    data['dissatisfied'] = (data['satisfaction_score'] < 5).astype(int)
    data['frequent_caller'] = (data['customer_service_calls'] > 3).astype(int)
    data['recent_activity_low'] = ((data['last_login_days_ago'] > 7) | 
                                   (data['last_payment_days_ago'] > 21)).astype(int)
    
    # Select features for modeling
    feature_columns = [
        'age', 'subscription_length_months', 'monthly_bill', 'total_usage_gb',
        'phone_service', 'multiple_lines', 'online_security', 'online_backup',
        'device_protection', 'tech_support', 'streaming_tv', 'streaming_movies',
        'paperless_billing', 'customer_service_calls', 'satisfaction_score',
        'last_payment_days_ago', 'last_login_days_ago', 'credit_score',
        'support_tickets', 'avg_monthly_usage_growth',
        'estimated_clv', 'service_count', 'engagement_score',
        'high_bill', 'new_customer', 'dissatisfied', 'frequent_caller', 'recent_activity_low'
    ]
    
    categorical_features = ['gender', 'location', 'internet_service', 'contract_type', 'payment_method']
    
    # Prepare features
    X = data[feature_columns].copy()
    
    # Add categorical features (one-hot encoded)
    for cat_col in categorical_features:
        dummies = pd.get_dummies(data[cat_col], prefix=cat_col)
        X = pd.concat([X, dummies], axis=1)
    
    y = data['churn']
    
    return X, y, feature_columns + [f"{cat}_{val}" for cat in categorical_features 
                                    for val in data[cat].unique()]

# Preprocess the data
print("\nPreprocessing data...")
X, y, feature_names = preprocess_data(df)
print(f"Feature matrix shape: {X.shape}")
print(f"Number of features: {len(feature_names)}")

# Split the data
X_train, X_test, y_train, y_test = train_test_split(X, y, test_size=0.2, random_state=42, stratify=y)
print(f"\nTraining set: {X_train.shape}")
print(f"Test set: {X_test.shape}")

# Scale the features
scaler = StandardScaler()
X_train_scaled = scaler.fit_transform(X_train)
X_test_scaled = scaler.transform(X_test)

# Define multiple models to compare
models = {
    'Random Forest': RandomForestClassifier(n_estimators=100, random_state=42, n_jobs=-1),
    'Gradient Boosting': GradientBoostingClassifier(n_estimators=100, random_state=42),
    'Logistic Regression': LogisticRegression(random_state=42, max_iter=1000),
    'SVM': SVC(random_state=42, probability=True)
}

# Train and evaluate models
results = {}
trained_models = {}

print("\nTraining and evaluating models...")
for name, model in models.items():
    print(f"\n=== {name} ===")
    
    # Train the model
    if name in ['Logistic Regression', 'SVM']:
        model.fit(X_train_scaled, y_train)
        y_pred = model.predict(X_test_scaled)
        y_pred_proba = model.predict_proba(X_test_scaled)[:, 1]
    else:
        model.fit(X_train, y_train)
        y_pred = model.predict(X_test)
        y_pred_proba = model.predict_proba(X_test)[:, 1]
    
    # Store the trained model
    trained_models[name] = model
    
    # Calculate metrics
    auc_score = roc_auc_score(y_test, y_pred_proba)
    
    # Cross-validation
    if name in ['Logistic Regression', 'SVM']:
        cv_scores = cross_val_score(model, X_train_scaled, y_train, cv=5, scoring='roc_auc')
    else:
        cv_scores = cross_val_score(model, X_train, y_train, cv=5, scoring='roc_auc')
    
    results[name] = {
        'auc_score': auc_score,
        'cv_mean': cv_scores.mean(),
        'cv_std': cv_scores.std(),
        'predictions': y_pred,
        'probabilities': y_pred_proba
    }
    
    print(f"AUC Score: {auc_score:.4f}")
    print(f"CV AUC: {cv_scores.mean():.4f} (+/- {cv_scores.std() * 2:.4f})")
    print("\nClassification Report:")
    print(classification_report(y_test, y_pred))

# Find the best model
best_model_name = max(results.keys(), key=lambda k: results[k]['auc_score'])
best_model = trained_models[best_model_name]
best_auc = results[best_model_name]['auc_score']

print(f"\n{'='*50}")
print(f"BEST MODEL: {best_model_name}")
print(f"AUC Score: {best_auc:.4f}")
print(f"{'='*50}")

# Feature importance for tree-based models
if best_model_name in ['Random Forest', 'Gradient Boosting']:
    feature_importance = pd.DataFrame({
        'feature': X.columns,
        'importance': best_model.feature_importances_
    }).sort_values('importance', ascending=False)
    
    print(f"\nTop 15 Feature Importances ({best_model_name}):")
    print(feature_importance.head(15))

# Save the best model and preprocessing components
print(f"\nSaving models and preprocessing components...")
joblib.dump(best_model, 'best_churn_model.pkl')
joblib.dump(scaler, 'feature_scaler.pkl')

# Save model metadata
model_metadata = {
    'model_name': best_model_name,
    'auc_score': best_auc,
    'features': X.columns.tolist(),
    'model_type': str(type(best_model).__name__),
    'cv_scores': {
        'mean': results[best_model_name]['cv_mean'],
        'std': results[best_model_name]['cv_std']
    }
}

import json
with open('model_metadata.json', 'w') as f:
    json.dump(model_metadata, f, indent=2)

print("Model artifacts saved:")
print("- best_churn_model.pkl")
print("- feature_scaler.pkl") 
print("- model_metadata.json")

# Create a sample prediction function
def predict_churn(customer_data, model, scaler, feature_columns):
    """Make churn prediction for a single customer"""
    # Ensure customer_data is a DataFrame with correct columns
    if isinstance(customer_data, dict):
        customer_data = pd.DataFrame([customer_data])
    
    # Preprocess the customer data (same as training)
    processed_data, _, _ = preprocess_data(customer_data)
    
    # Scale if needed
    if best_model_name in ['Logistic Regression', 'SVM']:
        processed_data = scaler.transform(processed_data)
    
    # Make prediction
    churn_prob = model.predict_proba(processed_data)[0, 1]
    churn_prediction = int(churn_prob >= 0.5)
    
    return {
        'churn_probability': round(churn_prob, 4),
        'churn_prediction': churn_prediction,
        'risk_level': 'High' if churn_prob >= 0.7 else 'Medium' if churn_prob >= 0.4 else 'Low'
    }

# Test the prediction function
print("\nTesting prediction function...")
sample_customer = df.iloc[0:1].copy()  # Take first customer
sample_prediction = predict_churn(sample_customer, best_model, scaler, X.columns.tolist())
print(f"Sample prediction: {sample_prediction}")

print("\nChurn prediction model training completed successfully!")