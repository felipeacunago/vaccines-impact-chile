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
from datetime import datetime as dt
from dateutil import parser as dtparser

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


class GraphWithSlider(html.Div):
    def __init__(self, children=None, className=None, preffix='', data=None, xaxis_field=''):
        self.preffix = preffix
        self.data = data
        self.xaxis_field = xaxis_field
        super().__init__(children=self.generate_children(), className=className)

    def generate_children(self):

        numdate = {el[0]:el[1] for el in enumerate(list(self.data[self.xaxis_field].unique()))}
        x_min = list(numdate.keys())[0]
        x_max = list(numdate.keys())[-1]

        graph = dcc.Graph(
                    id=f"{self.preffix}-graph",
                    figure={
                        "layout": {
                            "paper_bgcolor": "#192444",
                            "plot_bgcolor": "#192444",
                        }
                    },
                    config={"scrollZoom": True, "displayModeBar": False},
                )
        
        slider =  html.Div(
            dcc.RangeSlider(
                id=f"{self.preffix}-slider",
                min=x_min,
                max=x_max,
                value=[x_min, x_max]
            ),
            className='two-thirds column'
        )

        selected_min = html.Div(id=f'{self.preffix}-min-val', children=dtparser.isoparse(str(numdate[x_min])).strftime("%d %B, %Y"), className='one-sixth column')
        selected_max = html.Div(id=f'{self.preffix}-max-val', children=dtparser.isoparse(str(numdate[x_max])).strftime("%d %B, %Y"), className='one-sixth column')

        children = html.Div(
            [
                html.Div(graph, className='row'),
                html.Div([selected_min, slider,selected_max], className='slider row')
            ], className='container'
        )

        

        return children

def filter_dataset(dataset, min_value, max_value, filter_field):

    return dataset[
        (dataset[filter_field]>=min_value) & (dataset[filter_field]<=max_value)
    ]


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
                                    children=["Dashboard para visualizar el impacto de la vacuna sobre la pandemia",
                                    " siguiendo la idea de ",html.A(href='https://ourworldindata.org/vaccination-israel-impact', children='OurWorldInData'), ".\n"
                                    "Hecho por Felipe Acuña. "]
                                )
                            ],
                        )
                    ],
                ),
                html.Div(
                    className="row",
                    id="top-row-graphs",
                    children=[
                        # Vacunación
                        html.Div(
                            children=[
                                build_graph_title("Avance vacunación por edad"),
                                GraphWithSlider(preffix='vacunas-edad', data=df_vacunas, xaxis_field='datetime')
                            ],
                            className='graph-container'
                        ),
                        html.Div(
                            children=[
                                build_graph_title("Avance vacunación por edad"),
                                GraphWithSlider(preffix='vacunas-totales', data=df_vacunas, xaxis_field='datetime')
                            ],
                            className='graph-container'
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
                html.Div(
                    id="form-bar-container",
                    className="six columns",
                    children=[
                        build_graph_title("Incremental de contagios entre días (no diarios)"),
                        GraphWithSlider(preffix='inc-contagios-edad', data=df_casos_diarios, xaxis_field='date')
                    ],
                ),
                html.Div(
                    id="well-production-container",
                    className="six columns",
                    children=[
                        build_graph_title("Distribución de edad de los contagios (% del total de contagios)"),
                        GraphWithSlider(preffix='contagios-edad-dist', data=df_casos_diarios, xaxis_field='date')
                    ],
                ),
            ],
        ),
        # row de UCI
        html.Div(
            className="row",
            id="uci-row",
            children=[
                html.Div(
                    id="uci-ages-container",
                    className="six columns",
                    children=[
                        build_graph_title("Pacientes UCI por edad (diarios)"),
                        GraphWithSlider(preffix='uci-edad', data=df_uci, xaxis_field='date')
                    ],
                ),
                html.Div(
                    id="uci-dist-container",
                    className="six columns",
                    children=[
                        build_graph_title("Distribución edad de contagios (% del grupo etario con respecto al total UCI)"),
                        GraphWithSlider(preffix='uci-dist-edad', data=df_uci, xaxis_field='date')
                    ],
                ),
            ],
        )
    ]
)


