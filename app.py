import pathlib
import os

import pandas as pd
import numpy as np

import dash
import dash_core_components as dcc
import dash_html_components as html
import plotly.graph_objs as go
from dash.dependencies import Input, Output, State
from environs import Env

env = Env()
env.read_env()

# app initialize
app = dash.Dash(
    __name__,
    meta_tags=[
        {"name": "viewport", "content": "width=device-width, initial-scale=1.0"}
    ],
)
server = app.server
app.config["suppress_callback_exceptions"] = True

tot_chilenos = 19116208

# Load data
APP_PATH = str(pathlib.Path(__file__).parent.resolve())



# fuentes de datos
# tal vez reemplazar por SQL?
src_path = env('BUCKET_DASH_LOCATION')

df_vacunas = pd.read_csv(f"{src_path}/vacunas_diarias_edad_sexo.csv")

df_vacunas['datetime'] = pd.to_datetime(df_vacunas['datetime'])
df_vacunas['Total'] = df_vacunas[['60 o mas','Menores de 60']].sum(axis=1)

df_casos_diarios = pd.read_csv(f'{src_path}/casos_diarios.csv')
df_casos_diarios = df_casos_diarios[['date','60 o mas','Menores de 60','Totales']]
df_casos_diarios[['60 o mas','Menores de 60','Totales']] = df_casos_diarios[['60 o mas','Menores de 60','Totales']].fillna(0).astype(int)
df_casos_diarios['date'] = pd.to_datetime(df_casos_diarios['date'])

df_uci = pd.read_csv(f'{src_path}/uci_diarios.csv')

# total camas
df_camas_uci = pd.read_csv(f'{src_path}/camas_uci.csv')


def build_banner():
    return html.Div(
        id="banner",
        className="banner",
        children=[
            html.Img(src=app.get_asset_url("dash-logo.png")),
            html.H6("Impacto de la Vacuna"),
        ],
    )


def build_graph_title(title):
    return html.P(className="graph-title", children=title)


def generate_cases_stacked(processed_data):
    layout = dict(
        xaxis=dict(title="Fecha"), yaxis=dict(title="Distribución edad de contagios")
    )

    data = [
        dict(
            type="scatter",
            x=df_casos_diarios.date,
            y=df_casos_diarios['Menores de 60']/df_casos_diarios['Totales']*100,
            name="Menores de 60",
            mode="lines",
            hoverinfo="x+y+name",
            line=dict(width=0.5, color='rgb(131, 90, 241)'),
            stackgroup='one',
            marker=dict(
                symbol="hexagram-open", line={"width": "0.5"}
            )
        ),
        dict(
            type="scatter",
            x=df_casos_diarios.date,
            y=df_casos_diarios['60 o mas']/df_casos_diarios['Totales']*100,
            name="60 o mas",
            mode="lines",
            hoverinfo="x+y+name",
            stackgroup='one',
            line=dict(width=0.5, color='rgb(111, 231, 219)'),
            marker=dict(
                symbol="hexagram-open", line={"width": "0.5"}
            )
        ),
    ]

    return {"data": data, "layout": layout}

def generate_uci_dist_fig(processed_data):
    layout = dict(
        xaxis=dict(title="Fecha"), yaxis=dict(title="Distribución edad de pacientes UCI")
    )

    data = [
        dict(
            type="scatter",
            x=df_uci.date,
            y=df_uci['Menores de 60']/df_uci['Totales']*100,
            name="Menores de 60",
            mode="lines",
            hoverinfo="x+y+name",
            line=dict(width=0.5, color='rgb(131, 90, 241)'),
            stackgroup='one',
            marker=dict(
                symbol="hexagram-open", line={"width": "0.5"}
            )
        ),
        dict(
            type="scatter",
            x=df_uci.date,
            y=df_uci['60 o mas']/df_uci['Totales']*100,
            name="60 o mas",
            mode="lines",
            hoverinfo="x+y+name",
            stackgroup='one',
            line=dict(width=0.5, color='rgb(111, 231, 219)'),
            marker=dict(
                symbol="hexagram-open", line={"width": "0.5"}
            )
        ),
    ]

    return {"data": data, "layout": layout}


