import streamlit as st
import pandas as pd
import plotly.express as px
import plotly.graph_objects as go
from toolbox.plotting.plotly_barchart import stacked_barchart

st.set_page_config(
    page_title="Oral Cavity Tumors Dashboard",
    page_icon="🔬",
    layout="wide",
    initial_sidebar_state="expanded"
)

st.markdown("""
<style>
    .metric-card {
        background: #f8f9fa;
        border-radius: 8px;
        padding: 16px;
        text-align: center;
    }
    .metric-value { font-size: 28px; font-weight: 600; color: #1a1a2e; }
    .metric-label { font-size: 12px; color: #6c757d; margin-top: 2px; }
    .metric-sub { font-size: 11px; color: #adb5bd; margin-top: 1px; }
    .badge-pos { background:#fde8e8; color:#c0392b; padding:2px 8px; border-radius:12px; font-size:11px; font-weight:600; }
    .badge-close { background:#fef3cd; color:#856404; padding:2px 8px; border-radius:12px; font-size:11px; font-weight:600; }
    .badge-free { background:#d1fae5; color:#065f46; padding:2px 8px; border-radius:12px; font-size:11px; font-weight:600; }
    div[data-testid="stMetricValue"] { font-size: 28px !important; }
    .stTabs [data-baseweb="tab-list"] { gap: 4px; }
    .stTabs [data-baseweb="tab"] { padding: 8px 20px; font-size: 13px; }
</style>
""", unsafe_allow_html=True)

@st.cache_data
def load_data():
    df = pd.read_excel("Mondholte_tumoren__dashboardversie__Major_Version_3__3-0-0__extended.xlsx")
    df['aanvraagdatum'] = pd.to_datetime(df['aanvraagdatum'], errors='coerce')
    df['jaar_maand'] = df['aanvraagdatum'].dt.to_period('M').astype(str)
    df['locatie_display'] = df.apply(
        lambda r: r['mondholte_locatie'] if pd.notna(r['mondholte_locatie']) else r['liplocatie'], axis=1
    )
    df['marge_status'] = df['definitieve_minimale_tumorvrije_marge'].apply(
        lambda v: 'Positive (irradical)' if pd.notna(v) and v < 0
        else ('Close (<5 mm)' if pd.notna(v) and 0 <= v < 5
        else ('Free (≥5 mm)' if pd.notna(v) else 'Not assessed'))
    )
    df['graad_kort'] = df['differentiatiegraad'].apply(
        lambda v: 'G1' if pd.notna(v) and 'G1' in str(v)
        else ('G2' if pd.notna(v) and 'G2' in str(v)
        else ('G3' if pd.notna(v) and 'G3' in str(v) else 'N/A'))
    )
    def inv_status(v):
        if pd.isna(v): return 'Unknown'
        if 'niet aangetoond' in str(v): return 'Negative'
        if 'aangetoond' in str(v) and 'niet' not in str(v): return 'Positive'
        return 'N/A'
    df['lvi_status'] = df['lymfovasculaire_invasie'].apply(inv_status)
    df['pni_status'] = df['perineurale_invasie'].apply(inv_status)
    return df

df = load_data()

# ── Sidebar filters ──────────────────────────────────────────────────────────
with st.sidebar:

    st.image('TIRO_logo.png', width=200)
    st.markdown("**Filters**")

    lokalisaties = ['All locations', 'mondholte', 'lip']
    sel_lok = st.selectbox("Primary location", lokalisaties)

    datum_min = df['aanvraagdatum'].min().date()
    datum_max = df['aanvraagdatum'].max().date()
    datum_range = st.date_input("Period", value=(datum_min, datum_max),
                                 min_value=datum_min, max_value=datum_max)


# ── Apply filters ─────────────────────────────────────────────────────────────
dff = df.copy()
if sel_lok != 'All locations':
    dff = dff[dff['tumorlokalisatie_1'] == sel_lok]
if len(datum_range) == 2:
    dff = dff[
        (dff['aanvraagdatum'].dt.date >= datum_range[0]) &
        (dff['aanvraagdatum'].dt.date <= datum_range[1])
    ]

n = len(dff)

# ── Header ────────────────────────────────────────────────────────────────────
st.title("Oral Cavity Tumors")

if n == 0:
    st.warning("No reports found with the current filters.")
    st.stop()

