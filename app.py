"""
PARIVESH KYA Clearance Assistant - Streamlit UI
================================================
Zero-DLL, pure-Python: Playwright + Streamlit + onnxruntime (no torch here).
CAPTCHA solved via ONNX CNN; manual override via expander.

Result extraction strategy (discovered from DOM analysis):
  - Clearance Yes/No: div.col-sm-12.reportCard > div.row > div.clearanceborder[col-sm-10/col-sm-2]
  - Tab panes: #kyaaResult1-4 (Environmental, Forest, Wildlife, CRZ)
  - Project summary: first <table> (Project/Activity, Sub Activity, Capacity)
  - Proximity layers: table with 'Source', 'Distance' headers
"""

import os
import re
import json
import base64
import tempfile
import logging
import requests
import pandas as pd
import streamlit as st
from playwright.sync_api import sync_playwright

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

st.set_page_config(
    page_title="PARIVESH KYA Clearance Assistant",
    page_icon="🌿",
    layout="wide",
)

st.markdown("""
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
""", unsafe_allow_html=True)

BASE_API_URL = "https://parivesh.nic.in/parivesh_api/kya"
HEADERS = {
    "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 Chrome/120.0.0.0 Safari/537.36",
    "Accept": "application/json, text/plain, */*",
    "Referer": "https://parivesh.nic.in/",
}
CAPTCHA_PNG = "current_captcha.png"
CONFIDENCE_THRESHOLD = 0.40


# ── Master-data helpers ────────────────────────────────────────────────────────

@st.cache_data(ttl=3600)
def load_activities():
    if os.path.exists("parivesh_activities.json"):
        try:
            with open("parivesh_activities.json", "r", encoding="utf-8") as f:
                data = json.load(f)
                if data:
                    return data
        except Exception:
            pass
    try:
        res = requests.get(f"{BASE_API_URL}/getactivities", headers=HEADERS, timeout=10)
        if res.status_code == 200:
            return res.json()
    except Exception as e:
        st.error(f"Error fetching activities: {e}")
    return []


def get_subactivities(activity_id):
    url = f"{BASE_API_URL}/getSubactivity?id={activity_id}"
    try:
        res = requests.get(url, headers=HEADERS, timeout=10)
        if res.status_code == 200:
            data = res.json()
            if isinstance(data, list):
                return data
            if isinstance(data, dict):
                return data.get("data", data.get("result", []))
    except Exception as e:
        st.warning(f"Could not load sub-activities: {e}")
    return []


# ── CAPTCHA solver (ddddocr primary + ONNX fallback) ──────────────────────────

def _try_onnx_solve(img_bytes):
    try:
        from captcha_solver import solve_captcha_from_bytes
        return solve_captcha_from_bytes(img_bytes)
    except Exception as e:
        logger.warning("CAPTCHA solve error: %s", e)
        return "", 0.0


# ── Angular Material dropdown — robust 3-strategy selector ────────────────────

def _select_mat_option(page, nth_select, option_text, timeout_ms=8000):
    """
    Selects an option from the nth mat-select on the page.
    Uses exact / distinctive prefix matching rather than a single ambiguous word.
    """
    clean_target = " ".join(option_text.strip().split())

    # Strategy 1: Standard Playwright click flow
    try:
        selects = page.locator("mat-select")
        selects.nth(nth_select).wait_for(state="visible", timeout=6000)
        trigger = selects.nth(nth_select)
        trigger.scroll_into_view_if_needed()
        trigger.click()
        page.wait_for_timeout(800)

        # Wait for overlay to open
        page.locator(".cdk-overlay-container").wait_for(state="visible", timeout=4000)
        page.wait_for_timeout(400)

        # Use distinctive snippet (up to 35 chars) to avoid ambiguous single words
        snippet = clean_target[:35] if len(clean_target) > 35 else clean_target
        opts = page.locator(".cdk-overlay-container mat-option")
        opt = opts.filter(has_text=snippet).first
        if not opt.is_visible():
            opt = opts.filter(has_text=clean_target).first
        if opt.is_visible():
            opt.click()
            page.wait_for_timeout(1000)
            logger.info("Strategy 1 OK: selected option matching '%s'", snippet)
            return True
    except Exception as e1:
        logger.warning("Strategy 1 failed for '%s': %s", clean_target[:20], e1)

    # Strategy 2: JS evaluate fallback with exact / highest-overlap matching
    try:
        clicked = page.evaluate(
            """(args) => {
                const [nth, targetStr] = args;
                const selects = document.querySelectorAll('mat-select');
                if (selects[nth]) selects[nth].click();
                const targetLower = targetStr.toLowerCase();
                const opts = Array.from(document.querySelectorAll('.cdk-overlay-container mat-option, mat-option'));

                // 1. Exact match
                let match = opts.find(o => o.textContent.trim().toLowerCase() === targetLower);
                // 2. StartsWith match
                if (!match) match = opts.find(o => o.textContent.trim().toLowerCase().startsWith(targetLower.slice(0, 30)));
                // 3. Includes match
                if (!match) match = opts.find(o => o.textContent.trim().toLowerCase().includes(targetLower.slice(0, 30)));
                if (match) {
                    match.click();
                    return true;
                }
                return false;
            }""",
            [nth_select, clean_target],
        )
        if clicked:
            page.wait_for_timeout(1000)
            logger.info("Strategy 2 OK: selected option matching '%s'", clean_target[:20])
            return True
    except Exception as e2:
        logger.warning("Strategy 2 failed: %s", e2)

    return False


