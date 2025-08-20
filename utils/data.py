
import os
import pandas as pd

DATA_DIR = os.path.join(os.path.dirname(os.path.dirname(__file__)), "data")
SALES_PATH = os.path.join(DATA_DIR, "sales_data.csv")
STOCK_PATH = os.path.join(DATA_DIR, "stock_snapshot.csv")

def load_data():
    df = pd.read_csv(SALES_PATH, parse_dates=["order_date"])
    # Financials
    df["revenue"] = df["sales_qty"] * df["unit_price"]
    df["cogs"] = df["sales_qty"] * df["unit_cost"]
    df["commission"] = df["revenue"] * df["commission_rate"]
    df["shipping_cost"] = df["sales_qty"] * df["cargo_cost"]
    df["net_profit"] = df["revenue"] - (df["cogs"] + df["commission"] + df["shipping_cost"])
    df["return_rate"] = (df["return_qty"] / df["sales_qty"]).fillna(0.0)
    return df

def load_stock():
    stock = pd.read_csv(STOCK_PATH)
    return stock

def resample_time(df, freq="D"):
    # freq: "D" daily, "W" weekly, "M" monthly
    s = (df
         .groupby(pd.Grouper(key="order_date", freq=freq))
         .agg({"revenue":"sum","sales_qty":"sum","net_profit":"sum"})
         .reset_index())
    return s
