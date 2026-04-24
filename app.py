import streamlit as st
import pandas as pd
import numpy as np
import plotly.express as px
import plotly.graph_objects as go
from plotly.subplots import make_subplots

# Page configuration
st.set_page_config(
    page_title="Managerial Performance Analytics",
    page_icon="📊",
    layout="wide",
    initial_sidebar_state="expanded"
)

# Custom CSS for SaaS-style UI
st.markdown("""
<style>
    /* Import Inter font */
    @import url('[fonts.googleapis.com](https://fonts.googleapis.com/css2?family=Inter:wght@300;400;500;600;700&display=swap)');
    
    /* Main background */
    .stApp {
        background-color: #F4F7F6;
        font-family: 'Inter', sans-serif;
    }
    
    /* Sidebar styling */
    [data-testid="stSidebar"] {
        background: linear-gradient(180deg, #0F3D3E 0%, #145A5A 100%);
        border-radius: 0 20px 20px 0;
    }
    
    [data-testid="stSidebar"] .stMarkdown {
        color: #D1FAE5;
    }
    
    [data-testid="stSidebar"] label {
        color: #D1FAE5 !important;
        font-weight: 500;
    }
    
    [data-testid="stSidebar"] .stSelectbox label {
        color: #D1FAE5 !important;
    }
    
    /* Header styling */
    .main-header {
        background: white;
        padding: 20px 30px;
        border-radius: 16px;
        box-shadow: 0 4px 20px rgba(0,0,0,0.08);
        margin-bottom: 24px;
    }
    
    .main-title {
        font-size: 28px;
        font-weight: 700;
        color: #111827;
        margin: 0;
    }
    
    .sub-title {
        font-size: 14px;
        color: #6B7280;
        margin-top: 4px;
    }
    
    /* KPI Card styling */
    .kpi-card {
        background: white;
        border-radius: 16px;
        padding: 20px;
        box-shadow: 0 4px 20px rgba(0,0,0,0.08);
        transition: all 0.3s ease;
        height: 100%;
    }
    
    .kpi-card:hover {
        transform: translateY(-4px);
        box-shadow: 0 8px 30px rgba(0,0,0,0.12);
    }
    
    .kpi-label {
        font-size: 13px;
        color: #6B7280;
        font-weight: 500;
        margin-bottom: 8px;
    }
    
    .kpi-value {
        font-size: 28px;
        font-weight: 700;
        color: #1F2937;
    }
    
    .kpi-icon {
        font-size: 24px;
        margin-bottom: 8px;
    }
    
    /* Chart container */
    .chart-container {
        background: white;
        border-radius: 16px;
        padding: 24px;
        box-shadow: 0 4px 20px rgba(0,0,0,0.08);
        margin-bottom: 24px;
    }
    
    .chart-title {
        font-size: 18px;
        font-weight: 600;
        color: #111827;
        margin-bottom: 16px;
    }
    
    /* Insight card */
    .insight-card {
        background: linear-gradient(135deg, #E6F4F1 0%, #D1FAE5 100%);
        border-radius: 16px;
        padding: 20px;
        border-left: 4px solid #2F9E8F;
        margin-bottom: 16px;
    }
    
    .insight-label {
        font-size: 12px;
        color: #145A5A;
        font-weight: 600;
        text-transform: uppercase;
        letter-spacing: 0.5px;
    }
    
    .insight-value {
        font-size: 18px;
        font-weight: 600;
        color: #0F3D3E;
        margin-top: 4px;
    }
    
    /* Section header */
    .section-header {
        font-size: 20px;
        font-weight: 600;
        color: #111827;
        margin: 32px 0 16px 0;
        padding-bottom: 8px;
        border-bottom: 2px solid #E6F4F1;
    }
    
    /* Table styling */
    .dataframe {
        border-radius: 12px;
        overflow: hidden;
    }
    
    /* Hide Streamlit branding */
    #MainMenu {visibility: hidden;}
    footer {visibility: hidden;}
    
    /* Selectbox styling in sidebar */
    [data-testid="stSidebar"] .stSelectbox > div > div {
        background-color: rgba(255,255,255,0.1);
        border: 1px solid rgba(255,255,255,0.2);
        border-radius: 8px;
    }
</style>
""", unsafe_allow_html=True)


