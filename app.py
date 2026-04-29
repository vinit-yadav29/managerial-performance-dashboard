import streamlit as st
import pandas as pd
import numpy as np
import plotly.express as px
import plotly.graph_objects as go
from scipy import stats

st.set_page_config(page_title="Managerial Performance Analytics", layout="wide", initial_sidebar_state="expanded")

st.markdown("""<style>
@import url('https://fonts.googleapis.com/css2?family=Inter:wght@400;500;600;700&display=swap');
.stApp{background:#F0F4F8;font-family:'Inter',sans-serif;}
[data-testid="stSidebar"]{background:linear-gradient(180deg,#0F3D3E,#145A5A);border-radius:0 20px 20px 0;}
[data-testid="stSidebar"] .stMarkdown,[data-testid="stSidebar"] label{color:#ECFDF5 !important;font-weight:500;}
[data-testid="stSidebar"] .stSelectbox>div>div{background:rgba(255,255,255,0.1);border:1px solid rgba(255,255,255,0.3);border-radius:8px;}
[data-testid="stSidebar"] .stSlider>div{color:#ECFDF5;}
[data-testid="stSidebar"] .stToggle label{color:#ECFDF5 !important;}
.card{background:white;border-radius:16px;padding:20px;box-shadow:0 2px 12px rgba(0,0,0,0.07);margin-bottom:20px;}
.kpi-label{font-size:12px;color:#374151;font-weight:600;margin-bottom:4px;}
.kpi-value{font-size:26px;font-weight:700;color:#111827;}
.kpi-sub{font-size:11px;color:#6B7280;margin-top:2px;}
.section-header{font-size:18px;font-weight:700;color:#111827;margin:28px 0 6px;padding-bottom:8px;border-bottom:2px solid #D1FAE5;}
.bq{font-size:12px;color:#374151;font-style:italic;margin-bottom:14px;}
.insight-box{background:#F0FDF4;border-left:4px solid #059669;border-radius:0 10px 10px 0;padding:12px 16px;margin-top:8px;margin-bottom:4px;}
.insight-box p{margin:0;font-size:13px;color:#064E3B;line-height:1.6;}
.insight-box strong{color:#047857;}
.control-badge{display:inline-block;background:#D1FAE5;color:#065F46;font-size:11px;font-weight:600;padding:3px 10px;border-radius:20px;margin-bottom:8px;}
.main-title{font-size:24px;font-weight:700;color:#0F3D3E !important;margin:0;}
.sub-title{font-size:13px;color:#4B5563 !important;margin-top:4px;}
#MainMenu,footer{visibility:hidden;}
</style>""", unsafe_allow_html=True)

FONT = dict(family='Inter', color='#1F2937', size=12)
AXIS = dict(tickfont=dict(color='#1F2937',size=11), title_font=dict(color='#1F2937',size=12), gridcolor='#E5E7EB', zerolinecolor='#E5E7EB')
PAL  = ['#0F3D3E','#2F9E8F','#145A5A','#D97706','#DC2626','#4B5563','#059669','#7C3AED']
HIGHLIGHT_COLOR = '#D97706'   # gold — used when highlight mode is ON for top performers
TOP_COLOR       = '#2F9E8F'   # teal — default bar color


def bl(title, legend=False):
    return dict(title=dict(text=title,font=dict(size=14,color='#111827',family='Inter')),
                plot_bgcolor='white', paper_bgcolor='white', font=FONT,
                margin=dict(l=40,r=40,t=52,b=40), showlegend=legend,
                legend=dict(font=dict(color='#1F2937',size=11)) if legend else {})

def ef():
    f=go.Figure(); f.add_annotation(text="No data",xref="paper",yref="paper",x=0.5,y=0.5,showarrow=False); return f


# ── Data ─────────────────────────────────────────────────────────────────────
@st.cache_data
def load_data():
    df = pd.read_csv("data/processed/MPIA_EDA_READY2.csv")
    df['manager_name'] = df['manager_name'].astype(str).str.strip().str.lower()
    df['department']   = df['department'].astype(str).str.strip().str.lower()
    df['attrition']    = df['attrition'].astype(str).str.lower()
    for c in ['manager_experience','leadership_score','communication_score','manager_performance_score',
              'employee_performance','satisfaction_score','project_success_score','revenue_generated']:
        df[c] = pd.to_numeric(df[c], errors='coerce')
    return df.dropna(subset=['manager_name','department'])


# ── Helpers ───────────────────────────────────────────────────────────────────
def insight(text):
    st.markdown(f'<div class="insight-box"><p>{text}</p></div>', unsafe_allow_html=True)

def hex_to_rgba(hex_color, alpha=0.15):
    hex_color = hex_color.lstrip('#')
    r,g,b = int(hex_color[0:2],16), int(hex_color[2:4],16), int(hex_color[4:6],16)
    return f'rgba({r},{g},{b},{alpha})'

