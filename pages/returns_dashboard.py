
from dash import register_page, html, dcc, Input, Output, callback
import dash_bootstrap_components as dbc
import plotly.express as px
import plotly.graph_objects as go
import pandas as pd
from utils.data import load_data

register_page(__name__, path="/returns", name="İade & Müşteri")

df = load_data()

def kpi_card(title, value):
    return dbc.Card(dbc.CardBody([html.H6(title), html.H3(value)]), class_name="kpi-card")

layout = dbc.Container([
    dbc.Row([
        dbc.Col([
            dcc.DatePickerRange(
                id="ret-date",
                start_date=df["order_date"].min().date(),
                end_date=df["order_date"].max().date(),
                display_format="DD.MM.YYYY"
            )
        ], md=4),
        dbc.Col(dcc.Dropdown(sorted(df["marketplace"].unique()), id="ret-mp", multi=True, placeholder="Pazar yeri"), md=4),
        dbc.Col(dcc.Dropdown(sorted(df["category"].unique()), id="ret-cat", multi=True, placeholder="Kategori"), md=4),
    ], class_name="mb-3"),

    dbc.Row(id="ret-kpis", class_name="mb-3 g-3"),

    dbc.Row([
        dbc.Col(dcc.Graph(id="ret-pie-reasons"), md=5),
        dbc.Col(dcc.Graph(id="ret-heat-mp-cat"), md=7),
    ], class_name="mb-4"),

    dbc.Row([
        dbc.Col(dcc.Graph(id="ret-top-products"), md=12),
    ])
], fluid=True)

def _filter(dff, start, end, mp, cat):
    mask = (dff["order_date"]>=pd.to_datetime(start)) & (dff["order_date"]<=pd.to_datetime(end))
    if mp: mask &= dff["marketplace"].isin(mp)
    if cat: mask &= dff["category"].isin(cat)
    return dff.loc[mask]

@callback(
    Output("ret-kpis","children"),
    Output("ret-pie-reasons","figure"),
    Output("ret-heat-mp-cat","figure"),
    Output("ret-top-products","figure"),
    Input("ret-date","start_date"),
    Input("ret-date","end_date"),
    Input("ret-mp","value"),
    Input("ret-cat","value"),
)
def update_returns(start, end, mp, cat):
    dff = _filter(df, start, end, mp, cat)
    total_sales = dff["sales_qty"].sum()
    total_ret = dff["return_qty"].sum()
    total_loss = (dff["return_qty"] * dff["unit_price"]).sum()  # simple est.
    kpis = [
        dbc.Col(kpi_card("Toplam İade Oranı", f"{(total_ret/max(1,total_sales))*100:.1f}%"), md=3),
        dbc.Col(kpi_card("Toplam İade Adedi", f"{int(total_ret):,}"), md=3),
        dbc.Col(kpi_card("Tahmini İade Kayıp (₺)", f"{total_loss:,.0f}"), md=6),
    ]

    reasons = dff[dff["return_qty"]>0]["return_reason"].replace("", "Diğer")
    pie_df = reasons.value_counts().reset_index()
    pie_df.columns = ["reason","count"]
    fig_pie = px.pie(pie_df, values="count", names="reason", title="İade nedenleri dağılımı")

    # Heatmap: return rate by marketplace x category
    pivot = (dff.groupby(["marketplace","category"], as_index=False)
             .agg({"sales_qty":"sum","return_qty":"sum"}))
    pivot["ret_rate"] = pivot["return_qty"] / pivot["sales_qty"].replace(0, 1)
    heat = pivot.pivot(index="marketplace", columns="category", values="ret_rate").fillna(0)
    fig_heat = go.Figure(data=go.Heatmap(
        z=heat.values, x=heat.columns, y=heat.index, zmin=0, zmax=max(0.25, heat.values.max()),
        colorbar=dict(title="İade Oranı")
    ))
    fig_heat.update_layout(title="Pazar yeri × Kategori bazında iade oranı")

    top_ret = (dff.groupby(["product_name","brand"], as_index=False)
               .agg({"return_qty":"sum"})
               .sort_values("return_qty", ascending=False).head(15))
    fig_top = px.bar(top_ret, x="return_qty", y="product_name", orientation="h",
                     title="En çok iade edilen ürünler (adet)")

    return kpis, fig_pie, fig_heat, fig_top
