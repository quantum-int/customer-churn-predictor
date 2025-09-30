# Fix the probability issue and create comprehensive synthetic data
import pandas as pd
import numpy as np
from datetime import datetime, timedelta
import random
import json

# Set random seed for reproducibility
np.random.seed(42)
random.seed(42)

# Create comprehensive customer data with realistic patterns
def generate_customer_data(n_customers=5000):
    """Generate comprehensive synthetic customer data for churn prediction"""
    
    # Customer demographics
    customer_ids = [f"CUST_{str(i).zfill(6)}" for i in range(1, n_customers + 1)]
    
    # Realistic name generation
    first_names = ['James', 'Mary', 'Robert', 'Patricia', 'John', 'Jennifer', 'Michael', 'Linda', 
                   'David', 'Elizabeth', 'William', 'Barbara', 'Richard', 'Susan', 'Joseph', 'Jessica',
                   'Thomas', 'Sarah', 'Christopher', 'Karen', 'Charles', 'Nancy', 'Daniel', 'Lisa',
                   'Matthew', 'Betty', 'Anthony', 'Dorothy', 'Mark', 'Sandra', 'Donald', 'Donna']
    
    last_names = ['Smith', 'Johnson', 'Williams', 'Brown', 'Jones', 'Garcia', 'Miller', 'Davis',
                  'Rodriguez', 'Martinez', 'Hernandez', 'Lopez', 'Gonzalez', 'Wilson', 'Anderson',
                  'Thomas', 'Taylor', 'Moore', 'Jackson', 'Martin', 'Lee', 'Perez', 'Thompson',
                  'White', 'Harris', 'Sanchez', 'Clark', 'Ramirez', 'Lewis', 'Robinson']
    
    # Generate customer demographics
    ages = np.random.normal(45, 15, n_customers).astype(int)
    ages = np.clip(ages, 18, 80)  # Clip to reasonable age range
    
    genders = np.random.choice(['Male', 'Female'], n_customers, p=[0.52, 0.48])
    
    # Fix location probabilities to sum to 1.0
    location_probs = [0.15, 0.12, 0.08, 0.07, 0.06, 0.05, 0.05, 0.05, 0.05, 0.05,
                      0.04, 0.04, 0.04, 0.04, 0.21]  # Adjusted last value to make sum = 1.0
    
    locations = np.random.choice(['New York', 'Los Angeles', 'Chicago', 'Houston', 'Phoenix', 
                                 'Philadelphia', 'San Antonio', 'San Diego', 'Dallas', 'San Jose',
                                 'Austin', 'Jacksonville', 'Fort Worth', 'Columbus', 'Charlotte'],
                               n_customers, p=location_probs)
    
    # Generate subscription and usage patterns
    subscription_lengths = np.random.exponential(scale=18, size=n_customers).astype(int)
    subscription_lengths = np.clip(subscription_lengths, 1, 72)  # 1-72 months
    
    # Monthly bills with some correlation to usage
    base_bills = np.random.normal(75, 25, n_customers)
    monthly_bills = np.clip(base_bills, 20, 200)
    
    # Total usage with some correlation to bill amount
    usage_multiplier = monthly_bills / 75  # Normalize around base
    total_usage_gb = np.random.normal(50, 20, n_customers) * usage_multiplier
    total_usage_gb = np.clip(total_usage_gb, 5, 500)
    
    # Service features
    phone_service = np.random.choice([0, 1], n_customers, p=[0.1, 0.9])
    multiple_lines = np.random.choice([0, 1], n_customers, p=[0.6, 0.4])
    
    internet_service_types = ['DSL', 'Fiber optic', 'No']
    internet_service = np.random.choice(internet_service_types, n_customers, p=[0.4, 0.5, 0.1])
    
    online_security = np.random.choice([0, 1], n_customers, p=[0.5, 0.5])
    online_backup = np.random.choice([0, 1], n_customers, p=[0.6, 0.4])
    device_protection = np.random.choice([0, 1], n_customers, p=[0.6, 0.4])
    tech_support = np.random.choice([0, 1], n_customers, p=[0.7, 0.3])
    
    streaming_tv = np.random.choice([0, 1], n_customers, p=[0.6, 0.4])
    streaming_movies = np.random.choice([0, 1], n_customers, p=[0.6, 0.4])
    
    # Contract and payment features
    contract_types = ['Month-to-month', 'One year', 'Two year']
    contracts = np.random.choice(contract_types, n_customers, p=[0.5, 0.3, 0.2])
    
    paperless_billing = np.random.choice([0, 1], n_customers, p=[0.4, 0.6])
    
    payment_methods = ['Electronic check', 'Mailed check', 'Bank transfer (automatic)', 'Credit card (automatic)']
    payment_method = np.random.choice(payment_methods, n_customers, p=[0.35, 0.2, 0.2, 0.25])
    
    # Customer satisfaction and engagement metrics
    customer_service_calls = np.random.poisson(2, n_customers)
    satisfaction_score = np.random.normal(7.5, 1.5, n_customers)
    satisfaction_score = np.clip(satisfaction_score, 1, 10)
    
    # Recent activity indicators
    last_payment_days = np.random.exponential(15, n_customers).astype(int)
    last_login_days = np.random.exponential(7, n_customers).astype(int)
    
    # Calculate credit scores (correlated with payment behavior)
    base_credit_scores = np.random.normal(700, 80, n_customers)
    # Adjust based on payment method and history
    credit_score_adj = np.where(payment_method == 'Electronic check', -20, 
                               np.where(payment_method == 'Credit card (automatic)', 30, 0))
    credit_scores = np.clip(base_credit_scores + credit_score_adj, 300, 850).astype(int)
    
    # Churn calculation with realistic patterns
    churn_probability = np.zeros(n_customers)
    
    # Age factor (younger and older customers more likely to churn)
    age_factor = np.where((ages < 25) | (ages > 65), 0.1, 0)
    
    # Subscription length factor (newer customers more likely to churn)
    length_factor = np.where(subscription_lengths < 6, 0.15, 
                           np.where(subscription_lengths < 12, 0.1, 0))
    
    # Bill amount factor (very high or very low bills increase churn)
    bill_factor = np.where((monthly_bills > 150) | (monthly_bills < 30), 0.1, 0)
    
    # Contract factor (month-to-month more likely to churn)
    contract_factor = np.where(contracts == 'Month-to-month', 0.15, 0)
    
    # Service calls factor (more calls = higher churn probability)
    service_factor = np.where(customer_service_calls > 3, 0.1, 0)
    
    # Satisfaction factor (lower satisfaction = higher churn)
    satisfaction_factor = np.where(satisfaction_score < 6, 0.2, 0)
    
    # Recent activity factor (less recent activity = higher churn)
    activity_factor = np.where((last_payment_days > 30) | (last_login_days > 14), 0.1, 0)
    
    # Credit score factor (lower credit scores increase churn probability)
    credit_factor = np.where(credit_scores < 600, 0.1, 0)
    
    # Combine all factors
    churn_probability = (0.05 +  # Base churn rate
                        age_factor + 
                        length_factor + 
                        bill_factor + 
                        contract_factor + 
                        service_factor + 
                        satisfaction_factor +
                        activity_factor +
                        credit_factor)
    
    # Generate actual churn based on probability
    churn = np.random.binomial(1, churn_probability)
    
    # Create DataFrame
    df = pd.DataFrame({
        'customer_id': customer_ids,
        'first_name': [random.choice(first_names) for _ in range(n_customers)],
        'last_name': [random.choice(last_names) for _ in range(n_customers)],
        'age': ages,
        'gender': genders,
        'location': locations,
        'subscription_length_months': subscription_lengths,
        'monthly_bill': np.round(monthly_bills, 2),
        'total_usage_gb': np.round(total_usage_gb, 2),
        'phone_service': phone_service,
        'multiple_lines': multiple_lines,
        'internet_service': internet_service,
        'online_security': online_security,
        'online_backup': online_backup,
        'device_protection': device_protection,
        'tech_support': tech_support,
        'streaming_tv': streaming_tv,
        'streaming_movies': streaming_movies,
        'contract_type': contracts,
        'paperless_billing': paperless_billing,
        'payment_method': payment_method,
        'customer_service_calls': customer_service_calls,
        'satisfaction_score': np.round(satisfaction_score, 1),
        'last_payment_days_ago': last_payment_days,
        'last_login_days_ago': last_login_days,
        'credit_score': credit_scores,
        'churn_probability': np.round(churn_probability, 3),
        'churn': churn
    })
    
    return df

# Generate the data
print("Generating comprehensive customer churn dataset...")
customer_data = generate_customer_data(5000)

# Display basic statistics
print(f"\nDataset shape: {customer_data.shape}")
print(f"Churn rate: {customer_data['churn'].mean():.2%}")
print("\nChurn distribution:")
print(customer_data['churn'].value_counts())

# Show first few rows
print("\nFirst 5 rows of the dataset:")
print(customer_data.head())

# Save the dataset
customer_data.to_csv('customer_churn_dataset.csv', index=False)
print(f"\nDataset saved as 'customer_churn_dataset.csv'")
print(f"File size: {len(customer_data)} rows × {len(customer_data.columns)} columns")