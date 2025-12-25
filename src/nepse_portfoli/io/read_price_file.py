import pandas as pd
import streamlit as st


def load_price_file(file):
    if file is None:
        return None

    fname = file.name.lower()

    if fname.endswith(".csv"):
        df = pd.read_csv(
            file,
            engine="python",
            on_bad_lines="skip"
        )
    else:
        df = pd.read_excel(file)

    df.columns = [c.strip() for c in df.columns]

    if "Symbol" not in df.columns:
        raise ValueError("Price file must contain 'Symbol' column")

    df["Symbol"] = (
        df["Symbol"].astype(str)
        .str.strip()
        .str.upper()
    )

    return df
