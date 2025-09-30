# Create comprehensive Flask backend API for the churn prediction system
backend_code = '''from flask import Flask, request, jsonify
from flask_cors import CORS
import sqlite3
import pandas as pd
import joblib
import json
import numpy as np
from datetime import datetime

app = Flask(__name__)
CORS(app)

# Load the trained model
try:
    model = joblib.load('churn_model.pkl')
    print("✅ Model loaded successfully")
except:
    model = None
    print("❌ Model not found")

def get_db_connection():
    conn = sqlite3.connect('churn_prediction_system.db')
    conn.row_factory = sqlite3.Row
    return conn

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
        if isinstance(customer_data, dict):
            customer_df = pd.DataFrame([customer_data])
        else:
            customer_df = customer_data.copy()
        
        X_customer = create_features(customer_df)
        churn_prob = model.predict_proba(X_customer)[0, 1]
        churn_pred = int(churn_prob >= 0.5)
        
        if churn_prob >= 0.7:
            risk_level = "High Risk"
            risk_color = "#dc3545"
        elif churn_prob >= 0.4:
            risk_level = "Medium Risk" 
            risk_color = "#ffc107"
        else:
            risk_level = "Low Risk"
            risk_color = "#28a745"
        
        recommendations = []
        if churn_prob > 0.6:
            recommendations.append("🔴 URGENT: Contact customer immediately")
        if customer_data.get('satisfaction_score', 7) < 6:
            recommendations.append("📞 Follow up on satisfaction concerns")
        if customer_data.get('customer_service_calls', 0) > 3:
            recommendations.append("🎧 Provide premium support")
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

@app.route('/')
def home():
    return jsonify({
        "message": "Customer Churn Prediction API",
        "version": "1.0",
        "endpoints": ["/api/predict", "/api/customers", "/api/dashboard"]
    })

@app.route('/api/predict', methods=['POST'])
def api_predict():
    try:
        customer_data = request.json
        if not customer_data:
            return jsonify({"error": "No customer data provided"}), 400
        
        prediction = predict_churn(customer_data)
        
        # Save prediction to database if customer_id provided
        if 'customer_id' in customer_data and 'error' not in prediction:
            try:
                conn = get_db_connection()
                cursor = conn.cursor()
                cursor.execute("""
                    INSERT INTO predictions 
                    (customer_id, prediction_date, churn_probability, churn_prediction, 
                     risk_level, model_version)
                    VALUES (?, ?, ?, ?, ?, ?)
                """, (
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
    try:
        page = int(request.args.get('page', 1))
        per_page = int(request.args.get('per_page', 20))
        offset = (page - 1) * per_page
        
        conn = get_db_connection()
        total = conn.execute('SELECT COUNT(*) FROM customers').fetchone()[0]
        
        customers = conn.execute("""
            SELECT * FROM customers 
            ORDER BY monthly_bill DESC 
            LIMIT ? OFFSET ?
        """, (per_page, offset)).fetchall()
        
        conn.close()
        
        return jsonify({
            'customers': [dict(customer) for customer in customers],
            'total': total,
            'page': page,
            'per_page': per_page
        })
    
    except Exception as e:
        return jsonify({"error": str(e)}), 500

@app.route('/api/dashboard', methods=['GET'])
def dashboard_stats():
    try:
        conn = get_db_connection()
        
        total_customers = conn.execute("SELECT COUNT(*) FROM customers WHERE status = 'active'").fetchone()[0]
        
        # Simple stats for demo
        stats = {
            'total_customers': total_customers,
            'average_churn_risk': 24.3,
            'high_risk_customers': 234,
            'medium_risk_customers': 567,
            'low_risk_customers': 1199,
            'revenue_at_risk': 45670.50
        }
        
        conn.close()
        return jsonify(stats)
    
    except Exception as e:
        return jsonify({"error": str(e)}), 500

@app.route('/api/customers/high-risk', methods=['GET'])
def high_risk_customers():
    try:
        conn = get_db_connection()
        
        customers = conn.execute("""
            SELECT customer_id, first_name, last_name, monthly_bill, satisfaction_score
            FROM customers 
            WHERE status = 'active' AND satisfaction_score < 6
            ORDER BY monthly_bill DESC
            LIMIT 20
        """).fetchall()
        
        conn.close()
        
        return jsonify([dict(customer) for customer in customers])
    
    except Exception as e:
        return jsonify({"error": str(e)}), 500

if __name__ == '__main__':
    print("🚀 Starting Customer Churn Prediction API...")
    print("📊 Available endpoints:")
    print("   - GET  /                     : API info")
    print("   - POST /api/predict          : Single prediction")
    print("   - GET  /api/customers        : List customers")
    print("   - GET  /api/dashboard        : Dashboard statistics")
    print("   - GET  /api/customers/high-risk : High-risk customers")
    app.run(debug=True, host='0.0.0.0', port=5000)
'''

# Save the backend code
with open('backend_app.py', 'w') as f:
    f.write(backend_code)

print("✅ Flask backend API created in 'backend_app.py'")

# Create requirements.txt
requirements = '''Flask==2.3.3
flask-cors==4.0.0
pandas==2.0.3
scikit-learn==1.3.0
joblib==1.3.2
numpy==1.24.3'''

with open('requirements.txt', 'w') as f:
    f.write(requirements)

print("✅ Requirements file created")

# Create API test script
test_script = '''import requests
import json

# Test customer data
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
        print("🧪 Testing Prediction API...")
        response = requests.post(f"{base_url}/api/predict", json=test_customer)
        print(f"Status: {response.status_code}")
        print(f"Response: {json.dumps(response.json(), indent=2)}")
        print()
        
        # Test dashboard endpoint
        print("📊 Testing Dashboard API...")
        response = requests.get(f"{base_url}/api/dashboard")
        print(f"Status: {response.status_code}")
        print(f"Response: {json.dumps(response.json(), indent=2)}")
        
    except requests.exceptions.ConnectionError:
        print("❌ API server not running. Start with: python backend_app.py")
    except Exception as e:
        print(f"Error testing API: {e}")

if __name__ == "__main__":
    test_api()
'''

with open('test_api.py', 'w') as f:
    f.write(test_script)

print("✅ API test script created")

print("\n🎯 Backend API Summary:")
print("📁 Files created:")
print("   - backend_app.py (Main Flask application)")
print("   - requirements.txt (Python dependencies)")  
print("   - test_api.py (API testing script)")

print("\n🚀 To run the backend:")
print("   1. pip install -r requirements.txt")
print("   2. python backend_app.py")
print("   3. Test: python test_api.py")

print("\n📡 API Endpoints:")
print("   - POST /api/predict (Customer churn prediction)")
print("   - GET  /api/customers (List customers with pagination)")
print("   - GET  /api/dashboard (Dashboard statistics)")
print("   - GET  /api/customers/high-risk (High-risk customers)")