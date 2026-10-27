"""Regenerate docs/data.js from the canonical output/products.csv (stdlib only)."""
import json
import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT))
from analytics import load_products  # noqa: E402


def main():
    rows = load_products(ROOT / "output" / "products.csv")
    target = ROOT / "docs" / "data.js"
    target.parent.mkdir(parents=True, exist_ok=True)
    target.write_text("window.DEMOCART_PRODUCTS = " + json.dumps(rows, ensure_ascii=False, separators=(",", ":")) + ";\n", encoding="utf-8")
    print(f"Synced {len(rows)} products to {target}")


if __name__ == "__main__":
    main()