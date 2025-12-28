from __future__ import annotations


import streamlit as st
import pandas as pd
import matplotlib.pyplot as plt
from matplotlib.backends.backend_pdf import PdfPages
from pathlib import Path
import sys
import re

# make sure project root is importable
ROOT = Path(__file__).resolve().parents[2]
if str(ROOT) not in sys.path:
    sys.path.append(str(ROOT))

from nepse_portfoli.core.summary_pi import (
    build_symbol_summary_open,
    build_sector_summary_raw,
    plot_sector_pie,
    realized_profit_by_symbol,
    load_sector_map,
    
)
# 
from nepse_portfoli.io.portfolio_io import read_portfolio
    # NOTE: load_price_file already works with uploaded Streamlit files
from nepse_portfoli.io.read_price_file import load_price_file

#from app import load_trading_sheet   # add at top if needed

from nepse_portfoli.io.trading_loader import load_trading_sheet




OUT_DIR = Path("output")
OUT_DIR.mkdir(exist_ok=True)

PAGE_SIZE = (16.5, 11.7)



def extract_date_from_filename(filename: str) -> str:
    """
    Extract YYYY-MM-DD from something like:
    "Today's Price - 2025-12-25.csv"
    """
    m = re.search(r"\d{4}-\d{2}-\d{2}", filename)
    return m.group(0) if m else "Unknown"



# ------------------------------------------------------------
# HEADER TEXT
# ------------------------------------------------------------
def draw_header(fig, used_date, total_inv, total_mv, total_realized):
    fig.text(
        0.50, 0.975,
        "NEPSE Portfolio – Open Position",
        fontsize=15, weight="bold",
        color="navy",
        ha="center", va="top"
    )

    
    fig.text(
        0.50, 0.94,
        f"Price date: {used_date}  |  "
        f"Total Investment: NPR {total_inv:,.0f}  |  "
        f"Total Market Value: NPR {total_mv:,.0f}  |  "
        f"Total Realized Profit: NPR {total_realized:,.0f}",
        fontsize=13,
        weight="bold",
        ha="center", va="top"
    )


# ------------------------------------------------------------
# TABLE HELPERS (your nice formatting!)
# ------------------------------------------------------------
def wrap_header(text: str) -> str:
    parts = text.split()
    if len(parts) <= 1:
        return text
    mid = len(parts) // 2
    return " ".join(parts[:mid]) + "\n" + " ".join(parts[mid:])


def _plpct_to_float(x):
    if x is None:
        return None
    s = str(x).strip().replace("%", "").replace(",", "")
    if s == "":
        return None
    try:
        return float(s) / 100
    except:
        return None


def _mix_rgb(c0, c1, t: float):
    t = max(0.0, min(1.0, float(t)))
    return (
        c0[0] + (c1[0] - c0[0]) * t,
        c0[1] + (c1[1] - c0[1]) * t,
        c0[2] + (c1[2] - c0[2]) * t,
    )


def add_table(ax, df: pd.DataFrame, max_abs_pct=0.50):

    df = df.copy().fillna("")
    wrapped_headers = [wrap_header(c) for c in df.columns]

    col_widths = [
        0.035, 0.060, 0.065, 0.070,
        0.075, 0.085, 0.085,
        0.070, 0.060,
        0.055, 0.055
    ]

    table = ax.table(
        cellText=df.values,
        colLabels=wrapped_headers,
        colWidths=col_widths,
        loc="center",
        cellLoc="center",
    )

    table.auto_set_font_size(False)
    table.set_fontsize(11)
    table.scale(1.2, 1.4)

    n_rows, n_cols = df.shape

    # header styling
    for (r, c), cell in table.get_celld().items():
        if r == 0:
            cell.set_text_props(weight="bold")
            cell.set_fontsize(11)
            cell.set_facecolor((0.94, 0.94, 0.94))

    # increase header row height
    for c in range(n_cols):
        header_cell = table[(0, c)]
        header_cell.set_height(header_cell.get_height() * 1.8)

    # PL% gradient
    if "PL%" in df.columns:
        pl_col = list(df.columns).index("PL%")
        white = (1, 1, 1)
        green = (0.20, 0.70, 0.30)
        red = (0.85, 0.20, 0.20)

        for i in range(n_rows):
            v = _plpct_to_float(df.iloc[i, pl_col])

            if v is None:
                row_color = white
            else:
                intensity = min(abs(v) / max_abs_pct, 1.0)
                row_color = _mix_rgb(white, green, intensity) if v >= 0 else _mix_rgb(white, red, intensity)

            for c in range(n_cols):
                table[(i + 1, c)].set_facecolor(row_color)



