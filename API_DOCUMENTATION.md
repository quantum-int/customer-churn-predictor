# 🔌 Customer Churn Prediction API Documentation

## Base URL
```
http://localhost:5000
```

## Authentication
Currently no authentication required. In production, implement JWT or API key authentication.

## Endpoints

### 1. Health Check
**GET** `/`

Returns API information and available endpoints.

**Response:**
```json
{
    "message": "Customer Churn Prediction API",
    "version": "1.0",
    "endpoints": [
        "/api/predict",
        "/api/customers", 
        "/api/dashboard"
    ]
}
```

### 2. Single Customer Prediction
**POST** `/api/predict`

Predicts churn probability for a single customer.

**Request Body:**
```json
{
    "customer_id": "CUST_001234",
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
```

**Response:**
```json
{
    "churn_probability": 42.4,
    "churn_prediction": 0,
    "risk_level": "Medium Risk",
    "risk_color": "#ffc107",
    "recommendations": [
        "✅ Customer appears stable"
    ]
}
```

### 3. Get Customers
**GET** `/api/customers?page=1&per_page=20`

Returns paginated list of customers.

**Query Parameters:**
- `page` (optional): Page number (default: 1)
- `per_page` (optional): Items per page (default: 20)

**Response:**
```json
{
    "customers": [
        {
            "customer_id": "CUST_000001",
            "first_name": "John",
            "last_name": "Smith",
            "age": 45,
            "monthly_bill": 85.50,
            "risk_level": "Medium Risk"
        }
    ],
    "total": 2000,
    "page": 1,
    "per_page": 20
}
```

### 4. Get Specific Customer
**GET** `/api/customers/{customer_id}`

Returns detailed information for a specific customer.

**Response:**
```json
{
    "customer_id": "CUST_000001",
    "first_name": "John",
    "last_name": "Smith",
    "age": 45,
    "monthly_bill": 85.50,
    "latest_prediction": {
        "churn_probability": 0.424,
        "risk_level": "Medium Risk",
        "prediction_date": "2025-01-15T10:30:00"
    }
}
```

### 5. Dashboard Statistics
**GET** `/api/dashboard`

Returns key metrics for the dashboard.

**Response:**
```json
{
    "total_customers": 2000,
    "average_churn_risk": 24.3,
    "high_risk_customers": 234,
    "medium_risk_customers": 567,
    "low_risk_customers": 1199,
    "revenue_at_risk": 45670.50
}
```

### 6. High-Risk Customers
**GET** `/api/customers/high-risk`

Returns list of customers with high churn risk.

**Response:**
```json
[
    {
        "customer_id": "CUST_001234",
        "first_name": "John",
        "last_name": "Smith",
        "monthly_bill": 156.90,
        "churn_probability": 0.873,
        "risk_level": "High Risk"
    }
]
```

## Error Responses

All endpoints return errors in the following format:

```json
{
    "error": "Description of the error"
}
```

**Common HTTP Status Codes:**
- `200`: Success
- `400`: Bad Request (invalid input data)
- `404`: Not Found (customer not found)
- `500`: Internal Server Error

## Rate Limiting
Currently no rate limiting implemented. In production, consider implementing rate limiting to prevent abuse.

## Example Usage

### Python
```python
import requests

# Predict churn
response = requests.post('http://localhost:5000/api/predict', json={
    "age": 45,
    "monthly_bill": 85.50,
    # ... other fields
})
print(response.json())
```

### JavaScript
```javascript
// Predict churn
fetch('http://localhost:5000/api/predict', {
    method: 'POST',
    headers: {
        'Content-Type': 'application/json'
    },
    body: JSON.stringify({
        age: 45,
        monthly_bill: 85.50,
        // ... other fields
    })
})
.then(response => response.json())
.then(data => console.log(data));
```

### cURL
```bash
curl -X POST http://localhost:5000/api/predict \
     -H "Content-Type: application/json" \
     -d '{"age": 45, "monthly_bill": 85.50}'
```
