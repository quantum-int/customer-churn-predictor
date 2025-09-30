import plotly.graph_objects as go
import plotly.express as px
import pandas as pd

# Create the feature importance data
feature_data = [
    {"feature": "monthly_bill", "importance": 0.115, "rank": 1},
    {"feature": "clv_estimate", "importance": 0.091, "rank": 2},
    {"feature": "avg_monthly_usage_growth", "importance": 0.084, "rank": 3},
    {"feature": "total_usage_gb", "importance": 0.080, "rank": 4},
    {"feature": "credit_score", "importance": 0.068, "rank": 5},
    {"feature": "subscription_length_months", "importance": 0.067, "rank": 6},
    {"feature": "age", "importance": 0.065, "rank": 7},
    {"feature": "satisfaction_score", "importance": 0.062, "rank": 8},
    {"feature": "last_payment_days_ago", "importance": 0.062, "rank": 9},
    {"feature": "contract_monthly", "importance": 0.054, "rank": 10},
    {"feature": "customer_service_calls", "importance": 0.052, "rank": 11},
    {"feature": "services_count", "importance": 0.048, "rank": 12},
    {"feature": "last_login_days_ago", "importance": 0.045, "rank": 13},
    {"feature": "support_tickets", "importance": 0.041, "rank": 14},
    {"feature": "high_value", "importance": 0.038, "rank": 15}
]

df = pd.DataFrame(feature_data)

# Abbreviate feature names to stay under 15 characters
feature_abbrev = {
    "monthly_bill": "Monthly Bill",
    "clv_estimate": "CLV Estimate", 
    "avg_monthly_usage_growth": "Usage Growth",
    "total_usage_gb": "Total Usage GB",
    "credit_score": "Credit Score",
    "subscription_length_months": "Subscription",
    "age": "Age",
    "satisfaction_score": "Satisfaction",
    "last_payment_days_ago": "Last Payment",
    "contract_monthly": "Contract Type",
    "customer_service_calls": "Service Calls",
    "services_count": "Services Cnt",
    "last_login_days_ago": "Last Login",
    "support_tickets": "Support Tix",
    "high_value": "High Value"
}

df['feature_short'] = df['feature'].map(feature_abbrev)

# Sort by importance (descending) for display
df_sorted = df.sort_values('importance', ascending=True)  # ascending=True for horizontal bars

# Create horizontal bar chart with gradient colors
fig = go.Figure()

# Create a color scale from light blue to dark blue for professional ML look
colors = px.colors.sequential.Blues_r[:len(df_sorted)]

fig.add_trace(go.Bar(
    y=df_sorted['feature_short'],
    x=df_sorted['importance'],
    orientation='h',
    marker=dict(
        color=colors,
        line=dict(width=1, color='rgba(255,255,255,0.8)')
    ),
    text=[f"{imp:.3f}" for imp in df_sorted['importance']],
    textposition='outside',
    hovertemplate='<b>%{y}</b><br>Importance: %{x:.3f}<extra></extra>'
))

fig.update_layout(
    title="Feature Importance - Churn Prediction",
    xaxis_title="Importance",
    yaxis_title="Features",
    showlegend=False
)

fig.update_xaxes(range=[0, max(df['importance']) * 1.15])
fig.update_traces(cliponaxis=False)

# Save as both PNG and SVG
fig.write_image("feature_importance.png")
fig.write_image("feature_importance.svg", format="svg")

print("Chart saved as feature_importance.png and feature_importance.svg")