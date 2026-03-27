"""Tab 5: Patient list and data export."""

import streamlit as st


def render_tab_patient_list(dff, n):
    """Render the Patient list tab with searchable table and CSV export."""

    st.subheader(f"Patient list ({n} reports)")

    col_search, col_dl = st.columns([3, 1])
    with col_search:
        zoek = st.text_input("Search by location...", placeholder="e.g. oral cavity")
    with col_dl:
        st.markdown("<br>", unsafe_allow_html=True)

    display_cols = {
        'report_version_id': 'Report ID',
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
