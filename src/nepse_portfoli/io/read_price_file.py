import pandas as pd
import streamlit as st
from pathlib import Path


def load_price_file(file):
    if file is None:
        return None

    # --- HANDLE BOTH UploadedFile AND NORMAL PATH ---
    if hasattr(file, "name"):
        fname = file.name.lower()
        path = file
    else:
        path = str(file)
        fname = Path(path).name.lower()

    # --- READ FILE ---
    if fname.endswith(".csv"):
        df = pd.read_csv(
            path,
            engine="python",
            on_bad_lines="skip"
        )
    else:
        df = pd.read_excel(path)

    # --- CLEAN COLUMNS ---
    df.columns = [c.strip() for c in df.columns]

    if "Symbol" not in df.columns:
        raise ValueError("Price file must contain 'Symbol' column")

    df["Symbol"] = (
        df["Symbol"].astype(str)
        .str.strip()
        .str.upper()
    )

    return df
