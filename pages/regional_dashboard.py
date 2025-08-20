
from dash import register_page, html, dcc, Input, Output, callback
import dash_bootstrap_components as dbc
import plotly.express as px
import pandas as pd
from utils.data import load_data

register_page(__name__, path="/regional", name="Bölgesel Analiz")

df = load_data()

layout = dbc.Container([
    dbc.Row([
        dbc.Col([
            dcc.DatePickerRange(
                id="reg-date",
                start_date=df["order_date"].min().date(),
                end_date=df["order_date"].max().date(),
                display_format="DD.MM.YYYY"
            )
        ], md=4),
        dbc.Col(dcc.Dropdown(sorted(df["marketplace"].unique()), id="reg-mp", multi=True, placeholder="Pazar yeri"), md=4),
        dbc.Col(dcc.Dropdown(sorted(df["region"].unique()), id="reg-region", multi=True, placeholder="Bölge"), md=4),
    ], class_name="mb-3"),
    dbc.Row([
        dbc.Col(dcc.Graph(id="map-sales"), md=7),
        dbc.Col(dcc.Graph(id="top-cities"), md=5),
    ], class_name="mb-4"),
    dbc.Row([
        dbc.Col(dcc.Graph(id="region-returns"), md=6),
        dbc.Col(dcc.Graph(id="delivery-by-region"), md=6),
    ])
], fluid=True)

def _filter(dff, start, end, mp, regs):
    mask = (dff["order_date"]>=pd.to_datetime(start)) & (dff["order_date"]<=pd.to_datetime(end))
    if mp: mask &= dff["marketplace"].isin(mp)
    if regs: mask &= dff["region"].isin(regs)
    return dff.loc[mask]

@callback(
    Output("map-sales","figure"),
    Output("top-cities","figure"),
    Output("region-returns","figure"),
    Output("delivery-by-region","figure"),
    Input("reg-date","start_date"),
    Input("reg-date","end_date"),
    Input("reg-mp","value"),
    Input("reg-region","value"),
)
def update_reg(start, end, mp, regs):
    dff = _filter(df, start, end, mp, regs)
    geo = (dff.groupby(["city","lat","lon"], as_index=False)
           .agg({"revenue":"sum","sales_qty":"sum","return_qty":"sum"}))
    fig_map = px.scatter_geo(
        geo, lat="lat", lon="lon",
        size="revenue", hover_name="city",
        projection="natural earth", title="Şehirlere göre satış yoğunluğu (balon boyutu = ₺)"
    )
    top = geo.sort_values("revenue", ascending=False).head(15)
    fig_top = px.bar(top, x="revenue", y="city", orientation="h", title="En çok satış yapılan şehirler")

    reg = (dff.groupby("region", as_index=False)
           .agg({"sales_qty":"sum","return_qty":"sum","delivery_days":"mean"}))
    reg["ret_rate"] = reg["return_qty"]/reg["sales_qty"].replace(0,1)
    fig_ret = px.bar(reg, x="region", y="ret_rate", title="Bölge bazında iade oranı")

    fig_del = px.bar(reg, x="region", y="delivery_days", title="Bölgeye göre ort. teslimat süresi (gün)")

    return fig_map, fig_top, fig_ret, fig_del