def bar_colors(values, highlight, threshold_pct=0.75):
    """Return a list of colors. If highlight=True, gold for top quartile, else uniform teal."""
    if not highlight:
        return [TOP_COLOR] * len(values)
    thresh = np.quantile(values, threshold_pct)
    return [HIGHLIGHT_COLOR if v >= thresh else TOP_COLOR for v in values]

def add_top_annotation(fig, x_vals, y_vals, highlight, label="Top Performer", is_horizontal=False):
    """Annotate the single best bar when highlight mode is on."""
    if not highlight or len(y_vals) == 0:
        return
    if is_horizontal:
        idx = int(np.argmax(x_vals))
        fig.add_annotation(x=x_vals[idx], y=y_vals[idx],
                           text=f"⭐ {label}", showarrow=True, arrowhead=2,
                           arrowcolor=HIGHLIGHT_COLOR, font=dict(color=HIGHLIGHT_COLOR,size=11,family='Inter'),
                           xshift=10, ax=40, ay=0)
    else:
        idx = int(np.argmax(y_vals))
        fig.add_annotation(x=x_vals[idx], y=y_vals[idx],
                           text=f"⭐ {label}", showarrow=True, arrowhead=2,
                           arrowcolor=HIGHLIGHT_COLOR, font=dict(color=HIGHLIGHT_COLOR,size=11,family='Inter'),
                           yshift=10, ax=0, ay=-36)


# ── Q1 ────────────────────────────────────────────────────────────────────────
def q1_charts(df, top_n, highlight):
    if df.empty: return ef(), ef()
    fig1 = px.scatter(df, x='manager_performance_score', y='employee_performance',
                      trendline='ols', color_discrete_sequence=['#2F9E8F'], opacity=0.65,
                      hover_data=['manager_name'] if 'manager_name' in df.columns else None)
    fig1.update_traces(marker=dict(size=8, line=dict(width=1,color='white')))
    if highlight:
        thresh = df['manager_performance_score'].quantile(0.75)
        top_df = df[df['manager_performance_score'] >= thresh]
        fig1.add_trace(go.Scatter(x=top_df['manager_performance_score'], y=top_df['employee_performance'],
                                  mode='markers', marker=dict(size=11, color=HIGHLIGHT_COLOR,
                                  symbol='star', line=dict(width=1,color='white')),
                                  name='Top Performers', showlegend=True))
    fig1.update_layout(**bl('Manager Performance vs Employee Output', legend=highlight),
                       xaxis=dict(**AXIS,title='Manager Performance Score'),
                       yaxis=dict(**AXIS,title='Employee Performance'))

    mg = df.groupby('manager_name').agg(mgr_perf=('manager_performance_score','mean'),
                                         emp_perf=('employee_performance','mean')).reset_index()
    mg = mg.sort_values('emp_perf', ascending=False).head(top_n)
    mg['manager_name'] = mg['manager_name'].str.title()
    colors = bar_colors(mg['emp_perf'].values, highlight)
    fig2 = go.Figure()
    fig2.add_trace(go.Bar(name='Team Output', x=mg['manager_name'], y=mg['emp_perf'],
                          marker_color=colors, text=mg['emp_perf'].round(2), textposition='outside',
                          textfont=dict(color='#111827',size=11)))
    fig2.add_trace(go.Scatter(name='Mgr Performance', x=mg['manager_name'], y=mg['mgr_perf'],
                              mode='lines+markers', line=dict(color='#0F3D3E',width=2),
                              marker=dict(size=7,color='#0F3D3E')))
    add_top_annotation(fig2, mg['manager_name'].values, mg['emp_perf'].values, highlight, "Best Team Output")
    fig2.update_layout(**bl(f'Top {top_n} Managers: Team Output vs Their Score', legend=True),
                       xaxis=dict(**AXIS,title='',tickangle=30),
                       yaxis=dict(**AXIS,title='Score'))
    return fig1, fig2

def q1_insight(df):
    if df.empty: return
    r, p = stats.pearsonr(df['manager_performance_score'].dropna(), df['employee_performance'].dropna())
    top = df.groupby('manager_name')['employee_performance'].mean().idxmax()
    insight(f"<strong>Productivity Link:</strong> Manager performance and team output have a Pearson correlation of "
            f"<strong>r = {r:.2f}</strong> (p {'< 0.001' if p<0.001 else f'= {p:.3f}'}) — "
            f"{'a strong positive' if r>0.5 else 'a moderate' if r>0.3 else 'a weak'} relationship. "
            f"Manager <strong>{top.title()}</strong> drives the highest average team output.")


