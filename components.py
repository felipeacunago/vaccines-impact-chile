import plotly.graph_objs as go
from dash.dependencies import Input, Output, State
import dash_html_components as html
from datetime import datetime as dt
from dateutil import parser as dtparser
import dash_core_components as dcc
import pandas as pd

def filter_dataset(dataset, min_value, max_value, filter_field):

    return dataset[
        (dataset[filter_field]>=min_value) & (dataset[filter_field]<=max_value)
    ]

class GraphWithSlider(html.Div):
    def __init__(self, children=None, className=None, preffix='', data_json=None, layout_kwargs=None, **kwargs):
        self.preffix = preffix
        self.data_json = data_json
        self.layout_kwargs = layout_kwargs

        self.initial_min = kwargs.get('initial_min')
        self.initial_max = kwargs.get('initial_max')

        super().__init__(children=self.generate_children(), className=className)

    def layout(self):
        layout = go.Layout(
            **self.layout_kwargs
        )

        return layout

    def generate_children(self):

        numdate = {el[0]:el[1] for el in enumerate(list(self.data_json[0]['x']))}
        x_min = list(numdate.keys())[0]
        x_max = list(numdate.keys())[-1]
        # x_min = list(numdate.keys())[list(numdate.values()).index(self.initial_min)] if self.initial_min else list(numdate.keys())[0]
        # x_max = list(numdate.keys())[-1]

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
                value=[
                    list(numdate.keys())[list(numdate.values()).index(self.initial_min)] if self.initial_min else list(numdate.keys())[0],
                    list(numdate.keys())[list(numdate.values()).index(self.initial_max)] if self.initial_max else list(numdate.keys())[-1]
                ]
            ),
            className='two-thirds column'
        )

        # si se setea el valor inicial se usa ese
        selected_min = html.P(id=f'{self.preffix}-min-val', children=dtparser.isoparse(str(numdate[x_min])).strftime("%d %B, %Y"), className='slider-text')
        selected_max = html.P(id=f'{self.preffix}-max-val', children=dtparser.isoparse(str(numdate[x_max])).strftime("%d %B, %Y"), className='slider-text')

        children = html.Div(
            [
                html.Div(graph, className='row'),
                html.Div([html.Div(children=selected_min, className='one-sixth column', style={'padding-left':'10px'}), slider,html.Div(selected_max, className='one-sixth column')], className='slider row')
            ], className='container'
        )

        

        return children

    def generate_callback(self):
        def update_graph(slider):

            numdate = {el[0]:el[1] for el in enumerate(list(self.data_json[0]['x']))}
            selected_min = numdate[slider[0]]
            selected_max = numdate[slider[1]]

            data = [
                getattr(go, series['type'])(
                    **{
                        'x': filter_dataset(pd.DataFrame(list(zip(series['x'], series['y'])), columns=['x','y']), selected_min, selected_max, 'x')['x'], 
                        'y': filter_dataset(pd.DataFrame(list(zip(series['x'], series['y'])), columns=['x','y']), selected_min, selected_max, 'x')['y'],
                        'name': series['name'],
                        **series['kwargs']
                    }) for series in self.data_json]

            return [{"data": data, "layout": self.layout()}, dtparser.isoparse(str(selected_min)).strftime("%d %B, %Y"), dtparser.isoparse(str(selected_max)).strftime("%d %B, %Y")]
        return update_graph
