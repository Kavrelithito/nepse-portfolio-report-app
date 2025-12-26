import sys
from pathlib import Path
import tempfile
import requests
import streamlit as st
import pandas as pd
import re

# ----- PATH SETUP -----
ROOT = Path(__file__).resolve().parent
SRC = ROOT / "src"

if str(SRC) not in sys.path:
    sys.path.append(str(SRC))

from nepse_portfoli.app.make_report_pdf import make_pdf_report


# ----- DEFAULT FILES FROM GITHUB -----
DEFAULT_PRICE_URL = (
    "https://raw.githubusercontent.com/Kavrelithito/"
    "nepse-portfolio-report-app/main/data/Today%27s%20Price%20-%202025-12-25.csv"
)

DEFAULT_TRADING_URL = (
    "https://raw.githubusercontent.com/Kavrelithito/"
    "nepse-portfolio-report-app/main/data/trading_journal_template.xls"
)

DEFAULT_TRADING_NAME = "trading_journal_template.xls"


DEFAULT_TRADING_NAME = "trading_journal_template.xls"
DEFAULT_PRICE_NAME = "Today's Price - 2025-12-25.csv"


# ----- HELPERS -----
def download_to_temp(url):
    r = requests.get(url)
    r.raise_for_status()

    suffix = Path(url).suffix
    tmp = tempfile.NamedTemporaryFile(delete=False, suffix=suffix)
    tmp.write(r.content)
    tmp.seek(0)

    return tmp


def extract_date_from_filename(name):
    m = re.search(r"\d{4}-\d{2}-\d{2}", name)
    return m.group() if m else None


def get_price_date(price_file, filename):
    """
    Prefer date from inside file (row2,col2), fallback to filename date.
    """

    try:
        path = price_file.name
        suffix = Path(path).suffix.lower()

        if suffix == ".csv":
            df = pd.read_csv(path)
        else:
            df = pd.read_excel(path)

        value = str(df.iloc[0, 1]).strip()

        if value and value.lower() not in ["nan", "none", ""]:
            return value

    except Exception:
        pass

    d = extract_date_from_filename(filename)
    return d if d else "Unknown"


# ----- HEADER -----
st.markdown(
    """
    <h1 style="text-align:center; font-size:42px; margin-bottom:10px;">
        📊 NEPSE Portfolio Report Generator
    </h1>

    <p style="text-align:center; font-size:16px; color:#555;">
        👉 Just 3 clicks: <b>Upload Trading Journal</b> → <b>Upload NEPSE Price File</b> → <b>Generate PDF</b><br>
        (or simply click <b>Generate PDF</b> to try with the built-in test files)
    </p>
    """,
    unsafe_allow_html=True,
)


# ----- TRADING JOURNAL -----
uploaded_trading = st.file_uploader(
    "Upload Trading Journal (Excel)",
    type=["xls", "xlsx", "xlsm"]
)

st.caption("📌 Your trading journal must follow the required format.")

# Template download
template_url = DEFAULT_TRADING_URL
r = requests.get(template_url)
st.download_button(
    "⬇️ Download example trading journal template",
    r.content,
    "trading_journal_template.xlsm",
    mime="application/vnd.ms-excel.sheet.macroEnabled.12",
)


# ----- PRICE FILE -----
uploaded_price = st.file_uploader(
    "NEPSE price file (CSV/Excel)",
    type=["csv", "xls", "xlsx"],
    help="Download the latest price list from NEPSE, then upload it here."
)


# Hidden defaults
sheet_name = "Keshav"
price_col = "Last Updated Price"


# ----- SELECT FILE SOURCES -----
# Trading
if uploaded_trading:
    trading_source = uploaded_trading
    st.success(f"Using uploaded trading log: {uploaded_trading.name}")
else:
    trading_source = download_to_temp(DEFAULT_TRADING_URL)
    st.info(f"Using default trading log from GitHub: **{DEFAULT_TRADING_NAME}**")

# Price
if uploaded_price:
    price_source = uploaded_price
    price_filename = uploaded_price.name
    st.success(f"Using uploaded price file: {uploaded_price.name}")
else:
    price_source = download_to_temp(DEFAULT_PRICE_URL)
    price_filename = DEFAULT_PRICE_NAME
    st.info(f"Using default price file from GitHub: **{DEFAULT_PRICE_NAME}**")


# ----- PRICE DATE -----
price_date = get_price_date(price_source, price_filename)
#st.caption(f"📅 Price date: **{price_date}**")


# --- Button style (green) ---
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


# ----- GENERATE REPORT -----
if st.button("Generate PDF"):
    try:
        pdf = make_pdf_report(trading_source, price_source, sheet_name, price_col)

        st.success("Report created!")
        st.download_button(
            "Download PDF",
            data=open(pdf, "rb"),
            file_name="portfolio_report.pdf",
            mime="application/pdf"
        )

    except Exception as e:
        st.error(f"Error: {e}")