# Update incremental de contagios
@app.callback(
    [Output("inc-contagios-edad-graph", "figure"), Output("inc-contagios-edad-min-val", "children"), Output("inc-contagios-edad-max-val", "children")],
    [
        Input("inc-contagios-edad-slider", "value"),
    ],
)
def update_inc_contagios(slider):

    layout = go.Layout(
        #margin=dict(l=30, r=0, b=20, t=40),
        showlegend=False,
        xaxis_tickformat = '%d %B (%a)<br>%Y'
    )

    numdate = {el[0]:el[1] for el in enumerate(list(df_casos_diarios['date'].unique()))}
    aux = filter_dataset(df_casos_diarios, numdate[slider[0]], numdate[slider[1]], 'date')

    data = [
        dict(
            type="scatter",
            x=aux.date,
            y=aux['Menores de 60'],
            name="Menores de 60",
            mode="lines+markers",
            hoverinfo="x+y+name",
            marker=dict(
                symbol="hexagram-open", line={"width": "0.5"}
            )
        ),
        dict(
            type="scatter",
            x=aux.date,
            y=aux['60 o mas'],
            name="60 o más",
            mode="lines+markers",
            hoverinfo="x+y+name",
            marker=dict(
                symbol="hexagram-open", line={"width": "0.5"}
            )
        )
    ]

    return [{"data": data, "layout": layout}, dtparser.isoparse(str(numdate[slider[0]])).strftime("%d %B, %Y"), dtparser.isoparse(str(numdate[slider[1]])).strftime("%d %B, %Y")]


# Update vacunas totales
@app.callback(
    [Output("vacunas-totales-graph", "figure"), Output("vacunas-totales-min-val", "children"), Output("vacunas-totales-max-val", "children")],
    [
        Input("vacunas-totales-slider", 'value'),
    ],
)
def update_vac_totales(slider):

    layout = go.Layout(
        #margin=dict(l=30, r=0, b=20, t=40),
        showlegend=False,
        xaxis_tickformat = '%d %B (%a)<br>%Y'
    )

    numdate = {el[0]:el[1] for el in enumerate(list(df_vacunas['datetime'].unique()))}
    aux = filter_dataset(df_vacunas, numdate[slider[0]], numdate[slider[1]], 'datetime')

    data = [
        dict(
            type="scatter",
            x=aux[aux['Dosis']=='Primera'].datetime,
            y=aux[aux['Dosis']=='Primera']['Total']/tot_chilenos*100,
            name="1 Dosis",
            mode="lines+markers",
            hoverinfo="x+y+name",
            marker=dict(
                symbol="hexagram-open", line={"width": "0.5"}
            )
        ),
        dict(
            type="scatter",
            x=aux[aux['Dosis']=='Segunda'].datetime,
            y=aux[aux['Dosis']=='Segunda']['Total']/tot_chilenos*100,
            name="2 Dosis",
            mode="lines+markers",
            hoverinfo="x+y+name",
            marker=dict(
                symbol="hexagram-open", line={"width": "0.5"}
            )
        )
    ]

    return [{"data": data, "layout": layout}, dtparser.isoparse(str(numdate[slider[0]])).strftime("%d %B, %Y"), dtparser.isoparse(str(numdate[slider[1]])).strftime("%d %B, %Y")]

# Update vacunas edad
@app.callback(
    [Output("vacunas-edad-graph", "figure"), Output("vacunas-edad-min-val", "children"), Output("vacunas-edad-max-val", "children")],
    [
        Input("vacunas-edad-slider", 'value'),
    ]
)
def update_vacunas_edad(
    slider
):

    layout = go.Layout(
        #margin=dict(l=30, r=0, b=20, t=40),
        showlegend=False,
        xaxis_tickformat = '%d %B (%a)<br>%Y'
    )

    numdate = {el[0]:el[1] for el in enumerate(list(df_vacunas['datetime'].unique()))}
    aux = filter_dataset(df_vacunas, numdate[slider[0]], numdate[slider[1]], 'datetime')

    data = [
        dict(
            type="scatter",
            x=aux[aux['Dosis']=='Primera'].datetime,
            y=aux[aux['Dosis']=='Primera']['Menores de 60 (%)']*100,
            name="< 60 - 1 Dosis",
            mode="lines+markers",
            hoverinfo="x+y+name",
            marker=dict(
                symbol="hexagram-open", line={"width": "0.5"}
            )
        ),
        dict(
            type="scatter",
            x=aux[aux['Dosis']=='Segunda'].datetime,
            y=aux[aux['Dosis']=='Segunda']['Menores de 60 (%)']*100,
            name="< 60 - 1 Dosis",
            mode="lines+markers",
            hoverinfo="x+y+name",
            marker=dict(
                symbol="hexagram-open", line={"width": "0.5"}
            )
        ),
        dict(
            type="scatter",
            x=aux[aux['Dosis']=='Primera'].datetime,
            y=aux[aux['Dosis']=='Primera']['60 o mas (%)']*100,
            name=">= 60 - 1 Dosis",
            mode="lines+markers",
            hoverinfo="x+y+name",
            marker=dict(
                symbol="hexagram-open", line={"width": "0.5"}
            )
        ),
        dict(
            type="scatter",
            x=aux[aux['Dosis']=='Segunda'].datetime,
            y=aux[aux['Dosis']=='Segunda']['60 o mas (%)']*100,
            name=">= 60 - 2 Dosis",
            mode="lines+markers",
            hoverinfo="x+y+name",
            marker=dict(
                symbol="hexagram-open", line={"width": "0.5"}
            )
        )
    ]


    return [{"data": data, "layout": layout}, dtparser.isoparse(str(numdate[slider[0]])).strftime("%d %B, %Y"), dtparser.isoparse(str(numdate[slider[1]])).strftime("%d %B, %Y")]

