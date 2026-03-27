"""Tab 4: TNM staging analysis."""

import streamlit as st
import plotly.express as px


def render_tab_staging(dff):
    """Render the Staging tab with TNM prefix breakdowns."""

    stage_order = ['pTis', 'pT1', 'pT2', 'pT3', 'pT4a', 'pT4b']
    stage_colors = {
        'pTis': '#639922', 'pT1': '#97c459',
        'pT2': '#378add', 'pT3': '#ef9f27',
        'pT4a': '#e24b4a', 'pT4b': '#a32d2d'
    }

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
    c1, c2, c3, c4 = st.columns(4)

    # Define color schemes for each TNM prefix
    pt_color_map = {
        'pTis': '#639922', 'pT1': '#97c459',
        'pT2': '#378add', 'pT3': '#ef9f27',
        'pT4a': '#e24b4a', 'pT4b': '#a32d2d'
    }
    rpt_color_map = {
        'rpTis': '#639922', 'rpT0': '#f4a460', 'rpT1': '#97c459', 'rpT2': '#378add',
        'rpT3': '#ef9f27', 'rpT4a': '#e24b4a', 'rpT4b': '#a32d2d', 'rpTX': '#f5deb3'
    }
    ypt_color_map = {
        'ypTis': '#639922', 'ypT0': '#f4a460', 'ypT1': '#97c459', 'ypT2': '#378add',
        'ypT3': '#ef9f27', 'ypT4a': '#e24b4a', 'ypT4b': '#a32d2d', 'ypTX': '#f5deb3'
    }
    mpt_color_map = {
        'mpTis': '#639922', 'mpT0': '#f4a460', 'mpT1': '#97c459', 'mpT2': '#378add',
        'mpT3': '#ef9f27', 'mpT4a': '#e24b4a', 'mpT4b': '#a32d2d', 'mpTX': '#f5deb3'
    }

    with c1:
        st.caption("pT (primary)")
        pt = dff['pt_stage'].dropna().value_counts().reset_index()
        pt.columns = ['Stage', 'n']
        if len(pt) > 0:
            stage_order_pt = ['pTis', 'pT1', 'pT2', 'pT3', 'pT4a', 'pT4b']
            pt['order'] = pt['Stage'].apply(lambda s: stage_order_pt.index(s) if s in stage_order_pt else 99)
            pt = pt.sort_values('order')
            pt_total = pt['n'].sum()
            pt['pct'] = (pt['n'] / pt_total * 100).round(1)
            pt['label'] = pt['n'].astype(str) + ' (' + pt['pct'].astype(str) + '%)'
            fig_pt = px.bar(pt, x='pct', y='Stage', orientation='h',
                           color='Stage', color_discrete_map=pt_color_map, text='label')
            fig_pt.update_traces(textposition='outside')
            fig_pt.update_layout(showlegend=False, margin=dict(t=5, b=5, l=5, r=40), height=220,
                                xaxis_title='%', yaxis_title='')
            st.plotly_chart(fig_pt, use_container_width=True)
        else:
            st.info("No data available")

    with c2:
        st.caption("rpT (recurrence)")
        rpt = dff['rpt_stage'].dropna().value_counts().reset_index()
        rpt.columns = ['Stage', 'n']
        if len(rpt) > 0:
            stage_order_rpt = ['rpTis', 'rpT0', 'rpT1', 'rpT2', 'rpT3', 'rpT4a', 'rpT4b', 'rpTX']
            rpt['order'] = rpt['Stage'].apply(lambda s: stage_order_rpt.index(s) if s in stage_order_rpt else 99)
            rpt = rpt.sort_values('order')
            rpt_total = rpt['n'].sum()
            rpt['pct'] = (rpt['n'] / rpt_total * 100).round(1)
            rpt['label'] = rpt['n'].astype(str) + ' (' + rpt['pct'].astype(str) + '%)'
            fig_rpt = px.bar(rpt, x='pct', y='Stage', orientation='h',
                            color='Stage', color_discrete_map=rpt_color_map, text='label')
            fig_rpt.update_traces(textposition='outside')
            fig_rpt.update_layout(showlegend=False, margin=dict(t=5, b=5, l=5, r=40), height=220,
                                 xaxis_title='%', yaxis_title='')
            st.plotly_chart(fig_rpt, use_container_width=True)
        else:
            st.info("No data available")

    with c3:
        st.caption("ypT (post-neoadjuvant)")
        ypt = dff['ypt_stage'].dropna().value_counts().reset_index()
        ypt.columns = ['Stage', 'n']
        if len(ypt) > 0:
            stage_order_ypt = ['ypTis', 'ypT0', 'ypT1', 'ypT2', 'ypT3', 'ypT4a', 'ypT4b', 'ypTX']
            ypt['order'] = ypt['Stage'].apply(lambda s: stage_order_ypt.index(s) if s in stage_order_ypt else 99)
            ypt = ypt.sort_values('order')
            ypt_total = ypt['n'].sum()
            ypt['pct'] = (ypt['n'] / ypt_total * 100).round(1)
            ypt['label'] = ypt['n'].astype(str) + ' (' + ypt['pct'].astype(str) + '%)'
            fig_ypt = px.bar(ypt, x='pct', y='Stage', orientation='h',
                            color='Stage', color_discrete_map=ypt_color_map, text='label')
            fig_ypt.update_traces(textposition='outside')
            fig_ypt.update_layout(showlegend=False, margin=dict(t=5, b=5, l=5, r=40), height=220,
                                 xaxis_title='%', yaxis_title='')
            st.plotly_chart(fig_ypt, use_container_width=True)
        else:
            st.info("No data available")

    with c4:
        st.caption("mpT (multiple primary)")
        mpt = dff['mpt_stage'].dropna().value_counts().reset_index()
        mpt.columns = ['Stage', 'n']
        if len(mpt) > 0:
            stage_order_mpt = ['mpTis', 'mpT0', 'mpT1', 'mpT2', 'mpT3', 'mpT4a', 'mpT4b', 'mpTX']
            mpt['order'] = mpt['Stage'].apply(lambda s: stage_order_mpt.index(s) if s in stage_order_mpt else 99)
            mpt = mpt.sort_values('order')
            mpt_total = mpt['n'].sum()
            mpt['pct'] = (mpt['n'] / mpt_total * 100).round(1)
            mpt['label'] = mpt['n'].astype(str) + ' (' + mpt['pct'].astype(str) + '%)'
            fig_mpt = px.bar(mpt, x='pct', y='Stage', orientation='h',
                            color='Stage', color_discrete_map=mpt_color_map, text='label')
            fig_mpt.update_traces(textposition='outside')
            fig_mpt.update_layout(showlegend=False, margin=dict(t=5, b=5, l=5, r=40), height=220,
                                xaxis_title='%', yaxis_title='')
            st.plotly_chart(fig_mpt, use_container_width=True)
        else:
            st.info("No data available")
