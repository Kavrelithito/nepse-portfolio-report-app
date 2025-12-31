

# summary of the portfolio + sector pie
import pandas as pd
import matplotlib.pyplot as plt
import streamlit as st


PRICE_CANDIDATES = [
    "Last Updated Price",
    "Last Updated price",
]


def _detect_price_column(price_df: pd.DataFrame) -> str:
    """Find the correct NEPSE price column."""
    for c in PRICE_CANDIDATES:
        if c in price_df.columns:
            return c

    raise ValueError(
        f"Could not find price column in NEPSE file. Found: {list(price_df.columns)}"
    )
def load_sector_map(sector_info_file) -> pd.DataFrame:
    sector_df = pd.read_csv(
        sector_info_file,sep="\t"
        
    )

    return sector_df



def build_symbol_summary_open(
    df: pd.DataFrame,
    price_df: pd.DataFrame,
    sector_df: pd.DataFrame,
) -> pd.DataFrame:

    df = df.copy()
    df["Symbol"] = df["Symbol"].astype(str).str.strip().str.upper()

    price_df = price_df.copy()
    price_df["Symbol"] = price_df["Symbol"].astype(str).str.strip().str.upper()

    # detect correct price column (returns STRING)
    price_col = _detect_price_column(price_df)

    # rename to consistent name
    price_df = price_df.rename(columns={price_col: "Last_Updated_Price"})

    # --- CLEAN + MERGE SECTOR FILE ---
    sector_df = sector_df.copy()
    sector_df["Symbol"] = sector_df["Symbol"].astype(str).str.strip().str.upper()

    # attach sector to portfolio
    df = df.merge(sector_df, on="Symbol", how="left")

    # only open positions
    open_df = df[df["position"].astype(str).str.strip().str.lower() == "o"].copy()

    # merge prices
    open_df = open_df.merge(
        price_df[["Symbol", "Last_Updated_Price"]],
        on="Symbol",
        how="left"
    )

    # cleanup numbers
    for col in ["Buy price", "Total holding", "Last_Updated_Price"]:
        open_df[col] = pd.to_numeric(
            open_df[col].astype(str).str.replace(",", "", regex=False),
            errors="coerce"
        )

    # compute values
    open_df["Investment_NPR"] = open_df["Buy price"] * open_df["Total holding"]
    open_df["Market_Value_NPR"] = open_df["Last_Updated_Price"] * open_df["Total holding"]

    def _agg_symbol(g: pd.DataFrame) -> pd.Series:
        total_kitta = g["Total holding"].sum()
        investment = g["Investment_NPR"].sum()
        market_value = g["Market_Value_NPR"].sum()

        avg_buy_price = investment / total_kitta if total_kitta else pd.NA
        current_share_price = market_value / total_kitta if total_kitta else pd.NA

        pl = market_value - investment
        pl_pct = pl / investment if investment else pd.NA

        sector = g["Sector"].dropna().iloc[0] if g["Sector"].notna().any() else "Unknown"

        return pd.Series({
            "Symbol": g.name,
            "Total Kitta": total_kitta,
            "Current share Price": current_share_price,
            "Buy share price": avg_buy_price,
            "Investment_NPR": investment,
            "Market_Value_NPR": market_value,
            "PL": pl,
            "PL%": pl_pct,
            "Sector": sector,
        })

    summary = open_df.groupby("Symbol").apply(_agg_symbol).reset_index(drop=True)
    summary.insert(0, "sn", range(1, len(summary) + 1))

    keep_decimal = {"PL%"}

    for col in summary.columns:
        if col in {"sn", "Symbol", "Sector"}:
            continue
        if col in keep_decimal:
            summary[col] = summary[col].apply(
                lambda x: f"{x:.2%}" if pd.notnull(x) else ""
            )
        else:
            summary[col] = summary[col].apply(
                lambda x: f"{int(round(x)):,}" if pd.notnull(x) else ""
            )
    print("NPT")
    print(summary)
    return summary

