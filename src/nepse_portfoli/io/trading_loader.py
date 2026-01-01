import pandas as pd
import requests

from urllib.parse import urlparse, unquote
from pathlib import Path
import tempfile

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

# def load_sector_info_sheet(source):
#     """
#     Load sector info from path or uploaded file.
#     No branching needed — pandas handles both.
#     """
#     return pd.read_csv(source, header=None)

def short_name(source):
    parsed = urlparse(str(source))

    if parsed.scheme:   # it's a URL
        return Path(unquote(parsed.path)).name

    return Path(str(source)).name



def download_to_temp(url):
    r = requests.get(url)
    r.raise_for_status()
    suffix = Path(url).suffix
    tmp = tempfile.NamedTemporaryFile(delete=False, suffix=suffix)
    tmp.write(r.content)
    tmp.seek(0)
    return tmp
