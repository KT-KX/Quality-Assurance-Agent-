"""
a) Using the clustering results from marketing_campaign_clustered.csv, build a Streamlit dashboard
that enables users to explore customer segments interactively. The dashboard should include at least
five visual widgets (e.g., KPI card boxes, bar charts, histograms, scatterplots, etc) and at least one filter
(e.g., by cluster, cluster label) to refine the analysis view
"""

import streamlit as st
import pandas as pd
import numpy as np
import matplotlib.pyplot as plt
import seaborn as sns
import plotly.express as px
import plotly.graph_objects as go
from plotly.subplots import make_subplots

# Page configuration
st.set_page_config(
    page_title="Customer Segmentation Dashboard",
    layout="wide",
    initial_sidebar_state="expanded"
)


# Load data
@st.cache_data
def load_data():
    """Load and preprocess the clustered dataset"""
    df = pd.read_csv('marketing_campaign_clustered.csv')
    # Convert Dt_Customer to datetime if needed
    if 'Dt_Customer' in df.columns:
        df['Dt_Customer'] = pd.to_datetime(df['Dt_Customer'])
    return df

df = load_data()


st.sidebar.header("Filters")

cluster_options = sorted(df['Cluster_KMeans'].unique())
selected_clusters = st.sidebar.multiselect(
    "Select Clusters (K-Means)",
    options=cluster_options,
    default=cluster_options,
    help="Select one or more clusters to analyze"
)

education_options = ['All'] + sorted(df['Education'].unique().tolist())
selected_education = st.sidebar.selectbox(
    "Filter by Education",
    options=education_options,
    help="Filter customers by education level"
)


marital_options = ['All'] + sorted(df['Marital_Status'].unique().tolist())
selected_marital = st.sidebar.selectbox(
    "Filter by Marital Status",
    options=marital_options,
    help="Filter customers by marital status"
)


min_income = int(df['Income'].min())
max_income = int(df['Income'].max())
income_range = st.sidebar.slider(
    "Income Range (RM)",
    min_value=min_income,
    max_value=max_income,
    value=(min_income, max_income),
    help="Filter customers by income range"
)

# Apply filters
filtered_df = df[df['Cluster_KMeans'].isin(selected_clusters)]
filtered_df = filtered_df[
    (filtered_df['Income'] >= income_range[0]) & 
    (filtered_df['Income'] <= income_range[1])
]

if selected_education != 'All':
    filtered_df = filtered_df[filtered_df['Education'] == selected_education]
if selected_marital != 'All':
    filtered_df = filtered_df[filtered_df['Marital_Status'] == selected_marital]

# Main title
st.header('Customer Segmentation Dashboard')
st.markdown("---")

# KPI Cards - Widget 1
st.header("Key Performance Indicators")
col1, col2, col3, col4 = st.columns(4)

with col1:
    total_customers = len(filtered_df)
    st.metric(
        label="Total Customers",
        value=f"{total_customers:,}",
        delta=f"{total_customers - len(df):,}" if total_customers != len(df) else None
    )

with col2:
    avg_income = filtered_df['Income'].mean()
    st.metric(
        label="Average Income",
        value=f"RM{avg_income:,.0f}",
        delta=f"RM{avg_income - df['Income'].mean():,.0f}" if len(filtered_df) != len(df) else None
    )

with col3:
    avg_spending = filtered_df['TotalSpending'].mean()
    st.metric(
        label="Average Spending",
        value=f"RM{avg_spending:,.0f}",
        delta=f"RM{avg_spending - df['TotalSpending'].mean():,.0f}" if len(filtered_df) != len(df) else None
    )

with col4:
    response_rate = filtered_df['Response'].mean() * 100
    overall_response = df['Response'].mean() * 100
    st.metric(
        label="Response Rate",
        value=f"{response_rate:.1f}%",
        delta=f"{response_rate - overall_response:.1f}%" if len(filtered_df) != len(df) else None
    )

st.markdown("---")

st.header("Cluster Distribution")
col1, col2 = st.columns(2)

with col1:
    # Bar chart - Cluster counts
    cluster_counts = filtered_df['Cluster_KMeans'].value_counts().sort_index()
    cluster_df = pd.DataFrame({
        'Cluster': cluster_counts.index.astype(str),
        'Count': cluster_counts.values
    })
    fig_bar = px.bar(
        cluster_df,
        x='Cluster',
        y='Count',
        labels={'Cluster': 'Cluster', 'Count': 'Number of Customers'},
        title='Number of Customers per Cluster',
        color='Count',
        color_continuous_scale='Blues'
    )
    fig_bar.update_layout(showlegend=False, height=400)
    st.plotly_chart(fig_bar, use_container_width=True)

