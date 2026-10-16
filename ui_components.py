"""
ui_components.py
----------------
Presentation components, modern glassmorphism CSS design system, and custom HTML table renderers.
"""

from collections import defaultdict

# ── Modern Glassmorphism CSS ──────────────────────────────────────────────────
APP_CSS = """
<style>
@import url('https://fonts.googleapis.com/css2?family=Plus+Jakarta+Sans:wght@400;500;600;700;800&family=Inter:wght@400;500;600;700&display=swap');

html, body, [class*="css"] {
    font-family: 'Plus Jakarta Sans', 'Inter', -apple-system, BlinkMacSystemFont, sans-serif;
}

/* App Background & Base Layout */
.stApp {
    background: radial-gradient(circle at 10% 10%, rgba(16, 185, 129, 0.05) 0%, transparent 40%),
                radial-gradient(circle at 90% 90%, rgba(6, 182, 212, 0.04) 0%, transparent 40%),
                #0b0f19;
}

/* Header & Hero */
.hero-container {
    background: linear-gradient(135deg, rgba(16, 185, 129, 0.08) 0%, rgba(6, 182, 212, 0.04) 100%);
    border: 1px solid rgba(16, 185, 129, 0.2);
    border-radius: 16px;
    padding: 1.5rem 1.8rem;
    margin-bottom: 2rem;
    box-shadow: 0 10px 30px -10px rgba(0, 0, 0, 0.5);
    position: relative;
    overflow: hidden;
}

.hero-badge {
    display: inline-flex;
    align-items: center;
    gap: 6px;
    background: rgba(16, 185, 129, 0.15);
    border: 1px solid rgba(16, 185, 129, 0.35);
    color: #34d399;
    font-size: 0.75rem;
    font-weight: 700;
    letter-spacing: 0.8px;
    text-transform: uppercase;
    padding: 4px 12px;
    border-radius: 20px;
    margin-bottom: 0.75rem;
}

.hero-pulse {
    width: 7px;
    height: 7px;
    background-color: #10b981;
    border-radius: 50%;
    box-shadow: 0 0 10px #10b981;
    animation: pulse-ring 2s infinite;
}

@keyframes pulse-ring {
    0% { transform: scale(0.95); box-shadow: 0 0 0 0 rgba(16, 185, 129, 0.7); }
    70% { transform: scale(1); box-shadow: 0 0 0 8px rgba(16, 185, 129, 0); }
    100% { transform: scale(0.95); box-shadow: 0 0 0 0 rgba(16, 185, 129, 0); }
}

.hero-title {
    font-size: 2rem;
    font-weight: 800;
    margin: 0;
    background: linear-gradient(120deg, #ffffff 30%, #34d399 70%, #38bdf8 100%);
    -webkit-background-clip: text;
    -webkit-text-fill-color: transparent;
    letter-spacing: -0.5px;
}

.hero-subtitle {
    color: #94a3b8;
    font-size: 0.95rem;
    margin-top: 0.4rem;
    font-weight: 500;
}

/* Console Section Cards */
.console-card {
    background: rgba(15, 23, 42, 0.65);
    backdrop-filter: blur(16px);
    border: 1px solid rgba(255, 255, 255, 0.08);
    border-radius: 16px;
    padding: 1.5rem;
    margin-bottom: 1.25rem;
    box-shadow: 0 8px 32px 0 rgba(0, 0, 0, 0.36);
    transition: transform 0.2s ease, border-color 0.2s ease;
}

.console-card:hover {
    border-color: rgba(16, 185, 129, 0.3);
}

.section-tag {
    display: inline-flex;
    align-items: center;
    gap: 6px;
    color: #38bdf8;
    font-size: 0.8rem;
    font-weight: 700;
    letter-spacing: 0.8px;
    text-transform: uppercase;
    margin-bottom: 0.75rem;
}

/* Metric KPI Cards */
.kpi-grid {
    display: grid;
    grid-template-columns: repeat(4, 1fr);
    gap: 0.85rem;
    margin-bottom: 1.5rem;
}

.kpi-card {
    background: rgba(15, 23, 42, 0.75);
    border: 1px solid rgba(255, 255, 255, 0.08);
    border-radius: 12px;
    padding: 1rem;
    text-align: center;
    position: relative;
    overflow: hidden;
}

.kpi-card.kpi-yes {
    border-color: rgba(16, 185, 129, 0.4);
    background: linear-gradient(180deg, rgba(16, 185, 129, 0.1) 0%, rgba(15, 23, 42, 0.8) 100%);
}

.kpi-card.kpi-no {
    border-color: rgba(148, 163, 184, 0.2);
}

.kpi-label {
    font-size: 0.75rem;
    font-weight: 700;
    color: #94a3b8;
    text-transform: uppercase;
    letter-spacing: 0.5px;
    margin-bottom: 0.3rem;
}

.kpi-value {
    font-size: 1.4rem;
    font-weight: 800;
    color: #f8fafc;
}

.kpi-yes .kpi-value {
    color: #34d399;
}

/* Custom Clearances Table */
.clearance-table-wrapper {
    background: rgba(15, 23, 42, 0.8);
    border: 1px solid rgba(255, 255, 255, 0.1);
    border-radius: 14px;
    overflow: hidden;
    margin: 1rem 0 1.5rem 0;
    box-shadow: 0 4px 20px rgba(0, 0, 0, 0.25);
}

.clearance-table {
    width: 100%;
    border-collapse: collapse;
    text-align: left;
}

.clearance-table th {
    background: rgba(30, 41, 59, 0.7);
    padding: 0.9rem 1.1rem;
    font-size: 0.8rem;
    font-weight: 700;
    color: #94a3b8;
    text-transform: uppercase;
    letter-spacing: 0.6px;
    border-bottom: 1px solid rgba(255, 255, 255, 0.1);
}

.clearance-table td {
    padding: 1.1rem;
    font-size: 0.9rem;
    vertical-align: top;
    border-bottom: 1px solid rgba(255, 255, 255, 0.06);
    line-height: 1.55;
}

.clearance-table tr:last-child td {
    border-bottom: none;
}

.badge-yes {
    display: inline-flex;
    align-items: center;
    gap: 5px;
    background: rgba(16, 185, 129, 0.15);
    border: 1px solid rgba(16, 185, 129, 0.4);
    color: #34d399;
    padding: 4px 10px;
    border-radius: 20px;
    font-size: 0.75rem;
    font-weight: 700;
    letter-spacing: 0.4px;
    white-space: nowrap;
}

.badge-no {
    display: inline-flex;
    align-items: center;
    gap: 5px;
    background: rgba(148, 163, 184, 0.1);
    border: 1px solid rgba(148, 163, 184, 0.25);
    color: #94a3b8;
    padding: 4px 10px;
    border-radius: 20px;
    font-size: 0.75rem;
    font-weight: 600;
    letter-spacing: 0.4px;
    white-space: nowrap;
}

/* Primary Run Button Styling */
div.stButton > button:first-child {
    background: linear-gradient(135deg, #059669 0%, #10b981 50%, #06b6d4 100%) !important;
    color: #ffffff !important;
    font-weight: 700 !important;
    font-size: 1.05rem !important;
    padding: 0.75rem 1.5rem !important;
    border: none !important;
    border-radius: 12px !important;
    box-shadow: 0 4px 20px rgba(16, 185, 129, 0.4) !important;
    transition: all 0.3s cubic-bezier(0.4, 0, 0.2, 1) !important;
    letter-spacing: 0.3px !important;
    width: 100% !important;
}

div.stButton > button:first-child:hover {
    transform: translateY(-2px) !important;
    box-shadow: 0 6px 25px rgba(16, 185, 129, 0.6) !important;
    filter: brightness(1.08) !important;
}

div.stButton > button:first-child:active {
    transform: translateY(0px) !important;
}

/* Empty State Hero */
.empty-hero {
    background: rgba(15, 23, 42, 0.5);
    border: 1.5px dashed rgba(255, 255, 255, 0.12);
    border-radius: 16px;
    padding: 3rem 2rem;
    text-align: center;
    color: #94a3b8;
}

.empty-icon {
    font-size: 3rem;
    margin-bottom: 1rem;
    display: inline-block;
    filter: drop-shadow(0 0 15px rgba(16, 185, 129, 0.3));
}
</style>
"""

