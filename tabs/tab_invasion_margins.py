"""Tab 3: Invasion and margins analysis."""

import streamlit as st
import plotly.express as px
import plotly.graph_objects as go
from config import COLOR_RED, COLOR_AMBER, COLOR_GREEN, COLOR_GRAY


def render_tab_invasion_margins(dff, n):
    """Render the Invasion & Margins tab with invasion status and margin analysis."""

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
        inv_df = __import__('pandas').DataFrame(inv_data)
        inv_df['Pct'] = (inv_df['Positive'] / n * 100).round(1)
        inv_df['Negative/N/A'] = n - inv_df['Positive']
        fig = go.Figure()
        fig.add_bar(name='Positive', y=inv_df['Type'], x=inv_df['Positive'],
                    orientation='h', marker_color=COLOR_RED,
                    text=inv_df['Positive'].astype(str) + ' (' + inv_df['Pct'].astype(str) + '%)',
                    textposition='inside')
        fig.add_bar(name='Negative/N/A', y=inv_df['Type'], x=inv_df['Negative/N/A'],
                    orientation='h', marker_color='#e9ecef', textposition='none')
        fig.update_layout(barmode='stack', margin=dict(t=10, b=60, l=10, r=10),
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
        fig2.update_layout(showlegend=False, margin=dict(t=20, b=20, l=100, r=100), height=320)
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
                          hover_data={'patient_display': True, 'pt_stage': True,
                                      'idx': False, 'color': False},
                          labels={'definitieve_minimale_tumorvrije_marge': 'Margin (mm)',
                                  'idx': 'Patient (sorted)'})
        fig3.add_hline(y=0, line_dash='solid', line_color=COLOR_RED, line_width=1)
        fig3.add_hline(y=5, line_dash='dash', line_color=COLOR_AMBER, line_width=1,
                       annotation_text='5 mm threshold')
        fig3.update_layout(margin=dict(t=10, b=10, l=10, r=10), height=280,
                           legend=dict(orientation='h', y=-0.2))
        st.plotly_chart(fig3, use_container_width=True)
