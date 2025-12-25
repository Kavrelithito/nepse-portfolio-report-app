# summary of the portfoli based on symbol
#create pi chart

import pandas as pd
import matplotlib.pyplot as plt   # OK to import here for figure creation


def build_symbol_summary_open(df: pd.DataFrame, price_df: pd.DataFrame) -> pd.DataFrame:
    df = df.copy()
    df["Symbol"] = df["Symbol"].astype(str).str.strip().str.upper()

    price_df = price_df.copy()
    price_df["Symbol"] = price_df["Symbol"].astype(str).str.strip().str.upper()

    open_df = df[df["position"].astype(str).str.strip().str.lower() == "o"].copy()
    open_df = open_df.merge(price_df, on="Symbol", how="left")

    open_df["Investment_NPR"] = open_df["Buy price"] * open_df["Final holding after sell"]
    open_df["Market_Value_NPR"] = open_df["Current share Price"] * open_df["Final holding after sell"]

    def _agg_symbol(g: pd.DataFrame) -> pd.Series:
        total_kitta = g["Final holding after sell"].sum()
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

    # formatting (same style)
    keep_decimal = {"PL%"}
    for col in summary.columns:
        if col in {"sn", "Symbol", "Sector"}:
            continue
        if col in keep_decimal:
            summary[col] = summary[col].apply(lambda x: f"{x:.2%}" if pd.notnull(x) else "")
        else:
            summary[col] = summary[col].apply(lambda x: f"{int(round(x)):,}" if pd.notnull(x) else "")

    return summary


def build_sector_summary_raw(df_port: pd.DataFrame, price_df: pd.DataFrame) -> pd.DataFrame:
    df = df_port.copy()
    df["Symbol"] = df["Symbol"].astype(str).str.strip().str.upper()

    price_df = price_df.copy()
    price_df["Symbol"] = price_df["Symbol"].astype(str).str.strip().str.upper()

    open_df = df[df["position"].astype(str).str.strip().str.lower() == "o"].copy()
    open_df = open_df.merge(price_df, on="Symbol", how="left")

    open_df["Investment_NPR"] = open_df["Buy price"] * open_df["Final holding after sell"]
    open_df["Market_Value_NPR"] = open_df["Current share Price"] * open_df["Final holding after sell"]

    sector = (
        open_df.groupby("Sector", dropna=False, as_index=False)
        .agg(
            Total_Kitta=("Final holding after sell", "sum"),
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
    df["Sector"] = df["Sector"].fillna("Unknown").astype(str)
    df["Investment_NPR"] = pd.to_numeric(df["Investment_NPR"], errors="coerce").fillna(0.0)

    df = df[df["Investment_NPR"] > 0].copy()
    total = df["Investment_NPR"].sum()
    if total <= 0:
        raise ValueError("Total investment is 0; cannot plot pie chart.")

    labels = df["Sector"].tolist()
    values = df["Investment_NPR"].tolist()

    it = iter(zip(labels, values))

    def _autopct(pct):
        sector, val = next(it)
        # inside text, 3 lines: Sector / Amount / %
        return f"{sector}\n{val:,.0f}\n{pct:.1f}%"

    fig, ax = plt.subplots()
    ax.pie(
        values,
        labels=None,            # no outside labels
        autopct=_autopct,       # inside text
        pctdistance=0.72,       # inside (closer to center)
        startangle=90,
        textprops={"fontsize": 8},
    )
    ax.axis("equal")
    # no title
    return fig

