"""Data loading and preprocessing for the Oral Cavity Tumors Dashboard."""

import pandas as pd
import numpy as np
import streamlit as st


@st.cache_data
def load_data():
    """Load and preprocess tumor data from Excel file."""
    df = pd.read_excel("Mondholte_tumoren__dashboardversie__Major_Version_3__3-0-0__extended.xlsx")
    # Generate random dates between 1/1/24 and 28/3/26
    date_min = pd.Timestamp('2024-01-01')
    date_max = pd.Timestamp('2026-03-28')
    random_dates = np.random.uniform(date_min.timestamp(), date_max.timestamp(), len(df))
    df['aanvraagdatum'] = pd.to_datetime(random_dates, unit='s')
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
        if pd.isna(v):
            return 'Unknown'
        if 'niet aangetoond' in str(v):
            return 'Negative'
        if 'aangetoond' in str(v) and 'niet' not in str(v):
            return 'Positive'
        return 'N/A'
    df['lvi_status'] = df['lymfovasculaire_invasie'].apply(inv_status)
    df['pni_status'] = df['perineurale_invasie'].apply(inv_status)
    return df
