# DemoCart · Web Scraping Analytics Dashboard

**Working, interactive portfolio project** using a real extraction pipeline and a **fictional** sample storefront. It demonstrates how a Python web scraper turns multi-page product listings into searchable business intelligence. It is **not paid client work, real retailer data, or an automatically updating live feed**.

## At a glance

| Verification | Value |
|---|---:|
| Catalog pages | 5 |
| Extracted fictional products | 60 |
| Unique SKUs | 60 |
| Data columns | 7 |
| Dashboard analytics tests | 6 |

## Two free dashboard options

### 1) Vercel-ready browser dashboard (no Python packages)

The `docs/` folder contains a complete responsive, offline-friendly HTML/JavaScript dashboard. Data is bundled in `docs/data.js` and sourced from the extracted DemoCart CSV. Search, category, availability, rating, max-price filters, sorted product table, category bars, inventory donut, KPIs, and **filtered CSV/JSON download** work in your browser.

**Try it locally:** open `docs/index.html` by double-clicking, or serve locally:

```bash
python -m http.server 8000
```

Then visit **http://localhost:8000/docs/**. No dependencies or sign-in required.

**Deploy to Vercel (free Hobby plan, subject to eligibility):** This repository includes `vercel.json`, which publishes `docs/` as the site's static output directory. Once the GitHub changes have been committed:

1. Sign in at https://vercel.com/ with GitHub and select **Add New → Project**.
2. Import **Ankitlunawat/DemoCart**.
3. Select **Framework Preset: Other**, ensure **Root Directory:** `./` (repository root), and verify **Output Directory:** `docs`. Build command and install command are not needed for this static demo.
4. Choose **Deploy**. The generated Vercel URL will be displayed after deployment succeeds.
5. Open the URL and check the 60 products, filters, sortable rows, and CSV/JSON download before placing the public URL on Fiverr.

The Vercel frontend uses the *pre-generated* `docs/data.js`; the original Python scraper does not run on Vercel. To refresh the site, run `python run.py`, then `python scripts/sync_browser_data.py`, commit both CSV and `docs/data.js`, and push to `main` to trigger a new deployment. **No Vercel deployment or domain is assumed active until verified in the Vercel dashboard.**

### 2) Streamlit + Plotly analytics dashboard

```bash
python -m venv .venv
# Windows PowerShell:
.venv\Scripts\Activate.ps1
# macOS/Linux:
# source .venv/bin/activate
python -m pip install -r requirements-dashboard.txt
streamlit run streamlit_app.py
```

Streamlit will display a local link (normally `http://localhost:8501`). The app reads `output/products.csv` and offers filters, five KPIs, interactive Plotly charts, product explorer, CSV/JSON downloads, and a data-quality explanation tab.

The Streamlit version is provided for optional local analysis. **Vercel hosts the separate HTML/JavaScript interface in `docs/`**, not the Streamlit Python server.

## Run tests

```bash
python -m unittest discover -s tests -v
```

All tests for parsing the CSV, filtering, metrics, export round trips, empty selections and validation run with Python's standard library.

## Re-run original scraper

The repository's existing Python extraction pipeline, `parser.py`, `run.py`, and five pages in `source/`, remain intact.

```bash
python -m pip install -r requirements.txt
python run.py
```

This refreshes the original CSV, JSON, XLSX and quality report. **If the CSV changes**, regenerate `docs/data.js` with `python scripts/sync_browser_data.py` so the browser dashboard uses the same dataset. The Streamlit dashboard always loads `output/products.csv` when restarted.

## Project structure

```text
DemoCart/
  analytics.py                   # Validation/filtering/KPI/serialization
  streamlit_app.py               # Streamlit dashboard
  requirements-dashboard.txt    # Streamlit, pandas, Plotly
  docs/index.html                # Interactive, Vercel-ready web app
  docs/data.js                   # Products from original CSV
  vercel.json                    # Vercel static output directory config
  scripts/sync_browser_data.py  # Keeps browser dashboard data in sync
  tests/test_analytics.py        # Automated dashboard tests
  output/products.csv            # Original scraper output
  output/products.xlsx           # Original Excel output
  output/products.json           # Original JSON output
  parser.py, run.py, source/     # Preserved original scraping pipeline
```

## Honest portfolio positioning

> Self-initiated Python and dashboard demonstration using a fictional e-commerce sample. Parsed 5 local catalog pages to extract 60 structured product records. Built two dashboards, including an interactive public browser interface, validated filters and exports, and provided reproducible data and tests. No third-party retailer or customer data was collected.

**Privacy and reliability:** this demo needs no login, cookies, API keys, automated bypasses, or scraping of personal information. No network requests are made from the browser dashboard.