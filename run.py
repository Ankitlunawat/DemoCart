"""Repeatable catalog extraction, validation, deduplication and spreadsheet export."""
from pathlib import Path
from datetime import datetime, timezone
import json, statistics
from parser import scrape, export
from openpyxl import Workbook
from openpyxl.styles import Font, PatternFill
ROOT=Path(__file__).resolve().parent

def run():
    rows=scrape(ROOT/'source')
    if not rows: raise ValueError('Empty catalog')
    for x in rows:
        if not x['product_name'] or x['price_inr']<=0 or not 0<=x['rating']<=5:
            raise ValueError(f"Invalid row: {x['sku']}")
    out=ROOT/'output';export(rows,out)
    wb=Workbook();ws=wb.active;ws.title='Products'
    ws.append(list(rows[0]));
    for row in rows: ws.append(list(row.values()))
    ws.freeze_panes='A2';ws.auto_filter.ref=ws.dimensions
    for cell in ws[1]:cell.font=Font(color='FFFFFF',bold=True);cell.fill=PatternFill('solid',fgColor='123047')
    for col in ws.columns:ws.column_dimensions[col[0].column_letter].width=min(48,max(len(str(c.value)) for c in col)+3)
    wb.save(out/'products.xlsx')
    report={'run_at':datetime.now(timezone.utc).isoformat(),'source':'Self-created DemoCart HTML; fictional products, not client data','pages':len(list((ROOT/'source').glob('*.html'))),'products':len(rows),'unique_skus':len({x['sku'] for x in rows}),'invalid_rows':0,'categories':sorted({x['category'] for x in rows}),'average_price_inr':round(statistics.mean(x['price_inr'] for x in rows),2),'exports':['products.csv','products.json','products.xlsx']}
    (out/'quality_report.json').write_text(json.dumps(report,indent=2));print(json.dumps(report,indent=2));return rows,report
if __name__=='__main__':run()