# ── Q2 ────────────────────────────────────────────────────────────────────────
def q2_charts(df, top_n, highlight):
    if df.empty: return ef(), ef()
    fig1 = px.scatter(df, x='manager_performance_score', y='satisfaction_score',
                      trendline='ols', color='department',
                      color_discrete_sequence=PAL, opacity=0.7)
    if highlight:
        thresh = df['manager_performance_score'].quantile(0.75)
        top_df = df[df['manager_performance_score'] >= thresh]
        fig1.add_trace(go.Scatter(x=top_df['manager_performance_score'], y=top_df['satisfaction_score'],
                                  mode='markers', marker=dict(size=11, color=HIGHLIGHT_COLOR,
                                  symbol='star', line=dict(width=1,color='white')), name='Top Performers'))
    fig1.update_traces(marker=dict(size=8, line=dict(width=1,color='white')), selector=dict(type='scatter', mode='markers'))
    fig1.update_layout(**bl('Manager Performance vs Satisfaction (by Dept)', legend=True),
                       xaxis=dict(**AXIS,title='Manager Performance Score'),
                       yaxis=dict(**AXIS,title='Satisfaction Score'))

    d = df.copy()
    d['perf_tier'] = pd.cut(d['manager_performance_score'],
                             bins=[0, d['manager_performance_score'].quantile(0.33),
                                      d['manager_performance_score'].quantile(0.66),
                                      d['manager_performance_score'].max()+1],
                             labels=['Low Performer','Mid Performer','High Performer'])
    sat = d.groupby('perf_tier', observed=True)['satisfaction_score'].mean().reset_index()
    tier_colors = ['#DC2626','#D97706','#059669']
    if highlight:
        tier_colors = ['#DC2626','#D97706', HIGHLIGHT_COLOR]
    fig2 = px.bar(sat, x='perf_tier', y='satisfaction_score',
                  color='perf_tier', color_discrete_sequence=tier_colors,
                  text=sat['satisfaction_score'].round(2))
    fig2.update_traces(textposition='outside', textfont=dict(color='#111827',size=12))
    fig2.update_layout(**bl('Avg Satisfaction by Manager Performance Tier'),
                       xaxis=dict(**AXIS,title='Manager Tier'),
                       yaxis=dict(**AXIS,title='Avg Satisfaction Score'))
    return fig1, fig2

def q2_insight(df):
    if df.empty: return
    r, p = stats.pearsonr(df['manager_performance_score'].dropna(), df['satisfaction_score'].dropna())
    d = df.copy()
    d['tier'] = pd.qcut(d['manager_performance_score'], 3, labels=['Low','Mid','High'])
    sat = d.groupby('tier', observed=True)['satisfaction_score'].mean()
    diff = sat.get('High', 0) - sat.get('Low', 0)
    insight(f"<strong>Satisfaction Driver:</strong> Correlation between manager effectiveness and satisfaction is "
            f"<strong>r = {r:.2f}</strong>. Employees under <strong>high-performing managers score "
            f"{diff:+.2f} points higher</strong> in satisfaction than those under low performers.")


# ── Q3 ────────────────────────────────────────────────────────────────────────
def q3_charts(df, top_n, highlight):
    if df.empty: return ef(), ef()
    att = (df.groupby('manager_name')
             .apply(lambda x: pd.Series({'att_rate':(x['attrition']=='yes').sum()/len(x)*100,
                                          'mgr_perf':x['manager_performance_score'].mean()}),
                    include_groups=False)
             .reset_index())
    fig1 = px.scatter(att, x='mgr_perf', y='att_rate', trendline='ols',
                      color_discrete_sequence=['#DC2626'], opacity=0.75,
                      hover_data=['manager_name'])
    if highlight:
        top_perf = att[att['mgr_perf'] >= att['mgr_perf'].quantile(0.75)]
        fig1.add_trace(go.Scatter(x=top_perf['mgr_perf'], y=top_perf['att_rate'],
                                  mode='markers', marker=dict(size=11, color=HIGHLIGHT_COLOR,
                                  symbol='star', line=dict(width=1,color='white')), name='Top Performers'))
    fig1.update_traces(marker=dict(size=9, line=dict(width=1,color='white')), selector=dict(mode='markers'))
    fig1.update_layout(**bl('Manager Performance vs Team Attrition Rate', legend=highlight),
                       xaxis=dict(**AXIS,title='Avg Manager Performance Score'),
                       yaxis=dict(**AXIS,title='Attrition Rate (%)'))

    top_att = att.sort_values('att_rate', ascending=False).head(top_n).copy()
    top_att['manager_name'] = top_att['manager_name'].str.title()
    colors = ['#DC2626'] * len(top_att)
    if highlight:
        # Colour the lowest-attrition managers in gold to mark them as "best managed"
        min_idx = top_att['att_rate'].idxmin()
        colors = ['#DC2626' if i != min_idx else HIGHLIGHT_COLOR for i in top_att.index]
    fig2 = px.bar(top_att, x='att_rate', y='manager_name', orientation='h',
                  color='att_rate', color_continuous_scale=['#FEF3C7','#DC2626'],
                  text=top_att['att_rate'].round(1))
    fig2.update_traces(texttemplate='%{text}%', textposition='outside', textfont=dict(color='#111827',size=11))
    fig2.update_layout(**bl(f'Top {top_n} Managers by Team Attrition Rate'), coloraxis_showscale=False,
                       xaxis=dict(**AXIS,title='Attrition Rate (%)'),
                       yaxis=dict(tickfont=dict(color='#1F2937',size=11)))
    return fig1, fig2

