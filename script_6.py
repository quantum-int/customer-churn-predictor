# Create comprehensive database schema for the churn prediction system
import sqlite3
import pandas as pd
import json
from datetime import datetime, timedelta
import random

# Create SQLite database with comprehensive schema
def create_database_schema():
    """Create comprehensive database schema for churn prediction system"""
    
    conn = sqlite3.connect('churn_prediction_system.db')
    cursor = conn.cursor()
    
    # Drop existing tables if they exist
    cursor.execute('DROP TABLE IF EXISTS predictions')
    cursor.execute('DROP TABLE IF EXISTS customers')
    cursor.execute('DROP TABLE IF EXISTS customer_interactions')
    cursor.execute('DROP TABLE IF EXISTS model_performance')
    
    # Customers table - main customer information
    cursor.execute('''
        CREATE TABLE customers (
            customer_id TEXT PRIMARY KEY,
            first_name TEXT NOT NULL,
            last_name TEXT NOT NULL,
            email TEXT UNIQUE,
            phone TEXT,
            age INTEGER,
            gender TEXT,
            location TEXT,
            subscription_length_months INTEGER,
            monthly_bill REAL,
            total_usage_gb REAL,
            phone_service INTEGER,
            multiple_lines INTEGER,
            internet_service TEXT,
            online_security INTEGER,
            online_backup INTEGER,
            device_protection INTEGER,
            tech_support INTEGER,
            streaming_tv INTEGER,
            streaming_movies INTEGER,
            contract_type TEXT,
            paperless_billing INTEGER,
            payment_method TEXT,
            customer_service_calls INTEGER,
            satisfaction_score REAL,
            last_payment_days_ago INTEGER,
            last_login_days_ago INTEGER,
            credit_score INTEGER,
            support_tickets INTEGER,
            avg_monthly_usage_growth REAL,
            status TEXT DEFAULT 'active',
            created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
        )
    ''')
    
    # Customer interactions table
    cursor.execute('''
        CREATE TABLE customer_interactions (
            interaction_id INTEGER PRIMARY KEY AUTOINCREMENT,
            customer_id TEXT,
            interaction_type TEXT,
            interaction_date TIMESTAMP,
            details TEXT,
            outcome TEXT,
            FOREIGN KEY (customer_id) REFERENCES customers (customer_id)
        )
    ''')
    
    # Predictions table
    cursor.execute('''
        CREATE TABLE predictions (
            prediction_id INTEGER PRIMARY KEY AUTOINCREMENT,
            customer_id TEXT,
            prediction_date TIMESTAMP,
            churn_probability REAL,
            churn_prediction INTEGER,
            risk_level TEXT,
            model_version TEXT,
            FOREIGN KEY (customer_id) REFERENCES customers (customer_id)
        )
    ''')
    
    # Model performance table
    cursor.execute('''
        CREATE TABLE model_performance (
            performance_id INTEGER PRIMARY KEY AUTOINCREMENT,
            model_version TEXT,
            evaluation_date DATE,
            auc_score REAL,
            accuracy REAL,
            total_predictions INTEGER
        )
    ''')
    
    # Create indexes
    cursor.execute('CREATE INDEX idx_customer_status ON customers(status)')
    cursor.execute('CREATE INDEX idx_predictions_date ON predictions(prediction_date)')
    cursor.execute('CREATE INDEX idx_predictions_risk ON predictions(risk_level)')
    
    conn.commit()
    conn.close()
    print("✅ Database schema created successfully!")

# Execute database setup
print("🗄️ Setting up database system...")
create_database_schema()

# Populate with sample data
print("📊 Populating database with customer data...")

conn = sqlite3.connect('churn_prediction_system.db')
cursor = conn.cursor()

# Load our synthetic dataset
df = pd.read_csv('customer_churn_dataset.csv')

# Add email addresses to customers
domains = ['gmail.com', 'yahoo.com', 'hotmail.com', 'outlook.com']

print("Inserting customers...")
for idx, row in df.head(1000).iterrows():  # Use first 1000 for faster processing
    email = f"{row['first_name'].lower()}.{row['last_name'].lower()}{idx}@{random.choice(domains)}"
    phone = f"+1-{random.randint(100,999)}-{random.randint(100,999)}-{random.randint(1000,9999)}"
    
    cursor.execute('''
        INSERT OR REPLACE INTO customers (
            customer_id, first_name, last_name, email, phone, age, gender, location,
            subscription_length_months, monthly_bill, total_usage_gb,
            phone_service, multiple_lines, internet_service, online_security, online_backup,
            device_protection, tech_support, streaming_tv, streaming_movies, contract_type,
            paperless_billing, payment_method, customer_service_calls, satisfaction_score,
            last_payment_days_ago, last_login_days_ago, credit_score, support_tickets,
            avg_monthly_usage_growth, status
        ) VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?)
    ''', (
        row['customer_id'], row['first_name'], row['last_name'], email, phone,
        int(row['age']), row['gender'], row['location'],
        int(row['subscription_length_months']), float(row['monthly_bill']), float(row['total_usage_gb']),
        int(row['phone_service']), int(row['multiple_lines']), row['internet_service'],
        int(row['online_security']), int(row['online_backup']), int(row['device_protection']),
        int(row['tech_support']), int(row['streaming_tv']), int(row['streaming_movies']),
        row['contract_type'], int(row['paperless_billing']), row['payment_method'],
        int(row['customer_service_calls']), float(row['satisfaction_score']),
        int(row['last_payment_days_ago']), int(row['last_login_days_ago']), int(row['credit_score']),
        int(row['support_tickets']), float(row['avg_monthly_usage_growth']),
        'churned' if row['churn'] == 1 else 'active'
    ))

conn.commit()

# Add model performance record
cursor.execute('''
    INSERT INTO model_performance 
    (model_version, evaluation_date, auc_score, accuracy, total_predictions)
    VALUES (?, ?, ?, ?, ?)
''', ('v1.0', datetime.now().date(), 0.618, 0.59, 1000))

conn.commit()
conn.close()

# Test the database
print("🧪 Testing database...")
conn = sqlite3.connect('churn_prediction_system.db')

customers_count = pd.read_sql_query("SELECT COUNT(*) as count FROM customers", conn).iloc[0]['count']
print(f"Total customers in database: {customers_count}")

# Sample query
sample_customers = pd.read_sql_query("""
    SELECT customer_id, first_name, last_name, monthly_bill, satisfaction_score, status
    FROM customers 
    LIMIT 5
""", conn)

print("\nSample customers:")
print(sample_customers)

conn.close()

print("\n✅ Database setup completed successfully!")
print("📁 Created: churn_prediction_system.db")