# ── CAPTCHA canvas extractor ───────────────────────────────────────────────────

def _capture_captcha_canvas(page):
    """Waits for the canvas to render, then extracts via toDataURL(). Returns PNG bytes or None."""
    # Wait for canvas to appear and be non-trivial
    try:
        page.locator("canvas").wait_for(state="visible", timeout=8000)
        page.wait_for_timeout(500)  # extra render time
    except Exception:
        pass

    try:
        b64 = page.evaluate("""() => {
            const canvas = document.querySelector('canvas');
            if (!canvas || canvas.width < 50) return null;
            const tmp = document.createElement('canvas');
            tmp.width  = canvas.width;
            tmp.height = canvas.height;
            const ctx = tmp.getContext('2d');
            ctx.fillStyle = '#ffffff';
            ctx.fillRect(0, 0, tmp.width, tmp.height);
            ctx.drawImage(canvas, 0, 0);
            return tmp.toDataURL('image/png').split(',')[1];
        }""")
        if b64:
            return base64.b64decode(b64)
    except Exception as e:
        logger.warning("canvas.toDataURL failed: %s", e)

    # Fallback: screenshot the captcha area
    try:
        elem = page.locator(".file-upload, div:has(> canvas)").first
        if elem.is_visible():
            return elem.screenshot()
    except Exception as e:
        logger.warning("Element screenshot fallback failed: %s", e)
    return None


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
            
        rows.append(f"""
        <tr>
            <td style="font-weight: 700; color: #94a3b8; width: 6%; text-align: center;">{sno}</td>
            <td style="font-weight: 700; color: #f1f5f9; width: 26%; font-size: 0.95rem;">{approval}</td>
            <td style="width: 20%;">{badge_html}</td>
            <td style="color: #cbd5e1; font-size: 0.88rem; line-height: 1.6;">{remarks}</td>
        </tr>
        """)
        
    return f"""
    <div class="clearance-table-wrapper">
        <table class="clearance-table">
            <thead>
                <tr>
                    <th style="text-align: center;">#</th>
                    <th>Approval / Clearance</th>
                    <th>Applicability</th>
                    <th>Regulatory Remarks & Provisions</th>
                </tr>
            </thead>
            <tbody>
                {''.join(rows)}
            </tbody>
        </table>
    </div>
    """


# ── Toposheet and Location HTML Renderer (matches PARIVESH format) ─────────────

def render_geoloc_html(toposheet: str, locations: list) -> str:
    """
    Renders Toposheet No. box and State/District/Village table
    matching the exact visual format on PARIVESH 2.0 KYA report.
    """
    html = []

    # 1. Toposheet Box
    if toposheet:
        html.append(f"""
        <div style="background: rgba(255, 255, 255, 0.03); border: 1px solid rgba(255, 255, 255, 0.12); border-radius: 8px; padding: 1rem 1.25rem; margin: 1rem 0 1.25rem 0;">
            <div style="font-size: 0.85rem; font-weight: 700; color: #94a3b8; margin-bottom: 0.4rem;">Toposheet No.</div>
            <div style="color: #2563eb; font-size: 1.05rem; font-weight: 700; line-height: 1.6; word-break: break-word;">{toposheet}</div>
        </div>
        """)

    # 2. State / District / Village Table
    if locations:
        from collections import defaultdict
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
                    row_html += f'<td rowspan="{rowspan}" style="vertical-align: top; padding: 1rem; border-right: 1px solid rgba(255,255,255,0.08); font-weight: 800; color: #2563eb; font-size: 1.1rem; letter-spacing: 0.5px; text-transform: uppercase;">{st_name}</td>'
                row_html += f'<td style="vertical-align: top; padding: 1rem; border-right: 1px solid rgba(255,255,255,0.08); font-weight: 600; font-size: 0.95rem; white-space: nowrap;">{dist}</td>'
                row_html += f'<td style="vertical-align: top; padding: 1rem; color: #2563eb; font-size: 0.92rem; line-height: 1.65;">{vill}</td>'
                row_html += "</tr>"
                table_rows.append(row_html)

        html.append(f"""
        <div style="border: 1px solid rgba(255, 255, 255, 0.12); border-radius: 8px; overflow: hidden; margin-top: 0.5rem; background: rgba(255, 255, 255, 0.01);">
            <table style="width: 100%; border-collapse: collapse; text-align: left;">
                <thead>
                    <tr style="background: rgba(255, 255, 255, 0.05); border-bottom: 1px solid rgba(255, 255, 255, 0.12);">
                        <th style="padding: 0.85rem 1rem; font-size: 0.85rem; font-weight: 700; color: #94a3b8; width: 22%;">State <span style="font-size: 0.7rem; opacity: 0.7;">&#9662;</span></th>
                        <th style="padding: 0.85rem 1rem; font-size: 0.85rem; font-weight: 700; color: #94a3b8; width: 22%;">District <span style="font-size: 0.7rem; opacity: 0.7;">&#9662;</span></th>
                        <th style="padding: 0.85rem 1rem; font-size: 0.85rem; font-weight: 700; color: #94a3b8;">Village <span style="font-size: 0.7rem; opacity: 0.7;">&#9662;</span></th>
                    </tr>
                </thead>
                <tbody>
                    {"".join(table_rows)}
                </tbody>
            </table>
        </div>
        """)

    return "".join(html)


