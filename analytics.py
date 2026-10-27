"""Dependency-free, testable analytics logic for the fictional DemoCart catalog."""
from __future__ import annotations
import csv
import io
import json
from collections import Counter
from pathlib import Path
from statistics import mean
from typing import Iterable

REQUIRED_FIELDS = ("sku", "product_name", "category", "price_inr", "rating", "availability", "source_page")


def load_products(path: str | Path) -> list[dict]:
    """Load and validate a CSV; never silently deduplicate or fabricate records."""
    with Path(path).open(encoding="utf-8-sig", newline="") as handle:
        reader = csv.DictReader(handle)
        missing = set(REQUIRED_FIELDS) - set(reader.fieldnames or [])
        if missing:
            raise ValueError(f"Missing required columns: {', '.join(sorted(missing))}")
        records = []
        seen = set()
        for line, raw in enumerate(reader, 2):
            sku = raw["sku"].strip()
            if not sku or sku in seen:
                raise ValueError(f"Missing or duplicate SKU at CSV line {line}: {sku!r}")
            try:
                price, rating = float(raw["price_inr"]), float(raw["rating"])
            except (ValueError, TypeError) as exc:
                raise ValueError(f"Invalid numeric values at line {line}") from exc
            if price < 0 or not 0 <= rating <= 5:
                raise ValueError(f"Out-of-range price or rating at line {line}")
            record = {key: (raw[key] or "").strip() for key in REQUIRED_FIELDS}
            if not record["product_name"] or not record["category"]:
                raise ValueError(f"Missing product name/category at line {line}")
            record["price_inr"] = price
            record["rating"] = rating
            seen.add(sku)
            records.append(record)
    return records


def filter_products(products: Iterable[dict], *, search: str = "", categories: Iterable[str] | None = None,
                    availability: str = "All", min_price: float = 0.0,
                    max_price: float = float("inf"), min_rating: float = 0.0) -> list[dict]:
    needle = search.strip().casefold()
    allowed = None if categories is None else set(categories)
    return [p for p in products
            if (not needle or needle in (p["sku"] + " " + p["product_name"] + " " + p["category"]).casefold())
            and (allowed is None or p["category"] in allowed)
            and (availability == "All" or p["availability"] == availability)
            and min_price <= p["price_inr"] <= max_price
            and p["rating"] >= min_rating]


def summarize(products: Iterable[dict]) -> dict:
    products = list(products)
    return {"products": len(products), "unique_skus": len({p["sku"] for p in products}),
            "avg_price_inr": round(mean(p["price_inr"] for p in products), 2) if products else 0,
            "avg_rating": round(mean(p["rating"] for p in products), 2) if products else 0,
            "in_stock": sum(p["availability"] == "In Stock" for p in products),
            "out_of_stock": sum(p["availability"] == "Out of Stock" for p in products),
            "categories": dict(sorted(Counter(p["category"] for p in products).items())),
            "source_pages": dict(sorted(Counter(p["source_page"] for p in products).items()))}


def to_csv(products: Iterable[dict]) -> bytes:
    output = io.StringIO(newline="")
    writer = csv.DictWriter(output, fieldnames=REQUIRED_FIELDS)
    writer.writeheader()
    for p in products:
        writer.writerow({key: p[key] for key in REQUIRED_FIELDS})
    return output.getvalue().encode("utf-8-sig")


def to_json(products: Iterable[dict]) -> bytes:
    return json.dumps(list(products), indent=2, ensure_ascii=False).encode("utf-8")