# ── Hero Header ───────────────────────────────────────────────────────────────
HERO_HTML = """
<div class="hero-container">
    <div class="hero-badge">
        <span class="hero-pulse"></span> PARIVESH 2.0 AUTOMATION ENGINE
    </div>
    <h1 class="hero-title">🌿 Green Clearances Intelligence Console</h1>
    <div class="hero-subtitle">
        Automated MoEFCC Tentative Clearances (Environmental, Forest, Wildlife, CRZ) & Bharatmaps GIS Spatial Analysis
    </div>
</div>
"""

# ── Empty State Card ──────────────────────────────────────────────────────────
EMPTY_STATE_HTML = """
<div class="empty-hero">
    <div class="empty-icon">&#128752;</div>
    <h3 style="color: #f1f5f9; font-weight: 700; margin-bottom: 0.5rem;">Ready for Clearance Assessment</h3>
    <p style="max-width: 440px; margin: 0 auto; line-height: 1.6; font-size: 0.92rem;">
        Select your industry sector and supply coordinates or a KML boundary on the left. The system will automate the PARIVESH 2.0 evaluation and extract all clearance requirements.
    </p>
    <div style="display: flex; justify-content: center; gap: 14px; margin-top: 1.5rem; font-size: 0.8rem; font-weight: 600; color: #38bdf8;">
        <span>✓ Environmental</span>
        <span>✓ Forest</span>
        <span>✓ Wildlife</span>
        <span>✓ CRZ</span>
    </div>
</div>
"""