# ── Month-over-month delta ────────────────────────────────────────────────────
def mom_delta_label(series):
    timeline = series.groupby(dff['jaar_maand']).size().sort_index()
    if len(timeline) >= 2:
        delta = int(timeline.iloc[-1]) - int(timeline.iloc[-2])
        return f"{'+' if delta >= 0 else ''}{delta}"
    return None

timeline_all = dff.groupby('jaar_maand').size().sort_index()
if len(timeline_all) >= 2:
    mom_all = int(timeline_all.iloc[-1]) - int(timeline_all.iloc[-2])
    mom_all_label = f"{'+' if mom_all >= 0 else ''}{mom_all}"
else:
    mom_all_label = None

mondholte_series = dff[dff['tumorlokalisatie_1'] == 'mondholte']['tumorlokalisatie_1']
mom_mondholte_label = mom_delta_label(mondholte_series)

lip_series = dff[dff['tumorlokalisatie_1'] == 'lip']['tumorlokalisatie_1']
mom_lip_label = mom_delta_label(lip_series)

# ── Tabs ──────────────────────────────────────────────────────────────────────
tab1, tab2, tab3, tab4, tab5 = st.tabs(
    ["📍 General", "🔬 Tumor profile", "⚡ Invasion & Margins", "📊 Staging", "📋 Patient list"]
)

COLOR_TEAL  = '#1d9e75'
COLOR_BLUE  = '#378add'
COLOR_AMBER = '#ef9f27'
COLOR_RED   = '#e24b4a'
COLOR_GRAY  = '#888780'
COLOR_PURP  = '#7f77dd'
COLOR_GREEN = '#639922'

