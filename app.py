# =========================================
# FINAL MANAGERIAL DASHBOARD (FULL)
# =========================================

import streamlit as st
import pandas as pd
import matplotlib.pyplot as plt
import seaborn as sns

# -----------------------------
# PAGE CONFIG
# -----------------------------
st.set_page_config(page_title="Manager Dashboard", layout="wide")

# -----------------------------
# CUSTOM DARK UI
# -----------------------------
st.markdown("""
<style>
body {
    background-color: #0E1117;
    color: white;
}
.card {
    background-color: #161B22;
    padding: 20px;
    border-radius: 12px;
    margin-bottom: 10px;
}
.metric {
    font-size: 28px;
    font-weight: bold;
    color: #00FFAA;
}
.label {
    font-size: 14px;
    color: #AAAAAA;
}
</style>
""", unsafe_allow_html=True)

# -----------------------------
# LOAD DATA
# -----------------------------
df = pd.read_csv("data/processed/MPIA_EDA_READY.csv")

# Clean attrition (important)
df['attrition'] = df['attrition'].str.lower()

# -----------------------------
# SIDEBAR FILTERS
# -----------------------------
st.sidebar.title("Filters")

manager = st.sidebar.selectbox(
    "Select Manager",
    df['manager_name'].unique()
)

department = st.sidebar.selectbox(
    "Select Department",
    df['department'].unique()
)

filtered_df = df[
    (df['manager_name'] == manager) &
    (df['department'] == department)
]

# -----------------------------
# TITLE
# -----------------------------
st.title("Managerial Performance Dashboard")

# -----------------------------
# KPI CALCULATIONS
# -----------------------------
avg_perf = filtered_df['employee_performance'].mean()
avg_sat = filtered_df['satisfaction_score'].mean()
revenue = filtered_df['revenue_generated'].sum()

attrition_rate = (filtered_df['attrition'] == 'yes').mean() * 100

# -----------------------------
# KPI CARDS
# -----------------------------
col1, col2, col3, col4 = st.columns(4)

with col1:
    st.markdown(f"""
    <div class="card">
        <div class="label">Avg Performance</div>
        <div class="metric">{round(avg_perf,2)}</div>
    </div>
    """, unsafe_allow_html=True)

with col2:
    st.markdown(f"""
    <div class="card">
        <div class="label">Avg Satisfaction</div>
        <div class="metric">{round(avg_sat,2)}</div>
    </div>
    """, unsafe_allow_html=True)

with col3:
    st.markdown(f"""
    <div class="card">
        <div class="label">Revenue</div>
        <div class="metric">{int(revenue)}</div>
    </div>
    """, unsafe_allow_html=True)

with col4:
    st.markdown(f"""
    <div class="card">
        <div class="label">Attrition Rate</div>
        <div class="metric">{round(attrition_rate,2)}%</div>
    </div>
    """, unsafe_allow_html=True)

# -----------------------------
# CHARTS
# -----------------------------
col5, col6 = st.columns(2)

# Manager Performance (Improved)
with col5:
    st.subheader("Performance by Manager")

    # Prepare data (sorted)
    manager_perf = (
        df.groupby('manager_name')['employee_performance']
        .mean()
        .sort_values(ascending=False)
    )

    fig, ax = plt.subplots(figsize=(7,4))

    # Barplot
    bars = ax.bar(
        manager_perf.index,
        manager_perf.values,
        color="#00FFAA",
        edgecolor="white"
    )

    # Background styling
    ax.set_facecolor('#161B22')
    fig.patch.set_facecolor('#0E1117')

    # Labels
    ax.set_title("Average Employee Performance", color="white", fontsize=12)
    ax.set_xlabel("Manager", color="white")
    ax.set_ylabel("Performance Score", color="white")

    # Rotate x labels
    plt.xticks(rotation=30, ha='right', color="white")
    plt.yticks(color="white")

    # Add value labels on bars
    for bar in bars:
        height = bar.get_height()
        ax.text(
            bar.get_x() + bar.get_width()/2,
            height + 0.05,
            f"{round(height,2)}",
            ha='center',
            color='white',
            fontsize=9
        )

    # Remove top/right borders
    ax.spines['top'].set_visible(False)
    ax.spines['right'].set_visible(False)

    st.pyplot(fig)