with col2:
    # Pie chart - Cluster proportions
    fig_pie = px.pie(
        values=cluster_counts.values,
        names=cluster_counts.index.astype(str),
        title='Cluster Proportion',
        color_discrete_sequence=px.colors.qualitative.Set3
    )
    fig_pie.update_layout(height=400)
    st.plotly_chart(fig_pie, use_container_width=True)

st.markdown("---")

# Widget 3: Income vs Spending Scatter Plot
st.header("Income vs Spending Analysis")
col1, col2 = st.columns([2, 1])

with col1:
    # Scatter plot with cluster colors
    fig_scatter = px.scatter(
        filtered_df,
        x='Income',
        y='TotalSpending',
        color='Cluster_KMeans',
        size='TotalPurchases',
        hover_data=['Age', 'Education', 'Marital_Status', 'Response'],
        labels={'Cluster_KMeans': 'Cluster'},
        title='Income vs Total Spending by Cluster',
        color_discrete_sequence=px.colors.qualitative.Set2
    )
    fig_scatter.update_layout(height=500)
    st.plotly_chart(fig_scatter, use_container_width=True)

with col2:
    st.subheader("Cluster Statistics")
    cluster_stats = filtered_df.groupby('Cluster_KMeans').agg({
        'Income': 'mean',
        'TotalSpending': 'mean',
        'Age': 'mean',
        'Response': 'mean'
    }).round(2)
    cluster_stats.columns = ['Avg Income', 'Avg Spending', 'Avg Age', 'Response Rate']
    st.dataframe(cluster_stats, use_container_width=True)

st.markdown("---")

# Widget 4: Spending by Category - Grouped Bar Chart
st.header(" Spending Patterns by Product Category")
spending_cols = ['MntWines', 'MntFruits', 'MntMeatProducts', 'MntFishProducts', 
                 'MntSweetProducts', 'MntGoldProds']
spending_by_cluster = filtered_df.groupby('Cluster_KMeans')[spending_cols].mean()

fig_spending = go.Figure()
categories_short = ['Wines', 'Fruits', 'Meat', 'Fish', 'Sweet', 'Gold']
colors = px.colors.qualitative.Set3

for i, col in enumerate(spending_cols):
    fig_spending.add_trace(go.Bar(
        name=categories_short[i],
        x=spending_by_cluster.index.astype(str),
        y=spending_by_cluster[col],
        marker_color=colors[i % len(colors)]
    ))

fig_spending.update_layout(
    title='Average Spending by Product Category and Cluster',
    xaxis_title='Cluster',
    yaxis_title='Average Spending (RM)',
    barmode='group',
    height=500,
    legend=dict(orientation="h", yanchor="bottom", y=1.02, xanchor="right", x=1)
)
st.plotly_chart(fig_spending, use_container_width=True)

st.markdown("---")

# Widget 5: Age Distribution Histogram
st.header(" Demographic Analysis")
col1, col2 = st.columns(2)

with col1:
    # Age distribution by cluster
    fig_age = px.histogram(
        filtered_df,
        x='Age',
        color='Cluster_KMeans',
        nbins=30,
        title='Age Distribution by Cluster',
        labels={'Cluster_KMeans': 'Cluster'},
        barmode='overlay',
        opacity=0.7,
        color_discrete_sequence=px.colors.qualitative.Set2
    )
    fig_age.update_layout(height=400)
    st.plotly_chart(fig_age, use_container_width=True)

with col2:
    # Income distribution by cluster
    fig_income = px.histogram(
        filtered_df,
        x='Income',
        color='Cluster_KMeans',
        nbins=30,
        title='Income Distribution by Cluster',
        labels={'Cluster_KMeans': 'Cluster'},
        barmode='overlay',
        opacity=0.7,
        color_discrete_sequence=px.colors.qualitative.Set2
    )
    fig_income.update_layout(height=400)
    st.plotly_chart(fig_income, use_container_width=True)

st.markdown("---")

# Widget 6: Education and Marital Status Distribution
st.header(" Education & Marital Status Distribution")
col1, col2 = st.columns(2)