# ─── Tab 1: General ──────────────────────────────────────────────────────────
with tab1:
    # ── KPI row ───────────────────────────────────────────────────────────────
    c1, c2, c3, c4, c5, c6 = st.columns(6)
    c1.metric("Unique patients", n, mom_all_label)
    c2.metric("Reports", n, mom_all_label)
    c3.metric("First report", dff['aanvraagdatum'].min().strftime('%d/%m/%Y') if n > 0 else "—")
    c4.metric("Last report", dff['aanvraagdatum'].max().strftime('%d/%m/%Y') if n > 0 else "—")
    c5.metric("Oral cavity", f"{int((dff['tumorlokalisatie_1'] == 'mondholte').sum()/n*100)}%",
              mom_mondholte_label)
    c6.metric("Lip", f"{int((dff['tumorlokalisatie_1'] == 'lip').sum()/n*100)}%",
              mom_lip_label)

    # Timeline
    st.subheader("Patients over time")
    if 'y_view_timeline' not in st.session_state:
        st.session_state['y_view_timeline'] = 'Absolute values'
    if 'time_timeline' not in st.session_state:
        st.session_state['time_timeline'] = 'Monthly'
    stacked_barchart(dff, x_column='aanvraagdatum', stack_category='tumorlokalisatie_1',
                     key='timeline', Time=True, height=300, margin_top=40,
                     color_palette=[COLOR_PURP, COLOR_TEAL],
                     stacking_order=['lip', 'mondholte'])

    col1, col2 = st.columns(2)

    with col1:
        st.subheader("Primary location")
        lok_counts = dff['tumorlokalisatie_1'].value_counts().reset_index()
        lok_counts.columns = ['Location', 'Count']
        fig = px.pie(lok_counts, names='Location', values='Count',
                     color='Location',
                     color_discrete_map={'mondholte': '#1b9e75', 'lip': '#7f76dd'},
                     hole=0.45)
        fig.update_traces(textposition='outside', textinfo='percent+label')
        fig.update_layout(showlegend=False, margin=dict(t=20, b=20, l=20, r=20), height=300)
        st.plotly_chart(fig, use_container_width=True)

    with col2:
        st.subheader("Laterality")
        lat_order = ['links', 'rechts', 'mediaan', 'bilateraal']
        teal_shades_map = {'bilateraal': '#c7ece0', 'links': '#7dc9b3', 'mediaan': '#1d9e75', 'rechts': '#0d5c44'}
        purp_shades_map = {'bilateraal': '#d9d7f5', 'links': '#b0aaeb', 'mediaan': '#7f76dd', 'rechts': '#4a43b8'}
        lat = dff.groupby(['lateraliteit', 'tumorlokalisatie_1']).size().reset_index(name='Count')
        lat['order'] = lat['lateraliteit'].apply(lambda x: lat_order.index(x) if x in lat_order else 99)
        lat = lat.sort_values('order')
        fig_lat = go.Figure()
        seen_legend = set()
        for _, row in lat.iterrows():
            lok, lat_val = row['tumorlokalisatie_1'], row['lateraliteit']
            shade = teal_shades_map.get(lat_val, '#1d9e75') if lok == 'mondholte' else purp_shades_map.get(lat_val, '#7f76dd')
            fig_lat.add_trace(go.Bar(
                name=lok, y=[lat_val], x=[row['Count']], orientation='h',
                marker_color=shade, text=[str(row['Count'])],
                textposition='inside', insidetextanchor='middle',
                legendgroup=lok, showlegend=(lok not in seen_legend)
            ))
            seen_legend.add(lok)
        fig_lat.update_layout(barmode='stack', margin=dict(t=10, b=10, l=10, r=40), height=300,
                              yaxis={'title': '', 'categoryorder': 'array',
                                     'categoryarray': lat_order[::-1]},
                              xaxis_title='',
                              legend=dict(title='', orientation='h', y=-0.2))
        st.plotly_chart(fig_lat, use_container_width=True)

    col3, col4 = st.columns(2)

    with col3:
        st.subheader("Oral cavity location")
        mh_df = dff[dff['tumorlokalisatie_1'] == 'mondholte'].dropna(subset=['mondholte_locatie', 'lateraliteit'])
        mh_grouped = mh_df.groupby(['mondholte_locatie', 'lateraliteit']).size().reset_index(name='Count')
        teal_shades = ['#c7ece0', '#7dc9b3', '#1d9e75', '#0d5c44']
        lat_vals_mh = sorted(mh_grouped['lateraliteit'].unique())
        teal_map = dict(zip(lat_vals_mh, teal_shades[:len(lat_vals_mh)]))
        fig3 = px.bar(mh_grouped, x='Count', y='mondholte_locatie', color='lateraliteit',
                      orientation='h', color_discrete_map=teal_map, barmode='stack')
        fig3.update_layout(margin=dict(t=10, b=10, l=10, r=40), height=280,
                           yaxis_title='', xaxis_title='',
                           legend=dict(orientation='h', y=-0.2))
        st.plotly_chart(fig3, use_container_width=True)

    with col4:
        st.subheader("Lip location")
        lip_df = dff[dff['tumorlokalisatie_1'] == 'lip'].dropna(subset=['liplocatie', 'lateraliteit'])
        if len(lip_df) > 0:
            lip_grouped = lip_df.groupby(['liplocatie', 'lateraliteit']).size().reset_index(name='Count')
            purp_shades = ['#d9d7f5', '#b0aaeb', '#7f76dd', '#4a43b8']
            lat_vals_lip = sorted(lip_grouped['lateraliteit'].unique())
            purp_map = dict(zip(lat_vals_lip, purp_shades[:len(lat_vals_lip)]))
            fig4 = px.bar(lip_grouped, x='Count', y='liplocatie', color='lateraliteit',
                          orientation='h', color_discrete_map=purp_map, barmode='stack')
            fig4.update_layout(margin=dict(t=10, b=10, l=10, r=40), height=200,
                               yaxis_title='', xaxis_title='',
                               legend=dict(orientation='h', y=-0.2))
            st.plotly_chart(fig4, use_container_width=True)
        else:
            st.info("No lip locations in selection.")