# ── Result extraction from reportCard DOM ─────────────────────────────────────

def _extract_results_from_page(page, intercepted_data=None):
    """
    Extracts clearance results from the PARIVESH results page.
    Supports:
      1. Intercepted Camunda DMN /evaluate API payload (100% full, un-truncated remarks)
      2. Live DOM parsing of the Tentative Clearances table
      3. Project summary, proximity layers, Toposheet No., and administrative boundary data
    """
    results = {"clearances": [], "administrative": [], "toposheet": "", "proximity": [], "project": {}}

    # 1. Primary: Intercepted Camunda DMN evaluate JSON response
    if intercepted_data and "dmn_result" in intercepted_data:
        res = intercepted_data["dmn_result"]
        req = intercepted_data.get("dmn_request", {})

        env_flag = req.get("envclear", {}).get("value", False)
        fc_flag = req.get("forclear", {}).get("value", False)
        wl_flag = req.get("wildlifeclear", {}).get("value", False)
        crz_flag = req.get("crz", {}).get("value", False)

        ec_rem = res.get("remark_ec", {}).get("value", "")
        fc_rem = res.get("remark_fc", {}).get("value", "")
        wl_rem = res.get("remark_wl", {}).get("value", "")
        crz_rem = res.get("remark_crz", {}).get("value", "")

        def determine_app(flag, remark):
            rem_lower = str(remark).lower()
            if flag:
                return "Yes"
            if "not falling" in rem_lower or "not covered" in rem_lower:
                return "No"
            if "falling in" in rem_lower or "covered under" in rem_lower:
                return "Yes"
            return "No"

        results["clearances"] = [
            {
                "S.No": "1",
                "Approval": "Environmental clearance",
                "Applicability": determine_app(env_flag, ec_rem),
                "Remarks": ec_rem
            },
            {
                "S.No": "2",
                "Approval": "Forest Clearance",
                "Applicability": determine_app(fc_flag, fc_rem),
                "Remarks": fc_rem
            },
            {
                "S.No": "3",
                "Approval": "Wildlife Clearance",
                "Applicability": determine_app(wl_flag, wl_rem),
                "Remarks": wl_rem
            },
            {
                "S.No": "4",
                "Approval": "Coastal Regulation Clearance",
                "Applicability": determine_app(crz_flag, crz_rem),
                "Remarks": crz_rem
            }
        ]

    # 2. Secondary / DOM Fallback: Parse Tentative Clearances table directly from DOM
    dom_rows = page.evaluate("""() => {
        const out = [];
        const tbls = Array.from(document.querySelectorAll('table'));
        const targetTable = tbls.find(t => {
            const text = (t.innerText || '').toLowerCase();
            return text.includes('approval') && text.includes('applicability');
        });

        if (!targetTable) return [];

        const rows = Array.from(targetTable.querySelectorAll('tr'));
        for (let i = 1; i < rows.length; i++) {
            const cells = Array.from(rows[i].querySelectorAll('th, td'));
            if (cells.length >= 3) {
                const sno = cells[0].innerText.trim();
                const approval = cells[1].innerText.trim();

                let app = "No";
                const cellText = cells[2].innerText.trim();
                if (/\\byes\\b/i.test(cellText)) {
                    app = "Yes";
                } else if (/\\bno\\b/i.test(cellText)) {
                    app = "No";
                }

                let remarks = "";
                if (cells.length >= 4) {
                    remarks = cells[3].innerText.replace(/\\bMore\\b/gi, '').trim();
                }

                if (approval && !/approval/i.test(approval)) {
                    out.push({
                        "S.No": sno || String(out.length + 1),
                        "Approval": approval,
                        "Applicability": app,
                        "Remarks": remarks
                    });
                }
            }
        }
        return out;
    }""")

    if not results["clearances"] and dom_rows:
        results["clearances"] = dom_rows
    elif results["clearances"] and dom_rows:
        # Merge DOM applicability with un-truncated DMN remarks
        for d_row in dom_rows:
            d_appr = d_row.get("Approval", "").lower()
            for r in results["clearances"]:
                if r.get("Approval", "").lower() in d_appr or d_appr in r.get("Approval", "").lower():
                    # Update applicability from live DOM badge
                    r["Applicability"] = d_row.get("Applicability", r["Applicability"])

    # 3. Project summary from report boxes or table
    proj_data = page.evaluate("""() => {
        const out = {};
        // Primary: Report card boxes (div.col-sm-4 / container)
        const boxes = document.querySelectorAll('div');
        for (const b of boxes) {
            if (b.children.length === 2) {
                const title = b.children[0].innerText.trim();
                const val = b.children[1].innerText.trim();
                if (['Project / Activity', 'Sub Activity', 'Project Capacity / Extent'].includes(title)) {
                    out[title] = val;
                }
            }
        }
        if (Object.keys(out).length > 0) return out;

        // Fallback: Table format
        const tables = document.querySelectorAll('table');
        for (const tbl of tables) {
            const rows = tbl.querySelectorAll('tr');
            if (rows.length >= 2) {
                const hdrs = Array.from(rows[0].querySelectorAll('th, td')).map(c => c.innerText.trim());
                if (hdrs.includes('Project/Activity') || hdrs.includes('Sub Activity')) {
                    const vals = Array.from(rows[1].querySelectorAll('td')).map(c => c.innerText.trim());
                    hdrs.forEach((h, i) => { if (h) out[h] = vals[i] || ''; });
                    return out;
                }
            }
        }
        return {};
    }""")
    results["project"] = proj_data

    # 4. Proximity / spatial layers table
    prox_data = page.evaluate("""() => {
        const tables = document.querySelectorAll('table');
        for (const tbl of tables) {
            const rows = tbl.querySelectorAll('tr');
            const hdrs = rows.length > 0
                ? Array.from(rows[0].querySelectorAll('th,td')).map(c => c.innerText.trim())
                : [];
            if (hdrs.includes('Source') && hdrs.includes('Distance')) {
                const out = [];
                for (let i = 1; i < rows.length; i++) {
                    const cells = Array.from(rows[i].querySelectorAll('td')).map(c => c.innerText.trim());
                    if (cells.length >= 2 && cells[0]) out.push({Source: cells[0], Distance: cells[1]});
                }
                return out;
            }
        }
        return [];
    }""")
    results["proximity"] = prox_data

    # 5. Toposheet & Administrative Location (State / District / Village)
    loc_data = page.evaluate("""() => {
        const out = { toposheet: '', locations: [] };

        // Toposheet No. from #tid
        const tidEl = document.querySelector('#tid');
        if (tidEl) {
            out.toposheet = tidEl.innerText.replace(/\\s+/g, ' ').trim();
        }

        // State, District, Village table (#geoLocId)
        const geoTable = document.querySelector('#geoLocId');
        if (geoTable) {
            const stateRows = geoTable.querySelectorAll('tbody tr.state-row, tbody tr');
            stateRows.forEach(sr => {
                const stateEl = sr.querySelector('.state-cell strong, td.state-cell, td:first-child strong');
                const stateName = stateEl ? stateEl.innerText.trim() : '';

                const distRows = sr.querySelectorAll('.district-row');
                if (distRows.length > 0) {
                    distRows.forEach(dr => {
                        const distEl = dr.querySelector('.dist-value, .district-name');
                        const distName = distEl ? distEl.innerText.trim() : '';

                        const villages = Array.from(dr.querySelectorAll('.village-item'))
                            .map(v => v.innerText.replace(/,/g, '').trim())
                            .filter(Boolean);
                        const villageText = villages.length > 0 ? villages.join(', ') : (dr.querySelector('.village-list')?.innerText.trim() || '');

                        if (distName || villageText) {
                            out.locations.push({
                                State: stateName,
                                District: distName,
                                Village: villageText
                            });
                        }
                    });
                } else {
                    const cells = Array.from(sr.querySelectorAll('td'));
                    if (cells.length >= 3) {
                        out.locations.push({
                            State: cells[0].innerText.trim(),
                            District: cells[1].innerText.trim(),
                            Village: cells[2].innerText.trim()
                        });
                    }
                }
            });
        }
        return out;
    }""")
    if loc_data:
        results["toposheet"] = loc_data.get("toposheet", "")
        results["administrative"] = loc_data.get("locations", [])

    return results