def generate_well_map(dff, selected_data):
    dataset = df_vacunas[df_vacunas['Dosis']=='Primera']

    layout = go.Layout(
        #margin=dict(l=30, r=0, b=20, t=40),
        showlegend=False,
        xaxis_tickformat = '%d %B (%a)<br>%Y'
    )

    data = [
        dict(
            type="scatter",
            x=df_vacunas[df_vacunas['Dosis']=='Primera'].datetime,
            y=df_vacunas[df_vacunas['Dosis']=='Primera']['Menores de 60 (%)']*100,
            name="< 60 - 1 Dosis",
            mode="lines+markers",
            hoverinfo="x+y+name",
            marker=dict(
                symbol="hexagram-open", line={"width": "0.5"}
            )
        ),
        dict(
            type="scatter",
            x=df_vacunas[df_vacunas['Dosis']=='Segunda'].datetime,
            y=df_vacunas[df_vacunas['Dosis']=='Segunda']['Menores de 60 (%)']*100,
            name="< 60 - 1 Dosis",
            mode="lines+markers",
            hoverinfo="x+y+name",
            marker=dict(
                symbol="hexagram-open", line={"width": "0.5"}
            )
        ),
        dict(
            type="scatter",
            x=df_vacunas[df_vacunas['Dosis']=='Primera'].datetime,
            y=df_vacunas[df_vacunas['Dosis']=='Primera']['60 o mas (%)']*100,
            name=">= 60 - 1 Dosis",
            mode="lines+markers",
            hoverinfo="x+y+name",
            marker=dict(
                symbol="hexagram-open", line={"width": "0.5"}
            )
        ),
        dict(
            type="scatter",
            x=df_vacunas[df_vacunas['Dosis']=='Segunda'].datetime,
            y=df_vacunas[df_vacunas['Dosis']=='Segunda']['60 o mas (%)']*100,
            name=">= 60 - 2 Dosis",
            mode="lines+markers",
            hoverinfo="x+y+name",
            marker=dict(
                symbol="hexagram-open", line={"width": "0.5"}
            )
        )
    ]


    return {"data": data, "layout": layout}


def generate_vacs_total(dff, selected_data, contour_visible, marker_visible):

    # Generate contour

    layout = go.Layout(
        #margin=dict(l=30, r=0, b=20, t=40),
        showlegend=False,
        xaxis_tickformat = '%d %B (%a)<br>%Y'
    )

    data = [
        dict(
            type="scatter",
            x=df_vacunas[df_vacunas['Dosis']=='Primera'].datetime,
            y=df_vacunas[df_vacunas['Dosis']=='Primera']['Total']/tot_chilenos*100,
            name="1 Dosis",
            mode="lines+markers",
            hoverinfo="x+y+name",
            marker=dict(
                symbol="hexagram-open", line={"width": "0.5"}
            )
        ),
        dict(
            type="scatter",
            x=df_vacunas[df_vacunas['Dosis']=='Segunda'].datetime,
            y=df_vacunas[df_vacunas['Dosis']=='Segunda']['Total']/tot_chilenos*100,
            name="2 Dosis",
            mode="lines+markers",
            hoverinfo="x+y+name",
            marker=dict(
                symbol="hexagram-open", line={"width": "0.5"}
            )
        )
    ]

    return {"data": data, "layout": layout}


def generate_contour_text(a, b, c, name, text, visible):
    return dict(
        type="scatterternary",
        a=[a],
        b=[b],
        c=[c],
        name=name,
        text=text,
        mode="text",
        hoverinfo="none",
        textposition="middle center",
        textfont={"size": 11, "color": "#000000", "family": "sans-serif"},
        showlegend=False,
        legendgroup="Rock type",
        visible=visible,
    )