# Data loading and preprocessing
@st.cache_data
def load_data():
    """Load and preprocess the dataset."""
    # Generate sample data based on the provided structure
    np.random.seed(42)
    n_rows = 280
    
    departments = ['sales', 'marketing', 'engineering', 'hr', 'finance', 'operations']
    manager_names = [
        'amit kumar', 'neha jain', 'sneha kapoor', 'rahul sharma', 'priya singh',
        'vikram patel', 'anita gupta', 'rohit verma', 'kavita reddy', 'suresh kumar',
        'meena sharma', 'ajay singh', 'pooja patel', 'deepak gupta', 'sunita jain'
    ]
    
    data = {
        'employee_id': [f'emp_{str(i).zfill(4)}' for i in range(1, n_rows + 1)],
        'manager_id': np.random.randint(1, 16, n_rows),
        'manager_name': np.random.choice(manager_names, n_rows),
        'department': np.random.choice(departments, n_rows),
        'manager_experience': np.random.randint(5, 20, n_rows),
        'leadership_score': np.round(np.random.uniform(6.5, 9.5, n_rows), 2),
        'communication_score': np.round(np.random.uniform(6.5, 9.5, n_rows), 2),
        'manager_performance_score': np.round(np.random.uniform(6.5, 9.5, n_rows), 2),
        'employee_performance': np.round(np.random.uniform(5.0, 10.0, n_rows), 2),
        'satisfaction_score': np.round(np.random.uniform(5.0, 30.0, n_rows), 2),
        'project_success_score': np.round(np.random.uniform(5.5, 9.5, n_rows), 2),
        'revenue_generated': np.round(np.random.uniform(50000, 100000, n_rows), 2),
        'attrition': np.random.choice(['yes', 'no'], n_rows, p=[0.25, 0.75]),
        'performance_efficiency': np.round(np.random.uniform(0.5, 1.0, n_rows), 4)
    }
    
    df = pd.DataFrame(data)
    
    # Ensure numeric columns are numeric
    numeric_cols = ['manager_experience', 'leadership_score', 'communication_score',
                    'manager_performance_score', 'employee_performance', 'satisfaction_score',
                    'project_success_score', 'revenue_generated', 'performance_efficiency']
    
    for col in numeric_cols:
        df[col] = pd.to_numeric(df[col], errors='coerce')
    
    return df


def calculate_kpis(df):
    """Calculate KPI metrics from the dataframe."""
    if df.empty:
        return {
            'avg_employee_perf': 0,
            'avg_satisfaction': 0,
            'total_revenue': 0,
            'attrition_rate': 0,
            'avg_project_success': 0
        }
    
    attrition_rate = (df['attrition'].str.lower() == 'yes').sum() / len(df) * 100 if len(df) > 0 else 0
    
    return {
        'avg_employee_perf': df['employee_performance'].mean(),
        'avg_satisfaction': df['satisfaction_score'].mean(),
        'total_revenue': df['revenue_generated'].sum(),
        'attrition_rate': attrition_rate,
        'avg_project_success': df['project_success_score'].mean()
    }