# ── Clearances Table HTML Renderer ────────────────────────────────────────────
def render_clearances_html(clearances: list) -> str:
    """
    Renders executive-grade modern table for Tentative Clearances
    with glowing applicability badges and clear typography.
    """
    if not clearances:
        return ""

    rows = []
    for item in clearances:
        sno = item.get("S.No", "")
        approval = item.get("Approval", "")
        app = str(item.get("Applicability", "")).strip().capitalize()
        remarks = item.get("Remarks", "")

        if app.lower() == "yes":
            badge_html = '<span class="badge-yes"><span class="hero-pulse" style="width:6px; height:6px;"></span> APPLICABLE</span>'
        else:
            badge_html = '<span class="badge-no">NOT APPLICABLE</span>'

        rows.append(
            f'<tr>'
            f'<td style="font-weight: 700; color: #94a3b8; width: 6%; text-align: center;">{sno}</td>'
            f'<td style="font-weight: 700; color: #f1f5f9; width: 26%; font-size: 0.95rem;">{approval}</td>'
            f'<td style="width: 20%;">{badge_html}</td>'
            f'<td style="color: #cbd5e1; font-size: 0.88rem; line-height: 1.6;">{remarks}</td>'
            f'</tr>'
        )

    tbody = "".join(rows)
    return (
        '<div class="clearance-table-wrapper">'
        '<table class="clearance-table">'
        '<thead>'
        '<tr>'
        '<th style="text-align: center;">#</th>'
        '<th>Approval / Clearance</th>'
        '<th>Applicability</th>'
        '<th>Regulatory Remarks & Provisions</th>'
        '</tr>'
        '</thead>'
        f'<tbody>{tbody}</tbody>'
        '</table>'
        '</div>'
    )


# ── Toposheet and Location HTML Renderer ──────────────────────────────────────
def render_geoloc_html(toposheet: str, locations: list) -> str:
    """
    Renders Toposheet No. box and State/District/Village table
    matching the exact visual format on PARIVESH 2.0 KYA report.
    """
    html = []

    # 1. Toposheet Box
    if toposheet:
        html.append(
            f'<div style="background: rgba(255, 255, 255, 0.03); border: 1px solid rgba(255, 255, 255, 0.12); border-radius: 8px; padding: 1rem 1.25rem; margin: 1rem 0 1.25rem 0;">'
            f'<div style="font-size: 0.85rem; font-weight: 700; color: #94a3b8; margin-bottom: 0.4rem;">Toposheet No.</div>'
            f'<div style="color: #38bdf8; font-size: 1.05rem; font-weight: 700; line-height: 1.6; word-break: break-word;">{toposheet}</div>'
            f'</div>'
        )

    # 2. State / District / Village Table
    if locations:
        grouped = defaultdict(list)
        for loc in locations:
            st_name = loc.get("State", "").strip() or "N/A"
            grouped[st_name].append(loc)

        table_rows = []
        for st_name, dist_list in grouped.items():
            rowspan = len(dist_list)
            for idx, item in enumerate(dist_list):
                dist = item.get("District", "")
                vill = item.get("Village", "")
                row_html = '<tr style="border-bottom: 1px solid rgba(255,255,255,0.08);">'
                if idx == 0:
                    row_html += f'<td rowspan="{rowspan}" style="vertical-align: top; padding: 1rem; border-right: 1px solid rgba(255,255,255,0.08); font-weight: 800; color: #38bdf8; font-size: 1.1rem; letter-spacing: 0.5px; text-transform: uppercase;">{st_name}</td>'
                row_html += f'<td style="vertical-align: top; padding: 1rem; border-right: 1px solid rgba(255,255,255,0.08); font-weight: 600; font-size: 0.95rem; white-space: nowrap;">{dist}</td>'
                row_html += f'<td style="vertical-align: top; padding: 1rem; color: #94a3b8; font-size: 0.92rem; line-height: 1.65;">{vill}</td>'
                row_html += "</tr>"
                table_rows.append(row_html)

        tbody_loc = "".join(table_rows)
        html.append(
            f'<div style="border: 1px solid rgba(255, 255, 255, 0.12); border-radius: 8px; overflow: hidden; margin-top: 0.5rem; background: rgba(255, 255, 255, 0.01);">'
            f'<table style="width: 100%; border-collapse: collapse; text-align: left;">'
            f'<thead>'
            f'<tr style="background: rgba(255, 255, 255, 0.05); border-bottom: 1px solid rgba(255, 255, 255, 0.12);">'
            f'<th style="padding: 0.85rem 1rem; font-size: 0.85rem; font-weight: 700; color: #94a3b8; width: 22%;">State <span style="font-size: 0.7rem; opacity: 0.7;">&#9662;</span></th>'
            f'<th style="padding: 0.85rem 1rem; font-size: 0.85rem; font-weight: 700; color: #94a3b8; width: 22%;">District <span style="font-size: 0.7rem; opacity: 0.7;">&#9662;</span></th>'
            f'<th style="padding: 0.85rem 1rem; font-size: 0.85rem; font-weight: 700; color: #94a3b8;">Village <span style="font-size: 0.7rem; opacity: 0.7;">&#9662;</span></th>'
            f'</tr>'
            f'</thead>'
            f'<tbody>{tbody_loc}</tbody>'
            f'</table>'
            f'</div>'
        )

    return "".join(html)
