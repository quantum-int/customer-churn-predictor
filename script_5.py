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
    cursor.execute('DROP TABLE IF EXISTS subscription_history')
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
            subscription_start_date DATE,
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
            created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
            updated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
        )
    ''')
    
    # Customer interactions table - track all customer touchpoints
    cursor.execute('''
        CREATE TABLE customer_interactions (
            interaction_id INTEGER PRIMARY KEY AUTOINCREMENT,
            customer_id TEXT,
            interaction_type TEXT, -- email, call, support_ticket, login, payment
            interaction_date TIMESTAMP,
            details TEXT,
            outcome TEXT,
            agent_id TEXT,
            FOREIGN KEY (customer_id) REFERENCES customers (customer_id)
        )
    ''')
    
    # Subscription history table - track plan changes
    cursor.execute('''
        CREATE TABLE subscription_history (
            history_id INTEGER PRIMARY KEY AUTOINCREMENT,
            customer_id TEXT,
            change_date DATE,
            old_plan TEXT,
            new_plan TEXT,
            old_monthly_bill REAL,
            new_monthly_bill REAL,
            reason TEXT,
            FOREIGN KEY (customer_id) REFERENCES customers (customer_id)
        )
    ''')
    
    # Predictions table - store all churn predictions
    cursor.execute('''
        CREATE TABLE predictions (
            prediction_id INTEGER PRIMARY KEY AUTOINCREMENT,
            customer_id TEXT,
            prediction_date TIMESTAMP,
            churn_probability REAL,
            churn_prediction INTEGER,
            risk_level TEXT,
            model_version TEXT,
            features_json TEXT, -- JSON string of features used
            actual_churn INTEGER DEFAULT NULL, -- to be filled later for model evaluation
            FOREIGN KEY (customer_id) REFERENCES customers (customer_id)
        )
    ''')
    
    # Model performance table - track model metrics over time
    cursor.execute('''
        CREATE TABLE model_performance (
            performance_id INTEGER PRIMARY KEY AUTOINCREMENT,
            model_version TEXT,
            evaluation_date DATE,
            auc_score REAL,
            precision_score REAL,
            recall_score REAL,
            f1_score REAL,
            accuracy REAL,
            total_predictions INTEGER,
            notes TEXT
        )
    ''')
    
    # Create indexes for better performance
    cursor.execute('CREATE INDEX idx_customer_status ON customers(status)')
    cursor.execute('CREATE INDEX idx_predictions_date ON predictions(prediction_date)')
    cursor.execute('CREATE INDEX idx_interactions_customer ON customer_interactions(customer_id)')
    cursor.execute('CREATE INDEX idx_interactions_date ON customer_interactions(interaction_date)')
    cursor.execute('CREATE INDEX idx_predictions_risk ON predictions(risk_level)')
    
    conn.commit()
    conn.close()
    print("✅ Database schema created successfully!")

# Populate database with sample data
def populate_database():
    """Populate database with synthetic customer data"""
    
    conn = sqlite3.connect('churn_prediction_system.db')
    cursor = conn.cursor()
    
    # Load our synthetic dataset
    df = pd.read_csv('customer_churn_dataset.csv')
    
    print("Populating customers table...")
    
    # Add email addresses to customers
    domains = ['gmail.com', 'yahoo.com', 'hotmail.com', 'outlook.com', 'company.com']
    
    for _, row in df.iterrows():
        # Generate email
        email = f"{row['first_name'].lower()}.{row['last_name'].lower()}@{random.choice(domains)}"
        
        # Generate phone
        phone = f"+1-{random.randint(100,999)}-{random.randint(100,999)}-{random.randint(1000,9999)}"
        
        # Calculate subscription start date
        start_date = datetime.now() - timedelta(days=row['subscription_length_months'] * 30)
        
        cursor.execute('''
            INSERT INTO customers (
                customer_id, first_name, last_name, email, phone, age, gender, location,
                subscription_start_date, subscription_length_months, monthly_bill, total_usage_gb,
                phone_service, multiple_lines, internet_service, online_security, online_backup,
                device_protection, tech_support, streaming_tv, streaming_movies, contract_type,
                paperless_billing, payment_method, customer_service_calls, satisfaction_score,
                last_payment_days_ago, last_login_days_ago, credit_score, support_tickets,
                avg_monthly_usage_growth, status
            ) VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?)
        ''', (
            row['customer_id'], row['first_name'], row['last_name'], email, phone,
            row['age'], row['gender'], row['location'], start_date.date(),
            row['subscription_length_months'], row['monthly_bill'], row['total_usage_gb'],
            row['phone_service'], row['multiple_lines'], row['internet_service'],
            row['online_security'], row['online_backup'], row['device_protection'],
            row['tech_support'], row['streaming_tv'], row['streaming_movies'],
            row['contract_type'], row['paperless_billing'], row['payment_method'],
            row['customer_service_calls'], row['satisfaction_score'],
            row['last_payment_days_ago'], row['last_login_days_ago'], row['credit_score'],
            row['support_tickets'], row['avg_monthly_usage_growth'],
            'churned' if row['churn'] == 1 else 'active'
        ))
    
    print("Populating customer interactions...")
    
    # Generate sample customer interactions
    interaction_types = ['email', 'call', 'support_ticket', 'login', 'payment', 'chat']
    outcomes = ['resolved', 'escalated', 'pending', 'successful', 'failed']
    
    for customer_id in df['customer_id'].sample(1000):  # Sample interactions for 1000 customers
        # Generate 1-5 interactions per selected customer
        num_interactions = random.randint(1, 5)
        
        for _ in range(num_interactions):
            interaction_date = datetime.now() - timedelta(days=random.randint(0, 180))
            interaction_type = random.choice(interaction_types)
            outcome = random.choice(outcomes)
            details = f"{interaction_type.title()} interaction with customer"
            agent_id = f"AGENT_{random.randint(1000, 9999)}"
            
            cursor.execute('''
                INSERT INTO customer_interactions 
                (customer_id, interaction_type, interaction_date, details, outcome, agent_id)
                VALUES (?, ?, ?, ?, ?, ?)
            ''', (customer_id, interaction_type, interaction_date, details, outcome, agent_id))
    
    print("Populating model performance...")
    
    # Add model performance record
    cursor.execute('''
        INSERT INTO model_performance 
        (model_version, evaluation_date, auc_score, precision_score, recall_score, f1_score, accuracy, total_predictions, notes)
        VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?)
    ''', ('v1.0', datetime.now().date(), 0.618, 0.60, 0.76, 0.67, 0.59, 1000, 'Initial Random Forest model'))
    
    conn.commit()
    conn.close()
    print("✅ Database populated with sample data!")

# Create database access functions
def create_database_functions():
    """Create utility functions for database operations"""
    
    database_functions = '''
