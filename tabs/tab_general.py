"""Tab 1: General overview of tumor population."""

import pandas as pd
import streamlit as st
import plotly.express as px
import plotly.graph_objects as go

from config import COLOR_PURP, COLOR_TEAL
from utils import render_oral_cavity_svg

try:
    from plotting.plotly_barchart import stacked_barchart
except ImportError:
    stacked_barchart = None


def render_tab_general(dff, n, num_reports, mom_all_label, mom_mondholte_label, mom_lip_label):
    """Render the General tab with overview metrics and location analysis."""

    # KPI row
    c1, c2, c3, c4, c5, c6 = st.columns(6)
    c1.metric("Unique patients", n, mom_all_label)
    c2.metric("Reports", num_reports, mom_all_label)
    c3.metric("First report", dff['aanvraagdatum'].min().strftime('%d/%m/%Y') if num_reports > 0 else "—")
    c4.metric("Last report", dff['aanvraagdatum'].max().strftime('%d/%m/%Y') if num_reports > 0 else "—")
    c5.metric("Oral cavity", f"{int((dff['tumorlokalisatie_1'] == 'mondholte').sum()/num_reports*100)}%",
              mom_mondholte_label)
    c6.metric("Lip", f"{int((dff['tumorlokalisatie_1'] == 'lip').sum()/num_reports*100)}%",
              mom_lip_label)

    # Timeline
    st.subheader("Patients over time")
    if 'y_view_timeline' not in st.session_state:
        st.session_state['y_view_timeline'] = 'Absolute values'
    if 'time_timeline' not in st.session_state:
        st.session_state['time_timeline'] = 'Monthly'

    if stacked_barchart:
        stacked_barchart(dff, x_column='aanvraagdatum', stack_category='tumorlokalisatie_1',
                         key='timeline', Time=True, height=300, margin_top=40,
                         color_palette=[COLOR_PURP, COLOR_TEAL],
                         stacking_order=['lip', 'mondholte'])
    else:
        st.warning("stacked_barchart tool not available")

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

    #with col2:
    #    st.subheader("Laterality")
    #    lat_order = ['niet aangegeven', 'middenlijn', 'links', 'rechts']
    #    lat = dff.groupby(['lateraliteit', 'tumorlokalisatie_1']).size().reset_index(name='Count')
    #    lat['order'] = lat['lateraliteit'].apply(lambda x: lat_order.index(x) if x in lat_order else 99)
    #    lat = lat.sort_values('order')
    #    fig_lat = go.Figure()
    #    seen_legend = set()
    #    for _, row in lat.iterrows():
    #        lok, lat_val = row['tumorlokalisatie_1'], row['lateraliteit']
    #        color = '#1b9e75' if lok == 'mondholte' else '#7f76dd'
    #        fig_lat.add_trace(go.Bar(
    #            name=lok, y=[lat_val], x=[row['Count']], orientation='h',
    #            marker_color=color, text=[str(row['Count'])],
    #            textposition='inside', insidetextanchor='middle',
    #            legendgroup=lok, showlegend=(lok not in seen_legend)
    #        ))
    #        seen_legend.add(lok)
    #    fig_lat.update_layout(barmode='stack', margin=dict(t=10, b=10, l=10, r=40), height=300,
    #                          yaxis={'title': '', 'categoryorder': 'array',
    #                                 'categoryarray': lat_order[::-1]},
    #                          xaxis_title='',
    #                          legend=dict(title='', orientation='h', y=-0.2))
    #    st.plotly_chart(fig_lat, use_container_width=True)


    with col2:
        st.subheader("Anatomical distribution")
        svg = render_oral_cavity_svg(dff)
        if svg:
            st.markdown(svg, unsafe_allow_html=True)

        #st.subheader("Oral cavity location")
        #mh_df = dff[dff['tumorlokalisatie_1'] == 'mondholte'].dropna(subset=['mondholte_locatie', 'lateraliteit'])
        #mh_grouped = mh_df.groupby(['mondholte_locatie', 'lateraliteit']).size().reset_index(name='Count')
        #mh_lat_order = ['niet aangegeven', 'links', 'rechts', 'middellijn']
        #lat_vals_mh = [lat for lat in mh_lat_order if lat in mh_grouped['lateraliteit'].unique()]
        #teal_map = {
        #    'niet aangegeven': '#d6efe8',
        #    'links': '#79c8b1',
        #    'rechts': '#1b9e75',
        #    'middellijn': '#0f6b50',
        #}
        #fig3 = px.bar(mh_grouped, x='Count', y='mondholte_locatie', color='lateraliteit',
        #          orientation='h', color_discrete_map=teal_map,
        #          category_orders={'lateraliteit': lat_vals_mh}, barmode='stack')
        #fig3.update_traces(offsetgroup=None)
        #fig3.update_layout(barmode='stack', margin=dict(t=10, b=10, l=10, r=40), height=280,
        #                   yaxis_title='', xaxis_title='',
        #                   legend=dict(orientation='h', y=-0.2))
        #st.plotly_chart(fig3, use_container_width=True)

    #with col4:
    #    st.subheader("Lip location")
    #    lip_df = dff[dff['tumorlokalisatie_1'] == 'lip'].dropna(subset=['liplocatie', 'lateraliteit'])
    #    if len(lip_df) > 0:
    #        lip_grouped = lip_df.groupby(['liplocatie', 'lateraliteit']).size().reset_index(name='Count')
    #        lip_lat_order = ['niet aangegeven', 'links', 'middellijn', 'rechts']
    #        lat_vals_lip = [lat for lat in lip_lat_order if lat in lip_grouped['lateraliteit'].unique()]
    #        purp_map = {
    #            'niet aangegeven': '#e1def8',
    #            'links':'#b2abea',
    #            'rechts': '#7f76dd',
    #            'middellijn': '#564bc3'
    #        }
    #        fig4 = px.bar(lip_grouped, x='Count', y='liplocatie', color='lateraliteit',
    #                      orientation='h', color_discrete_map=purp_map,
    #                      category_orders={'lateraliteit': lat_vals_lip}, barmode='stack')
    #        fig4.update_traces(offsetgroup=None)
    #        fig4.update_layout(barmode='stack', margin=dict(t=10, b=10, l=10, r=40), height=200,
    #                           yaxis_title='', xaxis_title='',
    #                           legend=dict(title='', orientation='h', y=-0.2, x=0, xanchor='left', font=dict(size=12)))
    #        st.plotly_chart(fig4, use_container_width=True)
    #    else:
    #        st.info("No lip locations in selection.")