with col1:
    # Education by cluster
    edu_cluster = pd.crosstab(filtered_df['Cluster_KMeans'], filtered_df['Education'], normalize='index') * 100
    fig_edu = px.bar(
        edu_cluster,
        title='Education Distribution by Cluster (%)',
        labels={'value': 'Percentage (%)', 'index': 'Cluster'},
        color_discrete_sequence=px.colors.qualitative.Pastel
    )
    fig_edu.update_layout(height=400, legend=dict(orientation="h", yanchor="bottom", y=1.02, xanchor="right", x=1))
    st.plotly_chart(fig_edu, use_container_width=True)

with col2:
    # Marital status by cluster
    marital_cluster = pd.crosstab(filtered_df['Cluster_KMeans'], filtered_df['Marital_Status'], normalize='index') * 100
    fig_marital = px.bar(
        marital_cluster,
        title='Marital Status Distribution by Cluster (%)',
        labels={'value': 'Percentage (%)', 'index': 'Cluster'},
        color_discrete_sequence=px.colors.qualitative.Pastel
    )
    fig_marital.update_layout(height=400, legend=dict(orientation="h", yanchor="bottom", y=1.02, xanchor="right", x=1))
    st.plotly_chart(fig_marital, use_container_width=True)

st.markdown("---")

# Widget 7: Campaign Response Analysis
st.header("Campaign Performance by Cluster")
col1, col2 = st.columns(2)

with col1:
    # Response rate by cluster
    response_by_cluster = filtered_df.groupby('Cluster_KMeans')['Response'].mean() * 100
    response_df = pd.DataFrame({
        'Cluster': response_by_cluster.index.astype(str),
        'Response Rate': response_by_cluster.values
    })
    fig_response = px.bar(
        response_df,
        x='Cluster',
        y='Response Rate',
        labels={'Cluster': 'Cluster', 'Response Rate': 'Response Rate (%)'},
        title='Campaign Response Rate by Cluster',
        color='Response Rate',
        color_continuous_scale='Greens'
    )
    fig_response.update_layout(showlegend=False, height=400)
    st.plotly_chart(fig_response, use_container_width=True)

with col2:
    # Campaign acceptance by cluster
    campaign_cols = ['AcceptedCmp1', 'AcceptedCmp2', 'AcceptedCmp3', 'AcceptedCmp4', 'AcceptedCmp5']
    campaign_acceptance = filtered_df.groupby('Cluster_KMeans')[campaign_cols].mean() * 100
    
    fig_campaign = go.Figure()
    for i, col in enumerate(campaign_cols):
        fig_campaign.add_trace(go.Bar(
            name=f'Campaign {i+1}',
            x=campaign_acceptance.index.astype(str),
            y=campaign_acceptance[col],
            marker_color=px.colors.qualitative.Set3[i]
        ))
    
    fig_campaign.update_layout(
        title='Campaign Acceptance Rate by Cluster (%)',
        xaxis_title='Cluster',
        yaxis_title='Acceptance Rate (%)',
        barmode='group',
        height=400,
        legend=dict(orientation="h", yanchor="bottom", y=1.02, xanchor="right", x=1)
    )
    st.plotly_chart(fig_campaign, use_container_width=True)

st.markdown("---")

# Widget 8: Purchase Channel Analysis
st.header("Purchase Channel Preferences")
purchase_cols = ['NumWebPurchases', 'NumCatalogPurchases', 'NumStorePurchases', 'NumDealsPurchases']
purchase_by_cluster = filtered_df.groupby('Cluster_KMeans')[purchase_cols].mean()

fig_channels = go.Figure()
channel_names = ['Web', 'Catalog', 'Store', 'Deals']
colors_channels = px.colors.qualitative.Set1

for i, col in enumerate(purchase_cols):
    fig_channels.add_trace(go.Bar(
        name=channel_names[i],
        x=purchase_by_cluster.index.astype(str),
        y=purchase_by_cluster[col],
        marker_color=colors_channels[i % len(colors_channels)]
    ))

fig_channels.update_layout(
    title='Average Purchases by Channel and Cluster',
    xaxis_title='Cluster',
    yaxis_title='Average Number of Purchases',
    barmode='group',
    height=500,
    legend=dict(orientation="h", yanchor="bottom", y=1.02, xanchor="right", x=1)
)
st.plotly_chart(fig_channels, use_container_width=True)

st.markdown("---")

# Data Table
st.header("Detailed Data View")
st.dataframe(
    filtered_df[['ID', 'Age', 'Income', 'TotalSpending', 'Education', 'Marital_Status', 
                 'Cluster_KMeans', 'Response', 'TotalPurchases']].head(100),
    use_container_width=True,
    height=400
)


