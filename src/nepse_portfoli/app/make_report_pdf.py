from __future__ import annotations

from pathlib import Path

import pandas as pd
import matplotlib.pyplot as plt
from matplotlib.backends.backend_pdf import PdfPages

from nepse_portfoli.core.summary_pi import (
    build_symbol_summary_open,
    build_sector_summary_raw,
    plot_sector_pie,
    realized_profit_by_symbol,
)
from nepse_portfoli.io.portfolio_io import read_portfolio
from nepse_portfoli.io.git_hub_price_download import get_price_csv


# ============================================================
# CONFIG
# ============================================================

PROJECT_ROOT = Path(__file__).resolve().parents[3]
EXCEL_FILE = PROJECT_ROOT / "data" / "NEPSE_Kavrelibis_2025.xlsm"
PORTFOLIO_SHEET = "Keshav"
PRICE_COL = "Last Updated Price"

OUT_DIR = PROJECT_ROOT / "output"
OUT_DIR.mkdir(exist_ok=True)

# Tall portrait
PAGE_SIZE = (16.5, 11.7)


# ============================================================
# HELPERS
# ============================================================

def draw_header(fig, used_date: str,
                total_inv: float, total_mv: float, total_realized: float) -> None:
    # Center title
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



def load_portfolio(excel_file: Path, sheet: str) -> pd.DataFrame:
    return read_portfolio(str(excel_file), sheet)


def load_prices_latest(price_col: str) -> tuple[str, str, pd.DataFrame]:
    used_date, csv_path = get_price_csv(date_option="latest")

    price_raw = pd.read_csv(csv_path, on_bad_lines="skip", engine="python")

    if "Symbol" not in price_raw.columns:
        raise ValueError("Price file must contain a 'Symbol' column.")

    price_raw["Symbol"] = price_raw["Symbol"].astype(str).str.strip().str.upper()

    if price_col not in price_raw.columns:
        raise ValueError(f"Column '{price_col}' not found in price file.")

    df_price = price_raw[["Symbol", price_col]].rename(
        columns={price_col: "Current share Price"}
    )
    return str(used_date), str(csv_path), df_price


def _plpct_to_float(x) -> float | None:
    """Convert '12.3%' -> 0.123. Return None if blank/invalid."""
    if x is None:
        return None
    s = str(x).strip()
    if not s:
        return None
    s = s.replace("%", "").replace(",", "").strip()
    try:
        return float(s) / 100.0
    except ValueError:
        return None


def _mix_rgb(c0, c1, t: float):
    """Linear interpolate between RGB colors c0->c1 for t in [0,1]."""
    t = max(0.0, min(1.0, float(t)))
    return (c0[0] + (c1[0] - c0[0]) * t,
            c0[1] + (c1[1] - c0[1]) * t,
            c0[2] + (c1[2] - c0[2]) * t)

def wrap_header(text: str) -> str:
    """
    Split multi-word headers into two lines.
    Example: 'Avg Buy Price' -> 'Avg Buy\nPrice'
    """
    parts = text.split()
    if len(parts) <= 1:
        return text
    mid = len(parts) // 2
    return " ".join(parts[:mid]) + "\n" + " ".join(parts[mid:])

