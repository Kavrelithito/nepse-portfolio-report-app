import pandas as pd


def read_sector_map(excel_file) -> pd.DataFrame:
    df = pd.read_excel(
        excel_file,
        sheet_name="Sector info",
        usecols="B:C"
    )

    cols = list(df.columns)
    if len(cols) != 2:
        raise ValueError(f"'Sector info' sheet should have 2 columns, but has: {cols}")

    df = df.rename(columns={cols[0]: "Symbol", cols[1]: "Sector"})

    df["Symbol"] = df["Symbol"].astype(str).str.strip().str.upper()
    df["Sector"] = df["Sector"].astype(str).str.strip()

    return df.drop_duplicates(subset="Symbol", keep="first")


def read_portfolio(excel_file, sheet_name: str) -> pd.DataFrame:
    df = pd.read_excel(
        excel_file,
        sheet_name=sheet_name,
        usecols="A:W",
        header=3
    ).dropna(how="all").reset_index(drop=True)

    for col in ["Selling sum", "Realized P/L"]:
        if col not in df.columns:
            df[col] = 0.0

    df["Symbol"] = df["Symbol"].astype(str).str.strip().str.upper()

    sector_map = read_sector_map(excel_file)

    return df.merge(sector_map, on="Symbol", how="left")