# ─── Tab 2: Tumor profile ─────────────────────────────────────────────────────
with tab2:
    col1, col2 = st.columns(2)

    with col1:
        st.subheader("Histological type")
        ht = dff['histologisch_tumortype'].value_counts().reset_index()
        ht.columns = ['Type', 'Count']
        fig = px.bar(ht, x='Count', y='Type', orientation='h',
                     color_discrete_sequence=[COLOR_BLUE], text='Count')
        fig.update_traces(textposition='outside')
        fig.update_layout(margin=dict(t=10, b=10, l=10, r=40), height=300,
                          yaxis_title='', xaxis_title='')
        st.plotly_chart(fig, use_container_width=True)

        st.subheader("Differentiation grade")
        grd = dff['graad_kort'].value_counts().reset_index()
        grd.columns = ['Grade', 'Count']
        colors = {'G1': COLOR_GREEN, 'G2': COLOR_AMBER, 'G3': COLOR_RED, 'N/A': COLOR_GRAY}
        fig2 = px.bar(grd, x='Grade', y='Count',
                      color='Grade',
                      color_discrete_map=colors,
                      text='Count')
        fig2.update_traces(textposition='outside')
        fig2.update_layout(showlegend=False, margin=dict(t=10, b=10, l=10, r=10), height=260,
                           xaxis_title='', yaxis_title='')
        st.plotly_chart(fig2, use_container_width=True)

    with col2:
        st.subheader("Invasion depth")
        inv_order = ['≤ 5 mm', '> 5 mm en ≤ 10 mm', '> 10 mm', 'niet van toepassing']
        inv_col = ['#639922', '#ef9f27', '#e24b4a', '#888780']
        id_counts = dff['invasiediepte'].value_counts().reset_index()
        id_counts.columns = ['Depth', 'Count']
        id_counts['order'] = id_counts['Depth'].apply(
            lambda x: inv_order.index(x) if x in inv_order else 99)
        id_counts = id_counts.sort_values('order')
        fig3 = px.bar(id_counts, x='Depth', y='Count',
                      color='Depth',
                      color_discrete_sequence=inv_col,
                      text='Count')
        fig3.update_traces(textposition='outside')
        fig3.update_layout(showlegend=False, margin=dict(t=10, b=10, l=10, r=10), height=280,
                           xaxis_title='', yaxis_title='')
        st.plotly_chart(fig3, use_container_width=True)

        st.subheader("Worst Pattern of Invasion (WPOI)")
        wpoi = dff[dff['worst_pattern_of_invasion_wpoi'] != 'niet van toepassing']['worst_pattern_of_invasion_wpoi']
        if len(wpoi) > 0:
            wpoi_counts = wpoi.value_counts().reset_index()
            wpoi_counts.columns = ['WPOI', 'Count']
            wpoi_counts['WPOI_kort'] = wpoi_counts['WPOI'].str.extract(r'(WPOI-\d)')
            fig4 = px.bar(wpoi_counts, x='Count', y='WPOI_kort', orientation='h',
                          color_discrete_sequence=[COLOR_AMBER], text='Count',
                          hover_data={'WPOI': True, 'WPOI_kort': False})
            fig4.update_traces(textposition='outside')
            fig4.update_layout(margin=dict(t=10, b=10, l=10, r=40), height=240,
                               yaxis_title='', xaxis_title='')
            st.plotly_chart(fig4, use_container_width=True)

    # Dimension histogram
    st.subheader("Distribution of maximum tumor dimension (mm)")
    dim_data = dff['maximale_tumordimensie'].dropna()
    if len(dim_data) > 0:
        fig5 = px.histogram(dim_data, nbins=20,
                            color_discrete_sequence=[COLOR_BLUE],
                            labels={'value': 'Dimension (mm)', 'count': 'Count'})
        fig5.update_layout(margin=dict(t=10, b=10, l=10, r=10), height=220,
                           xaxis_title='Maximum dimension (mm)', yaxis_title='Count',
                           showlegend=False)
        fig5.add_vline(x=dim_data.mean(), line_dash='dash', line_color=COLOR_RED,
                       annotation_text=f'Mean: {dim_data.mean():.1f} mm')
        st.plotly_chart(fig5, use_container_width=True)

