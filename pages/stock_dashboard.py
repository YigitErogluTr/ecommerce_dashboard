
from dash import register_page, html, dcc, Input, Output, callback
import dash_bootstrap_components as dbc
import plotly.graph_objects as go
import plotly.express as px
import pandas as pd
from utils.data import load_data, load_stock

register_page(__name__, path="/stock", name="Stok Yönetimi")

df = load_data()
stock = load_stock()

product_options = (
    stock[["product_id", "product_name"]]
    .drop_duplicates()
    .assign(
        label=lambda x: x["product_name"] + " (" + x["product_id"] + ")",
        value=lambda x: x["product_id"]
    )[["label", "value"]]            # <-- fazladan alanları at
    .to_dict("records")
)

layout = dbc.Container([
    dbc.Row([
        dbc.Col(dcc.Dropdown(product_options, id="stock-product", placeholder="Ürün seç (gauge için)"), md=5),
        dbc.Col(dcc.Dropdown(sorted(stock["marketplace"].unique()), id="stock-mp", multi=True, placeholder="Pazar yeri"), md=4),
        dbc.Col(dcc.Slider(0, 30, 1, value=14, id="forecast-days", tooltip={"always_visible":True}, marks=None), md=3),
    ], class_name="mb-3"),
    dbc.Row([
        dbc.Col(dcc.Graph(id="gauge-stock"), md=4),
        dbc.Col(dcc.Graph(id="stock-by-mp"), md=4),
        dbc.Col(dcc.Graph(id="forecast-line"), md=4),
    ], class_name="mb-4"),
    dbc.Row([
        dbc.Col(dcc.Graph(id="critical-stock-table"), md=12)
    ])
], fluid=True)

@callback(
    Output("gauge-stock","figure"),
    Output("stock-by-mp","figure"),
    Output("forecast-line","figure"),
    Output("critical-stock-table","figure"),
    Input("stock-product","value"),
    Input("stock-mp","value"),
    Input("forecast-days","value"),
)
def update_stock(pid, mp_list, horizon):
    s = stock.copy()
    if mp_list:
        s = s[s["marketplace"].isin(mp_list)]
    # Gauge: pick the first matching row for product
    gauge_fig = go.Figure()
    if pid:
        row = s[s["product_id"]==pid].sort_values("current_stock", ascending=False).head(1)
        if not row.empty:
            cs = int(row["current_stock"].iloc[0])
            rl = int(row["reorder_level"].iloc[0])
            gauge_fig.add_trace(go.Indicator(
                mode="gauge+number",
                value=cs,
                title={"text":"Anlık Stok"},
                gauge={
                    "axis":{"range":[0, max(rl*2, cs*1.2, 10)]},
                    "bar":{"thickness":0.25},
                    "steps":[
                        {"range":[0, rl], "color":"#f8d7da"},
                        {"range":[rl, rl*1.5], "color":"#fff3cd"},
                        {"range":[rl*1.5, max(rl*2, cs*1.2, 10)], "color":"#d4edda"}
                    ]
                }
            ))
    gauge_fig.update_layout(height=300, margin=dict(l=10,r=10,t=40,b=10))

    # Stock by marketplace
    by_mp = s.groupby("marketplace", as_index=False).agg({"current_stock":"sum"})
    fig_mp = px.bar(by_mp, x="marketplace", y="current_stock", title="Pazar yeri bazında stok dağılımı")

    # Forecast line: naive depletion using daily_avg_sales
    f_line = go.Figure()
    if pid:
        rs = s[s["product_id"]==pid]
        if not rs.empty:
            cs_total = rs["current_stock"].sum()
            daily = max(0.2, rs["daily_avg_sales"].sum())
            days = list(range(horizon+1))
            proj = [max(0, cs_total - d*daily) for d in days]
            f_line.add_trace(go.Scatter(x=days, y=proj, mode="lines+markers", name="Proj. Stok"))
            f_line.update_layout(title=f"Stok bitiş tahmini (~{round(cs_total/daily,1)} gün)", xaxis_title="Gün", yaxis_title="Stok")

    # Critical stock table (bar chart as table-like)
    crit = s.copy()
    crit["coverage_days"] = (crit["current_stock"] / crit["daily_avg_sales"].replace(0, 0.25)).round(1)
    crit = crit.sort_values(["coverage_days","current_stock"]).head(25)
    fig_table = px.bar(crit, x="current_stock", y=crit["product_id"]+" | "+crit["marketplace"],
                       orientation="h", title="Kritik stok listesi (düşük coverage gün)",
                       hover_data=["reorder_level","daily_avg_sales","coverage_days"])

    return gauge_fig, fig_mp, f_line, fig_table
