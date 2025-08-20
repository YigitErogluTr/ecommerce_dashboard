# app.py
from dash import Dash, html, dcc, Input, Output, State, page_registry, no_update
import dash_bootstrap_components as dbc
import dash

external_stylesheets = [dbc.themes.BOOTSTRAP]

app = Dash(
    __name__,
    use_pages=True,
    external_stylesheets=external_stylesheets,
    suppress_callback_exceptions=True
)
server = app.server

def make_nav(auth, current_path):
    """Login dışındaki sayfaları menüye ekle + Yazdır/Çıkış butonları"""
    if not (auth and auth.get("logged_in")):
        return html.Div()

    pages = [
        p for p in page_registry.values()
        if p.get("path") and p["path"] != "/"
    ]

    # Menü sıralaması için öncelik tablosu
    order = {
        "/sales": 1, "/returns": 2, "/stocks": 3, "/profit": 4,
        "/finance": 5, "/regional": 6, "/geo": 7
    }
    pages.sort(key=lambda p: order.get(p["path"], 9999))

    nav_items = [
        dbc.NavItem(
            dbc.NavLink(
                p.get("name", p["path"].strip("/").capitalize()) or "Page",
                href=p["path"],
                active=("exact" if current_path == p["path"] else False)
            )
        )
        for p in pages
    ]

    return dbc.Navbar(
        dbc.Container([
            html.Div("E-Ticaret Dashboard", className="navbar-brand"),
            dbc.Nav(nav_items, className="ms-auto"),
            dbc.Button("Yazdır / PDF", id="print-btn", color="light", className="ms-3"),
            dbc.Button("Çıkış", id="logout-btn", color="secondary", className="ms-2", n_clicks=0),
        ]),
        color="dark", dark=True, className="mb-3"
    )

app.layout = html.Div([
    dcc.Location(id="url"),
    dcc.Store(id="auth", storage_type="session"),
    dcc.Location(id="gate", refresh=True),
    html.Div(id="nav-wrap"),
    html.Div(id="print-done", style={"display": "none"}),  # Yazdır işlemi için dummy hedef
    dash.page_container,
])

# Navbar
@app.callback(
    Output("nav-wrap", "children"),
    Input("auth", "data"),
    Input("url", "pathname"),
)
def render_nav(auth, pathname):
    return make_nav(auth, pathname or "/")

def protected_prefixes():
    """Login dışındaki tüm path'leri koru"""
    paths = [p["path"] for p in page_registry.values() if p.get("path")]
    return tuple(sorted([p for p in paths if p != "/"]))

# Guard
@app.callback(
    Output("gate", "href"),
    Input("url", "pathname"),
    State("auth", "data"),
    prevent_initial_call=False
)
def guard_routes(pathname, auth):
    if pathname is None:
        return no_update
    needs_auth = any(pathname.startswith(p) for p in protected_prefixes())
    is_logged_in = bool(auth and auth.get("logged_in"))
    if needs_auth and not is_logged_in:
        return "/"
    return no_update

# Logout
@app.callback(
    Output("auth", "data", allow_duplicate=True),
    Output("gate", "href", allow_duplicate=True),
    Input("logout-btn", "n_clicks"),
    prevent_initial_call=True
)
def logout(n):
    if n:
        return {}, "/"
    return no_update, no_update

# Yazdır (clientside)
app.clientside_callback(
    """
    function(n) {
      if (n && n > 0) {
        window.print();
        return "ok";
      }
      return "";
    }
    """,
    Output("print-done", "children"),
    Input("print-btn", "n_clicks")
)

if __name__ == "__main__":
    app.run(host="0.0.0.0", port=8100, debug=True)