def get_insights(df):
    """Generate business insights from the data."""
    if df.empty:
        return {
            'best_manager': 'N/A',
            'worst_manager': 'N/A',
            'highest_revenue_manager': 'N/A',
            'avg_attrition_rate': 0,
            'most_impactful_feature': 'N/A'
        }
    
    # Manager aggregations
    manager_stats = df.groupby('manager_name').agg({
        'manager_performance_score': 'mean',
        'revenue_generated': 'sum',
        'employee_performance': 'mean'
    }).reset_index()
    
    best_manager = manager_stats.loc[manager_stats['manager_performance_score'].idxmax(), 'manager_name']
    worst_manager = manager_stats.loc[manager_stats['manager_performance_score'].idxmin(), 'manager_name']
    highest_revenue_manager = manager_stats.loc[manager_stats['revenue_generated'].idxmax(), 'manager_name']
    
    # Attrition rate
    attrition_rate = (df['attrition'].str.lower() == 'yes').sum() / len(df) * 100
    
    # Most impactful feature (correlation with manager performance)
    numeric_cols = ['leadership_score', 'communication_score', 'manager_experience']
    correlations = {}
    for col in numeric_cols:
        corr = df[col].corr(df['manager_performance_score'])
        if not np.isnan(corr):
            correlations[col] = abs(corr)
    
    most_impactful = max(correlations, key=correlations.get) if correlations else 'N/A'
    feature_names = {
        'leadership_score': 'Leadership',
        'communication_score': 'Communication',
        'manager_experience': 'Experience'
    }
    most_impactful_display = feature_names.get(most_impactful, most_impactful)
    
    return {
        'best_manager': best_manager.title(),
        'worst_manager': worst_manager.title(),
        'highest_revenue_manager': highest_revenue_manager.title(),
        'avg_attrition_rate': attrition_rate,
        'most_impactful_feature': most_impactful_display
    }


def create_scatter_with_trendline(df, x_col, y_col, title, x_label, y_label):
    """Create a scatter plot with regression trendline."""
    if df.empty:
        fig = go.Figure()
        fig.add_annotation(text="No data available", xref="paper", yref="paper", x=0.5, y=0.5, showarrow=False)
        return fig
    
    fig = px.scatter(
        df, x=x_col, y=y_col,
        trendline="ols",
        color_discrete_sequence=['#2F9E8F'],
        opacity=0.7
    )
    
    fig.update_traces(marker=dict(size=10, line=dict(width=1, color='white')))
    fig.update_layout(
        title=dict(text=title, font=dict(size=16, color='#111827')),
        xaxis_title=x_label,
        yaxis_title=y_label,
        plot_bgcolor='white',
        paper_bgcolor='white',
        font=dict(family='Inter', color='#6B7280'),
        xaxis=dict(gridcolor='#E5E7EB', zerolinecolor='#E5E7EB'),
        yaxis=dict(gridcolor='#E5E7EB', zerolinecolor='#E5E7EB'),
        margin=dict(l=40, r=40, t=60, b=40)
    )
    
    return fig


def create_attrition_bar_chart(df):
    """Create attrition rate by manager bar chart."""
    if df.empty:
        fig = go.Figure()
        fig.add_annotation(text="No data available", xref="paper", yref="paper", x=0.5, y=0.5, showarrow=False)
        return fig
    
    attrition_by_manager = df.groupby('manager_name').apply(
        lambda x: (x['attrition'].str.lower() == 'yes').sum() / len(x) * 100
    ).reset_index()
    attrition_by_manager.columns = ['manager_name', 'attrition_rate']
    attrition_by_manager = attrition_by_manager.sort_values('attrition_rate', ascending=False).head(10)
    
    fig = px.bar(
        attrition_by_manager,
        x='attrition_rate',
        y='manager_name',
        orientation='h',
        color='attrition_rate',
        color_continuous_scale=['#E6F4F1', '#F97316'],
    )
    
    fig.update_layout(
        title=dict(text='Attrition Rate by Manager (Top 10)', font=dict(size=16, color='#111827')),
        xaxis_title='Attrition Rate (%)',
        yaxis_title='',
        plot_bgcolor='white',
        paper_bgcolor='white',
        font=dict(family='Inter', color='#6B7280'),
        showlegend=False,
        coloraxis_showscale=False,
        margin=dict(l=40, r=40, t=60, b=40)
    )
    
    return fig


