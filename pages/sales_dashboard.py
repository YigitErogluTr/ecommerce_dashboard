# pages/sales_dashboard.py

from dash import register_page, html, dcc, Input, Output, callback, no_update
import dash_bootstrap_components as dbc
import plotly.express as px
import pandas as pd
import numpy as np
from datetime import date, timedelta

# ---------- DATA LOADING ----------
try:
    from utils.data import load_data as _load_data, resample_time as _resample_time
    USE_UTILS = True
except Exception:
    USE_UTILS = False

def _demo_data(n_days=420, seed=42):
    rng = np.random.default_rng(seed)
    start = pd.Timestamp.today().normalize() - pd.Timedelta(days=n_days-1)
    dates = pd.date_range(start, periods=n_days, freq="D")

    marketplaces = ["Trendyol","Hepsiburada","Amazon","N11"]
    cats = ["Elektronik","Ev & Yaşam","Giyim","Kozmetik","Spor"]
    brands = ["MarkaA","MarkaB","MarkaC","MarkaD"]
    prods = [f"Ürün {i:03d}" for i in range(1,121)]

    rows = []
    for d in dates:
        for _ in range(int(rng.integers(60,121))):
            qty = int(rng.integers(1,5))
            price = rng.uniform(150, 2500)
            rev = qty * price
            ret = int(rng.integers(0,2) == 1 and rng.random() < 0.05)
            cost = rev * rng.uniform(0.6, 0.85)
            profit = rev - cost
            rows.append({
                "order_date": d,
                "marketplace": rng.choice(marketplaces),
                "category": rng.choice(cats),
                "product_name": rng.choice(prods),
                "brand": rng.choice(brands),
                "sales_qty": qty,
                "return_qty": ret,
                "unit_price": price,
                "unit_cost": price * rng.uniform(0.55, 0.8),
                "commission_rate": rng.uniform(0.05, 0.16),
                "cargo_cost": rng.uniform(20, 120),
                "revenue": rev,
                "net_profit": profit - ret * rng.uniform(50, 300),
            })
    df = pd.DataFrame(rows)
    return df

def load_data():
    if USE_UTILS:
        try:
            return _load_data()
        except Exception:
            pass
    try:
        df = pd.read_csv("./data/sales.csv", parse_dates=["order_date"])
        return df
    except Exception:
        return _demo_data()

def resample_time(df, freq="W", date_col="order_date", value_col="revenue"):
    if USE_UTILS:
        try:
            return _resample_time(df, date_col=date_col, value_col=value_col, freq=freq)
        except Exception:
            pass
    s = (df.sort_values(date_col)
           .set_index(date_col)
           .groupby(pd.Grouper(freq=freq))[value_col]
           .sum()
           .fillna(0)
           .reset_index())
    return s.rename(columns={date_col: "order_date"})

register_page(__name__, path="/sales", name="Satış Performansı")

df = load_data().copy()

# --- Veri temizliği / türetmeler ---
df["order_date"] = pd.to_datetime(df.get("order_date"), errors="coerce")
df = df.dropna(subset=["order_date"])

# Sayısalları güvenli çevir
for c in ["sales_qty","return_qty","unit_price","unit_cost","commission_rate","cargo_cost","revenue","net_profit"]:
    if c in df.columns:
        df[c] = pd.to_numeric(df[c], errors="coerce")

# revenue yoksa türet: (satılabilir adet) * unit_price
if "revenue" not in df.columns:
    qty_eff = (df.get("sales_qty", 0).fillna(0) - df.get("return_qty", 0).fillna(0)).clip(lower=0)
    df["revenue"] = qty_eff * df.get("unit_price", 0).fillna(0)

# net_profit yoksa kabaca türet (varsa alanları kullan)
if "net_profit" not in df.columns:
    qty_eff = (df.get("sales_qty", 0).fillna(0) - df.get("return_qty", 0).fillna(0)).clip(lower=0)
    unit_price = df.get("unit_price", 0).fillna(0)
    unit_cost  = df.get("unit_cost", 0).fillna(0)
    comm_rate  = df.get("commission_rate", 0).fillna(0)  # 0–1 beklenir
    cargo      = df.get("cargo_cost", 0).fillna(0)
    gross = qty_eff * (unit_price - unit_cost)
    comm = qty_eff * unit_price * comm_rate
    df["net_profit"] = gross - comm - cargo