def q3_insight(df):
    if df.empty: return
    att = (df.groupby('manager_name')
             .apply(lambda x: pd.Series({'att':(x['attrition']=='yes').sum()/len(x)*100,
                                          'perf':x['manager_performance_score'].mean()}),
                    include_groups=False).reset_index())
    r, _ = stats.pearsonr(att['perf'], att['att'])
    worst = att.sort_values('att', ascending=False).iloc[0]
    insight(f"<strong>Attrition Risk:</strong> Manager performance and team attrition show a correlation of "
            f"<strong>r = {r:.2f}</strong>. "
            f"Manager <strong>{worst['manager_name'].title()}</strong> has the highest attrition at "
            f"<strong>{worst['att']:.1f}%</strong> and should be prioritised for coaching or workload review.")


# ── Q4 ────────────────────────────────────────────────────────────────────────
def q4_charts(df, top_n, highlight):
    if df.empty: return ef(), ef()
    attrs = ['leadership_score','communication_score','manager_experience']
    targets = ['manager_performance_score','employee_performance','satisfaction_score','project_success_score']
    corr_data = []
    for a in attrs:
        for t in targets:
            r, _ = stats.pearsonr(df[a].dropna(), df[t].dropna())
            corr_data.append({'Attribute': a.replace('_score','').replace('_',' ').title(),
                               'Outcome': t.replace('_score','').replace('_',' ').title(), 'r': round(r,2)})
    cdf = pd.DataFrame(corr_data)

    colors = PAL[:len(cdf['Outcome'].unique())]
    fig1 = px.bar(cdf, x='Attribute', y='r', color='Outcome', barmode='group',
                  color_discrete_sequence=colors, text='r')
    if highlight:
        # Mark bars above 0.5 with a shape
        max_r = cdf.loc[cdf['r'].idxmax()]
        fig1.add_annotation(x=max_r['Attribute'], y=max_r['r'],
                            text=f"⭐ Strongest: {max_r['r']}", showarrow=True, arrowhead=2,
                            arrowcolor=HIGHLIGHT_COLOR, font=dict(color=HIGHLIGHT_COLOR,size=11,family='Inter'),
                            yshift=10, ax=0, ay=-36)
    fig1.update_traces(textposition='outside', textfont=dict(color='#111827',size=10))
    fig1.update_layout(**bl('Attribute Impact on Key Outcomes (Pearson r)', legend=True),
                       xaxis=dict(**AXIS,title='Managerial Attribute'),
                       yaxis=dict(**AXIS,title='Correlation (r)'))

    q_high = df[df['manager_performance_score'] >= df['manager_performance_score'].quantile(0.75)]
    q_low  = df[df['manager_performance_score'] <= df['manager_performance_score'].quantile(0.25)]
    cats   = ['Leadership Score','Communication Score','Manager Experience']
    high_v = [q_high['leadership_score'].mean(), q_high['communication_score'].mean(), q_high['manager_experience'].mean()]
    low_v  = [q_low['leadership_score'].mean(),  q_low['communication_score'].mean(),  q_low['manager_experience'].mean()]
    fig2   = go.Figure()
    high_col = HIGHLIGHT_COLOR if highlight else '#059669'
    for name, vals, col in [('Top Quartile', high_v, high_col),('Bottom Quartile', low_v,'#DC2626')]:
        fig2.add_trace(go.Scatterpolar(r=vals+[vals[0]], theta=cats+[cats[0]], fill='toself',
                                       name=name, line=dict(color=col,width=2), fillcolor=hex_to_rgba(col)))
    fig2.update_layout(**bl('Attribute Profile: Top vs Bottom Quartile Managers', legend=True),
                       polar=dict(radialaxis=dict(visible=True, tickfont=dict(color='#1F2937',size=10))))
    return fig1, fig2

def q4_insight(df):
    if df.empty: return
    attrs = {'leadership_score':'Leadership','communication_score':'Communication','manager_experience':'Experience'}
    corrs = {v: abs(stats.pearsonr(df[k].dropna(), df['manager_performance_score'].dropna())[0])
             for k,v in attrs.items()}
    top_attr = max(corrs, key=corrs.get)
    insight(f"<strong>Key Success Driver:</strong> Among all managerial attributes, "
            f"<strong>{top_attr}</strong> has the strongest correlation "
            f"(r = {corrs[top_attr]:.2f}) with overall manager performance.")