# ── Full automation engine ─────────────────────────────────────────────────────

def run_full_automated_lookup(
    activity_name, subactivity_name, capacity,
    location_mode, lat, lon, kml_bytes, kml_name, manual_captcha="",
):
    status = st.empty()
    status.info("Launching headless browser...")

    temp_kml_path = None
    if kml_bytes:
        temp_dir = tempfile.gettempdir()
        temp_kml_path = os.path.join(temp_dir, kml_name or "uploaded.kml")
        with open(temp_kml_path, "wb") as f:
            f.write(kml_bytes)

    with sync_playwright() as p:
        browser = p.chromium.launch(headless=True, args=["--disable-web-security"])
        page = browser.new_page(viewport={"width": 1366, "height": 900})

        intercepted_data = {}

        def handle_response(response):
            try:
                if "evaluate" in response.url and response.status == 200:
                    data = response.json()
                    if isinstance(data, list) and len(data) > 0 and ("remark_ec" in data[0] or "remark_fc" in data[0]):
                        intercepted_data["dmn_result"] = data[0]
                        logger.info("Captured DMN evaluate response: %s", data[0])
            except Exception:
                pass

        def handle_request(request):
            try:
                if "evaluate" in request.url and request.method == "POST":
                    post_data = request.post_data_json
                    if post_data and "variables" in post_data:
                        intercepted_data["dmn_request"] = post_data["variables"]
                        logger.info("Captured DMN evaluate request variables: %s", post_data["variables"])
            except Exception:
                pass

        page.on("response", handle_response)
        page.on("request", handle_request)

        # Intercept 100% accurate, case-sensitive CAPTCHA directly from canvas drawing
        page.add_init_script("""
            const orig = CanvasRenderingContext2D.prototype.fillText;
            CanvasRenderingContext2D.prototype.fillText = function(text) {
                if (text && text.length === 6) {
                    window.__PARIVESH_CAPTCHA__ = text;
                }
                return orig.apply(this, arguments);
            };
        """)

        try:
            status.info("Connecting to PARIVESH KYA Portal...")
            page.goto("https://parivesh.nic.in/kya/#/", timeout=45000)
            page.wait_for_load_state("networkidle")
            page.wait_for_timeout(2000)

            # Remove blocking overlays (keep GIS dialog intact)
            page.evaluate("""() => {
                const mob = document.getElementById('mobiledev');
                if (mob) mob.remove();
                document.querySelectorAll('.modal-backdrop, #backdrop, [id*="backdrop"]').forEach(e => e.remove());
            }""")

            # ── Activity ──────────────────────────────────────────────────
            status.info(f"Selecting Activity: {activity_name}...")
            act_ok = _select_mat_option(page, 0, activity_name.strip())
            if not act_ok:
                st.warning("Activity selection all 3 strategies failed — form may use default.")
            # Wait for Angular to cascade-load sub-activities
            page.wait_for_timeout(1500)

            # ── Sub-Activity ──────────────────────────────────────────────
            if subactivity_name and "No sub-activities" not in subactivity_name:
                status.info("Selecting Sub-Activity...")
                sub_ok = _select_mat_option(page, 1, subactivity_name.strip())
                if not sub_ok:
                    logger.warning("Sub-activity selection failed for '%s'", subactivity_name[:30])
                page.wait_for_timeout(800)

            # ── Project Capacity ──────────────────────────────────────────
            if capacity:
                try:
                    status.info(f"Filling Project Capacity: {capacity}...")
                    cap_locator = page.locator("input[type='number'], input.mat-input-element, input[placeholder*='strip'], input[placeholder*='Capacity']").first
                    cap_locator.wait_for(state="visible", timeout=6000)
                    cap_locator.click()
                    cap_locator.fill(str(capacity))
                    page.wait_for_timeout(300)
                    page.evaluate(
                        """(val) => {
                            const inp = document.querySelector("input[type='number'], input.mat-input-element");
                            if (inp) {
                                inp.value = val;
                                inp.dispatchEvent(new Event('input', {bubbles: true}));
                                inp.dispatchEvent(new Event('change', {bubbles: true}));
                            }
                        }""",
                        str(capacity),
                    )
                    logger.info("Project Capacity filled: %s", capacity)
                except Exception as e:
                    logger.warning("Capacity fill failed: %s", e)

            # ── Location ──────────────────────────────────────────────────
            if location_mode == "Upload KML" and temp_kml_path:
                status.info(f"Uploading KML: {os.path.basename(temp_kml_path)}...")
                try:
                    page.locator("mat-radio-button, [role='radio']").filter(has_text="Upload KML").first.click(force=True)
                    page.wait_for_timeout(500)
                except Exception:
                    pass
                fi = page.locator("input[type='file']").first
                if fi.count() > 0:
                    fi.set_input_files(temp_kml_path)
                    page.wait_for_timeout(1500)
            else:
                status.info(f"Entering coordinates: ({lat}, {lon})...")
                try:
                    page.locator("mat-radio-button, [role='radio']").filter(has_text="Point Location").first.click(force=True)
                    page.wait_for_timeout(500)
                except Exception:
                    pass
                lat_i = page.locator("input[placeholder*='Lat'], input[formcontrolname*='lat']").first
                lon_i = page.locator("input[placeholder*='Lon'], input[formcontrolname*='lon'], input[placeholder*='Long']").first
                if lat_i.is_visible() and lon_i.is_visible():
                    lat_i.fill(str(lat))
                    lon_i.fill(str(lon))

            # ── CAPTCHA Solving ───────────────────────────────────────────
            status.info("Resolving CAPTCHA...")
            captcha_val = (manual_captcha or "").strip()
            
            # Check if intercepted by canvas hook
            if not captcha_val:
                page.wait_for_timeout(800)
                intercepted = page.evaluate("() => window.__PARIVESH_CAPTCHA__")
                if intercepted and len(intercepted) == 6:
                    captcha_val = intercepted
                    st.session_state["last_captcha_text"] = captcha_val
                    st.session_state["last_captcha_conf"] = 1.0
                    logger.info("Captured CAPTCHA string via canvas hook: '%s'", captcha_val)

            # Fallback to OCR / canvas extraction if not intercepted
            if not captcha_val:
                captcha_bytes = _capture_captcha_canvas(page)
                if captcha_bytes:
                    with open(CAPTCHA_PNG, "wb") as f:
                        f.write(captcha_bytes)
                    captcha_auto_text, captcha_confidence = _try_onnx_solve(captcha_bytes)
                    captcha_val = captcha_auto_text
                    st.session_state["last_captcha_text"] = captcha_auto_text
                    st.session_state["last_captcha_conf"] = captcha_confidence
                    logger.info("ddddocr fallback solved CAPTCHA: '%s'", captcha_val)

            if captcha_val:
                status.info(f"Entering CAPTCHA: {captcha_val}...")
                captcha_input = page.locator("input[placeholder='Enter Captcha'], input[placeholder*='Captcha'], input[placeholder*='captcha']").first
                if captcha_input.is_visible():
                    captcha_input.fill("")
                    captcha_input.fill(captcha_val)
                page.evaluate(
                    """(val) => {
                        const inp = document.querySelector('input[placeholder*="aptcha"], input[placeholder*="Enter"]');
                        if (inp) {
                            inp.value = val;
                            inp.dispatchEvent(new Event('input', {bubbles:true}));
                            inp.dispatchEvent(new Event('change', {bubbles:true}));
                        }
                    }""",
                    captcha_val,
                )
                page.wait_for_timeout(400)

            # ── Submit Form ───────────────────────────────────────────────
            status.info("Submitting form...")
            submit = page.locator("button:has-text('Upload & Submit'), button:has-text('Submit'), button:has-text('Proceed')").first
            submit.click(force=True)
            page.wait_for_timeout(2000)

            # ── Handle GIS Confirmation Dialog ───────────────────────────
            status.info("Waiting for GIS map confirmation...")
            try:
                # Must wait for button to become ENABLED (Bharatmaps removes disabled attribute when ready)
                proceed_btn = page.locator("#proceedId:not([disabled]), button:has-text('YES'):not([disabled])").first
                proceed_btn.wait_for(state="visible", timeout=35000)
                status.info("GIS Confirmation is ready! Clicking YES...")
                page.wait_for_timeout(500)
                proceed_btn.click(force=True)
                page.evaluate("() => document.getElementById('proceedId')?.click()")
                page.wait_for_timeout(1000)
            except Exception as e:
                logger.info("GIS YES button not found or already proceeded: %s", e)

            # ── Wait for Bharatmaps GIS & Tentative Clearances Table ──────
            status.info("Waiting for Bharatmaps spatial analysis & clearance evaluation...")
            # Poll for DMN intercept or rendered clearance table rows
            for i in range(25):
                if intercepted_data.get("dmn_result"):
                    logger.info("DMN evaluate result intercepted on attempt %d!", i)
                    break
                has_clearance_rows = page.evaluate("""() => {
                    const tbls = Array.from(document.querySelectorAll('table'));
                    const target = tbls.find(t => {
                        const txt = (t.innerText || '').toLowerCase();
                        return txt.includes('approval') && txt.includes('applicability');
                    });
                    if (target && target.querySelectorAll('tr').length >= 4) {
                        return true;
                    }
                    return false;
                }""")
                if has_clearance_rows:
                    logger.info("Tentative Clearances table with 4+ rows detected in DOM!")
                    break
                page.wait_for_timeout(1000)

            # Settle time for rendering
            page.wait_for_timeout(1500)

            # ── Capture GIS Map Screenshot ────────────────────────────────
            os.makedirs("debug", exist_ok=True)
            map_path = os.path.join("debug", "parivesh_map_view.png")
            try:
                map_el = page.locator(".esri-view, #map, div.col-sm-7:has(canvas), div:has(> canvas.esri-display-object)").first
            except Exception as me:
                logger.warning("Map screenshot error: %s", me)

            # Save debug artifacts
            page.screenshot(path=os.path.join("debug", "debug_parivesh_page.png"))
            with open(os.path.join("debug", "debug_parivesh_dom.html"), "w", encoding="utf-8") as f:
                f.write(page.content())

            # ── Extract results ───────────────────────────────────────────
            status.info("Extracting clearances...")
            results = _extract_results_from_page(page, intercepted_data)
            if os.path.exists(map_path):
                results["map_png"] = map_path

            if results["clearances"]:
                status.success(f"Retrieved {len(results['clearances'])} clearance entries!")
            else:
                status.warning("No clearances found — debug artifacts saved to debug/")

            browser.close()
            return results

        except Exception as exc:
            status.error(f"Execution halted: {exc}")
            try:
                os.makedirs("debug", exist_ok=True)
                page.screenshot(path=os.path.join("debug", "debug_parivesh_error.png"))
                browser.close()
            except Exception:
                pass
            return None


