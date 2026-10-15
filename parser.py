"""Parse a controlled, offline sample storefront into clean CSV and JSON files."""
from __future__ import annotations
import argparse
import csv
import json
import re
from html.parser import HTMLParser
from pathlib import Path

FIELDS = ["sku", "product_name", "category", "price_inr", "rating", "availability", "source_page"]

class CatalogParser(HTMLParser):
    def __init__(self):
        super().__init__()
        self.products = []
        self.item = None
        self.capture = None
        self.depth = 0

    def handle_starttag(self, tag, attrs):
        a = dict(attrs)
        classes = set(a.get("class", "").split())
        if tag == "article" and "product" in classes:
            self.item = {"sku": a.get("data-sku", "")}
            self.depth = 1
        elif self.item is not None:
            if tag == "article":
                self.depth += 1
            for key, field in (("product-name", "product_name"), ("category", "category"), ("price", "price_inr"), ("rating", "rating"), ("stock", "availability")):
                if key in classes:
                    self.capture = field
                    break

    def handle_data(self, data):
        if self.item is not None and self.capture:
            self.item[self.capture] = self.item.get(self.capture, "") + data.strip()

    def handle_endtag(self, tag):
        if self.item is None:
            return
        if tag in {"h2", "span"}:
            self.capture = None
        if tag == "article":
            self.depth -= 1
            if self.depth == 0:
                self.products.append(self.item)
                self.item = None
                self.capture = None

def scrape(store: Path):
    found, seen = [], set()
    pages = sorted(store.glob("page-*.html"), key=lambda p: int(p.stem.split("-")[-1]))
    if not pages:
        raise FileNotFoundError(f"No page-N.html files in {store}")
    for page in pages:
        parser = CatalogParser()
        parser.feed(page.read_text(encoding="utf-8"))
        for item in parser.products:
            sku = item.get("sku", "").strip()
            if not sku or sku in seen:
                continue
            seen.add(sku)
            price = float(re.sub(r"[^0-9.]", "", item.get("price_inr", "0")))
            rating = float(item.get("rating", "0"))
            found.append({"sku": sku, "product_name": item.get("product_name", "").strip(), "category": item.get("category", "").strip(), "price_inr": price, "rating": rating, "availability": item.get("availability", "").strip(), "source_page": page.name})
    return found

def export(items, output):
    output.mkdir(parents=True, exist_ok=True)
    with (output / "products.csv").open("w", encoding="utf-8-sig", newline="") as f:
        writer = csv.DictWriter(f, fieldnames=FIELDS)
        writer.writeheader()
        writer.writerows(items)
    (output / "products.json").write_text(json.dumps(items, indent=2, ensure_ascii=False), encoding="utf-8")

def main():
    ap=argparse.ArgumentParser(description="Scrape a local sample e-commerce storefront")
    ap.add_argument("--store", type=Path, default=Path(__file__).resolve().parent / "source")
    ap.add_argument("--output", type=Path, default=Path(__file__).resolve().parent / "output")
    args=ap.parse_args()
    data=scrape(args.store)
    export(data,args.output)
    print(f"Processed {len(list(args.store.glob('page-*.html')))} pages; extracted {len(data)} unique products; CSV/JSON saved to {args.output}")

if __name__ == "__main__":
    main()