def build_sector_summary_raw(
    df_port: pd.DataFrame,
    price_df: pd.DataFrame,
    sector_df: pd.DataFrame,
) -> pd.DataFrame:

    df = df_port.copy()
    df["Symbol"] = df["Symbol"].astype(str).str.strip().str.upper()

    price_df = price_df.copy()
    price_df["Symbol"] = price_df["Symbol"].astype(str).str.strip().str.upper()

    price_col = _detect_price_column(price_df)
    price_df = price_df.rename(columns={price_col: "Last_Updated_Price"})

    open_df = df[df["position"].astype(str).str.strip().str.lower() == "o"].copy()

    # merge prices
    open_df = open_df.merge(
        price_df[["Symbol", "Last_Updated_Price"]],
        on="Symbol",
        how="left"
    )

    # --- MERGE SECTOR MAP (THIS IS THE IMPORTANT PART) ---
    sector_df = sector_df.copy()
    sector_df["Symbol"] = sector_df["Symbol"].astype(str).str.strip().str.upper()

    open_df = open_df.merge(
        sector_df[["Symbol", "Sector"]],
        on="Symbol",
        how="left"
    )

    print("\nDEBUG — OPEN POSITIONS (from build_sector_summary_raw)")
    print(open_df.columns)

    for col in ["Buy price", "Total holding", "Last_Updated_Price"]:
        open_df[col] = pd.to_numeric(
            open_df[col].astype(str).str.replace(",", "", regex=False),
            errors="coerce"
        )

    open_df["Investment_NPR"] = open_df["Buy price"] * open_df["Total holding"]
    open_df["Market_Value_NPR"] = open_df["Last_Updated_Price"] * open_df["Total holding"]

    sector = (
        open_df.groupby("Sector", dropna=False, as_index=False)
        .agg(
            Total_Kitta=("Total holding", "sum"),
            Investment_NPR=("Investment_NPR", "sum"),
            Market_Value_NPR=("Market_Value_NPR", "sum"),
        )
    )

    sector["Sector"] = sector["Sector"].fillna("Unknown")
    sector["PL"] = sector["Market_Value_NPR"] - sector["Investment_NPR"]
    sector["PL%"] = sector["PL"] / sector["Investment_NPR"].replace({0: pd.NA})

    total_inv = sector["Investment_NPR"].sum()
    sector["Allocation%"] = sector["Investment_NPR"] / total_inv if total_inv else pd.NA

    sector["Label"] = sector.apply(
        lambda r: f"{r['Sector']} ({r['Allocation%']*100:.1f}%)"
        if pd.notnull(r["Allocation%"]) else f"{r['Sector']} (0.0%)",
        axis=1
    )

    sector.insert(0, "sn", range(1, len(sector) + 1))
    return sector

def realized_profit_by_symbol(df: pd.DataFrame) -> pd.DataFrame:
    c = df.copy()
    c = c[c["position"].astype(str).str.strip().str.lower() == "c"].copy()

    for col in ["Sell price", "Buy price", "Total holding"]:
        c[col] = pd.to_numeric(
            c[col].astype(str).str.replace(",", "", regex=False).str.strip(),
            errors="coerce"
        )

    c = c.dropna(subset=["Symbol", "Sell price", "Buy price", "Total holding"])
    c["Realized_Profit_NPR"] = (c["Sell price"] - c["Buy price"]) * c["Total holding"]

    return (
        c.groupby("Symbol", as_index=False)["Realized_Profit_NPR"]
        .sum()
        .sort_values("Realized_Profit_NPR", ascending=False)
    )


def plot_sector_pie(sector_raw: pd.DataFrame) -> plt.Figure:
    df = sector_raw.copy()
    #st.write("TEST TEST ##########33333")
    #st.dataframe(df)
    df["Sector"] = df["Sector"].fillna("Unknown").astype(str)
    df["Investment_NPR"] = pd.to_numeric(df["Investment_NPR"], errors="coerce").fillna(0)

    df = df[df["Investment_NPR"] > 0]

    if df.empty:
        raise ValueError("No active investments — pie chart skipped.")

    # if len(df) == 1:
    #     raise ValueError(
    #         f"Portfolio contains only one sector ({df.iloc[0]['Sector']}). Pie chart skipped."
    #     )

    fig, ax = plt.subplots()
    ax.pie(
        df["Investment_NPR"],
        labels=df["Sector"],
        autopct=lambda pct: f"{pct:.1f}%",
        startangle=90,
        textprops={"fontsize": 9},
    )
    ax.axis("equal")
    return fig



