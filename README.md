# 🌿 PARIVESH 2.0 KYA Clearance Assistant

An executive-grade web application and automation console built with **Streamlit** and **Playwright** to query and evaluate Tentative Clearances (Environmental, Forest, Wildlife, and CRZ) from the Ministry of Environment, Forest and Climate Change (MoEFCC) **PARIVESH 2.0 KYA (Know Your Approvals)** portal.

---

## 🚀 Key Features

- **Executive Glassmorphism UI:** Modern dark-mode console with custom typography (*Plus Jakarta Sans* & *Inter*), responsive glowing status badges, and 4-metric KPI summary cards.
- **Automated KYA Evaluation:** Automates project activity selection, sub-activity classification, capacity input, and location submission on `parivesh.nic.in/kya/#/`.
- **Dual Location Modes:**
  - **Point Location:** Provide custom Latitude and Longitude coordinates.
  - **Upload KML:** Upload any project boundary `.kml` polygon file.
- **Zero-Click CAPTCHA Engine:** Fully automatic recognition using **`ddddocr`** (~95% accuracy) backed by a local ONNX CNN fallback model (`captcha_model.onnx`).
- **Camunda DMN Network Intercept:** Intercepts the portal's background `/evaluate` decision payload to guarantee 100% complete, un-truncated legal remarks and official applicability status.
- **Comprehensive Clearance Intelligence:**
  - Full Tentative Clearances card across all 4 pillars (Environmental, Forest, Wildlife, CRZ) with glowing applicability badges.
  - Toposheet Number & hierarchical administrative location tables (State, District, Village).
  - Proximity spatial layers to eco-sensitive zones and water bodies.
  - One-click export to CSV and JSON formats.

---

## 📁 Project Structure

```text
parivesh_scrap/
│
├── app.py                      # Thin Streamlit UI controller (~180 lines)
├── parivesh_engine.py          # Playwright automation, Camunda DMN intercept & extraction engine
├── parivesh_api.py             # API client and local caching for master activities
├── ui_components.py            # Glassmorphism CSS design system & custom HTML table cards
├── captcha_solver.py           # Dual-engine CAPTCHA solver (ddddocr + ONNX CNN fallback)
├── captcha_model.onnx          # Neural network model architecture
├── captcha_model.onnx.data     # Model weights for ONNX fallback solver
├── parivesh_activities.json    # Local activities cache for instant dropdown loading
├── start_app_with_tunnel.bat   # 1-click launcher for Streamlit + Cloudflare Tunnel
├── requirements.txt            # Python dependencies for production deployment
├── Dockerfile                  # Container definition based on official Playwright Linux image
├── render.yaml                 # Blueprint configuration for cloud deployments
├── .dockerignore               # Docker build exclusions
├── .gitignore                  # Git exclusions (venv, cache, temporary files)
└── README.md                   # Project documentation
```

---

## 🛠️ Prerequisites & Installation

### 1. Requirements
- **Python:** 3.10 or higher
- **Google Chrome / Chromium:** Managed automatically via Playwright

### 2. Setup Virtual Environment
If cloning or setting up on a new machine:
```bash
# Create virtual environment
python -m venv venv

# Activate virtual environment (Windows PowerShell)
.\venv\Scripts\Activate.ps1
```

### 3. Install Required Packages
```bash
pip install -r requirements.txt
playwright install chromium
```

---

## 🏃 Running the Application

### Option A: 1-Click Launch with Cloudflare Tunnel (Recommended)
Because `parivesh.nic.in` is an Indian Government portal protected by Geo-Firewalls, running the app locally through your Indian internet connection guarantees unblocked access, while Cloudflare provides a public HTTPS URL accessible from anywhere:

1. Double-click **`start_app_with_tunnel.bat`**.
2. The script will automatically launch Streamlit and output a secure public URL (e.g. `https://your-tunnel-name.trycloudflare.com`).

---

### Option B: Local Streamlit Execution
```powershell
.\venv\Scripts\Activate.ps1
streamlit run app.py
```
Open your browser at `http://localhost:8501`.

---

### Option C: Docker Container Deployment
Build and run the containerized application:
```bash
docker build -t parivesh-kya-assistant .
docker run -p 10000:10000 parivesh-kya-assistant
```

---

## 📖 How to Use

1. **Project Specifications:** Select the relevant industry/activity and sub-activity from the dropdowns, then specify the project extent/capacity.
2. **Geospatial Location:**
   - Choose **Point Location** and enter Latitude & Longitude, OR
   - Choose **Upload KML** and upload a project `.kml` boundary.
3. **Click "EVALUATE TENTATIVE CLEARANCES":**
   - The system launches headless Chromium, fills form parameters, solves the CAPTCHA automatically, and evaluates clearance requirements via Camunda DMN.
4. **Review Report:**
   - Review the **KPI Stat Strip** (Total Clearances, Applicable count, Exempt count, Toposheet).
   - Inspect the **Tentative Clearances Summary** card with official applicability badges and un-truncated legal remarks.
   - View the hierarchical State/District/Village location breakdown and proximity buffer tables.
   - Download the full report as CSV or JSON.

---

## ⚖️ License & Disclaimer
This tool is designed for research, environmental compliance analysis, and educational purposes to interact with public government environmental approval portals. Ensure compliance with PARIVESH portal terms of service when utilizing automated queries.