# ── Q5 ────────────────────────────────────────────────────────────────────────
def q5_charts(df, top_n, highlight):
    if df.empty: return ef(), ef()
    fig1 = px.box(df, x='department', y='manager_performance_score', color='department',
                  color_discrete_sequence=PAL, points='outliers')
    fig1.update_layout(**bl('Manager Performance Distribution by Department'),
                       xaxis=dict(**AXIS,title='Department'),
                       yaxis=dict(**AXIS,title='Manager Performance Score'))

    dept = df.groupby('department').agg(
        perf=('manager_performance_score','mean'),
        sat=('satisfaction_score','mean'),
        att=('attrition',lambda x:(x=='yes').sum()/len(x)*100),
        rev=('revenue_generated','sum')).reset_index()
    dept['department'] = dept['department'].str.title()

    perf_colors = [HIGHLIGHT_COLOR if highlight and v == dept['perf'].max() else '#0F3D3E' for v in dept['perf']]
    fig2 = go.Figure()
    fig2.add_trace(go.Bar(name='Avg Mgr Perf', x=dept['department'], y=dept['perf'],
                          marker_color=perf_colors, text=dept['perf'].round(1),
                          textposition='outside', textfont=dict(color='#111827',size=10)))
    fig2.add_trace(go.Bar(name='Avg Satisfaction', x=dept['department'], y=dept['sat'],
                          marker_color='#2F9E8F', text=dept['sat'].round(1),
                          textposition='outside', textfont=dict(color='#111827',size=10)))
    fig2.add_trace(go.Bar(name='Attrition %', x=dept['department'], y=dept['att'],
                          marker_color='#DC2626', text=dept['att'].round(1),
                          textposition='outside', textfont=dict(color='#111827',size=10)))
    fig2.update_layout(**bl('Department Scorecard: Performance, Satisfaction & Attrition', legend=True),
                       barmode='group', xaxis=dict(**AXIS,title=''), yaxis=dict(**AXIS,title='Score / Rate'))
    return fig1, fig2

def q5_insight(df):
    if df.empty: return
    dept = df.groupby('department')['manager_performance_score'].mean()
    best_d, worst_d = dept.idxmax(), dept.idxmin()
    gap = dept.max() - dept.min()
    insight(f"<strong>Department Gaps:</strong> <strong>{best_d.title()}</strong> leads with an avg manager performance "
            f"of <strong>{dept.max():.2f}</strong>, while <strong>{worst_d.title()}</strong> trails at "
            f"<strong>{dept.min():.2f}</strong> — a gap of <strong>{gap:.2f} points</strong>.")


# ── Q6 ────────────────────────────────────────────────────────────────────────
def q6_charts(df, top_n, highlight):
    if df.empty: return ef(), ef()
    mg = df.groupby('manager_name').agg(
        perf=('manager_performance_score','mean'),
        lead=('leadership_score','mean'),
        comm=('communication_score','mean'),
        att=('attrition',lambda x:(x=='yes').sum()/len(x)*100),
        sat=('satisfaction_score','mean')).reset_index()
    mg['risk_score'] = (mg['att']/mg['att'].max()*0.4 +
                        (1 - mg['perf']/mg['perf'].max())*0.35 +
                        (1 - mg['sat']/mg['sat'].max())*0.25)
    mg = mg.sort_values('risk_score', ascending=False)
    top_risk = mg.head(top_n).copy()
    top_risk['manager_name'] = top_risk['manager_name'].str.title()
    colors = ['#DC2626' if r>0.6 else '#D97706' if r>0.4 else '#2F9E8F' for r in top_risk['risk_score']]
    fig1 = go.Figure(go.Bar(x=top_risk['risk_score'], y=top_risk['manager_name'],
                             orientation='h', marker_color=colors,
                             text=top_risk['risk_score'].round(2), textposition='outside',
                             textfont=dict(color='#111827',size=11)))
    if highlight:
        worst = top_risk.iloc[0]
        fig1.add_annotation(x=worst['risk_score'], y=worst['manager_name'],
                            text="⚠ Highest Risk", showarrow=True, arrowhead=2,
                            arrowcolor='#DC2626', font=dict(color='#DC2626',size=11,family='Inter'),
                            xshift=8, ax=50, ay=0)
    fig1.update_layout(**bl(f'Top {top_n} Manager Risk Scores (attrition + perf + satisfaction)'),
                       xaxis=dict(**AXIS,title='Composite Risk Score (0–1)'),
                       yaxis=dict(tickfont=dict(color='#1F2937',size=11), autorange='reversed'))

    tc = df.groupby('manager_name').size().rename('team_size').reset_index()
    mg2 = mg.merge(tc, on='manager_name')
    mg2['manager_name'] = mg2['manager_name'].str.title()
    fig2 = px.scatter(mg2, x='perf', y='att', size='team_size', color='risk_score',
                      color_continuous_scale=['#059669','#D97706','#DC2626'],
                      hover_name='manager_name', size_max=40,
                      labels={'perf':'Avg Manager Performance','att':'Attrition Rate (%)','risk_score':'Risk'})
    if highlight:
        safest = mg2.loc[mg2['risk_score'].idxmin()]
        fig2.add_annotation(x=safest['perf'], y=safest['att'],
                            text=f"⭐ Safest: {safest['manager_name']}", showarrow=True, arrowhead=2,
                            arrowcolor=HIGHLIGHT_COLOR, font=dict(color=HIGHLIGHT_COLOR,size=11,family='Inter'),
                            ax=40, ay=-30)
    fig2.update_layout(**bl('Risk Landscape: Performance vs Attrition (bubble = team size)'),
                       xaxis=dict(**AXIS,title='Avg Manager Performance'),
                       yaxis=dict(**AXIS,title='Attrition Rate (%)'))
    return fig1, fig2

