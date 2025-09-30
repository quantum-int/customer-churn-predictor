import requests
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
