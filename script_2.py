# Check and fix probabilities
import pandas as pd
import numpy as np
from datetime import datetime, timedelta
import random

# Set random seed for reproducibility
np.random.seed(42)
random.seed(42)

# Check probabilities sum
location_probs = [0.15, 0.12, 0.08, 0.07, 0.06, 0.05, 0.05, 0.05, 0.05, 0.05,
                  0.04, 0.04, 0.04, 0.04, 0.21]

print(f"Current probabilities sum: {sum(location_probs)}")
print("Let me normalize them...")

# Normalize probabilities to sum to 1.0
location_probs = np.array(location_probs)
location_probs = location_probs / location_probs.sum()
print(f"Normalized probabilities sum: {location_probs.sum()}")

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
    ages = np.clip(ages, 18, 80)
    
    genders = np.random.choice(['Male', 'Female'], n_customers, p=[0.52, 0.48])
    
    # Use normalized probabilities for locations
    locations = np.random.choice(['New York', 'Los Angeles', 'Chicago', 'Houston', 'Phoenix', 
                                 'Philadelphia', 'San Antonio', 'San Diego', 'Dallas', 'San Jose',
                                 'Austin', 'Jacksonville', 'Fort Worth', 'Columbus', 'Charlotte'],
                               n_customers, p=location_probs)
    
    # Generate subscription and usage patterns
    subscription_lengths = np.random.exponential(scale=18, size=n_customers).astype(int)
    subscription_lengths = np.clip(subscription_lengths, 1, 72)
    
    # Monthly bills with realistic distribution
    monthly_bills = np.random.lognormal(mean=4.2, sigma=0.4, size=n_customers)  # Log-normal for realistic bill distribution
    monthly_bills = np.clip(monthly_bills, 20, 300)
    
    # Total usage correlated with bill amount
    usage_base = np.random.exponential(scale=40, size=n_customers)
    usage_multiplier = (monthly_bills - 20) / 100  # Scale with bill amount
    total_usage_gb = usage_base * (1 + usage_multiplier)
    total_usage_gb = np.clip(total_usage_gb, 1, 1000)
    
    # Service features with realistic correlations
    phone_service = np.random.choice([0, 1], n_customers, p=[0.1, 0.9])
    multiple_lines = np.where(phone_service == 1, 
                             np.random.choice([0, 1], n_customers, p=[0.6, 0.4]),
                             0)
    
    internet_service = np.random.choice(['DSL', 'Fiber optic', 'No'], n_customers, p=[0.4, 0.5, 0.1])
    
    # Additional services correlated with internet service
    has_internet = (internet_service != 'No').astype(int)
    online_security = np.where(has_internet, np.random.choice([0, 1], n_customers, p=[0.5, 0.5]), 0)
    online_backup = np.where(has_internet, np.random.choice([0, 1], n_customers, p=[0.6, 0.4]), 0)
    device_protection = np.where(has_internet, np.random.choice([0, 1], n_customers, p=[0.6, 0.4]), 0)
    tech_support = np.where(has_internet, np.random.choice([0, 1], n_customers, p=[0.7, 0.3]), 0)
    
    streaming_tv = np.where(has_internet, np.random.choice([0, 1], n_customers, p=[0.6, 0.4]), 0)
    streaming_movies = np.where(has_internet, np.random.choice([0, 1], n_customers, p=[0.6, 0.4]), 0)
    
    # Contract and payment features
    contracts = np.random.choice(['Month-to-month', 'One year', 'Two year'], n_customers, p=[0.5, 0.3, 0.2])
    paperless_billing = np.random.choice([0, 1], n_customers, p=[0.4, 0.6])
    payment_method = np.random.choice(['Electronic check', 'Mailed check', 'Bank transfer', 'Credit card'], 
                                    n_customers, p=[0.35, 0.2, 0.2, 0.25])
    
    # Customer behavior and satisfaction metrics
    customer_service_calls = np.random.poisson(2, n_customers)
    satisfaction_score = np.random.beta(7, 3, n_customers) * 10  # Beta distribution skewed toward higher satisfaction
    satisfaction_score = np.round(satisfaction_score, 1)
    
    # Recent activity
    last_payment_days = np.random.exponential(12, n_customers).astype(int)
    last_login_days = np.random.exponential(5, n_customers).astype(int)
    
    # Credit scores
    credit_scores = np.random.normal(680, 100, n_customers)
    credit_scores = np.clip(credit_scores, 300, 850).astype(int)
    
    # Generate additional behavioral features
    support_tickets = np.random.poisson(1.5, n_customers)
    avg_monthly_usage_growth = np.random.normal(0.05, 0.15, n_customers)  # 5% average growth
    
    # Calculate churn with multiple realistic factors
    churn_score = np.zeros(n_customers)
    
    # Age influence (U-shaped: young and old more likely to churn)
    age_normalized = (ages - ages.min()) / (ages.max() - ages.min())
    age_influence = 0.1 * (4 * age_normalized * (1 - age_normalized))  # Inverted parabola
    
    # Tenure influence (exponential decay - newer customers more likely to churn)
    tenure_influence = 0.2 * np.exp(-subscription_lengths / 12)
    
    # Bill amount influence (extreme values increase churn)
    bill_percentiles = np.percentile(monthly_bills, [25, 75])
    bill_influence = np.where((monthly_bills < bill_percentiles[0]) | (monthly_bills > bill_percentiles[1]), 0.15, 0)
    
    # Contract influence
    contract_influence = np.where(contracts == 'Month-to-month', 0.2, 
                                np.where(contracts == 'One year', 0.1, 0))
    
    # Satisfaction influence (exponential relationship)
    satisfaction_influence = 0.25 * np.exp(-(satisfaction_score - 1) / 2)
    
    # Service calls influence
    service_influence = 0.1 * np.tanh(customer_service_calls / 3)
    
    # Recent activity influence
    activity_influence = 0.1 * np.tanh((last_payment_days + last_login_days) / 20)
    
    # Usage growth influence (declining usage increases churn)
    growth_influence = np.where(avg_monthly_usage_growth < -0.1, 0.15, 0)
    
    # Combine all influences
    churn_score = (0.05 +  # Base rate
                  age_influence +
                  tenure_influence +
                  bill_influence +
                  contract_influence +
                  satisfaction_influence +
                  service_influence +
                  activity_influence +
                  growth_influence)
    
    churn_score = np.clip(churn_score, 0, 0.8)  # Cap at 80% probability
    
    # Generate churn based on probability
    churn = np.random.binomial(1, churn_score)
    
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
        'total_usage_gb': np.round(total_usage_gb, 1),
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
        'satisfaction_score': satisfaction_score,
        'last_payment_days_ago': last_payment_days,
        'last_login_days_ago': last_login_days,
        'credit_score': credit_scores,
        'support_tickets': support_tickets,
        'avg_monthly_usage_growth': np.round(avg_monthly_usage_growth, 3),
        'churn_probability': np.round(churn_score, 3),
        'churn': churn
    })
    
    return df

# Generate the comprehensive dataset
print("Generating comprehensive customer churn dataset...")
customer_data = generate_customer_data(5000)

print(f"\nDataset shape: {customer_data.shape}")
print(f"Churn rate: {customer_data['churn'].mean():.2%}")
print("\nChurn distribution:")
print(customer_data['churn'].value_counts())

# Save the dataset
customer_data.to_csv('customer_churn_dataset.csv', index=False)
print(f"\nDataset saved as 'customer_churn_dataset.csv'")

# Display sample data
print("\nSample data:")
print(customer_data.head())

# Show feature statistics
print("\nFeature statistics:")
print(customer_data.describe())