def add_table(ax, df: pd.DataFrame, max_abs_pct: float = 0.50) -> None:
    """
    Color-grade whole rows based on PL% intensity.
    max_abs_pct controls saturation:
      - 0.30 means ±30% gives strongest shading
    """
    df = df.copy().fillna("")

   # Wrap headers into two lines if needed
    wrapped_headers = [wrap_header(c) for c in df.columns]

    # Column widths (relative)
    col_widths = [
        0.035,  # SN
        0.060,  # Symbol
        0.065,  # Total Kitta
        0.070,  # Current Price
        0.075,  # Avg Buy Price
        0.085,  # Investment (NPR)
        0.085,  # Market Value (NPR)
        0.070,  # P/L (NPR)
        0.060,  # PL%
        0.055,  # Symbol_R (duplicate)
        0.055,  # Sector
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

    # Header styling
    for (r, c), cell in table.get_celld().items():
        if r == 0:
            cell.set_text_props(weight="bold")
            cell.set_fontsize(11)
            cell.set_facecolor((0.94, 0.94, 0.94))
            # ---- Increase ONLY header row height ----
    for c in range(n_cols):
        header_cell = table[(0, c)]
        header_cell.set_height(header_cell.get_height() * 1.8)

    # Gradient by PL%
    if "PL%" in df.columns:
        pl_col = list(df.columns).index("PL%")

        white = (1.0, 1.0, 1.0)
        green = (0.20, 0.70, 0.30)   # deep green
        red   = (0.85, 0.20, 0.20)   # deep red

        for i in range(n_rows):
            v = _plpct_to_float(df.iloc[i, pl_col])

            if v is None:
                row_color = white
            else:
                intensity = min(abs(v) / max_abs_pct, 1.0)
                row_color = _mix_rgb(white, green, intensity) if v >= 0 else _mix_rgb(white, red, intensity)

            for c in range(n_cols):
                table[(i + 1, c)].set_facecolor(row_color)


# ============================================================
# MAIN (ONE PAGE)
# ============================================================
SHOW_PIE = False


def make_pdf_report(
    excel_file: Path = EXCEL_FILE,
    sheet_name: str = PORTFOLIO_SHEET,
    price_col: str = PRICE_COL,
) -> Path:

    df_port = load_portfolio(excel_file, sheet_name)
    used_date, csv_path, df_price = load_prices_latest(price_col)

    symbol_summary = build_symbol_summary_open(df_port, df_price)
    sector_raw = build_sector_summary_raw(df_port, df_price)

    total_inv = float(sector_raw["Investment_NPR"].sum())
    total_mv = float(sector_raw["Market_Value_NPR"].sum())

    rp_by_symbol = realized_profit_by_symbol(df_port)
    total_realized = float(rp_by_symbol["Realized_Profit_NPR"].sum()) if not rp_by_symbol.empty else 0.0

    # ✅ Rename headings ONLY for PDF display (do it here, after symbol_summary exists)
    # Keep "PL%" unchanged so row-color gradient still works.
    symbol_summary_pdf = symbol_summary.rename(columns={
        "sn": "SN",
        "Current share Price": "Current Price",
        "Buy share price": "Avg Buy Price",
        "Investment_NPR": "Investment (NPR)",
        "Market_Value_NPR": "Market Value (NPR)",
        "PL": "P/L (NPR)",
        # "PL%": keep as-is
    })

    # ---- Duplicate Symbol after PL% ----
    cols = list(symbol_summary_pdf.columns)

    pl_idx = cols.index("PL%")
    cols.insert(pl_idx + 1, "Symbol_R")

    symbol_summary_pdf["Symbol_R"] = symbol_summary_pdf["Symbol"]

    symbol_summary_pdf = symbol_summary_pdf[cols]

    # ---- Format PL% column: round & remove % sign ----
    if "PL%" in symbol_summary_pdf.columns:
        symbol_summary_pdf["PL%"] = (
            symbol_summary_pdf["PL%"]
            .astype(str)
            .str.replace("%", "", regex=False)
            .str.replace(",", "", regex=False)
            .astype(float)
            .round(0)
            .astype(int)
            .astype(str) + "%"
        )


    out_pdf = OUT_DIR / "nepse_portfolio_report_latest.pdf"
    if out_pdf.exists():
        out_pdf.unlink()

    with PdfPages(out_pdf) as pdf:
        fig = plt.figure(figsize=PAGE_SIZE)

         # ⭐ ADD THE HEADER HERE! ⭐
        draw_header(fig, used_date, total_inv, total_mv, total_realized)

        ax_table = fig.add_axes([0.02, 0.08, 0.98, 0.82])

        ax_table.set_axis_off()
        ax_table.set_frame_on(False)     # ⬅ IMPORTANT
        add_table(ax_table, symbol_summary_pdf)

        # Pie area (bottom)
        ax_pie = fig.add_axes([0.18, 0.03, 0.64, 0.28])
        ax_pie.axis("off")

        pie_fig = plot_sector_pie(sector_raw) if SHOW_PIE else None
        if pie_fig is not None:
            pie_fig.set_size_inches(12.0, 8.0)
            pie_fig.canvas.draw()
            img = pie_fig.canvas.buffer_rgba()
            ax_pie.imshow(img)
            plt.close(pie_fig)

        fig.text(
            0.01, 0.01,
            f"Input source: MEGA Cloud ({EXCEL_FILE.name})\n"
            f"Runtime path: {str(EXCEL_FILE)}",
            fontsize=9,
            color="gray",
            ha="left",
            va="bottom"
        )


        pdf.savefig(fig, bbox_inches="tight")
        plt.close(fig)

    print(f"Saved PDF: {out_pdf}")
    print(f"Price file used: {csv_path}")
    return out_pdf


if __name__ == "__main__":
    make_pdf_report()