# ─── Tab 3: Invasion & Margins ────────────────────────────────────────────────
with tab3:
    col1, col2 = st.columns(2)

    with col1:
        st.subheader("Invasion status overview")
        inv_data = {
            'Type': ['Lymphovascular (LVI)', 'Perineural (PNI)', 'Bone invasion', 'Neck invasion', 'Lip invasion', 'Sinus invasion'],
            'Positive': [
                (dff['lymfovasculaire_invasie'].str.contains('aangetoond', na=False) & ~dff['lymfovasculaire_invasie'].str.contains('niet aangetoond', na=False)).sum(),
                (dff['perineurale_invasie'].str.contains('aangetoond', na=False) & ~dff['perineurale_invasie'].str.contains('niet aangetoond', na=False)).sum(),
                (dff['invasie_van_bot'] == 'aanwezig').sum(),
                (dff['invasie_van_nek'] == 'aanwezig').sum(),
                (dff['invasie_van_lip'] == 'aanwezig').sum(),
                (dff['invasie_van_sinus'] == 'aanwezig').sum(),
            ]
        }
        inv_df = pd.DataFrame(inv_data)
        inv_df['Pct'] = (inv_df['Positive'] / n * 100).round(1)
        inv_df['Negative/N/A'] = n - inv_df['Positive']
        fig = go.Figure()
        fig.add_bar(name='Positive', y=inv_df['Type'], x=inv_df['Positive'],
                    orientation='h', marker_color=COLOR_RED,
                    text=inv_df['Positive'].astype(str) + ' (' + inv_df['Pct'].astype(str) + '%)',
                    textposition='inside')
        fig.add_bar(name='Negative/N/A', y=inv_df['Type'], x=inv_df['Negative/N/A'],
                    orientation='h', marker_color='#e9ecef', textposition='none')
        fig.update_layout(barmode='stack', margin=dict(t=10, b=10, l=10, r=10),
                          height=320, xaxis_title='Number of patients',
                          yaxis_title='', legend=dict(orientation='h', y=-0.15))
        st.plotly_chart(fig, use_container_width=True)

    with col2:
        st.subheader("Resection margin status")
        marge_counts = dff['marge_status'].value_counts().reset_index()
        marge_counts.columns = ['Status', 'Count']
        marge_colors = {
            'Positive (irradical)': COLOR_RED,
            'Close (<5 mm)': COLOR_AMBER,
            'Free (≥5 mm)': COLOR_GREEN,
            'Not assessed': COLOR_GRAY
        }
        fig2 = px.pie(marge_counts, names='Status', values='Count',
                      color='Status', color_discrete_map=marge_colors, hole=0.4)
        fig2.update_traces(textposition='outside', textinfo='percent+label')
        fig2.update_layout(showlegend=False, margin=dict(t=20, b=20, l=20, r=20), height=320)
        st.plotly_chart(fig2, use_container_width=True)

    # Margin scatter
    st.subheader("Minimum margin per patient (mm)")
    marge_data = dff[dff['definitieve_minimale_tumorvrije_marge'].notna()].copy()
    marge_data = marge_data.sort_values('definitieve_minimale_tumorvrije_marge')
    marge_data['idx'] = range(len(marge_data))
    marge_data['color'] = marge_data['definitieve_minimale_tumorvrije_marge'].apply(
        lambda v: 'Positive' if v < 0 else ('Close' if v < 5 else 'Free'))
    if len(marge_data) > 0:
        fig3 = px.scatter(marge_data, x='idx', y='definitieve_minimale_tumorvrije_marge',
                          color='color',
                          color_discrete_map={'Positive': COLOR_RED, 'Close': COLOR_AMBER, 'Free': COLOR_GREEN},
                          hover_data={'report_id': True, 'pt_stage': True,
                                      'idx': False, 'color': False},
                          labels={'definitieve_minimale_tumorvrije_marge': 'Margin (mm)',
                                  'idx': 'Patient (sorted)'})
        fig3.add_hline(y=0, line_dash='solid', line_color=COLOR_RED, line_width=1)
        fig3.add_hline(y=5, line_dash='dash', line_color=COLOR_AMBER, line_width=1,
                       annotation_text='5 mm threshold')
        fig3.update_layout(margin=dict(t=10, b=10, l=10, r=10), height=280,
                           legend=dict(orientation='h', y=-0.2))
        st.plotly_chart(fig3, use_container_width=True)