# ── Streamlit Interface ────────────────────────────────────────────────────────

st.markdown("""
<div class="hero-container">
    <div class="hero-badge">
        <span class="hero-pulse"></span> PARIVESH 2.0 AUTOMATION ENGINE
    </div>
    <h1 class="hero-title">🌿 Green Clearances Intelligence Console</h1>
    <div class="hero-subtitle">
        Automated MoEFCC Tentative Clearances (Environmental, Forest, Wildlife, CRZ) & Bharatmaps GIS Spatial Analysis
    </div>
</div>
""", unsafe_allow_html=True)

col_left, col_right = st.columns([1, 1], gap="large")

with col_left:
    st.markdown("""
    <div class="section-tag">
        <span style="background: rgba(56, 189, 248, 0.15); padding: 2px 7px; border-radius: 6px;">01</span> PROJECT PARAMETERS
    </div>
    """, unsafe_allow_html=True)
    
    activities_list = load_activities()
    activity_map = {}
    for a in activities_list:
        if isinstance(a, dict):
            name = a.get("name") or a.get("activity_name") or a.get("activityName") or str(a)
            act_id = a.get("id") or a.get("activity_id") or a.get("activityId")
            activity_map[name] = act_id
        elif isinstance(a, str):
            activity_map[a] = None

    activity_options = list(activity_map.keys()) or ["Airports"]
    selected_activity = st.selectbox("Project / Activity *", options=activity_options, index=0, key="sel_activity")

    selected_act_id = activity_map.get(selected_activity)
    subactivity_names = []
    if selected_act_id is not None:
        subactivities = get_subactivities(selected_act_id)
        for s in subactivities:
            if isinstance(s, dict):
                label = s.get("name") or s.get("sub_activity_name") or s.get("subActivityName") or s.get("name_of_subactivity") or s.get("activity_name") or str(s)
                subactivity_names.append(label)
            elif isinstance(s, str):
                subactivity_names.append(s)

    selected_subactivity = st.selectbox("Sub Activity *", options=subactivity_names or ["No sub-activities available"], index=0, key="sel_subactivity")

    col_cap, col_unit = st.columns([2, 1])
    with col_cap:
        capacity_val = st.text_input("Project Extent / Capacity *", value="250")
    with col_unit:
        st.text_input("Unit", value="sqmtr", disabled=True)

    st.markdown("""
    <div class="section-tag" style="margin-top: 1.4rem;">
        <span style="background: rgba(56, 189, 248, 0.15); padding: 2px 7px; border-radius: 6px;">02</span> GEOSPATIAL LOCATION
    </div>
    """, unsafe_allow_html=True)

    loc_mode = st.radio("Location Mode", ["Upload KML", "Point Location"], horizontal=True)
    kml_bytes = None
    kml_filename = None
    lat_val, lon_val = 21.1976, 72.8356

    if loc_mode == "Upload KML":
        uploaded_kml = st.file_uploader("Upload project area .kml file *", type=["kml"], key="kml_up")
        if uploaded_kml:
            kml_bytes = uploaded_kml.read()
            kml_filename = uploaded_kml.name
            st.success(f"Loaded: `{kml_filename}` ({len(kml_bytes):,} bytes)")
    else:
        c1, c2 = st.columns(2)
        with c1:
            lat_val = st.number_input("Latitude", value=21.1976, format="%.5f")
        with c2:
            lon_val = st.number_input("Longitude", value=72.8356, format="%.5f")

    user_captcha = ""

    st.markdown("<div style='height: 10px;'></div>", unsafe_allow_html=True)
    start_btn = st.button("🚀 EVALUATE TENTATIVE CLEARANCES", type="primary", use_container_width=True, key="start_btn")