def create_correlation_heatmap(df):
    """Create correlation heatmap for attribute importance."""
    if df.empty:
        fig = go.Figure()
        fig.add_annotation(text="No data available", xref="paper", yref="paper", x=0.5, y=0.5, showarrow=False)
        return fig
    
    cols = ['leadership_score', 'communication_score', 'manager_experience', 
            'manager_performance_score', 'employee_performance', 'satisfaction_score']
    
    corr_matrix = df[cols].corr()
    
    labels = ['Leadership', 'Communication', 'Experience', 'Mgr Performance', 'Emp Performance', 'Satisfaction']
    
    fig = go.Figure(data=go.Heatmap(
        z=corr_matrix.values,
        x=labels,
        y=labels,
        colorscale=[[0, '#E6F4F1'], [0.5, '#2F9E8F'], [1, '#0F3D3E']],
        text=np.round(corr_matrix.values, 2),
        texttemplate='%{text}',
        textfont=dict(size=11),
        hoverongaps=False
    ))
    
    fig.update_layout(
        title=dict(text='Attribute Correlation Matrix', font=dict(size=16, color='#111827')),
        plot_bgcolor='white',
        paper_bgcolor='white',
        font=dict(family='Inter', color='#6B7280'),
        margin=dict(l=40, r=40, t=60, b=40),
        xaxis=dict(tickangle=45)
    )
    
    return fig


def create_department_boxplot(df):
    """Create department performance distribution box plot."""
    if df.empty:
        fig = go.Figure()
        fig.add_annotation(text="No data available", xref="paper", yref="paper", x=0.5, y=0.5, showarrow=False)
        return fig
    
    fig = px.box(
        df,
        x='department',
        y='manager_performance_score',
        color='department',
        color_discrete_sequence=['#2F9E8F', '#145A5A', '#FBBF24', '#F97316', '#6B7280', '#0F3D3E']
    )
    
    fig.update_layout(
        title=dict(text='Manager Performance Distribution by Department', font=dict(size=16, color='#111827')),
        xaxis_title='Department',
        yaxis_title='Manager Performance Score',
        plot_bgcolor='white',
        paper_bgcolor='white',
        font=dict(family='Inter', color='#6B7280'),
        showlegend=False,
        xaxis=dict(gridcolor='#E5E7EB'),
        yaxis=dict(gridcolor='#E5E7EB'),
        margin=dict(l=40, r=40, t=60, b=40)
    )
    
    return fig


def create_underperforming_chart(df):
    """Create horizontal bar chart for underperforming managers."""
    if df.empty:
        fig = go.Figure()
        fig.add_annotation(text="No data available", xref="paper", yref="paper", x=0.5, y=0.5, showarrow=False)
        return fig
    
    manager_perf = df.groupby('manager_name')['manager_performance_score'].mean().reset_index()
    manager_perf = manager_perf.sort_values('manager_performance_score', ascending=True).head(10)
    
    colors = ['#F97316' if x < manager_perf['manager_performance_score'].quantile(0.3) else '#FBBF24' 
              if x < manager_perf['manager_performance_score'].quantile(0.6) else '#2F9E8F' 
              for x in manager_perf['manager_performance_score']]
    
    fig = go.Figure(go.Bar(
        x=manager_perf['manager_performance_score'],
        y=manager_perf['manager_name'],
        orientation='h',
        marker_color=colors,
        text=manager_perf['manager_performance_score'].round(2),
        textposition='outside'
    ))
    
    fig.update_layout(
        title=dict(text='Underperforming Managers (Bottom 10)', font=dict(size=16, color='#111827')),
        xaxis_title='Average Performance Score',
        yaxis_title='',
        plot_bgcolor='white',
        paper_bgcolor='white',
        font=dict(family='Inter', color='#6B7280'),
        xaxis=dict(gridcolor='#E5E7EB'),
        margin=dict(l=40, r=40, t=60, b=40)
    )
    
    return fig


def create_manager_ranking_table(df):
    """Create manager ranking dataframe."""
    if df.empty:
        return pd.DataFrame()
    
    ranking = df.groupby('manager_name').agg({
        'manager_performance_score': 'mean',
        'employee_performance': 'mean',
        'satisfaction_score': 'mean',
        'revenue_generated': 'sum',
        'project_success_score': 'mean',
        'attrition': lambda x: (x.str.lower() == 'yes').sum() / len(x) * 100
    }).reset_index()
    
    ranking.columns = ['Manager', 'Avg Performance', 'Avg Team Performance', 
                       'Avg Satisfaction', 'Total Revenue', 'Avg Project Success', 'Attrition Rate (%)']
    
    ranking = ranking.sort_values('Avg Performance', ascending=False)
    ranking['Rank'] = range(1, len(ranking) + 1)
    ranking = ranking[['Rank', 'Manager', 'Avg Performance', 'Avg Team Performance', 
                       'Avg Satisfaction', 'Total Revenue', 'Avg Project Success', 'Attrition Rate (%)']]
    
    # Round numeric columns
    numeric_cols = ['Avg Performance', 'Avg Team Performance', 'Avg Satisfaction', 
                    'Total Revenue', 'Avg Project Success', 'Attrition Rate (%)']
    for col in numeric_cols:
        ranking[col] = ranking[col].round(2)
    
    ranking['Manager'] = ranking['Manager'].str.title()
    
    return ranking


