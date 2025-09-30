import plotly.graph_objects as go
import plotly.express as px
import pandas as pd
import json

# Parse the provided data
data = [
    {"demographic": "Age 18-25", "churn_rate": 28.5, "customer_count": 234, "category": "age"},
    {"demographic": "Age 26-35", "churn_rate": 22.1, "customer_count": 567, "category": "age"},
    {"demographic": "Age 36-45", "churn_rate": 18.3, "customer_count": 892, "category": "age"},
    {"demographic": "Age 46-55", "churn_rate": 19.7, "customer_count": 743, "category": "age"},
    {"demographic": "Age 56-65", "churn_rate": 24.2, "customer_count": 432, "category": "age"},
    {"demographic": "Age 65+", "churn_rate": 31.8, "customer_count": 187, "category": "age"},
    {"demographic": "Male", "churn_rate": 23.4, "customer_count": 1623, "category": "gender"},
    {"demographic": "Female", "churn_rate": 25.1, "customer_count": 1432, "category": "gender"}
]

df = pd.DataFrame(data)

# Create a grouped bar chart showing churn rates by demographics
fig = go.Figure()

# Separate age and gender data
age_data = df[df['category'] == 'age']
gender_data = df[df['category'] == 'gender']

# Add age group bars
fig.add_trace(go.Bar(
    name='Age Groups',
    x=age_data['demographic'].str.replace('Age ', ''),
    y=age_data['churn_rate'],
    marker_color='#1FB8CD',
    hovertemplate='<b>%{x}</b><br>Churn Rate: %{y}%<br>Customers: %{customdata}<extra></extra>',
    customdata=age_data['customer_count']
))

# Add gender bars  
fig.add_trace(go.Bar(
    name='Gender',
    x=gender_data['demographic'],
    y=gender_data['churn_rate'],
    marker_color='#2E8B57',
    hovertemplate='<b>%{x}</b><br>Churn Rate: %{y}%<br>Customers: %{customdata}<extra></extra>',
    customdata=gender_data['customer_count']
))

# Update layout
fig.update_layout(
    title='Customer Churn Rate by Demographics',
    xaxis_title='Demographic',
    yaxis_title='Churn Rate (%)',
    barmode='group',
    legend=dict(orientation='h', yanchor='bottom', y=1.05, xanchor='center', x=0.5)
)

# Update traces for better display
fig.update_traces(cliponaxis=False)

# Format y-axis to show percentage
fig.update_yaxes(ticksuffix='%')

# Save as both PNG and SVG
fig.write_image('churn_demographics.png')
fig.write_image('churn_demographics.svg', format='svg')

print("Chart saved successfully!")