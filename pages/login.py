# pages/login.py
from dash import register_page, html, dcc, Input, Output, State, callback
import dash_bootstrap_components as dbc

register_page(__name__, path="/", name="Giriş")

layout = dbc.Container([
    dbc.Row([
        dbc.Col([
            dbc.Card([
                dbc.CardBody([
                    html.H3("Giriş Yap", className="mb-3"),
                    dbc.Alert(id="login-alert", is_open=False, color="danger"),
                    dbc.Form([
                        dbc.Label("Kullanıcı Adı"),
                        dbc.Input(id="login-user", placeholder="admin", type="text"),
                        dbc.Label("Şifre", className="mt-2"),
                        dbc.Input(id="login-pass", placeholder="••••", type="password"),
                        dbc.Button("Giriş", id="login-btn", color="primary", className="mt-3 w-100")
                    ]),
                    dcc.Location(id="login-nav")  # redirect için
                ])
            ], className="shadow-sm")
        ], md=4, className="mx-auto")
    ], className="mt-5")
], fluid=True)

@callback(
    Output("login-alert", "children"),
    Output("login-alert", "is_open"),
    Output("login-nav", "href"),
    Output("auth", "data", allow_duplicate=True),
    Input("login-btn", "n_clicks"),
    State("login-user", "value"),
    State("login-pass", "value"),
    prevent_initial_call=True
)
def do_login(n, user, pw):
    # Basit sabit kimlik doğrulama
    if (user or "").strip().lower() == "admin" and (pw or "") == "1234":
        # başarılı → /sales
        return "", False, "/sales", {"logged_in": True, "user": "admin"}
    # hata
    return "Hatalı kullanıcı adı veya şifre.", True, None, {}

