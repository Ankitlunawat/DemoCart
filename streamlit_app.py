"""DemoCart — interactive portfolio dashboard (run: streamlit run streamlit_app.py)."""
from pathlib import Path
from collections import Counter
import pandas as pd
import plotly.express as px
import streamlit as st
from analytics import load_products, filter_products, summarize, to_csv, to_json

ROOT = Path(__file__).resolve().parent
DATA = ROOT / "output" / "products.csv"

st.set_page_config(page_title="DemoCart | Product Intelligence", page_icon="📊", layout="wide", initial_sidebar_state="expanded")
st.markdown("""<style>
.block-container{padding-top:1.6rem;padding-bottom:2.2rem;max-width:1480px}
[data-testid="stMetric"]{background:#111e32;border:1px solid #243650;border-radius:15px;padding:1rem}
[data-testid="stMetricLabel"]{color:#b6c6da}
.hero{background:linear-gradient(110deg,#162c47,#0d4451);padding:24px 28px;border-radius:18px;border:1px solid #255369;margin-bottom:18px}
.hero h1{font-size:2.2rem;color:#f7fbff;margin:0}.hero p{color:#b6d7e2;margin:7px 0 0}
.demo-note{border-left:3px solid #22c7b8;padding:8px 13px;color:#c6d6e8;background:#142638;border-radius:6px}
</style>""", unsafe_allow_html=True)

@st.cache_data(show_spinner=False)
def get_products():
    return load_products(DATA)

try:
    products = get_products()
except (OSError, ValueError) as exc:
    st.error(f"Could not load validated DemoCart data: {exc}")
    st.stop()

st.markdown('<div class="hero"><h1>DemoCart · Product Intelligence</h1><p>From raw catalog pages to clean, filterable product insights — built with Python.</p></div>', unsafe_allow_html=True)
st.markdown('<div class="demo-note">PORTFOLIO DEMO · The 60 products are fictional and were extracted from five local HTML pages. This is not live market data or a client project.</div>', unsafe_allow_html=True)

with st.sidebar:
    st.title("Explore data")
    st.caption("All controls update KPIs, charts and download files.")
    search = st.text_input("Search SKU, product or category", placeholder="e.g., Atlas, SKU-0001")
    category_options = sorted({p["category"] for p in products})
    selected = st.multiselect("Categories", category_options, default=category_options)
    avail = st.selectbox("Stock status", ["All", "In Stock", "Out of Stock"])
    low = float(min(p["price_inr"] for p in products))
    high = float(max(p["price_inr"] for p in products))
    bounds = st.slider("Price range · INR", min_value=int(low), max_value=int(high)+1,
                       value=(int(low), int(high)+1), step=1)
    rating = st.slider("Minimum rating", min_value=0.0, max_value=5.0, value=0.0, step=0.5)
    st.divider()
    if st.button("Reset filters", use_container_width=True):
        st.session_state.clear()
        st.rerun()
    st.caption("Source: original DemoCart CSV · 5 sample pages")

filtered = filter_products(products, search=search, categories=selected, availability=avail,
                           min_price=bounds[0], max_price=bounds[1], min_rating=rating)
metrics = summarize(filtered)

k1,k2,k3,k4,k5 = st.columns(5)
k1.metric("Matching products", metrics["products"])
k2.metric("Avg. price", f"₹{metrics['avg_price_inr']:,.2f}")
k3.metric("Avg. rating", f"{metrics['avg_rating']:.2f} / 5")
k4.metric("In stock", metrics["in_stock"])
k5.metric("Categories", len(metrics["categories"]))

explore, data_tab, quality_tab = st.tabs(["📈 Overview", "📋 Product Explorer", "✅ Data & methodology"])
with explore:
    if not filtered:
        st.info("No products match these filters. Try broadening the search.")
    else:
        c1,c2 = st.columns(2)
        chart_data = pd.DataFrame([{"Category": k, "Products": v} for k,v in metrics["categories"].items()])
        with c1:
            fig = px.bar(chart_data, x="Category", y="Products", color="Products", color_continuous_scale="Teal",
                         title="Products by category", text_auto=True)
            fig.update_layout(showlegend=False, coloraxis_showscale=False, margin=dict(t=55,b=20,l=10,r=10))
            st.plotly_chart(fig, use_container_width=True)
        with c2:
            fig = px.pie(values=[metrics["in_stock"],metrics["out_of_stock"]],
                         names=["In Stock","Out of Stock"], title="Availability breakdown", hole=0.64,
                         color_discrete_sequence=["#20b9ae", "#eb9877"])
            fig.update_layout(margin=dict(t=55,b=20,l=10,r=10))
            st.plotly_chart(fig, use_container_width=True)
        c3,c4 = st.columns(2)
        with c3:
            fig=px.histogram(pd.DataFrame(filtered), x="price_inr", nbins=12,
                             title="Price distribution (₹)", labels={"price_inr":"Price (INR)"},
                             color_discrete_sequence=["#20b9ae"])
            fig.update_layout(margin=dict(t=55,b=20,l=10,r=10), yaxis_title="Products")
            st.plotly_chart(fig,use_container_width=True)
        with c4:
            source_df = pd.DataFrame([{"Source page": k, "Products": v} for k,v in metrics["source_pages"].items()])
            fig=px.bar(source_df,x="Source page",y="Products",title="Products by source page",text_auto=True,
                       color_discrete_sequence=["#4a9ee0"])
            fig.update_layout(margin=dict(t=55,b=20,l=10,r=10))
            st.plotly_chart(fig,use_container_width=True)
with data_tab:
    st.subheader("Explore extracted products")
    df = pd.DataFrame(filtered)
    if filtered:
        df = df.rename(columns={"sku":"SKU","product_name":"Product name","category":"Category",
                                "price_inr":"Price (₹)","rating":"Rating","availability":"Availability",
                                "source_page":"Source page"})
        st.dataframe(df, use_container_width=True, hide_index=True,
                     column_config={"Price (₹)":st.column_config.NumberColumn(format="₹%.2f"),
                                    "Rating":st.column_config.NumberColumn(format="%.1f")})
    else:
        st.info("No matching products to display or export.")
    b1,b2 = st.columns(2)
    b1.download_button("⬇ Download filtered CSV",to_csv(filtered),"democart_filtered.csv","text/csv",use_container_width=True)
    b2.download_button("⬇ Download filtered JSON",to_json(filtered),"democart_filtered.json","application/json",use_container_width=True)
    st.caption(f"Exports contain {len(filtered)} records, matching your selected filters.")
with quality_tab:
    st.subheader("Reproducible, verified sample")
    st.write("The included Python scraper reads five fictional HTML catalog pages, validates records, deduplicates by SKU, and exports the dataset. The dashboard reads that exact CSV. Nothing is fetched from real retailers or APIs.")
    overall = summarize(products)
    q1,q2,q3,q4 = st.columns(4)
    q1.metric("Source pages", len(overall["source_pages"]))
    q2.metric("Unique SKUs", overall["unique_skus"])
    q3.metric("Categories", len(overall["categories"]))
    q4.metric("Duplicate SKUs", len(products)-overall["unique_skus"])
    st.code("python run.py\npython -m unittest discover -s tests -v\nstreamlit run streamlit_app.py", language="bash")
    st.caption("Open source demo · No login required · Built for Fiverr portfolio demonstration")