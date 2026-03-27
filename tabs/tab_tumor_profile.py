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
        total = ht['Count'].sum()
        ht['Percentage'] = (ht['Count'] / total * 100).round(1)
        ht['Label'] = ht['Percentage'].astype(str) + '%'
        fig = px.bar(ht, x='Percentage', y='Type', orientation='h',
                     color_discrete_sequence=[COLOR_BLUE], text='Label')
        fig.update_traces(textposition='outside')
        fig.update_layout(margin=dict(t=10, b=10, l=10, r=40), height=300,
                          yaxis_title='', xaxis_title='')
        st.plotly_chart(fig, use_container_width=True)


    with col2:
        st.subheader("Invasion depth")
        inv_order = ['≤ 5 mm', '> 5 mm en ≤ 10 mm', '> 10 mm', 'niet van toepassing']
        inv_col = ['#639922', '#ef9f27', '#e24b4a', '#888780']
        id_counts = dff['invasiediepte'].value_counts().reset_index()
        id_counts.columns = ['Depth', 'Count']
        id_counts['order'] = id_counts['Depth'].apply(
            lambda x: inv_order.index(x) if x in inv_order else 99)
        id_counts = id_counts.sort_values('order')
        total = id_counts['Count'].sum()
        id_counts['Percentage'] = (id_counts['Count'] / total * 100).round(1)
        id_counts['Label'] = id_counts['Count'].astype(str)
        fig3 = px.bar(id_counts, x='Count', y='Depth',
                      color='Depth',
                      color_discrete_sequence=inv_col,
                      orientation='h',
                      text='Label')
        fig3.update_traces(textposition='inside')
        fig3.update_layout(showlegend=False, margin=dict(t=10, b=10, l=10, r=40), height=300,
                           xaxis_title='', yaxis_title='')
        st.plotly_chart(fig3, use_container_width=True)


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
