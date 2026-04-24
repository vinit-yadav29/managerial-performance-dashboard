# =========================================
# MANAGERIAL PERFORMANCE DASHBOARD
# =========================================

import streamlit as st
import pandas as pd
import matplotlib.pyplot as plt
import seaborn as sns

st.set_page_config(page_title="Manager Dashboard", layout="wide")

# =========================================
# THEME
# =========================================
st.markdown("""
<style>
body {background-color: #0E1117; color: white;}
.card {
    background-color: #161B22;
    padding: 20px;
    border-radius: 12px;
    text-align: center;
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

# =========================================
# LOAD DATA
# =========================================
df = pd.read_csv("data/processed/MPIA_EDA_READY.csv")

df['manager_name'] = df['manager_name'].astype(str).str.strip()
df['department'] = df['department'].astype(str).str.strip()
df['attrition'] = df['attrition'].astype(str).str.lower()

# =========================================
# FILTERS
# =========================================
st.sidebar.title("Filters")

manager = st.sidebar.selectbox(
    "Select Manager",
    sorted(df['manager_name'].dropna().unique())
)

filtered_departments = df[df['manager_name'] == manager]['department']

department = st.sidebar.selectbox(
    "Select Department",
    sorted(filtered_departments.dropna().unique())
)

filtered_df = df[
    (df['manager_name'] == manager) &
    (df['department'] == department)
]

if filtered_df.empty:
    st.warning("No data available")
    st.stop()

# =========================================
# TITLE
# =========================================
st.title("Managerial Performance Dashboard")

# =========================================
# KPI
# =========================================
def safe_mean(series):
    return round(series.mean(), 2) if not series.empty else 0

avg_perf = safe_mean(filtered_df['employee_performance'])
avg_sat = safe_mean(filtered_df['satisfaction_score'])
revenue = int(filtered_df['revenue_generated'].sum())
attrition_rate = round((filtered_df['attrition'] == 'yes').mean() * 100, 2)

col1, col2, col3, col4 = st.columns(4)

def kpi(title, value):
    return f"""
    <div class="card">
        <div class="label">{title}</div>
        <div class="metric">{value}</div>
    </div>
    """

col1.markdown(kpi("Avg Performance", avg_perf), unsafe_allow_html=True)
col2.markdown(kpi("Avg Satisfaction", avg_sat), unsafe_allow_html=True)
col3.markdown(kpi("Revenue", revenue), unsafe_allow_html=True)
col4.markdown(kpi("Attrition %", f"{attrition_rate}%"), unsafe_allow_html=True)

# =========================================
# INSIGHTS
# =========================================
st.subheader("Key Business Insights")

best_manager = df.groupby('manager_name')['employee_performance'].mean().idxmax()
worst_manager = df.groupby('manager_name')['employee_performance'].mean().idxmin()
top_revenue_manager = df.groupby('manager_name')['revenue_generated'].sum().idxmax()

st.markdown(f"""
✔ Best Performing Manager: **{best_manager}**  
✔ Lowest Performing Manager: **{worst_manager}**  
✔ Highest Revenue Generator: **{top_revenue_manager}**  
✔ Current Attrition Risk: **{attrition_rate}%**
""")

# =========================================
# ROW 1
# =========================================
col5, col6 = st.columns(2)

with col5:
    st.subheader("Performance by Manager")
    perf = df.groupby('manager_name')['employee_performance'].mean().sort_values()
    fig, ax = plt.subplots()
    perf.plot(kind='barh', color="#00FFAA", ax=ax)
    ax.set_facecolor('#161B22')
    fig.patch.set_facecolor('#0E1117')
    ax.tick_params(colors='white')
    st.pyplot(fig)

with col6:
    st.subheader("Revenue by Manager")
    rev = df.groupby('manager_name')['revenue_generated'].sum().sort_values()
    fig2, ax2 = plt.subplots()
    rev.plot(kind='barh', color="#4CAF50", ax=ax2)
    ax2.set_facecolor('#161B22')
    fig2.patch.set_facecolor('#0E1117')
    ax2.tick_params(colors='white')
    st.pyplot(fig2)

# =========================================
# ROW 2
# =========================================
col7, col8 = st.columns(2)

with col7:
    st.subheader("😊 Satisfaction by Manager")
    sat = df.groupby('manager_name')['satisfaction_score'].mean().sort_values()
    fig5, ax5 = plt.subplots()
    sat.plot(kind='barh', color="#00BFFF", ax=ax5)
    ax5.set_facecolor('#161B22')
    fig5.patch.set_facecolor('#0E1117')
    ax5.tick_params(colors='white')
    st.pyplot(fig5)

with col8:
    st.subheader("⚠️ Attrition Rate by Manager")
    attrition_df = df.copy()
    attrition_df['attrition_flag'] = (attrition_df['attrition'] == 'yes').astype(int)
    attrition_rate_mgr = attrition_df.groupby('manager_name')['attrition_flag'].mean().sort_values()
    fig6, ax6 = plt.subplots()
    attrition_rate_mgr.plot(kind='barh', color="#FF4C4C", ax=ax6)
    ax6.set_facecolor('#161B22')
    fig6.patch.set_facecolor('#0E1117')
    ax6.tick_params(colors='white')
    st.pyplot(fig6)

# =========================================
# ROW 3
# =========================================
col9, col10 = st.columns(2)

with col9:
    st.subheader("🏢 Performance by Department")
    dept_perf = df.groupby('department')['employee_performance'].mean().sort_values()
    fig8, ax8 = plt.subplots()
    dept_perf.plot(kind='bar', color="#9C27B0", ax=ax8)
    ax8.set_facecolor('#161B22')
    fig8.patch.set_facecolor('#0E1117')
    ax8.tick_params(colors='white')
    st.pyplot(fig8)

with col10:
    st.subheader("Satisfaction Distribution")
    fig3, ax3 = plt.subplots()
    sns.histplot(df['satisfaction_score'], kde=True, color="#00FFAA", ax=ax3)
    ax3.set_facecolor('#161B22')
    fig3.patch.set_facecolor('#0E1117')
    ax3.tick_params(colors='white')
    st.pyplot(fig3)

# =========================================
# FULL WIDTH
# =========================================
st.subheader("Employee Performance vs Revenue")

fig4, ax4 = plt.subplots(figsize=(10,5))
sns.scatterplot(data=df, x='employee_performance', y='revenue_generated', color="#00FFAA", ax=ax4)
sns.regplot(data=df, x='employee_performance', y='revenue_generated', scatter=False, color="red", ax=ax4)

ax4.set_facecolor('#161B22')
fig4.patch.set_facecolor('#0E1117')
ax4.tick_params(colors='white')

st.pyplot(fig4)

# =========================================
# TABLES
# =========================================
st.subheader("🏆 Manager Ranking")
ranking = df.groupby('manager_name')['employee_performance'].mean().sort_values(ascending=False)
st.dataframe(ranking.reset_index().rename(columns={'employee_performance': 'Avg Performance'}))

st.subheader("Filtered Data")
st.dataframe(filtered_df.reset_index(drop=True))