
from dash import register_page, html, dcc, Input, Output, callback
import dash_bootstrap_components as dbc
import plotly.express as px
import plotly.graph_objects as go
import pandas as pd
from utils.data import load_data, resample_time

register_page(__name__, path="/finance", name="Finans & Kârlılık")

df = load_data()

def kpi(title, value):
    return dbc.Card(dbc.CardBody([html.H6(title), html.H3(value)]), class_name="kpi-card")

layout = dbc.Container([
    dbc.Row([
        dbc.Col([
            dcc.DatePickerRange(
                id="fin-date",
                start_date=df["order_date"].min().date(),
                end_date=df["order_date"].max().date(),
                display_format="DD.MM.YYYY"
            )
        ], md=5),
        dbc.Col(dcc.Dropdown(sorted(df["marketplace"].unique()), id="fin-mp", multi=True, placeholder="Pazar yeri"), md=4),
        dbc.Col(dcc.Dropdown(sorted(df["category"].unique()), id="fin-cat", multi=True, placeholder="Kategori"), md=3),
    ], class_name="mb-3"),

    dbc.Row(id="fin-kpis", class_name="g-3 mb-3"),

    dbc.Row([
        dbc.Col(dcc.Graph(id="waterfall"), md=6),
        dbc.Col(dcc.Graph(id="profit-trend"), md=6),
    ], class_name="mb-4"),

    dbc.Row([
        dbc.Col(dcc.Graph(id="low-margin-products"), md=12)
    ])
], fluid=True)

def _filter(dff, start, end, mp, cat):
    mask = (dff["order_date"]>=pd.to_datetime(start)) & (dff["order_date"]<=pd.to_datetime(end))
    if mp: mask &= dff["marketplace"].isin(mp)
    if cat: mask &= dff["category"].isin(cat)
    return dff.loc[mask]

@callback(
    Output("fin-kpis","children"),
    Output("waterfall","figure"),
    Output("profit-trend","figure"),
    Output("low-margin-products","figure"),
    Input("fin-date","start_date"),
    Input("fin-date","end_date"),
    Input("fin-mp","value"),
    Input("fin-cat","value"),
)
def update_fin(start, end, mp, cat):
    dff = _filter(df, start, end, mp, cat)

    revenue = dff["revenue"].sum()
    cogs = dff["cogs"].sum()
    commission = dff["commission"].sum()
    shipping = dff["shipping_cost"].sum()
    net = revenue - (cogs + commission + shipping)
    margin = (net / revenue * 100) if revenue>0 else 0

    kpis = [
        dbc.Col(kpi("Toplam Gelir", f"{revenue:,.0f} ₺"), md=3),
        dbc.Col(kpi("Toplam Gider", f"{(cogs+commission+shipping):,.0f} ₺"), md=3),
        dbc.Col(kpi("Net Kâr", f"{net:,.0f} ₺"), md=3),
        dbc.Col(kpi("Kâr Marjı", f"{margin:.1f}%"), md=3),
    ]

    wf = go.Figure(go.Waterfall(
        name="Finans",
        orientation="v",
        measure=["relative","relative","relative","total"],
        x=["Satış", "Komisyon", "Kargo", "Net Kâr"],
        textposition="outside",
        y=[revenue, -commission, -shipping, net - (revenue - commission - shipping)],
    ))
    wf.update_layout(title="Waterfall: Satış → Komisyon → Kargo → Net Kâr")

    ts = resample_time(dff, freq="M")
    fig_trend = px.line(ts, x="order_date", y="net_profit", title="Aylık Net Kâr Trendi")

    prod = (dff.groupby(["product_name","brand"], as_index=False)
            .agg({"revenue":"sum","cogs":"sum","commission":"sum","shipping_cost":"sum"}))
    prod["net_profit"] = prod["revenue"] - (prod["cogs"]+prod["commission"]+prod["shipping_cost"])
    prod["margin"] = prod["net_profit"] / prod["revenue"].replace(0,1)
    low = prod.sort_values("margin").head(20)
    fig_low = px.bar(low, x="margin", y="product_name", orientation="h",
                     title="Kâr marjı düşük ürünler", hover_data=["revenue","net_profit"])

    return kpis, wf, fig_trend, fig_low
