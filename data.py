"""Data loading and preprocessing for the Oral Cavity Tumors Dashboard."""

import pandas as pd
import streamlit as st


@st.cache_data
def load_data():
    """Load and preprocess tumor data from Excel file."""
    df = pd.read_excel("Mondholte_tumoren__dashboardversie__Major_Version_3__3-0-0__extended.xlsx")
    df['aanvraagdatum'] = pd.to_datetime(df['aanvraagdatum'], errors='coerce')
    df['jaar_maand'] = df['aanvraagdatum'].dt.to_period('M').astype(str)

    # Clean: mondholte_locatie should only have values when tumorlokalisatie_1 == 'mondholte'
    invalid_mondholte = (df['tumorlokalisatie_1'] != 'mondholte') & (df['mondholte_locatie'].notna())
    if invalid_mondholte.sum() > 0:
        st.warning(f"⚠️ Cleaned {invalid_mondholte.sum()} rows: mondholte_locatie values cleared when tumorlokalisatie_1 ≠ 'mondholte'")
        df.loc[invalid_mondholte, 'mondholte_locatie'] = pd.NA

    # Clean: mondholte_locatie should never contain 'lip'
    has_lip = df['mondholte_locatie'] == 'lip'
    if has_lip.sum() > 0:
        st.warning(f"⚠️ Cleaned {has_lip.sum()} rows: removed 'lip' values from mondholte_locatie")
        df.loc[has_lip, 'mondholte_locatie'] = pd.NA

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