# Eksik kategorik kolonları doldur
for c in ["marketplace","category","product_name","brand","city","region"]:
    if c not in df.columns:
        df[c] = "Bilinmiyor"

# Nihai tip güvenliği
for c in ["revenue","sales_qty","return_qty","net_profit"]:
    df[c] = pd.to_numeric(df.get(c, 0), errors="coerce").fillna(0.0)

def kpi_card(title, value, subtitle=None):
    return dbc.Card(
        dbc.CardBody([
            html.H6(title, className="card-title mb-1"),
            html.H3(value, className="card-value mb-0"),
            html.Small(subtitle or "", className="text-muted")
        ]),
        class_name="kpi-card"
    )

# ---------------- UI ----------------
layout = dbc.Container([
    dbc.Row([
        dbc.Col([
            dcc.DatePickerRange(
                id="sales-date",
                start_date=(df["order_date"].min().date() if not df.empty else date.today()-timedelta(days=30)),
                end_date=(df["order_date"].max().date() if not df.empty else date.today()),
                display_format="DD.MM.YYYY"
            )
        ], md=4),
        dbc.Col([
            dcc.Dropdown(sorted(df["marketplace"].dropna().unique().tolist()),
                         id="sales-mp", multi=True, placeholder="Pazar yeri seç (opsiyonel)")
        ], md=4),
        dbc.Col([
            dcc.Dropdown(sorted(df["category"].dropna().unique().tolist()),
                         id="sales-cat", multi=True, placeholder="Kategori seç (opsiyonel)")
        ], md=4),
    ], class_name="mb-3"),

    dbc.Row([
        dbc.Col(dcc.RadioItems(
            id="freq",
            options=[{"label":"Günlük","value":"D"},{"label":"Haftalık","value":"W"},{"label":"Aylık","value":"M"}],
            value="W", inline=True
        ), md=6),
        dbc.Col(dcc.RadioItems(
            id="agg_mode",
            options=[{"label":"Dönemsel Toplam","value":"periodic"},
                     {"label":"Kümülatif","value":"cumulative"}],
            value="periodic", inline=True
        ), md=6, class_name="text-md-end")
    ], class_name="mb-2"),

    dbc.Row([dbc.Col(html.Div(id="data-alert"))], class_name="mb-2"),

    dbc.Row(id="sales-kpis", class_name="mb-3 g-3"),

    dbc.Row([
        dbc.Col(dcc.Graph(id="bar-mp-revenue"), md=6),
        dbc.Col(dcc.Graph(id="treemap-cat-brand"), md=6),  # <-- yeni: Kategori → Marka oranı
    ], class_name="mb-3"),

    dbc.Row([dbc.Col(dcc.Graph(id="line-total-sales"), md=12)], class_name="mb-4"),
    dbc.Row([dbc.Col(dcc.Graph(id="top-products"), md=12)])
], fluid=True)

def _filter(dff, start, end, mp, cat):
    if dff.empty:
        return dff
    if pd.isna(start) or pd.isna(end):
        start = dff["order_date"].min()
        end = dff["order_date"].max()
    mask = (dff["order_date"] >= pd.to_datetime(start)) & (dff["order_date"] <= pd.to_datetime(end))
    if mp:  mask &= dff["marketplace"].isin(mp)
    if cat: mask &= dff["category"].isin(cat)
    return dff.loc[mask].copy()

