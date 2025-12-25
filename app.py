import sys
from pathlib import Path

# project root
ROOT = Path(__file__).resolve().parent

# src folder
SRC = ROOT / "src"

# add src to Python path
sys.path.insert(0, str(SRC))

import streamlit as st
from nepse_portfoli.app.make_report_pdf import make_pdf_report


import streamlit as st

from nepse_portfoli.app.make_report_pdf import make_pdf_report

st.title("📊 NEPSE Portfolio Report Generator")

trading_file = st.file_uploader("Upload trading log (Excel)", type=["xls", "xlsx", "xlsm"])
price_file = st.file_uploader("Upload price file (CSV or Excel)", type=["csv", "xls", "xlsx"])

sheet_name = st.text_input("Sheet name", value="Keshav")
price_col = st.text_input("Price column name", value="Last Updated Price")

if st.button("Generate PDF"):
    try:
        pdf = make_pdf_report(trading_file, price_file, sheet_name, price_col)

        st.success("Report created!")
        st.download_button(
            "Download PDF",
            data=open(pdf, "rb"),
            file_name="portfolio_report.pdf",
            mime="application/pdf"
        )

    except Exception as e:
        st.error(f"Error: {e}")
