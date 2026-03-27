"""Utility functions for the Oral Cavity Tumors Dashboard."""

import re
import pandas as pd


def render_oral_cavity_svg(dff):
    """Render an SVG of the oral cavity with tumor location heatmap."""
    n_total = len(dff)
    if n_total == 0:
        return None

    def normalize_label(value):
        if pd.isna(value):
            return None
        return re.sub(r'\s+', ' ', str(value).strip().lower())

    mondholte_norm = dff['mondholte_locatie'].map(normalize_label)
    liplocatie_norm = dff['liplocatie'].map(normalize_label)

    DATA_TO_SVG_MONDHOLTE = {
        # Current data values
        'voorste 2/3 tong':       'voorste 2/3 tong (NNO)',
        'voorste 2/3 tong (NNO)': 'voorste 2/3 tong (NNO)',
        'mondbodem':              'mondbodem',
        'tandvlees':              'tandvlees',
        'wangslijmvlies':         'wangslijmvlies',
        'retromolaire gebied':    'retromolaire gebied',
        'hard gehemelte':         'hard gehemelte',
        'zacht gehemelte':        'zacht gehemelte',
        'tanden':                 'tanden',
        'huig':                   'huig',
        'keelamandel':            'keelamandel',
        'lip':                    'lip',
        # Legacy values
        'tongrand':               'voorste 2/3 tong (NNO)',
        'gingiva onderkaak':      'tandvlees',
        'gingiva bovenkaak':      'tandvlees',
        'wangmucosa':             'wangslijmvlies',
        'retromolaire trigon':    'retromolaire gebied',
        'harde verhemelte':       'hard gehemelte',
        # Additional common variants
        'harde gehemelte':        'hard gehemelte',
        'zachte gehemelte':       'zacht gehemelte',
        'zachte verhemelte':      'zacht gehemelte',
    }
    DATA_TO_SVG_LIP = {
        # Current lip values
        'mucosa onderlip':     'lip',
        'mucosa van bovenlip': 'lip',
        'lip (NNO)':           'lip',
        # Legacy
        'mucosa bovenlip':     'lip',
        'mondcommissuur':      'lip',
    }

    svg_counts = {}
    for val, svg_region in DATA_TO_SVG_MONDHOLTE.items():
        count = int((mondholte_norm == normalize_label(val)).sum())
        svg_counts[svg_region] = svg_counts.get(svg_region, 0) + count

    # Count lip from tumorlokalisatie_1 instead of liplocatie
    lip_count = int((dff['tumorlokalisatie_1'] == 'lip').sum())
    svg_counts['lip'] = svg_counts.get('lip', 0) + lip_count

    svg_pcts = {k: v / n_total * 100 for k, v in svg_counts.items()}
    max_pct = max(svg_pcts.values()) if svg_pcts else 1

    def teal_color(pct):
        if pct == 0:
            return '#EAEAEA'
        elif 'hard gehemelte' in region:
            return '#9fbeb4'
        elif 'voorste 2/3 tong' in region:
            return '#9fbeb4'
        t = min(pct / max_pct, 1.0)
        r = int(0xf8 + (0x0d - 0xf8) * t)
        g = int(0xfc + (0x5c - 0xfc) * t)
        b = int(0xfa + (0x44 - 0xfa) * t)
        return f'#{r:02x}{g:02x}{b:02x}'

    def purple_color(pct):
        if pct == 0:
            return '#D5D5D5'
        else:
            return '#aca7ea'

    def mint_color(pct):
        if pct == 0:
            return '#E6F3EA'
        t = min(pct / max_pct, 1.0)
        r = int(0xe6 + (0x4f - 0xe6) * t)
        g = int(0xf3 + (0xa3 - 0xf3) * t)
        b = int(0xea + (0x72 - 0xea) * t)
        return f'#{r:02x}{g:02x}{b:02x}'

    # Label positions (x, y) in SVG coordinate space (213×321, y=0 is back of mouth, y=321 is lips)
    LABEL_POSITIONS = {
        'lip':                    (106, 15),
        'mondbodem':              (106, 255),
        'voorste 2/3 tong (NNO)': (100, 228),
        'wangslijmvlies':         (28,  205),
        'retromolaire gebied':    (35,  187),
        'tandvlees':              (140, 70),
        'tanden':                 (106, 50),
        'hard gehemelte':         (106, 90),
        'zacht gehemelte':        (106, 130),
        'keelamandel':            (28,  148),
        'huig':                   (106, 148),
    }

    with open('mouth-bsp.svg', 'r') as f:
        svg_content = f.read()

    for region, pct in svg_pcts.items():
        if region == 'lip':
            color = purple_color(pct)
        #elif region == 'zacht gehemelte':
        #    color = mint_color(pct)
        else:
            color = teal_color(pct)
        svg_content = re.sub(
            r'(fill=")([^"]*)("[^>]*?data-display="' + re.escape(region) + r'")',
            r'\g<1>' + color + r'\g<3>',
            svg_content
        )

    DISPLAY_NAMES = {
        'lip':                    'Lip',
        'mondbodem':              'Mondbodem',
        'voorste 2/3 tong (NNO)': 'Tong',
        'wangslijmvlies':         'Wang',
        'retromolaire gebied':    'Retromol.',
        'tandvlees':              'Tandvlees',
        'tanden':                 'Tanden',
        'hard gehemelte':         'Hard gehemelte',
        'zacht gehemelte':        'Zacht gehemelte',
        'keelamandel':            'Amandel',
        'huig':                   'Huig',
    }

    texts = []
    for region, (x, y) in LABEL_POSITIONS.items():
        pct = svg_pcts.get(region, 0)
        if pct > 0:
            name_label = DISPLAY_NAMES.get(region, region)
            full_label = f'{name_label} {pct:.1f}%'
            w = len(full_label) * 4 + 8
            texts.append(
                f'<rect x="{x - w // 2}" y="{y - 7}" width="{w}" height="12" '
                f'fill="white" fill-opacity="0.85" rx="2"/>'
                f'<text x="{x}" y="{y}" text-anchor="middle" dominant-baseline="middle" '
                f'font-family="sans-serif" font-size="7" font-weight="bold" fill="#1a1a2e">'
                f'{full_label}</text>'
            )

    svg_content = svg_content.replace('</svg>', '\n'.join(texts) + '\n</svg>')
    return svg_content