# Main Application
def main():
    # Load data
    df = load_data()
    
    # Sidebar
    with st.sidebar:
        st.markdown("""
        <div style="padding: 20px 0;">
            <h2 style="color: #D1FAE5; font-size: 22px; font-weight: 600; margin-bottom: 8px;">
                📊 Performance Analytics
            </h2>
            <p style="color: #9CA3AF; font-size: 13px;">
                Managerial Insights Dashboard
            </p>
        </div>
        """, unsafe_allow_html=True)
        
        st.markdown("---")
        
        # Filters
        st.markdown('<p style="color: #D1FAE5; font-weight: 600; margin-bottom: 16px;">🔍 Filters</p>', 
                    unsafe_allow_html=True)
        
        # Department filter
        departments = ['All'] + sorted(df['department'].unique().tolist())
        selected_dept = st.selectbox('Department', departments, key='dept_filter')
        
        # Manager filter
        if selected_dept == 'All':
            managers = ['All'] + sorted(df['manager_name'].str.title().unique().tolist())
        else:
            managers = ['All'] + sorted(df[df['department'] == selected_dept]['manager_name'].str.title().unique().tolist())
        
        selected_manager = st.selectbox('Manager', managers, key='manager_filter')
        
        st.markdown("---")
        
        st.markdown("""
        <div style="padding: 20px 0;">
            <p style="color: #9CA3AF; font-size: 11px; text-align: center;">
                Built with Streamlit<br>
                © 2024 Analytics Dashboard
            </p>
        </div>
        """, unsafe_allow_html=True)
    
    # Apply filters
    filtered_df = df.copy()
    
    if selected_dept != 'All':
        filtered_df = filtered_df[filtered_df['department'] == selected_dept]
    
    if selected_manager != 'All':
        filtered_df = filtered_df[filtered_df['manager_name'].str.title() == selected_manager]
    
    # Main content area
    # Header
    st.markdown("""
    <div class="main-header">
        <div style="display: flex; justify-content: space-between; align-items: center;">
            <div>
                <h1 class="main-title">Managerial Performance Dashboard</h1>
                <p class="sub-title">Comprehensive analytics for team and manager performance insights</p>
            </div>
            <div style="display: flex; align-items: center; gap: 16px;">
                <span style="color: #6B7280; font-size: 14px;">📅 Last Updated: Today</span>
            </div>
        </div>
    </div>
    """, unsafe_allow_html=True)
    
    # KPI Section
    kpis = calculate_kpis(filtered_df)
    
    col1, col2, col3, col4, col5 = st.columns(5)
    
    with col1:
        st.markdown(f"""
        <div class="kpi-card">
            <div class="kpi-icon">👥</div>
            <div class="kpi-label">Avg Employee Performance</div>
            <div class="kpi-value">{kpis['avg_employee_perf']:.2f}</div>
        </div>
        """, unsafe_allow_html=True)
    
    with col2:
        st.markdown(f"""
        <div class="kpi-card">
            <div class="kpi-icon">😊</div>
            <div class="kpi-label">Avg Satisfaction Score</div>
            <div class="kpi-value">{kpis['avg_satisfaction']:.2f}</div>
        </div>
        """, unsafe_allow_html=True)
    
    with col3:
        st.markdown(f"""
        <div class="kpi-card">
            <div class="kpi-icon">💰</div>
            <div class="kpi-label">Total Revenue</div>
            <div class="kpi-value">${kpis['total_revenue']:,.0f}</div>
        </div>
        """, unsafe_allow_html=True)
    
    with col4:
        st.markdown(f"""
        <div class="kpi-card">
            <div class="kpi-icon">📉</div>
            <div class="kpi-label">Attrition Rate</div>
            <div class="kpi-value" style="color: {'#F97316' if kpis['attrition_rate'] > 20 else '#2F9E8F'};">
                {kpis['attrition_rate']:.1f}%
            </div>
        </div>
        """, unsafe_allow_html=True)
    
    with col5:
        st.markdown(f"""
        <div class="kpi-card">
            <div class="kpi-icon">🎯</div>
            <div class="kpi-label">Avg Project Success</div>
            <div class="kpi-value">{kpis['avg_project_success']:.2f}</div>
        </div>
        """, unsafe_allow_html=True)
    
    st.markdown("<br>", unsafe_allow_html=True)
    
    # Insights Section
    st.markdown('<div class="section-header">📌 Key Business Insights</div>', unsafe_allow_html=True)
    
    insights = get_insights(filtered_df)
    
    col1, col2, col3, col4, col5 = st.columns(5)
    
    with col1:
        st.markdown(f"""
        <div class="insight-card">
            <div class="insight-label">🏆 Best Performing Manager</div>
            <div class="insight-value">{insights['best_manager']}</div>
        </div>
        """, unsafe_allow_html=True)
    
    with col2:
        st.markdown(f"""
        <div class="insight-card">
            <div class="insight-label">⚠️ Needs Improvement</div>
            <div class="insight-value">{insights['worst_manager']}</div>
        </div>
        """, unsafe_allow_html=True)
    
    with col3:
        st.markdown(f"""
        <div class="insight-card">
            <div class="insight-label">💎 Top Revenue Generator</div>
            <div class="insight-value">{insights['highest_revenue_manager']}</div>
        </div>
        """, unsafe_allow_html=True)
    
    with col4:
        st.markdown(f"""
        <div class="insight-card">
            <div class="insight-label">📊 Overall Attrition</div>
            <div class="insight-value">{insights['avg_attrition_rate']:.1f}%</div>
        </div>
        """, unsafe_allow_html=True)
    
    with col5:
        st.markdown(f"""
        <div class="insight-card">
            <div class="insight-label">🔑 Key Success Factor</div>
            <div class="insight-value">{insights['most_impactful_feature']}</div>
        </div>
        """, unsafe_allow_html=True)
    
    st.markdown("<br>", unsafe_allow_html=True)
    
    # Charts Section
    st.markdown('<div class="section-header">📈 Performance Analytics</div>', unsafe_allow_html=True)
    
    # Row 1: Performance vs Productivity & Performance vs Satisfaction
    col1, col2 = st.columns(2)
    
    with col1:
        st.markdown('<div class="chart-container">', unsafe_allow_html=True)
        fig1 = create_scatter_with_trendline(
            filtered_df, 
            'manager_performance_score', 
            'employee_performance',
            'Manager Performance vs Team Productivity',
            'Manager Performance Score',
            'Employee Performance'
        )
        st.plotly_chart(fig1, use_container_width=True)
        st.markdown('</div>', unsafe_allow_html=True)
    
    with col2:
        st.markdown('<div class="chart-container">', unsafe_allow_html=True)
        fig2 = create_scatter_with_trendline(
            filtered_df,
            'manager_performance_score',
            'satisfaction_score',
            'Manager Performance vs Employee Satisfaction',
            'Manager Performance Score',
            'Satisfaction Score'
        )
        st.plotly_chart(fig2, use_container_width=True)
        st.markdown('</div>', unsafe_allow_html=True)
    
    # Row 2: Attrition & Correlation Heatmap
    col1, col2 = st.columns(2)
    
    with col1:
        st.markdown('<div class="chart-container">', unsafe_allow_html=True)
        fig3 = create_attrition_bar_chart(filtered_df)
        st.plotly_chart(fig3, use_container_width=True)
        st.markdown('</div>', unsafe_allow_html=True)
    
    with col2:
        st.markdown('<div class="chart-container">', unsafe_allow_html=True)
        fig4 = create_correlation_heatmap(filtered_df)
        st.plotly_chart(fig4, use_container_width=True)
        st.markdown('</div>', unsafe_allow_html=True)
    
    # Row 3: Department Distribution & Underperforming Managers
    col1, col2 = st.columns(2)
    
    with col1:
        st.markdown('<div class="chart-container">', unsafe_allow_html=True)
        fig5 = create_department_boxplot(filtered_df)
        st.plotly_chart(fig5, use_container_width=True)
        st.markdown('</div>', unsafe_allow_html=True)
    
    with col2:
        st.markdown('<div class="chart-container">', unsafe_allow_html=True)
        fig6 = create_underperforming_chart(filtered_df)
        st.plotly_chart(fig6, use_container_width=True)
        st.markdown('</div>', unsafe_allow_html=True)
    
    # Row 4: Business Impact - Revenue & Project Success
    st.markdown('<div class="section-header">💼 Business Impact Analysis</div>', unsafe_allow_html=True)
    
    col1, col2 = st.columns(2)
    
    with col1:
        st.markdown('<div class="chart-container">', unsafe_allow_html=True)
        fig7 = create_scatter_with_trendline(
            filtered_df,
            'manager_performance_score',
            'revenue_generated',
            'Manager Performance vs Revenue Generated',
            'Manager Performance Score',
            'Revenue Generated ($)'
        )
        st.plotly_chart(fig7, use_container_width=True)
        st.markdown('</div>', unsafe_allow_html=True)
    
    with col2:
        st.markdown('<div class="chart-container">', unsafe_allow_html=True)
        fig8 = create_scatter_with_trendline(
            filtered_df,
            'manager_performance_score',
            'project_success_score',
            'Manager Performance vs Project Success',
            'Manager Performance Score',
            'Project Success Score'
        )
        st.plotly_chart(fig8, use_container_width=True)
        st.markdown('</div>', unsafe_allow_html=True)
    
    # Manager Ranking Table
    st.markdown('<div class="section-header">🏅 Manager Rankings</div>', unsafe_allow_html=True)
    
    ranking_df = create_manager_ranking_table(filtered_df)
    
    if not ranking_df.empty:
        st.markdown('<div class="chart-container">', unsafe_allow_html=True)
        st.dataframe(
            ranking_df,
            use_container_width=True,
            hide_index=True,
            column_config={
                "Rank": st.column_config.NumberColumn("Rank", width="small"),
                "Manager": st.column_config.TextColumn("Manager", width="medium"),
                "Avg Performance": st.column_config.NumberColumn("Avg Performance", format="%.2f"),
                "Avg Team Performance": st.column_config.NumberColumn("Team Perf", format="%.2f"),
                "Avg Satisfaction": st.column_config.NumberColumn("Satisfaction", format="%.2f"),
                "Total Revenue": st.column_config.NumberColumn("Revenue", format="$%.0f"),
                "Avg Project Success": st.column_config.NumberColumn("Project Success", format="%.2f"),
                "Attrition Rate (%)": st.column_config.NumberColumn("Attrition %", format="%.1f%%")
            }
        )
        st.markdown('</div>', unsafe_allow_html=True)
    else:
        st.info("No data available for the selected filters.")
    
    # Filtered Dataset Preview
    st.markdown('<div class="section-header">📋 Filtered Dataset Preview</div>', unsafe_allow_html=True)
    
    st.markdown('<div class="chart-container">', unsafe_allow_html=True)
    
    display_df = filtered_df.copy()
    display_df['manager_name'] = display_df['manager_name'].str.title()
    display_df['department'] = display_df['department'].str.title()
    
    st.dataframe(
        display_df.head(50),
        use_container_width=True,
        hide_index=True
    )
    
    st.markdown(f"<p style='color: #6B7280; font-size: 13px; margin-top: 8px;'>Showing {min(50, len(filtered_df))} of {len(filtered_df)} records</p>", unsafe_allow_html=True)
    st.markdown('</div>', unsafe_allow_html=True)


if __name__ == "__main__":
    main()