def q6_insight(df):
    if df.empty: return
    mg = df.groupby('manager_name').agg(
        perf=('manager_performance_score','mean'),
        att=('attrition',lambda x:(x=='yes').sum()/len(x)*100),
        sat=('satisfaction_score','mean')).reset_index()
    mg['risk'] = (mg['att']/mg['att'].max()*0.4 +
                  (1-mg['perf']/mg['perf'].max())*0.35 +
                  (1-mg['sat']/mg['sat'].max())*0.25)
    high_risk = (mg['risk'] > 0.5).sum()
    worst = mg.sort_values('risk',ascending=False).iloc[0]
    insight(f"<strong>Early Warning System:</strong> A composite risk score flags <strong>{high_risk} managers</strong> "
            f"as high-risk (score > 0.5). <strong>{worst['manager_name'].title()}</strong> is the highest-risk manager "
            f"with a score of <strong>{worst['risk']:.2f}</strong>.")


# ── Q7 ────────────────────────────────────────────────────────────────────────
def q7_charts(df, top_n, highlight):
    if df.empty: return ef(), ef()
    fig1 = px.scatter(df, x='manager_performance_score', y='revenue_generated',
                      trendline='ols', size='project_success_score',
                      color='department', color_discrete_sequence=PAL, opacity=0.7, size_max=18,
                      labels={'manager_performance_score':'Manager Performance','revenue_generated':'Revenue ($)'})
    if highlight:
        top_rev_df = df[df['revenue_generated'] >= df['revenue_generated'].quantile(0.85)]
        fig1.add_trace(go.Scatter(x=top_rev_df['manager_performance_score'], y=top_rev_df['revenue_generated'],
                                  mode='markers', marker=dict(size=13, color=HIGHLIGHT_COLOR, symbol='star',
                                  line=dict(width=1,color='white')), name='Top Revenue'))
    fig1.update_layout(**bl('Performance vs Revenue (bubble = project success)', legend=True),
                       xaxis=dict(**AXIS,title='Manager Performance Score'),
                       yaxis=dict(**AXIS,title='Revenue Generated ($)'))

    mg = df.groupby('manager_name').agg(
        perf=('manager_performance_score','mean'),
        rev=('revenue_generated','sum'),
        proj=('project_success_score','mean')).reset_index()
    top10 = mg.sort_values('rev', ascending=False).head(top_n)
    top10['manager_name'] = top10['manager_name'].str.title()
    rev_colors = [HIGHLIGHT_COLOR if highlight and i == 0 else '#0F3D3E' for i in range(len(top10))]
    fig2 = go.Figure()
    fig2.add_trace(go.Bar(name='Revenue ($)', x=top10['manager_name'], y=top10['rev'],
                          marker_color=rev_colors,
                          text=(top10['rev']/1000).round(0).astype(int),
                          texttemplate='$%{text}K', textposition='outside',
                          textfont=dict(color='#111827',size=10), yaxis='y1'))
    fig2.add_trace(go.Scatter(name='Project Success', x=top10['manager_name'], y=top10['proj'],
                              mode='lines+markers', line=dict(color='#2F9E8F',width=2),
                              marker=dict(size=7), yaxis='y2'))
    fig2.update_layout(**bl(f'Top {top_n} Revenue Managers: Revenue & Project Success', legend=True),
                       yaxis=dict(**AXIS, title='Revenue ($)'),
                       yaxis2=dict(title='Project Success Score', overlaying='y', side='right',
                                   tickfont=dict(color='#2F9E8F',size=11), title_font=dict(color='#2F9E8F',size=12)),
                       xaxis=dict(**AXIS,title='',tickangle=30))
    return fig1, fig2

def q7_insight(df):
    if df.empty: return
    r_rev, _  = stats.pearsonr(df['manager_performance_score'].dropna(), df['revenue_generated'].dropna())
    r_proj, _ = stats.pearsonr(df['manager_performance_score'].dropna(), df['project_success_score'].dropna())
    top_rev = df.groupby('manager_name')['revenue_generated'].sum().idxmax()
    insight(f"<strong>Business Impact:</strong> Manager performance correlates <strong>r = {r_rev:.2f}</strong> with "
            f"revenue and <strong>r = {r_proj:.2f}</strong> with project success. "
            f"<strong>{top_rev.title()}</strong> is the top revenue generator.")


