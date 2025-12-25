import pandas as pd
from datetime import date as Date

def read_sector_map(excel_file: str) -> pd.DataFrame:
    """
    Read Symbol -> Sector from sheet 'Sector info'
    Column B = Symbol, Column C = Sector
    """

    df = pd.read_excel(
        excel_file,
        sheet_name="Sector info",
        usecols="B:C"      # Symbol in B, Sector in C
    )

    # Ensure correct column names
    cols = list(df.columns)
    if len(cols) != 2:
        raise ValueError(f"'Sector info' sheet should have 2 columns, but has: {cols}")

    df = df.rename(columns={cols[0]: "Symbol", cols[1]: "Sector"})

    # Clean up
    df["Symbol"] = df["Symbol"].astype(str).str.strip().str.upper()
    df["Sector"] = df["Sector"].astype(str).str.strip()

    # Remove duplicates
    df = df.drop_duplicates(subset="Symbol", keep="first")

    return df


def read_portfolio(excel_file: str, sheet_name: str) -> pd.DataFrame:
    """
    Read portfolio from Excel:
    - Columns: A:W
    - Header row: index=3 (row 4)
    - Drop empty rows
    - Add 'Selling sum' and 'Realized P/L' if missing
    - Merge Sector column from 'Sector info' sheet
    """

    # Read main portfolio
    df = pd.read_excel(
        excel_file,
        sheet_name=sheet_name,
        usecols="A:W",
        header=3
    )

    df = df.dropna(how="all").reset_index(drop=True)

    # Mandatory columns (fallback = 0)
    for col in ["Selling sum", "Realized P/L"]:
        if col not in df.columns:
            df[col] = 0.0

    # Clean symbol
    df["Symbol"] = df["Symbol"].astype(str).str.strip().str.upper()

    # --- Read and merge sector info ---
    sector_map = read_sector_map(excel_file)
    df = df.merge(sector_map, on="Symbol", how="left")

    return df


# --- test run ---
if __name__ == "__main__":
    df = read_portfolio("data/NEPSE_Kavrelibis_2025.xlsm", "Keshav")
    print(df.head())