import sqlite3
import pandas as pd
import json
from datetime import datetime

class ChurnDatabase:
    def __init__(self, db_path='churn_prediction_system.db'):
        self.db_path = db_path
    
    def get_connection(self):
        return sqlite3.connect(self.db_path)
    
    def get_customer(self, customer_id):
        """Get customer by ID"""
        conn = self.get_connection()
        query = "SELECT * FROM customers WHERE customer_id = ?"
        customer = pd.read_sql_query(query, conn, params=(customer_id,))
        conn.close()
        return customer.iloc[0].to_dict() if not customer.empty else None
    
    def get_customers_by_risk(self, risk_level):
        """Get customers by risk level from latest predictions"""
        conn = self.get_connection()
        query = """
        SELECT c.*, p.churn_probability, p.risk_level, p.prediction_date
        FROM customers c
        JOIN predictions p ON c.customer_id = p.customer_id
        WHERE p.risk_level = ? 
        AND p.prediction_date = (
            SELECT MAX(prediction_date) 
            FROM predictions p2 
            WHERE p2.customer_id = c.customer_id
        )
        ORDER BY p.churn_probability DESC
        """
        customers = pd.read_sql_query(query, conn, params=(risk_level,))
        conn.close()
        return customers
    
    def save_prediction(self, customer_id, prediction_result, model_version='v1.0'):
        """Save prediction to database"""
        conn = self.get_connection()
        cursor = conn.cursor()
        
        cursor.execute('''
            INSERT INTO predictions 
            (customer_id, prediction_date, churn_probability, churn_prediction, 
             risk_level, model_version, features_json)
            VALUES (?, ?, ?, ?, ?, ?, ?)
        ''', (
            customer_id,
            datetime.now(),
            prediction_result['churn_probability'] / 100,  # Convert back to decimal
            prediction_result['churn_prediction'],
            prediction_result['risk_level'],
            model_version,
            json.dumps({})  # Can store feature values if needed
        ))
        
        conn.commit()
        conn.close()
    
    def get_dashboard_stats(self):
        """Get key statistics for dashboard"""
        conn = self.get_connection()
        
        # Total customers
        total_customers = pd.read_sql_query("SELECT COUNT(*) as count FROM customers WHERE status = 'active'", conn).iloc[0]['count']
        
        # Churn rate (from latest predictions)
        churn_stats = pd.read_sql_query("""
            SELECT 
                AVG(churn_probability) as avg_churn_prob,
                COUNT(*) as total_predictions,
                SUM(CASE WHEN risk_level = 'High Risk' THEN 1 ELSE 0 END) as high_risk_count,
                SUM(CASE WHEN risk_level = 'Medium Risk' THEN 1 ELSE 0 END) as medium_risk_count,
                SUM(CASE WHEN risk_level = 'Low Risk' THEN 1 ELSE 0 END) as low_risk_count
            FROM predictions p1
            WHERE p1.prediction_date = (
                SELECT MAX(p2.prediction_date) 
                FROM predictions p2 
                WHERE p2.customer_id = p1.customer_id
            )
        """, conn).iloc[0]
        
        # Monthly revenue at risk
        revenue_at_risk = pd.read_sql_query("""
            SELECT 
                SUM(c.monthly_bill) as total_revenue_at_risk
            FROM customers c
            JOIN predictions p ON c.customer_id = p.customer_id
            WHERE p.risk_level = 'High Risk'
            AND p.prediction_date = (
                SELECT MAX(prediction_date) 
                FROM predictions p2 
                WHERE p2.customer_id = c.customer_id
            )
        """, conn).iloc[0]['total_revenue_at_risk'] or 0
        
        conn.close()
        
        return {
            'total_customers': total_customers,
            'average_churn_risk': round(churn_stats['avg_churn_prob'] * 100, 1),
            'high_risk_customers': int(churn_stats['high_risk_count']),
            'medium_risk_customers': int(churn_stats['medium_risk_count']),
            'low_risk_customers': int(churn_stats['low_risk_count']),
            'revenue_at_risk': round(revenue_at_risk, 2)
        }
    
    def get_prediction_trends(self, days=30):
        """Get prediction trends over time"""
        conn = self.get_connection()
        
        query = """
        SELECT 
            DATE(prediction_date) as date,
            AVG(churn_probability) as avg_churn_prob,
            COUNT(*) as predictions_count
        FROM predictions
        WHERE prediction_date >= date('now', '-{} days')
        GROUP BY DATE(prediction_date)
        ORDER BY date
        """.format(days)
        
        trends = pd.read_sql_query(query, conn)
        conn.close()
        return trends

