import streamlit as st
from plotting.plotly_barchart import stacked_barchart

from config import STYLES
from data import load_data
from tabs.tab_general import render_tab_general
from tabs.tab_tumor_profile import render_tab_tumor_profile
from tabs.tab_invasion_margins import render_tab_invasion_margins
from tabs.tab_staging import render_tab_staging
from tabs.tab_patient_list import render_tab_patient_list

st.set_page_config(
    page_title="Oral Cavity Tumors Dashboard",
    page_icon="🔬",
    layout="wide",
    initial_sidebar_state="expanded"
)

st.markdown(STYLES, unsafe_allow_html=True)

# ── Data loading ──────────────────────────────────────────────────────────────
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

# ── Records added this month as percentage of total ───────────────────────────
records_this_month = int(timeline_all.iloc[-1]) if len(timeline_all) > 0 else 0
pct_this_month = (records_this_month / n * 100) if n > 0 else 0
pct_this_month_label = f"{pct_this_month:.1f}%"

# ── Tabs ──────────────────────────────────────────────────────────────────────
tab1, tab2, tab3, tab4, tab5 = st.tabs(
    ["📍 General", "🔬 Tumor profile", "⚡ Invasion & Margins", "📊 Staging", "📋 Patient list"]
)

with tab1:
    render_tab_general(dff, n, mom_all_label, mom_mondholte_label, mom_lip_label,
                      records_this_month, pct_this_month_label)

with tab2:
    render_tab_tumor_profile(dff)

with tab3:
    render_tab_invasion_margins(dff, n)

with tab4:
    render_tab_staging(dff)

with tab5:
    render_tab_patient_list(dff, n)