# Revenue by Manager (Improved)
with col6:
    st.subheader("Revenue by Manager")

    # Prepare data (sorted)
    manager_rev = (
        df.groupby('manager_name')['revenue_generated']
        .sum()
        .sort_values(ascending=False)
    )

    fig2, ax2 = plt.subplots(figsize=(7,4))

    # Bar chart
    bars = ax2.bar(
        manager_rev.index,
        manager_rev.values,
        color="#4CAF50",
        edgecolor="white"
    )

    # Background styling
    ax2.set_facecolor('#161B22')
    fig2.patch.set_facecolor('#0E1117')

    # Titles & labels
    ax2.set_title("Total Revenue by Manager", color="white", fontsize=12)
    ax2.set_xlabel("Manager", color="white")
    ax2.set_ylabel("Revenue", color="white")

    # Rotate labels
    plt.xticks(rotation=30, ha='right', color="white")
    plt.yticks(color="white")

    # Add value labels
    for bar in bars:
        height = bar.get_height()
        ax2.text(
            bar.get_x() + bar.get_width()/2,
            height,
            f"{int(height)}",
            ha='center',
            va='bottom',
            color='white',
            fontsize=9
        )

    # Clean look
    ax2.spines['top'].set_visible(False)
    ax2.spines['right'].set_visible(False)

    st.pyplot(fig2)

# -----------------------------
# SATISFACTION DISTRIBUTION (IMPROVED)
# -----------------------------
st.subheader("Satisfaction Score Distribution")

fig3, ax3 = plt.subplots(figsize=(7,4))

# Histogram + KDE
sns.histplot(
    df['satisfaction_score'],
    kde=True,
    bins=20,
    color="#00FFAA",
    edgecolor="white",
    ax=ax3
)

# Background styling
ax3.set_facecolor('#161B22')
fig3.patch.set_facecolor('#0E1117')

# Labels
ax3.set_title("Distribution of Satisfaction Scores", color="white", fontsize=12)
ax3.set_xlabel("Satisfaction Score", color="white")
ax3.set_ylabel("Frequency", color="white")

# Tick colors
ax3.tick_params(colors='white')

# Mean line (VERY IMPORTANT 🔥)
mean_val = df['satisfaction_score'].mean()
ax3.axvline(mean_val, color='red', linestyle='--', linewidth=2)

# Mean label
ax3.text(
    mean_val,
    ax3.get_ylim()[1]*0.9,
    f"Mean: {round(mean_val,2)}",
    color='red',
    ha='center'
)

# Clean look
ax3.spines['top'].set_visible(False)
ax3.spines['right'].set_visible(False)

st.pyplot(fig3)

# -----------------------------
# CORRELATION HEATMAP (IMPROVED)
# -----------------------------
st.subheader("🔥 Correlation Heatmap")

# Select numeric data
corr = df.select_dtypes(include='number').corr()

fig4, ax4 = plt.subplots(figsize=(10,6))

# Heatmap
sns.heatmap(
    corr,
    annot=True,              # show values
    fmt=".2f",               # 2 decimal
    cmap="coolwarm",
    linewidths=0.5,
    linecolor='black',
    cbar=True,
    ax=ax4
)

# Background styling
ax4.set_facecolor('#161B22')
fig4.patch.set_facecolor('#0E1117')

# Title
ax4.set_title("Feature Correlation Matrix", color="white", fontsize=12)

# Tick styling
ax4.tick_params(colors='white')
plt.xticks(rotation=45, ha='right', color='white')
plt.yticks(color='white')

st.pyplot(fig4)
# -----------------------------
# TABLE
# -----------------------------
st.subheader("Filtered Data")
st.dataframe(filtered_df)

# test