import sys
from pathlib import Path
import tempfile
import requests
import streamlit as st
import pandas as pd
import re
import matplotlib as plt

print("USING PYTHON:", sys.executable)

st.set_page_config(layout="wide")


# ----- PATH SETUP -----
ROOT = Path(__file__).resolve().parent
SRC = ROOT / "src"

print("__file__ =", __file__)
print("ROOT =", ROOT)


if str(SRC) not in sys.path:
    sys.path.append(str(SRC))
    
from nepse_portfoli.io.trading_loader import load_trading_sheet

from nepse_portfoli.app.make_report_pdf import make_pdf_report
from nepse_portfoli.core.summary_pi import (
    
    build_symbol_summary_open,
    build_sector_summary_raw,
    realized_profit_by_symbol,
    plot_sector_pie,
    load_sector_map,
)

DEFAULT_PRICE_URL = (
    "https://raw.githubusercontent.com/Kavrelithito/nepse-portfolio-report-app/main/data/Today%27s%20Price%20-%202025-12-25.csv"
)

DEFAULT_TRADING_URL = (
    "https://raw.githubusercontent.com/Kavrelithito/nepse-portfolio-report-app/main/data/trading_journal_template.xls"
)

DEFAULT_TRADING_NAME = DEFAULT_TRADING_URL
DEFAULT_PRICE_NAME = DEFAULT_PRICE_URL

def download_to_temp(url):
    r = requests.get(url)
    r.raise_for_status()
    suffix = Path(url).suffix
    tmp = tempfile.NamedTemporaryFile(delete=False, suffix=suffix)
    tmp.write(r.content)
    tmp.seek(0)
    return tmp





st.markdown(
    """
    <h1 style="text-align:center; font-size:42px; margin-bottom:10px;">
        📊 NEPSE Portfolio Report Generator
    </h1>
    <p style="text-align:center; font-size:16px; color:#555;">
        Upload Trading Journal → Upload Price File → Generate PDF
    </p>
    """,
    unsafe_allow_html=True,
)

uploaded_trading = st.file_uploader(
    "Upload Trading Journal (Excel)",
    type=["xls", "xlsx", "xlsm"]
)

template_url = DEFAULT_TRADING_URL
r = requests.get(template_url)
st.download_button(
    "⬇️ Download example trading journal template",
    r.content,
    "trading_journal_template.xls",
    mime="application/vnd.ms-excel.sheet.macroEnabled.12",
)

uploaded_price = st.file_uploader(
    "NEPSE price file (CSV/Excel)",
    type=["csv", "xls", "xlsx"],
)

sheet_name = "Keshav"
price_col = "Last Updated Price"

sector_info= "sector_info.csv"

# trading source
if uploaded_trading:
    trading_source = uploaded_trading
    st.success(f"Using uploaded trading log: {uploaded_trading.name}")
else:
    trading_source = download_to_temp(DEFAULT_TRADING_URL)
    st.info(f"Using default trading log: **{DEFAULT_TRADING_NAME}**")

# price source
if uploaded_price:
    price_source = uploaded_price
    price_filename = uploaded_price.name
    st.success(f"Using uploaded price file: {uploaded_price.name}")
else:
    price_source = download_to_temp(DEFAULT_PRICE_URL)
    price_filename = DEFAULT_PRICE_NAME
    st.info(f"Using default price file: **{DEFAULT_PRICE_NAME}**")

#price_date = get_price_date(price_source, price_filename)

st.markdown(
    """
    <style>
        .stButton>button {
            background-color: #28a745;
            color: white;
            border-radius: 6px;
            padding: 0.6rem 1.2rem;
            border: none;
            font-weight: 600;
        }
        .stButton>button:hover {
            background-color: #1f8a39;
            color: white;
        }
    </style>
    """,
    unsafe_allow_html=True,
)

if st.button("Generate PDF"):
    try:
        # trading
        port_df = load_trading_sheet(trading_source, sheet_name)

        # sector
        ROOT = Path(__file__).resolve().parent
        sector_info_file = ROOT / "data" / "Sector_info.csv"

        sector_df = load_sector_map(sector_info_file)

        # price
        if str(price_source.name).lower().endswith(".csv"):
            price_df = pd.read_csv(price_source, engine="python", on_bad_lines="skip")
        else:
            price_df = pd.read_excel(price_source)

        # ️⃣ FIRST — build PDF + download button
        pdf = make_pdf_report(trading_source, price_source, sheet_name, price_col)

        st.success("Report created!")
        st.download_button(
            "Download PDF",
            data=open(pdf, "rb"),
            file_name="portfolio_report.pdf",
            mime="application/pdf",
        )

        # THEN summaries + charts
        symbol_summary = build_symbol_summary_open(port_df, price_df, sector_df)
        sector_summary = build_sector_summary_raw(port_df, price_df, sector_df)
        realized_df = realized_profit_by_symbol(port_df)

        st.subheader("📄 Portfolio — Open Positions")
        st.dataframe(symbol_summary)

        fig = plot_sector_pie(sector_summary)
        fig.set_size_inches(1, 1)
        # higher resolution
        fig.set_dpi(1400)
        for text in fig.axes[0].texts:
            text.set_fontsize(2)
        #st.pyplot(fig)

    except Exception as e:
        st.error(f"Error: {e}")