def generate_formation_bar(dff, selected_data):

    layout = go.Layout(
        #margin=dict(l=30, r=0, b=20, t=40),
        showlegend=False,
        xaxis_tickformat = '%d %B (%a)<br>%Y'
    )

    data = [
        dict(
            type="scatter",
            x=df_casos_diarios.date,
            y=df_casos_diarios['Menores de 60'],
            name="Menores de 60",
            mode="lines+markers",
            hoverinfo="x+y+name",
            marker=dict(
                symbol="hexagram-open", line={"width": "0.5"}
            )
        ),
        dict(
            type="scatter",
            x=df_casos_diarios.date,
            y=df_casos_diarios['60 o mas'],
            name="60 o más",
            mode="lines+markers",
            hoverinfo="x+y+name",
            marker=dict(
                symbol="hexagram-open", line={"width": "0.5"}
            )
        )
    ]

    return {"data": data, "layout": layout}


# Helper for extracting select index from mapbox and tern selectData
def get_selection(data, formation, selection_data, starting_index):
    ind = []
    current_curve = data["fm_name"].unique().tolist().index(formation)
    for point in selection_data["points"]:
        if point["curveNumber"] - starting_index == current_curve:
            ind.append(point["pointNumber"])
    return ind

def generate_uci_ages_fig(*args):
    layout = go.Layout(
        #margin=dict(l=30, r=0, b=20, t=40),
        xaxis_tickformat = '%d %B (%a)<br>%Y'
    )

    data = [
        dict(
            type="scatter",
            x=df_uci.date,
            y=df_uci['Menores de 60'],
            name="Menores de 60",
            mode="lines+markers",
            hoverinfo="x+y+name",
            stackgroup='one',
            marker=dict(
                symbol="hexagram-open", line={"width": "0.5"}
            )
        ),
        dict(
            type="scatter",
            x=df_uci.date,
            y=df_uci['60 o mas'],
            name="60 o más",
            mode="lines+markers",
            hoverinfo="x+y+name",
            stackgroup='one',
            marker=dict(
                symbol="hexagram-open", line={"width": "0.5"}
            )
        ),
        dict(
            type="scatter",
            x=df_camas_uci.date,
            y=df_camas_uci['Camas UCI Habilitadas'],
            name="Total camas UCI Habilitadas",
            mode="lines",
            hoverinfo="x+y+name",
            line=dict(width=0.5, color='black', dash='dash'),
            marker=dict(
                symbol="hexagram-open", line={"width": "0.5"}
            )
        ),
        dict(
            type="scatter",
            x=df_camas_uci.date,
            y=df_camas_uci['Camas no Covid-19 ocupadas'],
            name="Camas no Covid-19 ocupadas",
            mode="lines",
            hoverinfo="x+y+name",
            stackgroup='one',
            marker=dict(
                symbol="hexagram-open", line={"width": "0.5"}
            )
        ),
    ]

    return {"data": data, "layout": layout}

# Helper for extracting select index from bar
def get_selection_by_bar(bar_selected_data):
    dict = {}
    if bar_selected_data is not None:
        for point in bar_selected_data["points"]:
            if point["x"] is not None:
                dict[(point["x"])] = list(range(0, point["y"]))
    return dict


