"""
PARIVESH KYA Clearance Assistant - Streamlit UI Controller
==========================================================
Modularized Streamlit application connecting:
  - parivesh_api: Master activities & sub-activities client
  - parivesh_engine: Headless Playwright browser automation & Camunda DMN evaluator
  - ui_components: Modern glassmorphism CSS design system & custom HTML table renderers
"""

import os
import json
import pandas as pd
import streamlit as st

from parivesh_api import load_activities, get_subactivities
from parivesh_engine import run_full_automated_lookup
from ui_components import (
    APP_CSS,
    HERO_HTML,
    EMPTY_STATE_HTML,
    render_clearances_html,
    render_geoloc_html,
)

# ── Streamlit Page Configuration ───────────────────────────────────────────────
st.set_page_config(
    page_title="PARIVESH KYA Clearance Assistant",
    page_icon="🌿",
    layout="wide",
)

# Inject styling and hero header
st.markdown(APP_CSS, unsafe_allow_html=True)
st.markdown(HERO_HTML, unsafe_allow_html=True)

col_left, col_right = st.columns([1, 1], gap="large")

# ── Left Column: Configuration Console ─────────────────────────────────────────
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

    st.markdown("<div style='height: 10px;'></div>", unsafe_allow_html=True)
    start_btn = st.button("🚀 EVALUATE TENTATIVE CLEARANCES", type="primary", use_container_width=True, key="start_btn")


# ── Right Column: Clearance Intelligence Report ────────────────────────────────
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
            status_box = st.empty()
            with st.spinner("Processing clearance evaluation via PARIVESH portal..."):
                report = run_full_automated_lookup(
                    activity_name=selected_activity,
                    subactivity_name=selected_subactivity,
                    capacity=capacity_val,
                    location_mode=loc_mode,
                    lat=lat_val, lon=lon_val,
                    kml_bytes=kml_bytes, kml_name=kml_filename,
                    manual_captcha="",
                    status_callback=status_box,
                    session_state=st.session_state,
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
        st.markdown(EMPTY_STATE_HTML, unsafe_allow_html=True)