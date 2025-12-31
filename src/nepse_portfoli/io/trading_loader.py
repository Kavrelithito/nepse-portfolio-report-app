import pandas as pd

def load_trading_sheet(path, sheet="Keshav"):
    df = pd.read_excel(
        path,
        sheet_name=sheet,
        header=3,
        usecols="B:O"
    )

    df = df.dropna(how="all")
    df = df.reset_index(drop=True)
    return df

# def load_sector_info_sheet(path, sheet="Sector info"):
#     df = pd.read_excel(
#         path,
#         sheet_name=sheet,
#         usecols="E:F",
#     )

#     # df = df.dropna()
#     # df = df.reset_index(drop=True)

#     return df

def load_sector_info_sheet(source):
    """
    Load sector info from path or uploaded file.
    No branching needed — pandas handles both.
    """
    return pd.read_csv(source, header=None)