# ------------------------------------------------------------
# MAIN PDF BUILD
# ------------------------------------------------------------
def make_pdf_report(trading_file, price_file, sheet_name, price_col):
    print("PDF RUN START")
    print("DEBUG — type(trading_file):", type(trading_file))
    print("DEBUG — type(price_file):", type(price_file))

   
    # reset uploaded files (important)
    if hasattr(trading_file, "seek"):
        trading_file.seek(0)

    if hasattr(price_file, "seek"):
        price_file.seek(0)

    if trading_file is None:
        raise ValueError("No trading log uploaded")

    if price_file is None:
        raise ValueError("No price file uploaded")

    # 1️⃣ Load trading journal (portfolio)
    df_port = load_trading_sheet(trading_file, sheet_name)

    # 2️⃣ Load price file (RAW)
    price_raw = load_price_file(price_file)

    filename = Path(str(price_file)).name
    used_date = extract_date_from_filename(filename)


    # 3️⃣ Load sector map
    sector_df = load_sector_map(trading_file)


        # 4️⃣ Build OPEN POSITIONS dataframe
    #   open_positions_df = build_open_positions(df_port)

    # 5️⃣ Build summaries
    print("PDF — calling build_symbol_summary_open()")
    symbol_summary_open = build_symbol_summary_open(
        df_port,
        price_raw,
        sector_df,
        )

    print("PDF — calling build_sector_summary_raw()")
    sector_raw = build_sector_summary_raw(
        df_port,
        price_raw,
        sector_df
    )

    print("PDF — after summaries:", list(sector_raw.columns))

    total_inv = float(sector_raw["Investment_NPR"].sum())
    total_mv = float(sector_raw["Market_Value_NPR"].sum())

    rp = realized_profit_by_symbol(df_port)
    total_realized = float(rp["Realized_Profit_NPR"].sum()) if not rp.empty else 0.0

    # rename for PDF formatting
    symbol_summary_pdf = symbol_summary_open.rename(columns={
        "sn": "SN",
        "Current share Price": "Current Price",
        "Buy share price": "Avg Buy Price",
        "Investment_NPR": "Investment (NPR)",
        "Market_Value_NPR": "Market Value (NPR)",
        "PL": "P/L (NPR)",
    })

    out_pdf = OUT_DIR / "nepse_portfolio_report_latest.pdf"

    with PdfPages(out_pdf) as pdf:
        fig = plt.figure(figsize=PAGE_SIZE)

        draw_header(fig, used_date, total_inv, total_mv, total_realized)

        ax = fig.add_axes([0.02, 0.08, 0.98, 0.82])
        ax.axis("off")

        add_table(ax, symbol_summary_pdf)

        pdf.savefig(fig, bbox_inches="tight")
        plt.close(fig)

    with PdfPages(out_pdf) as pdf:
        # -------- PAGE 1 (KEEP SAME) --------
        fig = plt.figure(figsize=PAGE_SIZE)

        draw_header(fig, used_date, total_inv, total_mv, total_realized)

        ax = fig.add_axes([0.02, 0.08, 0.98, 0.82])
        ax.axis("off")

        add_table(ax, symbol_summary_pdf)

        pdf.savefig(fig, bbox_inches="tight")
        plt.close(fig)

        print("PDF DEBUG — sector_raw columns:", list(sector_raw.columns))

        # -------- PAGE 2 (PIE CHART) --------
        pie_input = sector_raw.copy()

        if "Sector" not in pie_input.columns and "Label" in pie_input.columns:
            # rebuild Sector from Label text
            pie_input["Sector"] = pie_input["Label"].str.replace(r"\s*\(.*\)", "", regex=True)

        pie_fig = plot_sector_pie(pie_input)


        # Make sure size fits A4 landscape
        pie_fig.set_size_inches(PAGE_SIZE)

        pdf.savefig(pie_fig, bbox_inches="tight")
        plt.close(pie_fig)

    return out_pdf

if __name__ == "__main__":
    # ---- CHANGE THESE TO REAL FILE PATHS ----
    trading_file = r"C:\Users\npt_e\Documents\MEGA\Nepse_portfoli\nepse-portfolio-report-app\data\trading_journal_template.xls"
    price_file   = r"C:\Users\npt_e\Documents\MEGA\Nepse_portfoli\nepse-portfolio-report-app\data\Today's Price - 2025-12-25.csv"

    sheet_name = "Keshav"
    price_col  = "Last Updated Price"

    try:
        pdf_path = make_pdf_report(
            trading_file=trading_file,
            price_file=price_file,
            sheet_name=sheet_name,
            price_col=price_col,
        )

        print("\nPDF created successfully:\n", pdf_path)

    except Exception as e:
        print("\nFAILED while generating PDF:\n")
        print(e)