# Update uci edad
@app.callback(
    [Output("uci-edad-graph", "figure"), Output("uci-edad-min-val", "children"), Output("uci-edad-max-val", "children")],
    [
        Input("uci-edad-slider", 'value'),
    ]
)
def update_uci_ages(
    slider
):
    layout = go.Layout(
        #margin=dict(l=30, r=0, b=20, t=40),
        xaxis_tickformat = '%d %B (%a)<br>%Y'
    )

    numdate = {el[0]:el[1] for el in enumerate(list(df_uci['date'].unique()))}
    aux = filter_dataset(df_uci, numdate[slider[0]], numdate[slider[1]], 'date')
    aux_2 = filter_dataset(df_camas_uci, numdate[slider[0]], numdate[slider[1]], 'date')
    

    data = [
        dict(
            type="scatter",
            x=aux.date,
            y=aux['Menores de 60'],
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
            x=aux.date,
            y=aux['60 o mas'],
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
            x=aux_2.date,
            y=aux_2['Camas UCI Habilitadas'],
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
            x=aux_2.date,
            y=aux_2['Camas no Covid-19 ocupadas'],
            name="Camas no Covid-19 ocupadas",
            mode="lines",
            hoverinfo="x+y+name",
            stackgroup='one',
            marker=dict(
                symbol="hexagram-open", line={"width": "0.5"}
            )
        ),
    ]

    return [{"data": data, "layout": layout}, dtparser.isoparse(str(numdate[slider[0]])).strftime("%d %B, %Y"), dtparser.isoparse(str(numdate[slider[1]])).strftime("%d %B, %Y")]

# Update uci dist fig
@app.callback(
    [Output("uci-dist-edad-graph", "figure"), Output("uci-dist-edad-min-val", "children"), Output("uci-dist-edad-max-val", "children")],
    [
        Input("uci-dist-edad-slider", 'value'),
    ]
)
def update_uci_dist(
    slider
):
    layout = dict(
        xaxis=dict(title="Fecha"), yaxis=dict(title="Distribución edad de pacientes UCI")
    )

    numdate = {el[0]:el[1] for el in enumerate(list(df_uci['date'].unique()))}
    aux = filter_dataset(df_uci, numdate[slider[0]], numdate[slider[1]], 'date')

    data = [
        dict(
            type="scatter",
            x=aux.date,
            y=aux['Menores de 60']/df_uci['Totales']*100,
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
            x=aux.date,
            y=aux['60 o mas']/aux['Totales']*100,
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

    return [{"data": data, "layout": layout}, dtparser.isoparse(str(numdate[slider[0]])).strftime("%d %B, %Y"), dtparser.isoparse(str(numdate[slider[1]])).strftime("%d %B, %Y")]


# Update contagios distribucion edad
@app.callback(
    [Output("contagios-edad-dist-graph", "figure"), Output("contagios-edad-dist-min-val", "children"), Output("contagios-edad-dist-max-val", "children")],
    [
        Input("contagios-edad-dist-slider", 'value'),
    ]
)
def update_contagios_dist(slider):

    # Find which one has been triggered
    layout = dict(
        xaxis=dict(title="Fecha"), yaxis=dict(title="Distribución (%)")
    )

    numdate = {el[0]:el[1] for el in enumerate(list(df_casos_diarios['date'].unique()))}
    aux = filter_dataset(df_casos_diarios, numdate[slider[0]], numdate[slider[1]], 'date')

    data = [
        dict(
            type="scatter",
            x=aux.date,
            y=aux['Menores de 60']/aux['Totales']*100,
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
            x=aux.date,
            y=aux['60 o mas']/aux['Totales']*100,
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

    return [{"data": data, "layout": layout}, dtparser.isoparse(str(numdate[slider[0]])).strftime("%d %B, %Y"), dtparser.isoparse(str(numdate[slider[1]])).strftime("%d %B, %Y")]


# Running the server
if __name__ == "__main__":
    app.run_server(debug=True, host='0.0.0.0')