# ─── Tab 4: Staging ───────────────────────────────────────────────────────────
with tab4:
    col1, col2 = st.columns(2)

    with col1:
        st.subheader("pT stage distribution")
        stage_order = ['pTis', 'pT1', 'pT2', 'pT3', 'pT4a', 'pT4b']
        stage_colors = {
            'pTis': '#639922', 'pT1': '#97c459',
            'pT2': '#378add', 'pT3': '#ef9f27',
            'pT4a': '#e24b4a', 'pT4b': '#a32d2d'
        }
        pt_counts = dff['pt_stage'].value_counts().reset_index()
        pt_counts.columns = ['Stage', 'Count']
        pt_counts['order'] = pt_counts['Stage'].apply(
            lambda s: stage_order.index(s) if s in stage_order else 99)
        pt_counts = pt_counts.sort_values('order')
        fig = px.bar(pt_counts, x='Stage', y='Count',
                     color='Stage', color_discrete_map=stage_colors,
                     text='Count')
        fig.update_traces(textposition='outside')
        fig.update_layout(showlegend=False, margin=dict(t=10, b=10, l=10, r=10), height=320,
                          xaxis_title='', yaxis_title='Number of patients')
        st.plotly_chart(fig, use_container_width=True)

    # Staging vs dimension
    st.subheader("Tumor dimension per stage")
    dim_stage = dff[dff['maximale_tumordimensie'].notna() & dff['pt_stage'].notna()].copy()
    if len(dim_stage) > 0:
        dim_stage['pt_order'] = dim_stage['pt_stage'].apply(
            lambda s: stage_order.index(s) if s in stage_order else 99)
        dim_stage = dim_stage.sort_values('pt_order')
        fig3 = px.box(dim_stage, x='pt_stage', y='maximale_tumordimensie',
                      color='pt_stage', color_discrete_map=stage_colors,
                      points='all',
                      labels={'pt_stage': 'Stage', 'maximale_tumordimensie': 'Dimension (mm)'})
        fig3.update_layout(showlegend=False, margin=dict(t=10, b=10, l=10, r=10), height=300,
                           xaxis_title='', yaxis_title='Maximum dimension (mm)')
        st.plotly_chart(fig3, use_container_width=True)

    # Prefix breakdown
    st.subheader("Staging per TNM prefix")
    c1, c2, c3 = st.columns(3)
    with c1:
        st.caption("mpT (multiple primary)")
        mpt = dff['mpt_stage'].dropna().value_counts().reset_index()
        mpt.columns = ['Stage', 'n']
        st.dataframe(mpt, hide_index=True, use_container_width=True)
    with c2:
        st.caption("rpT (recurrence)")
        rpt = dff['rpt_stage'].dropna().value_counts().reset_index()
        rpt.columns = ['Stage', 'n']
        st.dataframe(rpt, hide_index=True, use_container_width=True)
    with c3:
        st.caption("ypT (post-neoadjuvant)")
        ypt = dff['ypt_stage'].dropna().value_counts().reset_index()
        ypt.columns = ['Stage', 'n']
        st.dataframe(ypt, hide_index=True, use_container_width=True)

# ─── Tab 5: Patient list ──────────────────────────────────────────────────────
with tab5:
    st.subheader(f"Patient list ({n} reports)")

    col_search, col_dl = st.columns([3, 1])
    with col_search:
        zoek = st.text_input("Search by location...", placeholder="e.g. oral cavity")
    with col_dl:
        st.markdown("<br>", unsafe_allow_html=True)

    display_cols = {
        'report_id': 'Report ID',
        'aanvraagdatum': 'Date',
        'tumorlokalisatie_1': 'Primary loc.',
        'locatie_display': 'Sublocation',
        'lateraliteit': 'Laterality',
        'histologisch_tumortype': 'Histological type',
        'graad_kort': 'Grade',
        'pt_stage': 'pT',
        'lvi_status': 'LVI',
        'pni_status': 'PNI',
        'maximale_tumordimensie': 'Dim. (mm)',
        'marge_status': 'Margin',
        'neoadjuvante_therapie': 'Neoadj.'
    }

    tabel = dff[list(display_cols.keys())].rename(columns=display_cols).copy()
    tabel['Date'] = tabel['Date'].dt.strftime('%d-%m-%Y')

    if zoek:
        mask = tabel.apply(lambda row: row.astype(str).str.contains(zoek, case=False).any(), axis=1)
        tabel = tabel[mask]

    def kleur_marge(val):
        if 'Positive' in str(val):
            return 'background-color:#fde8e8;color:#c0392b'
        if 'Close' in str(val):
            return 'background-color:#fef3cd;color:#856404'
        if 'Free' in str(val):
            return 'background-color:#d1fae5;color:#065f46'
        return ''

    def kleur_stage(val):
        sc = {'pTis':'background-color:#d1fae5;color:#065f46',
              'pT1':'background-color:#d1fae5;color:#065f46',
              'pT2':'background-color:#dbeafe;color:#1e40af',
              'pT3':'background-color:#fef3cd;color:#856404',
              'pT4a':'background-color:#fde8e8;color:#c0392b',
              'pT4b':'background-color:#fde8e8;color:#c0392b'}
        return sc.get(str(val), '')

    styled = tabel.style.applymap(kleur_marge, subset=['Margin']) \
                        .applymap(kleur_stage, subset=['pT'])

    st.dataframe(styled, use_container_width=True, height=500, hide_index=True)

    csv = tabel.to_csv(index=False).encode('utf-8')
    st.download_button("⬇️ Download as CSV", csv, "oral_cavity_tumors_export.csv", "text/csv")
