# Create comprehensive Flask backend API for the churn prediction system
backend_code = '''
from flask import Flask, request, jsonify, render_template
from flask_cors import CORS
import sqlite3
import pandas as pd
import joblib
import json
import numpy as np
from datetime import datetime, timedelta
import os

app = Flask(__name__)
CORS(app)

# Load the trained model
try:
    model = joblib.load('churn_model.pkl')
    print("✅ Model loaded successfully")
except:
    model = None
    print("❌ Model not found")

# Database connection function
def get_db_connection():
    conn = sqlite3.connect('churn_prediction_system.db')
    conn.row_factory = sqlite3.Row
    return conn

# Feature engineering function (same as training)
def create_features(data):
    """Create engineered features for churn prediction"""
    
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

def predict_churn(customer_data):
    """Predict churn for a customer"""
    if model is None:
        return {"error": "Model not loaded"}
    
    try:
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
            risk_color = "#dc3545"
        elif churn_prob >= 0.4:
            risk_level = "Medium Risk" 
            risk_color = "#ffc107"
        else:
            risk_level = "Low Risk"
            risk_color = "#28a745"
        
        # Generate recommendations
        recommendations = []
        if churn_prob > 0.6:
            recommendations.append("🔴 URGENT: Contact customer immediately")
        if customer_data.get('satisfaction_score', 7) < 6:
            recommendations.append("📞 Follow up on satisfaction concerns")
        if customer_data.get('customer_service_calls', 0) > 3:
            recommendations.append("🎧 Provide premium support")
        if customer_data.get('contract_type') == 'Month-to-month':
            recommendations.append("📋 Offer long-term contract incentive")
        if customer_data.get('monthly_bill', 50) > 100:
            recommendations.append("💰 Consider loyalty discount")
        if not recommendations:
            recommendations.append("✅ Customer appears stable")
        
        return {
            'churn_probability': round(churn_prob * 100, 1),
            'churn_prediction': churn_pred,
            'risk_level': risk_level,
            'risk_color': risk_color,
            'recommendations': recommendations
        }
    
    except Exception as e:
        return {"error": str(e)}

# API Routes

@app.route('/')
def home():
    return jsonify({
        "message": "Customer Churn Prediction API",
        "version": "1.0",
        "endpoints": [
            "/api/predict",
            "/api/customers",
            "/api/dashboard",
            "/api/customers/high-risk"
        ]
    })

@app.route('/api/predict', methods=['POST'])
def api_predict():
    """Predict churn for a single customer"""
    try:
        customer_data = request.json
        
        if not customer_data:
            return jsonify({"error": "No customer data provided"}), 400
        
        prediction = predict_churn(customer_data)
        
        # Save prediction to database if customer_id provided
        if 'customer_id' in customer_data and 'error' not in prediction:
            try:
                conn = get_db_connection()
                conn.execute('''
                    INSERT INTO predictions 
                    (customer_id, prediction_date, churn_probability, churn_prediction, 
                     risk_level, model_version)
                    VALUES (?, ?, ?, ?, ?, ?)
                ''', (
                    customer_data['customer_id'],
                    datetime.now(),
                    prediction['churn_probability'] / 100,
                    prediction['churn_prediction'],
                    prediction['risk_level'],
                    'v1.0'
                ))
                conn.commit()
                conn.close()
            except Exception as e:
                print(f"Error saving prediction: {e}")
        
        return jsonify(prediction)
    
    except Exception as e:
        return jsonify({"error": str(e)}), 500

@app.route('/api/customers', methods=['GET'])
def get_customers():
    """Get all customers with pagination"""
    try:
        page = int(request.args.get('page', 1))
        per_page = int(request.args.get('per_page', 20))
        offset = (page - 1) * per_page
        
        conn = get_db_connection()
        
        # Get total count
        total = conn.execute('SELECT COUNT(*) FROM customers').fetchone()[0]
        
        # Get customers
        customers = conn.execute('''
            SELECT * FROM customers 
            ORDER BY monthly_bill DESC 
            LIMIT ? OFFSET ?
        ''', (per_page, offset)).fetchall()
        
        conn.close()
        
        return jsonify({
            'customers': [dict(customer) for customer in customers],
            'total': total,
            'page': page,
            'per_page': per_page,
            'pages': (total + per_page - 1) // per_page
        })
    
    except Exception as e:
        return jsonify({"error": str(e)}), 500

@app.route('/api/customers/<customer_id>', methods=['GET'])
def get_customer(customer_id):
    """Get specific customer details"""
    try:
        conn = get_db_connection()
        
        customer = conn.execute('''
            SELECT * FROM customers WHERE customer_id = ?
        ''', (customer_id,)).fetchone()
        
        if not customer:
            return jsonify({"error": "Customer not found"}), 404
        
        # Get latest prediction
        prediction = conn.execute('''
            SELECT * FROM predictions 
            WHERE customer_id = ? 
            ORDER BY prediction_date DESC 
            LIMIT 1
        ''', (customer_id,)).fetchone()
        
        conn.close()
        
        result = dict(customer)
        if prediction:
            result['latest_prediction'] = dict(prediction)
        
        return jsonify(result)
    
    except Exception as e:
        return jsonify({"error": str(e)}), 500

@app.route('/api/dashboard', methods=['GET'])
def dashboard_stats():
    """Get dashboard statistics"""
    try:
        conn = get_db_connection()
        
        # Total customers
        total_customers = conn.execute('''
            SELECT COUNT(*) FROM customers WHERE status = 'active'
        ''').fetchone()[0]
        
        # Get latest predictions stats
        prediction_stats = conn.execute('''
            SELECT 
                AVG(churn_probability) as avg_churn_prob,
                COUNT(*) as total_predictions,
                SUM(CASE WHEN risk_level = 'High Risk' THEN 1 ELSE 0 END) as high_risk_count,
                SUM(CASE WHEN risk_level = 'Medium Risk' THEN 1 ELSE 0 END) as medium_risk_count,
                SUM(CASE WHEN risk_level = 'Low Risk' THEN 1 ELSE 0 END) as low_risk_count
            FROM (
                SELECT DISTINCT customer_id, 
                       FIRST_VALUE(churn_probability) OVER (PARTITION BY customer_id ORDER BY prediction_date DESC) as churn_probability,
                       FIRST_VALUE(risk_level) OVER (PARTITION BY customer_id ORDER BY prediction_date DESC) as risk_level
                FROM predictions
            ) latest_predictions
        ''').fetchone()
        
        # Revenue at risk
        revenue_at_risk = conn.execute('''
            SELECT SUM(c.monthly_bill) as total_revenue
            FROM customers c
            JOIN (
                SELECT customer_id, 
                       FIRST_VALUE(risk_level) OVER (PARTITION BY customer_id ORDER BY prediction_date DESC) as risk_level
                FROM predictions
            ) p ON c.customer_id = p.customer_id
            WHERE p.risk_level = 'High Risk' AND c.status = 'active'
        ''').fetchone()
        
        # Churn trends (last 30 days)
        trends = conn.execute('''
            SELECT 
                DATE(prediction_date) as date,
                AVG(churn_probability) as avg_churn_prob,
                COUNT(*) as predictions_count
            FROM predictions
            WHERE prediction_date >= date('now', '-30 days')
            GROUP BY DATE(prediction_date)
            ORDER BY date
        ''').fetchall()
        
        conn.close()
        
        return jsonify({
            'total_customers': total_customers,
            'average_churn_risk': round((prediction_stats[0] or 0) * 100, 1),
            'high_risk_customers': prediction_stats[2] or 0,
            'medium_risk_customers': prediction_stats[3] or 0,
            'low_risk_customers': prediction_stats[4] or 0,
            'revenue_at_risk': round(revenue_at_risk[0] or 0, 2),
            'trends': [{'date': row[0], 'avg_churn_prob': round((row[1] or 0) * 100, 1), 'count': row[2]} for row in trends]
        })
    
    except Exception as e:
        return jsonify({"error": str(e)}), 500

@app.route('/api/customers/high-risk', methods=['GET'])
def high_risk_customers():
    """Get high-risk customers"""
    try:
        conn = get_db_connection()
        
        customers = conn.execute('''
            SELECT c.*, p.churn_probability, p.risk_level, p.prediction_date
            FROM customers c
            JOIN (
                SELECT customer_id, churn_probability, risk_level, prediction_date,
                       ROW_NUMBER() OVER (PARTITION BY customer_id ORDER BY prediction_date DESC) as rn
                FROM predictions
            ) p ON c.customer_id = p.customer_id
            WHERE p.rn = 1 AND p.risk_level = 'High Risk' AND c.status = 'active'
            ORDER BY p.churn_probability DESC
            LIMIT 50
        ''').fetchall()
        
        conn.close()
        
        return jsonify([dict(customer) for customer in customers])
    
    except Exception as e:
        return jsonify({"error": str(e)}), 500

@app.route('/api/batch-predict', methods=['POST'])
def batch_predict():
    """Predict churn for multiple customers"""
    try:
        customers_data = request.json
        
        if not customers_data or not isinstance(customers_data, list):
            return jsonify({"error": "Expected list of customer data"}), 400
        
        predictions = []
        for customer_data in customers_data:
            prediction = predict_churn(customer_data)
            prediction['customer_id'] = customer_data.get('customer_id', 'unknown')
            predictions.append(prediction)
        
        return jsonify({
            'predictions': predictions,
            'total_processed': len(predictions)
        })
    
    except Exception as e:
        return jsonify({"error": str(e)}), 500

if __name__ == '__main__':
    print("🚀 Starting Customer Churn Prediction API...")
    print("📊 Available endpoints:")
    print("   - GET  /                     : API info")
    print("   - POST /api/predict          : Single prediction")
    print("   - POST /api/batch-predict    : Batch predictions") 
    print("   - GET  /api/customers        : List customers")
    print("   - GET  /api/customers/<id>   : Get customer details")
    print("   - GET  /api/dashboard        : Dashboard statistics")
    print("   - GET  /api/customers/high-risk : High-risk customers")
    print()
    app.run(debug=True, host='0.0.0.0', port=5000)
'''