@callback(
    Output("data-alert","children"),
    Output("sales-kpis","children"),
    Output("bar-mp-revenue","figure"),
    Output("treemap-cat-brand","figure"),
    Output("line-total-sales","figure"),
    Output("top-products","figure"),
    Input("sales-date","start_date"),
    Input("sales-date","end_date"),
    Input("sales-mp","value"),
    Input("sales-cat","value"),
    Input("freq","value"),
    Input("agg_mode","value")
)
def update_sales(start, end, mp, cat, freq, agg_mode):
    if pd.to_datetime(start) > pd.to_datetime(end):
        start = df["order_date"].min().date()
        end = df["order_date"].max().date()

    dff = _filter(df, start, end, mp, cat)

    alert = None
    if dff.empty:
        alert = dbc.Alert(
            "Seçili filtrelerde veri bulunamadı. Tarih aralığını veya filtreleri genişletin.",
            color="warning", dismissable=True
        )

    # KPIs
    total_rev = float(dff["revenue"].sum()) if not dff.empty else 0.0
    total_qty = int(dff["sales_qty"].sum()) if not dff.empty else 0
    net_profit = float(dff["net_profit"].sum()) if not dff.empty else 0.0
    return_rate = (dff["return_qty"].sum() / max(1, total_qty) * 100.0) if total_qty > 0 else 0.0

    kpis = [
        dbc.Col(kpi_card("Toplam Satış (₺)", f"{total_rev:,.0f}"), md=3),
        dbc.Col(kpi_card("Toplam Adet", f"{total_qty:,}"), md=3),
        dbc.Col(kpi_card("Net Kâr (₺)", f"{net_profit:,.0f}"), md=3),
        dbc.Col(kpi_card("İade Oranı", f"{return_rate:.1f}%"), md=3),
    ]

    # Pazar yeri bar
    bar_df = (dff.groupby("marketplace", as_index=False)["revenue"].sum()
                .sort_values("revenue", ascending=False)) if not dff.empty else \
             pd.DataFrame({"marketplace": [], "revenue": []})
    fig_bar = px.bar(bar_df, x="marketplace", y="revenue", text_auto=".2s",
                     title="Pazar yeri bazında satış (₺)")
    fig_bar.update_layout(xaxis_title="", yaxis_title="Satış (₺)", margin=dict(t=60,l=10,r=10,b=10))

    # --- YENİ: Kategori → Marka treemap (satış oranı, ₺ bazlı) ---
    if not dff.empty:
        cb_df = dff.groupby(["category","brand"], as_index=False)["revenue"].sum()
    else:
        cb_df = pd.DataFrame({"category": [], "brand": [], "revenue": []})
    fig_tree_cb = px.treemap(
        cb_df, path=["category","brand"], values="revenue",
        title="Kategori → Marka satış oranı (₺)"
    )
    fig_tree_cb.update_layout(margin=dict(t=60,l=10,r=10,b=10))

    # Zaman serisi
    ts = resample_time(dff if not dff.empty else df, freq=freq, value_col="revenue")
    ts = ts.rename(columns={"revenue": "value"})
    if agg_mode == "cumulative":
        ts["value"] = ts["value"].cumsum()

    fig_line = px.line(ts, x="order_date", y="value",
                       title="Zaman serisinde toplam satış" + (" (kümülatif)" if agg_mode=="cumulative" else " (dönemsel)"))
    fig_line.update_layout(xaxis_title="", yaxis_title="Satış (₺)", margin=dict(t=60,l=10,r=10,b=10))

    # En çok satan ürünler
    top_df = (dff.groupby(["product_name","brand"], as_index=False)
                .agg(revenue=("revenue","sum"), sales_qty=("sales_qty","sum"))
                .sort_values("revenue", ascending=False)
                .head(15)) if not dff.empty else \
             pd.DataFrame({"product_name": [], "brand": [], "revenue": [], "sales_qty": []})

    fig_top = px.bar(top_df, x="revenue", y="product_name", orientation="h",
                     text="sales_qty", title="En çok satan ürünler (₺) — (etikette adet)")
    fig_top.update_layout(xaxis_title="Satış (₺)", yaxis_title="", margin=dict(t=60,l=10,r=10,b=10))
    fig_top.update_yaxes(autorange="reversed")

    return alert, kpis, fig_bar, fig_tree_cb, fig_line, fig_top