# Example usage
if __name__ == "__main__":
    db = ChurnDatabase()
    stats = db.get_dashboard_stats()
    print("Dashboard Stats:", stats)
'''
    
    with open('database_functions.py', 'w') as f:
        f.write(database_functions)
    
    print("✅ Database functions created in 'database_functions.py'")

# Execute all database setup
print("🗄️ Setting up comprehensive database system...")

create_database_schema()
populate_database()
create_database_functions()

# Test database functions
print("\n📊 Testing database functions...")

import sqlite3
conn = sqlite3.connect('churn_prediction_system.db')

# Check data
customers_count = pd.read_sql_query("SELECT COUNT(*) as count FROM customers", conn).iloc[0]['count']
interactions_count = pd.read_sql_query("SELECT COUNT(*) as count FROM customer_interactions", conn).iloc[0]['count']
print(f"Total customers: {customers_count}")
print(f"Total interactions: {interactions_count}")

# Sample query - high value customers
high_value_customers = pd.read_sql_query("""
    SELECT customer_id, first_name, last_name, monthly_bill, satisfaction_score
    FROM customers 
    WHERE monthly_bill > 100 
    ORDER BY monthly_bill DESC 
    LIMIT 10
""", conn)

print("\nTop 10 High-Value Customers:")
print(high_value_customers)

conn.close()

print("\n✅ Database system setup completed!")
print("📁 Files created:")
print("   - churn_prediction_system.db (SQLite database)")
print("   - database_functions.py (Database utility functions)")