app.layout = html.Div(
    children=[
        html.Div(
            id="top-row",
            children=[
                html.Div(
                    className="row",
                    id="top-row-header",
                    children=[
                        html.Div(
                            id="header-container",
                            children=[
                                build_banner(),
                                html.P(
                                    id="instructions",
                                    children="Dashboard para visualizar el impacto de la vacuna sobre la pandemia"
                                    "siguiendo la idea de <a href='https://ourworldindata.org/vaccination-israel-impact'>Ourworldindata</a>."
                                    "Hecho por Felipe Acuña. "
                                )
                            ],
                        )
                    ],
                ),
                html.Div(
                    className="row",
                    id="top-row-graphs",
                    children=[
                        # Well map
                        html.Div(
                            id="well-map-container",
                            children=[
                                build_graph_title("Avance vacunación por edad"),
                                dcc.Graph(
                                    id="well-map",
                                    figure={
                                        "layout": {
                                            "paper_bgcolor": "#192444",
                                            "plot_bgcolor": "#192444",
                                        }
                                    },
                                    config={"scrollZoom": True, "displayModeBar": False},
                                ),
                            ],
                        ),
                        # Ternary map
                        html.Div(
                            id="ternary-map-container",
                            children=[
                                html.Div(
                                    id="ternary-header",
                                    children=[
                                        build_graph_title(
                                            "Avance vacunación población"
                                        )
                                    ],
                                ),
                                dcc.Graph(
                                    id="ternary-map",
                                    figure={
                                        "layout": {
                                            "paper_bgcolor": "#192444",
                                            "plot_bgcolor": "#192444",
                                        }
                                    },
                                    config={
                                        "scrollZoom": True,
                                        "displayModeBar": False,
                                    },
                                ),
                            ],
                        ),
                    ],
                ),
            ],
        ),
        # row de contagios
        html.Div(
            className="row",
            id="bottom-row",
            children=[
                # Formation bar plots
                html.Div(
                    id="form-bar-container",
                    className="six columns",
                    children=[
                        build_graph_title("Incremental de contagios entre días (no diarios)"),
                        dcc.Graph(id="form-by-bar"),
                    ],
                ),
                html.Div(
                    # Selected well productions
                    id="well-production-container",
                    className="six columns",
                    children=[
                        build_graph_title("Distribución de edad de los contagios (% del total de contagios)"),
                        dcc.Graph(id="production-fig"),
                    ],
                ),
            ],
        ),
        # row de UCI
        html.Div(
            className="row",
            id="uci-row",
            children=[
                # Formation bar plots
                html.Div(
                    id="uci-ages-container",
                    className="six columns",
                    children=[
                        build_graph_title("Pacientes UCI por edad (diarios)"),
                        dcc.Graph(id="uci-ages-fig"),
                    ],
                ),
                html.Div(
                    # Selected well productions
                    id="uci-dist-container",
                    className="six columns",
                    children=[
                        build_graph_title("Distribución de edad de los pacientes UCI"),
                        dcc.Graph(id="uci-dist-fig"),
                    ],
                ),
            ],
        ),
    ]
)


# Update bar plot
@app.callback(
    Output("form-by-bar", "figure"),
    [
        Input("well-map", "selectedData"),
        Input("ternary-map", "selectedData"),
    ],
)
def update_bar(map_selected_data, tern_selected_data):


    return generate_formation_bar(None, None)


# Update ternary map
@app.callback(
    Output("ternary-map", "figure"),
    [
        Input("well-map", "selectedData"),
        Input("form-by-bar", "selectedData"),
        Input("form-by-bar", "clickData"),
    ],
    state=[State("ternary-map", "figure")],
)
def update_ternary_map(
    map_selected_data,
    bar_selected_data,
    bar_click_data,
    curr_fig,
):
    

    return generate_vacs_total(
        None, None, None, None
    )

# Update well map
@app.callback(
    Output("well-map", "figure"),
    [
        Input("ternary-map", "selectedData"),
        Input("form-by-bar", "selectedData"),
        Input("form-by-bar", "clickData"),
    ],
)
def update_well_map(
    tern_selected_data, bar_selected_data, bar_click_data
):
    

    return generate_well_map(None, None)

# Update well map
@app.callback(
    Output("uci-ages-fig", "figure"),
    [
        Input("ternary-map", "selectedData"),
        Input("form-by-bar", "selectedData"),
        Input("form-by-bar", "clickData"),
    ],
)
def update_uci_ages(
    tern_selected_data, bar_selected_data, bar_click_data
):

    return generate_uci_ages_fig(None, None)

# Update uci dist fig
@app.callback(
    Output("uci-dist-fig", "figure"),
    [
        Input("ternary-map", "selectedData"),
        Input("form-by-bar", "selectedData"),
        Input("form-by-bar", "clickData"),
    ],
)
def update_uci_ages(
    tern_selected_data, bar_selected_data, bar_click_data
):

    return generate_uci_dist_fig(None)


# Update production plot
@app.callback(
    Output("production-fig", "figure"),
    [
        Input("well-map", "selectedData"),
        Input("ternary-map", "selectedData"),
        Input("form-by-bar", "selectedData"),
    ],
)
def update_production(map_select, tern_select, bar_select):

    # Find which one has been triggered
    

    return generate_cases_stacked(None)


# Running the server
if __name__ == "__main__":
    app.run_server(debug=True)