with col_right:
    st.markdown("""
    <div class="section-tag">
        <span style="background: rgba(56, 189, 248, 0.15); padding: 2px 7px; border-radius: 6px;">03</span> CLEARANCES & COMPLIANCE REPORT
    </div>
    """, unsafe_allow_html=True)

    if start_btn:
        if loc_mode == "Upload KML" and not kml_bytes:
            st.warning("Please upload a `.kml` file first.")
        else:
            with st.spinner("Processing clearance evaluation via PARIVESH portal..."):
                report = run_full_automated_lookup(
                    activity_name=selected_activity,
                    subactivity_name=selected_subactivity,
                    capacity=capacity_val,
                    location_mode=loc_mode,
                    lat=lat_val, lon=lon_val,
                    kml_bytes=kml_bytes, kml_name=kml_filename,
                    manual_captcha=user_captcha,
                )

            if report is None:
                st.error("Evaluation could not be completed. Please verify your inputs and try again.")

            elif report.get("clearances"):
                clearances = report["clearances"]
                total_count = len(clearances)
                yes_count = sum(1 for c in clearances if str(c.get("Applicability", "")).strip().lower() == "yes")
                no_count = sum(1 for c in clearances if str(c.get("Applicability", "")).strip().lower() == "no")
                toposheet_val = report.get("toposheet", "N/A") or "N/A"

                # ── KPI Stat Strip ───────────────────────────────────────────
                st.markdown(f"""
                <div class="kpi-grid">
                    <div class="kpi-card">
                        <div class="kpi-label">Total Clearances</div>
                        <div class="kpi-value">{total_count}</div>
                    </div>
                    <div class="kpi-card kpi-yes">
                        <div class="kpi-label">Applicable</div>
                        <div class="kpi-value">{yes_count}</div>
                    </div>
                    <div class="kpi-card kpi-no">
                        <div class="kpi-label">Not Required</div>
                        <div class="kpi-value">{no_count}</div>
                    </div>
                    <div class="kpi-card">
                        <div class="kpi-label">Toposheet</div>
                        <div class="kpi-value" style="font-size: 1.05rem; padding-top: 4px;">{toposheet_val}</div>
                    </div>
                </div>
                """, unsafe_allow_html=True)

                # ── Custom Executive Clearances Table ─────────────────────────
                st.markdown("#### 📋 Tentative Clearances Summary")
                st.markdown(render_clearances_html(clearances), unsafe_allow_html=True)

                # ── Project Parameters Summary ────────────────────────────────
                if report.get("project"):
                    proj = report["project"]
                    non_empty = {k: v for k, v in proj.items() if v and v != ""}
                    if non_empty:
                        with st.expander("📌 Project Parameters Summary", expanded=False):
                            st.table(non_empty)

                # ── Toposheet & Administrative Location Table ────────────────
                if report.get("toposheet") or report.get("administrative"):
                    st.markdown("#### 📍 Administrative Location & Survey Bounds")
                    st.markdown(
                        render_geoloc_html(
                            report.get("toposheet", ""),
                            report.get("administrative", [])
                        ),
                        unsafe_allow_html=True
                    )

                # ── GIS Map View ──────────────────────────────────────────────
                if report.get("map_png") and os.path.exists(report["map_png"]):
                    st.markdown("#### 🗺️ Project Area GIS Spatial View (Bharatmaps)")
                    st.image(report["map_png"], use_container_width=True)

                # ── Proximity Spatial Layers ──────────────────────────────────
                if report.get("proximity"):
                    st.markdown("#### 🌐 Proximity Spatial Layers")
                    st.dataframe(pd.DataFrame(report["proximity"]), use_container_width=True, hide_index=True)

                # ── Downloads ─────────────────────────────────────────────────
                st.markdown("---")
                col_d1, col_d2 = st.columns(2)
                with col_d1:
                    full_df = pd.DataFrame(report["clearances"])
                    st.download_button("📥 Download Clearances CSV", full_df.to_csv(index=False).encode("utf-8"), "parivesh_clearances.csv", "text/csv", use_container_width=True)
                with col_d2:
                    st.download_button("📥 Download Full Report JSON", json.dumps(report, indent=2).encode("utf-8"), "parivesh_report.json", "application/json", use_container_width=True)

            else:
                st.warning("Finished but no clearance rows found. Check debug outputs.")
    else:
        st.markdown("""
        <div class="empty-hero">
            <div class="empty-icon">🛰️</div>
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
        """, unsafe_allow_html=True)