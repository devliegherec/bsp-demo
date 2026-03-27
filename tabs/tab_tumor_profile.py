"""Tab 2: Tumor profile analysis."""

import streamlit as st
import plotly.express as px
from config import COLOR_BLUE, COLOR_AMBER, COLOR_RED, COLOR_GRAY, COLOR_GREEN


def render_tab_tumor_profile(dff):
    """Render the Tumor profile tab with histological and dimensional analysis."""

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
        grade_order = ['G1', 'G2', 'G3', 'N/A']
        grd['order'] = grd['Grade'].apply(
            lambda x: grade_order.index(x) if x in grade_order else 99)
        grd = grd.sort_values('order')
        colors = {'G1': COLOR_GREEN, 'G2': COLOR_AMBER, 'G3': COLOR_RED, 'N/A': COLOR_GRAY}
        fig2 = px.bar(grd, x='Count', y='Grade',
                      color='Grade',
                      color_discrete_map=colors,
                      orientation='h',
                      text='Count')
        fig2.update_traces(textposition='outside')
        fig2.update_layout(showlegend=False, margin=dict(t=10, b=10, l=10, r=10), height=450,
                           xaxis_title='', yaxis_title='',
                           yaxis={'categoryorder': 'array', 'categoryarray': ['N/A', 'G3', 'G2', 'G1']})
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
        fig3 = px.bar(id_counts, x='Count', y='Depth',
                      color='Depth',
                      color_discrete_sequence=inv_col,
                      orientation='h',
                      text='Count')
        fig3.update_traces(textposition='outside')
        fig3.update_layout(showlegend=False, margin=dict(t=10, b=10, l=10, r=10), height=450,
                           xaxis_title='', yaxis_title='')
        st.plotly_chart(fig3, use_container_width=True)

        st.subheader("Worst Pattern of Invasion (WPOI)")
        wpoi = dff[dff['worst_pattern_of_invasion_wpoi'] != 'niet van toepassing']['worst_pattern_of_invasion_wpoi']
        if len(wpoi) > 0:
            wpoi_counts = wpoi.value_counts().reset_index()
            wpoi_counts.columns = ['WPOI', 'Count']
            wpoi_counts['WPOI_kort'] = wpoi_counts['WPOI'].str.extract(r'(WPOI-\d+)', expand=False)
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