# Save the backend code
with open('backend_app.py', 'w') as f:
    f.write(backend_code)

print("✅ Flask backend API created in 'backend_app.py'")

# Create requirements.txt for the backend
requirements = '''
Flask==2.3.3
flask-cors==4.0.0
pandas==2.0.3
scikit-learn==1.3.0
joblib==1.3.2
numpy==1.24.3
'''

with open('requirements.txt', 'w') as f:
    f.write(requirements)

print("✅ Requirements file created: 'requirements.txt'")

# Create a simple test script to verify the API
test_script = '''
import requests
import json

# Test data
test_customer = {
    "customer_id": "TEST_001",
    "age": 45,
    "subscription_length_months": 12,
    "monthly_bill": 85.50,
    "total_usage_gb": 45.2,
    "customer_service_calls": 2,
    "satisfaction_score": 7.5,
    "last_payment_days_ago": 5,
    "last_login_days_ago": 2,
    "credit_score": 720,
    "support_tickets": 1,
    "avg_monthly_usage_growth": 0.05,
    "phone_service": 1,
    "multiple_lines": 0,
    "online_security": 1,
    "online_backup": 1,
    "device_protection": 1,
    "tech_support": 0,
    "streaming_tv": 0,
    "streaming_movies": 1,
    "paperless_billing": 1,
    "contract_type": "One year",
    "payment_method": "Credit card",
    "internet_service": "Fiber optic"
}

def test_api():
    base_url = "http://localhost:5000"
    
    try:
        # Test prediction endpoint
        response = requests.post(f"{base_url}/api/predict", json=test_customer)
        print("Prediction API Test:")
        print(f"Status: {response.status_code}")
        print(f"Response: {response.json()}")
        print()
        
        # Test dashboard endpoint
        response = requests.get(f"{base_url}/api/dashboard")
        print("Dashboard API Test:")
        print(f"Status: {response.status_code}")
        print(f"Response: {response.json()}")
        
    except requests.exceptions.ConnectionError:
        print("❌ API server not running. Start with: python backend_app.py")
    except Exception as e:
        print(f"Error testing API: {e}")

if __name__ == "__main__":
    test_api()
'''

