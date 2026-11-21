import pandas as pd
import seaborn as sns
import matplotlib.pyplot as plt
import plotly.express as px
import streamlit as st

# Page Configuration & Branding
st.set_page_config(
    page_title="Executive Sales Analytics Dashboard",
    page_icon="📊",
    layout="wide"
)

# Load & Cache Data
@st.cache_data
def load_data():
    df = pd.read_csv("sales_data.csv")
    df["Date"] = pd.to_datetime(df["Date"])
    df["Month"] = df["Date"].dt.to_period("M").astype(str)
    # Derive Customer Value Tier for Segmentation
    df["Customer_Segment"] = pd.qcut(
        df["Total_Sales"], q=3, labels=["Standard Tier", "Growth Tier", "Enterprise Tier"]
    )
    return df

df = load_data()

# Sidebar Filters (Interactive Controls)
st.sidebar.header("🎛️ Dashboard Filters")
selected_regions = st.sidebar.multiselect(
    "Select Regions:", options=sorted(df["Region"].unique()), default=sorted(df["Region"].unique())
)
selected_products = st.sidebar.multiselect(
    "Select Products:", options=sorted(df["Product"].unique()), default=sorted(df["Product"].unique())
)

filtered_df = df[df["Region"].isin(selected_regions) & df["Product"].isin(selected_products)]

# Header & Executive KPI Row
st.title("📊 Interactive Sales Performance & Customer Segmentation Dashboard")
st.markdown("Cohesive statistical and interactive visual analytics covering **Q1–Q2 2024** transactions.")

kpi1, kpi2, kpi3, kpi4 = st.columns(4)
kpi1.metric("Total Revenue", f"${filtered_df['Total_Sales'].sum():,.0f}")
kpi2.metric("Average Order Value", f"${filtered_df['Total_Sales'].mean():,.0f}")
kpi3.metric("Total Units Sold", f"{filtered_df['Quantity'].sum():,}")
kpi4.metric("Active Customers", f"{filtered_df['Customer_ID'].nunique()}")

st.divider()

# Row 1: Interactive Sales Trend (Chart 1) & Customer Segmentation Sunburst (Chart 2)
col1, col2 = st.columns([3, 2])

with col1:
    daily_trend = filtered_df.groupby(["Date", "Product"], as_index=False)["Total_Sales"].sum()
    fig_trend = px.line(
        daily_trend, x="Date", y="Total_Sales", color="Product",
        title="1. Daily Sales Trend by Product (Interactive Hover & Zoom)",
        color_discrete_sequence=px.colors.sequential.Viridis_r,
        markers=True
    )
    fig_trend.update_layout(hovermode="x unified", yaxis_title="Sales ($)")
    st.plotly_chart(fig_trend, use_container_width=True)

with col2:
    fig_sunburst = px.sunburst(
        filtered_df, path=["Region", "Customer_Segment", "Product"], values="Total_Sales",
        title="2. Customer Segmentation Hierarchy (Region → Tier → Product)",
        color="Total_Sales", color_continuous_scale="Viridis"
    )
    st.plotly_chart(fig_sunburst, use_container_width=True)

# Row 2: Animated Price vs. Quantity Bubble Chart (Chart 3) & Interactive Box Plot (Chart 4)
col3, col4 = st.columns(2)

with col3:
    fig_scatter = px.scatter(
        filtered_df, x="Price", y="Quantity", size="Total_Sales", color="Product",
        animation_frame="Month", hover_name="Customer_ID",
        hover_data={"Region": True, "Total_Sales": ":$,.0f"},
        range_x=[0, 55000], range_y=[0, 10],
        title="3. Monthly Price vs. Quantity Dynamics (Animated)",
        color_discrete_sequence=px.colors.sequential.Viridis_r
    )
    st.plotly_chart(fig_scatter, use_container_width=True)

with col4:
    fig_box = px.box(
        filtered_df, x="Product", y="Total_Sales", color="Region",
        title="4. Order Value Distribution by Product & Region (Interactive Box Plot)",
        color_discrete_sequence=px.colors.qualitative.Prism
    )
    st.plotly_chart(fig_box, use_container_width=True)

# Row 3: Seaborn Statistical Summary (Chart 5: Heatmap & Violin Plot)
st.subheader("🔬 Statistical Distribution & Correlation Analysis (Seaborn Engine)")
s_col1, s_col2 = st.columns(2)

with s_col1:
    fig_heat, ax_heat = plt.subplots(figsize=(6, 4))
    sns.heatmap(
        filtered_df[["Quantity", "Price", "Total_Sales"]].corr(),
        annot=True, fmt=".2f", cmap="coolwarm", vmin=-1, vmax=1, ax=ax_heat
    )
    ax_heat.set_title("5A. Feature Correlation Matrix")
    st.pyplot(fig_heat)

with s_col2:
    fig_vio, ax_vio = plt.subplots(figsize=(6, 4))
    sns.violinplot(x="Region", y="Price", data=filtered_df, palette="magma", inner="quartile", ax=ax_vio)
    ax_vio.set_title("5B. Unit Price Density by Region")
    st.pyplot(fig_vio)