# DemoCart

## What is this project used for?
DemoCart turns a multi-page product catalog into organized files for filtering, inventory review and product comparison. It demonstrates replacing repetitive copying with a repeatable extraction and quality-check pipeline.

## Features
- Parse five included HTML catalog pages.
- Extract SKU, product name, category, INR price, rating, availability and source page.
- Deduplicate products by SKU and validate names, prices and ratings.
- Export CSV, JSON and formatted Excel with filters and a frozen header.
- Write a quality report with counts, categories and average price.

## Run locally
Python 3.12 or later:
```bash
python -m venv .venv
# Activate: Windows .venv\Scripts\activate; macOS/Linux source .venv/bin/activate
python -m pip install -r requirements.txt
python run.py
python -m unittest -v
```
Outputs are written to `output/`. The included example has 60 unique products.

## Files
`parser.py`: HTML parsing and CSV/JSON export. `run.py`: validation and Excel/report generation. `source/`: sample catalog. `output/`: inspectable sample deliverables.

## Scope
This is a self-created project with fictional DemoCart products, not paid client work. It runs offline and does not scrape arbitrary websites. Adapting it to another site requires a new parser and a feasibility review.
