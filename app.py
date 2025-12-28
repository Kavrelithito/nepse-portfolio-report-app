import sys
from pathlib import Path
import tempfile
import requests
import streamlit as st
import pandas as pd
import re
import matplotlib as plt

print("USING PYTHON:", sys.executable)

# ----- PATH SETUP -----
ROOT = Path(__file__).resolve().parent
SRC = ROOT / "src"

if str(SRC) not in sys.path:
    sys.path.append(str(SRC))
    
from nepse_portfoli.io.trading_loader import load_trading_sheet, load_sector_info_sheet

from nepse_portfoli.app.make_report_pdf import make_pdf_report
from nepse_portfoli.core.summary_pi import (
    load_sector_map,
    build_symbol_summary_open,
    build_sector_summary_raw,
    realized_profit_by_symbol,
    plot_sector_pie,
)

DEFAULT_PRICE_URL = (
    "https://raw.githubusercontent.com/Kavrelithito/"
    "nepse-portfolio-report-app/main/data/Today%27s%20Price%20-%202025-12-25.csv"
)

DEFAULT_TRADING_URL = (
    "https://raw.githubusercontent.com/Kavrelithito/"
    "nepse-portfolio-report-app/main/data/trading_journal_template.xls"
)

DEFAULT_TRADING_NAME = "data/trading_journal_template.xls"
DEFAULT_PRICE_NAME = "Today's Price - 2025-12-25.csv"


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

price_date = get_price_date(price_source, price_filename)

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


# def load_trading_sheet(path, sheet="Keshav"):
#     # Header is on 4th row visually → index=3
#     df = pd.read_excel(
#         path,
#         sheet_name=sheet,
#         header=3,
#         usecols="B:O"
#     )

#     df = df.dropna(how="all").reset_index(drop=True)
#     return df


if st.button("Generate PDF"):
    try:
        # 1️⃣ trading
        port_df = load_trading_sheet(trading_source, sheet_name)
        #sector_info_df = load_sector_info_sheet(DEFAULT_TRADING_NAME)

        
        #st.dataframe(sector_info_df)
        # 2️⃣ price
        if str(price_source.name).lower().endswith(".csv"):
            price_df = pd.read_csv(
                price_source,
                engine="python",
                on_bad_lines="skip",
            )
        else:
            price_df = pd.read_excel(price_source)

        # 3️⃣ sector mapping
        sector_df = load_sector_map(trading_source)
        #st.write("npt_2")
        #st.dataframe(sector_df)
        #st.subheader("DEBUG — OPEN POSITIONS (from build_sector_summary_raw)")
        tmp_sector_debug = build_sector_summary_raw(port_df, price_df, sector_df)

        
        # 4️⃣ summaries
        symbol_summary = build_symbol_summary_open(port_df, price_df, sector_df)
        sector_summary = build_sector_summary_raw(port_df, price_df, sector_df)
        realized_df = realized_profit_by_symbol(port_df)
 
        try:
            # fig = plot_sector_pie(sector_summary)
            fig = plot_sector_pie(sector_summary)
            st.pyplot(fig)
        except Exception as pie_err:
            st.info(str(pie_err))

        # reset file pointers
        if hasattr(trading_source, "seek"):
            trading_source.seek(0)

        if hasattr(price_source, "seek"):
            price_source.seek(0)

        # 5️⃣ build the PDF
        pdf = make_pdf_report(trading_source, price_source, sheet_name, price_col)

        st.success("Report created!")
        st.download_button(
            "Download PDF",
            data=open(pdf, "rb"),
            file_name="portfolio_report.pdf",
            mime="application/pdf",
        )

    except Exception as e:
        st.error(f"Error: {e}")



