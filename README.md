# 🌿 PARIVESH 2.0 KYA Clearance Assistant

An automated web application and scraper built with **Streamlit** and **Playwright** to query and extract Tentative Clearances (Environmental, Forest, Wildlife, and CRZ) from the Ministry of Environment, Forest and Climate Change (MoEFCC) **PARIVESH 2.0 KYA (Know Your Approvals)** portal.

---

## 🚀 Key Features

- **Automated KYA Evaluation:** Automates project activity selection, capacity input, and location submission on `parivesh.nic.in/kya/#/`.
- **Dual Location Modes:**
  - **Point Location:** Provide custom Latitude and Longitude coordinates.
  - **Upload KML:** Upload any project boundary `.kml` file.
- **Dual-Engine CAPTCHA Solver:**
  - **Primary:** `ddddocr` pre-trained alphanumeric OCR (~95% accuracy).
  - **Fallback:** Local custom ONNX CNN model (`captcha_model.onnx`) with strip segmentation.
  - **Manual Override:** Interactive expander in Streamlit allowing manual CAPTCHA correction if needed.
- **Camunda DMN Network Intercept:** Intercepts the portal's background `/evaluate` API response to guarantee 100% complete, un-truncated legal remarks and applicability badges (Yes/No).
- **Comprehensive Clearance Report:**
  - Full Tentative Clearances summary table across all 4 clearances (Environmental, Forest, Wildlife, CRZ).
  - Toposheet Number & hierarchical State / District / Village location tables.
  - Proximity to eco-sensitive layers, protected areas, and water bodies.

---

## 📁 Project Structure

```text
parivesh_scrap/
│
├── app.py                      # Main Streamlit web application & Playwright automation
├── captcha_solver.py           # CAPTCHA recognition engine (ddddocr + ONNX CNN fallback)
├── captcha_model.onnx          # ONNX neural network model architecture
├── captcha_model.onnx.data     # Model weights for ONNX fallback solver
├── parivesh_activities.json    # Local cache of project activities for instant dropdown loading
├── test_polygon.kml            # Sample polygon file for testing KML upload
├── README.md                   # Project documentation
└── venv/                       # Python virtual environment (dependencies & Playwright browsers)
```

---

## 🛠️ Prerequisites & Installation

### 1. Requirements
- **Python:** 3.10 or higher
- **Google Chrome / Chromium:** Managed automatically via Playwright

### 2. Setup Virtual Environment
If setting up on a new machine:
```bash
# Create virtual environment
python -m venv venv

# Activate virtual environment (Windows PowerShell)
.\venv\Scripts\Activate.ps1
```

### 3. Install Required Packages
```bash
pip install streamlit playwright ddddocr onnxruntime pillow requests pandas
playwright install chromium
```

---

## 🏃 How to Run

1. Open a terminal in the project directory:
   ```bash
   cd d:\Train\15oct26\parivesh_scrap
   ```

2. Activate the virtual environment:
   ```powershell
   .\venv\Scripts\Activate.ps1
   ```

3. Launch the Streamlit application:
   ```bash
   streamlit run app.py
   ```

4. Open your web browser and navigate to:
   ```text
   http://localhost:8501
   ```

---

## 📖 How to Use

1. **Select Activity & Sub-Activity:** Choose the relevant industry/project sector from the dropdowns.
2. **Set Project Capacity:** Enter the project extent/capacity value (e.g. `250`).
3. **Specify Location:**
   - Choose **Point Location** and enter Latitude & Longitude, OR
   - Choose **Upload KML** and upload a `.kml` boundary file (or use `test_polygon.kml` for testing).
4. **Click "Check Tentative Clearances":**
   - The app launches headless Chromium, fills all form fields, auto-solves the portal CAPTCHA, and evaluates clearance requirements.
5. **View Results:**
   - Review the Tentative Clearances table with official applicability badges (**Applicable** / **Not Applicable**).
   - Inspect the generated Toposheet number and hierarchical administrative location tables.
   - If the portal ever generates an ambiguous CAPTCHA, expand the **🔐 CAPTCHA Override** panel, enter the code manually, and re-submit.

---

## ⚖️ License & Disclaimer
This tool is designed for research, compliance assistance, and educational purposes to interact with public government environmental approval portals. Ensure compliance with PARIVESH portal terms of service when utilizing automated queries.