with open('test_api.py', 'w') as f:
    f.write(test_script)

print("✅ API test script created: 'test_api.py'")

# Create Docker configuration
dockerfile = '''
FROM python:3.9-slim

WORKDIR /app

COPY requirements.txt .
RUN pip install --no-cache-dir -r requirements.txt

COPY . .

EXPOSE 5000

CMD ["python", "backend_app.py"]
'''

with open('Dockerfile', 'w') as f:
    f.write(dockerfile)

docker_compose = '''
version: '3.8'

services:
  churn-api:
    build: .
    ports:
      - "5000:5000"
    volumes:
      - .:/app
    environment:
      - FLASK_ENV=development
    restart: unless-stopped

  churn-frontend:
    image: node:16-alpine
    working_dir: /app
    ports:
      - "3000:3000"
    volumes:
      - ./frontend:/app
    command: npm start
    depends_on:
      - churn-api
'''

with open('docker-compose.yml', 'w') as f:
    f.write(docker_compose)

print("✅ Docker configuration created:")
print("   - Dockerfile")
print("   - docker-compose.yml")

print("\n🎯 Backend API Summary:")
print("📁 Files created:")
print("   - backend_app.py (Main Flask application)")
print("   - requirements.txt (Python dependencies)")
print("   - test_api.py (API testing script)")
print("   - Dockerfile (Docker configuration)")
print("   - docker-compose.yml (Multi-container setup)")
print("\n🚀 To run the backend:")
print("   1. pip install -r requirements.txt")
print("   2. python backend_app.py")
print("   3. Test with: python test_api.py")