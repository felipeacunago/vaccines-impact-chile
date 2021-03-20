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
    def __init__(self, children=None, className=None, preffix='', data=None, data_json=None, layout_kwargs=None):
        self.preffix = preffix
        self.data = data
        self.data_json = data_json
        self.layout_kwargs = layout_kwargs
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

    def generate_callback(self):
        def update_graph(slider):

            numdate = {el[0]:el[1] for el in enumerate(list(self.data_json[0]['x']))}
            min_selected = numdate[slider[0]]
            max_selected = numdate[slider[1]]

            data = [
                getattr(go, series['type'])(
                    **{
                        'x': filter_dataset(pd.DataFrame(list(zip(series['x'], series['y'])), columns=['x','y']), min_selected, max_selected, 'x')['x'], 
                        'y': filter_dataset(pd.DataFrame(list(zip(series['x'], series['y'])), columns=['x','y']), min_selected, max_selected, 'x')['y'],
                        'name': series['name'],
                        **series['kwargs']
                    }) for series in self.data_json]

            return [{"data": data, "layout": self.layout()}, dtparser.isoparse(str(min_selected)).strftime("%d %B, %Y"), dtparser.isoparse(str(max_selected)).strftime("%d %B, %Y")]
        return update_graph