# ── Main ──────────────────────────────────────────────────────────────────────
def main():
    df = load_data()

    with st.sidebar:
        st.markdown('<div style="padding:14px 0"><h2 style="color:#ECFDF5;font-size:19px;font-weight:700;margin:0">'
                    'Performance Analytics</h2><p style="color:#D1FAE5;font-size:12px;margin-top:4px">'
                    'Managerial Insights Dashboard</p></div>', unsafe_allow_html=True)
        st.markdown("---")
        st.markdown('<p style="color:#ECFDF5;font-weight:600;margin-bottom:10px">Filters</p>', unsafe_allow_html=True)

        # Department filter (unchanged)
        sel_dept = st.selectbox('Department', ['All'] + sorted(df['department'].unique().tolist()))

        st.markdown("---")
        st.markdown('<p style="color:#ECFDF5;font-weight:600;margin-bottom:10px">Chart Controls</p>', unsafe_allow_html=True)

        # ── NEW: Top-N slider ────────────────────────────────────────────────
        top_n = st.slider(
            'Top Managers to Display',
            min_value=5, max_value=20, value=10, step=1,
            help="Controls how many top managers appear in ranking charts across all questions."
        )

        st.markdown('<p style="color:#D1FAE5;font-size:11px;margin-top:4px;margin-bottom:12px">'
                    'Applies to all ranking charts</p>', unsafe_allow_html=True)

        # ── NEW: Highlight toggle ────────────────────────────────────────────
        highlight = st.toggle(
            '⭐  Highlight Top Performers',
            value=False,
            help="Emphasises top-quartile managers with gold markers and annotations across all charts."
        )
        if highlight:
            st.markdown('<p style="color:#FCD34D;font-size:11px;margin-top:4px">'
                        'Gold stars mark top-quartile performers</p>', unsafe_allow_html=True)

        st.markdown("---")
        st.markdown('<p style="color:#D1FAE5;font-size:11px;text-align:center">© 2024 Analytics Dashboard</p>',
                    unsafe_allow_html=True)

    # Apply department filter
    fdf = df.copy()
    if sel_dept != 'All':
        fdf = fdf[fdf['department'] == sel_dept]

    # ── Header ────────────────────────────────────────────────────────────────
    hl_badge = ('<span style="background:#FEF3C7;color:#92400E;font-size:11px;font-weight:600;'
                'padding:3px 10px;border-radius:20px;margin-left:10px">⭐ Highlight ON</span>'
                if highlight else '')
    st.markdown(f'<div class="card" style="margin-bottom:20px">'
                f'<div style="display:flex;justify-content:space-between;align-items:center">'
                f'<div><h1 class="main-title">Managerial Performance Analytics Dashboard{hl_badge}</h1>'
                f'<p class="sub-title">Answering 7 key business questions about manager effectiveness and organisational impact</p></div>'
                f'<div style="text-align:right">'
                f'<span style="color:#374151;font-size:12px">Records: <strong>{len(fdf):,}</strong></span><br>'
                f'<span style="color:#6B7280;font-size:11px">Showing Top {top_n} in ranking charts</span>'
                f'</div></div></div>', unsafe_allow_html=True)

    # ── KPIs ──────────────────────────────────────────────────────────────────
    k = dict(emp=fdf['employee_performance'].mean(), sat=fdf['satisfaction_score'].mean(),
             rev=fdf['revenue_generated'].sum(),
             att=(fdf['attrition']=='yes').sum()/max(len(fdf),1)*100,
             proj=fdf['project_success_score'].mean(),
             mgr=fdf['manager_performance_score'].mean())
    kpi_items = [("Avg Manager Score",f"{k['mgr']:.2f}","vs team benchmark",None),
                 ("Avg Employee Output",f"{k['emp']:.2f}","team productivity",None),
                 ("Avg Satisfaction",f"{k['sat']:.2f}","employee sentiment",None),
                 ("Attrition Rate",f"{k['att']:.1f}%","flight risk",('#DC2626' if k['att']>20 else '#059669')),
                 ("Avg Project Success",f"{k['proj']:.2f}","delivery quality",None),
                 ("Total Revenue",f"${k['rev']/1e6:.1f}M","business output",None)]
    for col,(label,val,sub,color) in zip(st.columns(6), kpi_items):
        col.markdown(f'<div class="card"><div class="kpi-label">{label}</div>'
                     f'<div class="kpi-value"{f" style=color:{color}" if color else ""}>{val}</div>'
                     f'<div class="kpi-sub">{sub}</div></div>', unsafe_allow_html=True)

    # ── Q1 ────────────────────────────────────────────────────────────────────
    st.markdown('<div class="section-header">Q1 — How does manager performance influence team productivity?</div>', unsafe_allow_html=True)
    st.markdown('<p class="bq">Examining the direct relationship between manager scores and employee output metrics.</p>', unsafe_allow_html=True)
    f1, f2 = q1_charts(fdf, top_n, highlight)
    c1, c2 = st.columns(2)
    c1.plotly_chart(f1, use_container_width=True)
    c2.plotly_chart(f2, use_container_width=True)
    q1_insight(fdf)

    # ── Q2 ────────────────────────────────────────────────────────────────────
    st.markdown('<div class="section-header">Q2 — What is the link between manager effectiveness and employee satisfaction?</div>', unsafe_allow_html=True)
    st.markdown('<p class="bq">Satisfaction is a leading indicator of retention and engagement.</p>', unsafe_allow_html=True)
    f1, f2 = q2_charts(fdf, top_n, highlight)
    c1, c2 = st.columns(2)
    c1.plotly_chart(f1, use_container_width=True)
    c2.plotly_chart(f2, use_container_width=True)
    q2_insight(fdf)

    # ── Q3 ────────────────────────────────────────────────────────────────────
    st.markdown('<div class="section-header">Q3 — How does manager performance impact employee attrition?</div>', unsafe_allow_html=True)
    st.markdown('<p class="bq">Managers account for up to 70% of variance in employee engagement — and attrition.</p>', unsafe_allow_html=True)
    f1, f2 = q3_charts(fdf, top_n, highlight)
    c1, c2 = st.columns(2)
    c1.plotly_chart(f1, use_container_width=True)
    c2.plotly_chart(f2, use_container_width=True)
    q3_insight(fdf)

    # ── Q4 ────────────────────────────────────────────────────────────────────
    st.markdown('<div class="section-header">Q4 — Which managerial attributes contribute most to team success?</div>', unsafe_allow_html=True)
    st.markdown('<p class="bq">Leadership, communication, and experience — which one moves the needle most?</p>', unsafe_allow_html=True)
    f1, f2 = q4_charts(fdf, top_n, highlight)
    c1, c2 = st.columns(2)
    c1.plotly_chart(f1, use_container_width=True)
    c2.plotly_chart(f2, use_container_width=True)
    q4_insight(fdf)

    # ── Q5 ────────────────────────────────────────────────────────────────────
    st.markdown('<div class="section-header">Q5 — How do managers perform across different departments?</div>', unsafe_allow_html=True)
    st.markdown('<p class="bq">Identifying high and low performing departments surfaces systemic issues and best practices.</p>', unsafe_allow_html=True)
    f1, f2 = q5_charts(fdf, top_n, highlight)
    c1, c2 = st.columns(2)
    c1.plotly_chart(f1, use_container_width=True)
    c2.plotly_chart(f2, use_container_width=True)
    q5_insight(fdf)

    # ── Q6 ────────────────────────────────────────────────────────────────────
    st.markdown('<div class="section-header">Q6 — Can underperforming managers be identified early?</div>', unsafe_allow_html=True)
    st.markdown('<p class="bq">A composite risk score combining attrition, performance, and satisfaction flags managers before problems escalate.</p>', unsafe_allow_html=True)
    f1, f2 = q6_charts(fdf, top_n, highlight)
    c1, c2 = st.columns(2)
    c1.plotly_chart(f1, use_container_width=True)
    c2.plotly_chart(f2, use_container_width=True)
    q6_insight(fdf)

    # ── Q7 ────────────────────────────────────────────────────────────────────
    st.markdown('<div class="section-header">Q7 — What is the impact on revenue, project success, and business outcomes?</div>', unsafe_allow_html=True)
    st.markdown('<p class="bq">Connecting managerial effectiveness to the metrics that matter to the business bottom line.</p>', unsafe_allow_html=True)
    f1, f2 = q7_charts(fdf, top_n, highlight)
    c1, c2 = st.columns(2)
    c1.plotly_chart(f1, use_container_width=True)
    c2.plotly_chart(f2, use_container_width=True)
    q7_insight(fdf)

    # ── Rankings table ────────────────────────────────────────────────────────
    st.markdown('<div class="section-header">Full Manager Rankings</div>', unsafe_allow_html=True)
    r = fdf.groupby('manager_name').agg(
        Perf=('manager_performance_score','mean'), Team=('employee_performance','mean'),
        Sat=('satisfaction_score','mean'), Rev=('revenue_generated','sum'),
        Proj=('project_success_score','mean'),
        Att=('attrition',lambda x:(x=='yes').sum()/len(x)*100)).reset_index()
    r.columns = ['Manager','Avg Perf','Team Output','Satisfaction','Revenue','Project Success','Attrition %']
    r = r.sort_values('Avg Perf', ascending=False).reset_index(drop=True)
    r.insert(0,'Rank', range(1,len(r)+1))
    r['Manager'] = r['Manager'].str.title()
    r = r.round(2)
    if not r.empty:
        st.dataframe(r, use_container_width=True, hide_index=True,
                     column_config={"Revenue": st.column_config.NumberColumn("Revenue",format="$%.0f"),
                                    "Attrition %": st.column_config.NumberColumn("Attrition %",format="%.1f%%")})

if __name__ == "__main__":
    main()