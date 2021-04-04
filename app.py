import pathlib
import os

import dash
import dash_core_components as dcc
import dash_html_components as html
import plotly.graph_objs as go
from dash.dependencies import Input, Output, State


from components import GraphWithSlider, ProgressGraph
from graphs_config import graphs_data, completion_graph_data


# app initialize
app = dash.Dash(
    __name__,
    meta_tags=[
        {"name": "viewport", "content": "width=device-width, initial-scale=1.0"}
    ],
)
server = app.server
app.config["suppress_callback_exceptions"] = True
app.title = 'Impacto Vacunación en Chile'


# Load data
APP_PATH = str(pathlib.Path(__file__).parent.resolve())



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
        

graphs = { graph_data['name']: GraphWithSlider(preffix=graph_data['name'], data_json=graph_data['data'], layout_kwargs=graph_data['layout'], **graph_data.get('kwargs', {})) for graph_data in graphs_data}

completion_graph = ProgressGraph(preffix='completados-segmentos', data_json=completion_graph_data['data'], progress_data=completion_graph_data['progress_data'], layout_kwargs=completion_graph_data['layout'], **completion_graph_data.get('kwargs', {}))

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
            ],
        ),
        # row progress bar
        html.Div(
            className="graphs row",
            children=[
                html.Div(
                    className="six columns",
                    children=[
                        build_graph_title("Vacunación por edad + Pacientes UCI (con respecto al máximo del período post-vacunación de su tramo etario)"),
                        completion_graph
                    ],
                )
            ],
        ),
        # row vacunacion
        html.Div(
            className="graphs row",
            children=[
                html.Div(
                    className="six columns",
                    children=[
                        build_graph_title("Avance vacunación por edad"),
                        graphs['vacunas-edad']
                    ],
                ),
                html.Div(
                    className="six columns",
                    children=[
                        build_graph_title("Avance vacunación general"),
                        graphs['vacunas-totales']
                    ],
                ),
            ],
        ),
        # row de contagios
        html.Div(
            className="graphs row",
            children=[
                html.Div(
                    className="six columns",
                    children=[
                        build_graph_title("Contagios diarios por grupo etario"),
                        graphs['inc-contagios-edad']
                    ],
                ),
                html.Div(
                    className="six columns",
                    children=[
                        build_graph_title("Contagios por grupo etario en base 100 (con respecto a número contagios de su grupo etario el 03/02/21)"),
                        graphs['inc-contagios-base100']
                    ],
                ),
            ],
        ),
        # row de UCI
        html.Div(
            className="graphs row",
            children=[
                html.Div(
                    className="six columns",
                    children=[
                        build_graph_title("Pacientes UCI por edad (diarios)"),
                        graphs['uci-edad']
                    ],
                ),
                html.Div(
                    className="six columns",
                    children=[
                        build_graph_title("Distribución edad de pacientes UCI (% del grupo etario con respecto al total UCI)"),
                        graphs['uci-dist-edad']
                    ],
                ),
            ],
        ),
        # estudio la tercera
        html.Div(
            className="graphs row",
            children=[
                html.Div(
                    className="six columns",
                    children=[
                        build_graph_title("Pacientes UCI base 100 (con respecto a número hospitalizados de su grupo etario el 03/02/21)"),
                        graphs["uci-edad-base-100-60"]
                    ],
                ),
                html.Div(
                    className="six columns",
                    children=[
                        build_graph_title("Pacientes UCI base 100 (con respecto a número hospitalizados de su grupo etario el 03/02/21)"),
                        graphs["uci-edad-base-100-70"]
                    ],
                ),
            ],
        ),
        # row de contagios
        html.Div(
            className="graphs row",
            children=[
                html.Div(
                    className="six columns",
                    children=[
                        build_graph_title("Fallecidos diarios por grupo etario"),
                        graphs['fallecidos-edad']
                    ],
                ),
                html.Div(
                    className="six columns",
                    children=[
                        build_graph_title("Promedio a 7 días de fallecidos por grupo etario base 100 (con respecto a número fallecidos de su grupo etario el 03/02/21)"),
                        graphs['fallecidos-edad-base100']
                    ],
                ),
            ],
        ),
        # row de contagios 50-70
        html.Div(
            className="graphs row",
            children=[
                html.Div(
                    className="six columns",
                    children=[
                        build_graph_title("Fallecidos diarios por grupo etario"),
                        graphs['fallecidos-edad-70']
                    ],
                ),
                html.Div(
                    className="six columns",
                    children=[
                        build_graph_title("Promedio a 7 días de fallecidos por grupo etario base 100 (con respecto a número fallecidos de su grupo etario el 03/02/21)"),
                        graphs['fallecidos-edad-70-base100']
                    ],
                ),
            ],
        ),
    ]
)


# se generan los callbacks (filtros de fechas)
[app.callback(
    [Output(f"{name}-graph", "figure"), Output(f"{name}-min-val", "children"), Output(f"{name}-max-val", "children")],
    [
        Input(f"{name}-slider", 'value'),
    ],
) (graph.generate_callback()) for name, graph in graphs.items() ]

app.callback(
    [Output("completados-segmentos-graph", "figure"), Output("completados-segmentos-min-val", "children"), Output("completados-segmentos-max-val", "children")],
    [
        Input("completados-segmentos-slider", 'value'),
    ],
) (completion_graph.generate_callback())


# Running the server
if __name__ == "__main__":
    app.run_server(debug=True, host='0.0.0.0')