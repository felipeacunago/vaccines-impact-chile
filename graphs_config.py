import pandas as pd
from environs import Env

env = Env()
env.read_env()

tot_chilenos = 19116208

# fuentes de datos
# tal vez reemplazar por SQL?
src_path = env('BUCKET_DASH_LOCATION')

df_vacunas = pd.read_csv(f"{src_path}/vacunas_diarias_edad_sexo.csv")

df_vacunas['datetime'] = pd.to_datetime(df_vacunas['datetime'], utc=True)
df_vacunas['Total'] = df_vacunas[['60 o mas','Menores de 60']].sum(axis=1)


df_casos_diarios = pd.read_csv(f'{src_path}/casos_diarios.csv')
df_casos_diarios = df_casos_diarios[['date','60 o mas','Menores de 60','Totales']]
df_casos_diarios[['60 o mas','Menores de 60','Totales']] = df_casos_diarios[['60 o mas','Menores de 60','Totales']].fillna(0).astype(int)
df_casos_diarios['date'] = pd.to_datetime(df_casos_diarios['date'])

df_uci = pd.read_csv(f'{src_path}/uci_diarios.csv')

# total camas
df_camas_uci = pd.read_csv(f'{src_path}/camas_uci_general.csv')

# fallecidos
df_muertes_diarias = pd.read_csv(f'{src_path}/fallecidos_diarios.csv')
# promedio 7 dias
df_muertes_diarias['60 o mas (SMA-7)'] = df_muertes_diarias['60 o mas'].rolling(window=7).mean()
df_muertes_diarias['Menores de 60 (SMA-7)'] = df_muertes_diarias['Menores de 60'].rolling(window=7).mean()

# corte 50-70
df_muertes_diarias['Menores de 50'] = df_muertes_diarias[['<=39','40-49']].sum(axis=1)
df_muertes_diarias['70 o más'] = df_muertes_diarias[['70-79','80-89','>=90']].sum(axis=1)
df_muertes_diarias['Menores de 50 (SMA-7)'] = df_muertes_diarias['Menores de 50'].rolling(window=7).mean()
df_muertes_diarias['70 o más (SMA-7)'] = df_muertes_diarias['70 o más'].rolling(window=7).mean()

# demograficas
df_demo = pd.read_csv(f'{src_path}/Chile-2020.csv')



# graficos a hacer con datos y layout
graphs_data = [
    {
        'name': 'vacunas-totales',
        'data': [
            {'x': df_vacunas[df_vacunas['Dosis']=='Primera'].datetime, 'y': df_vacunas[df_vacunas['Dosis']=='Primera']['Total']/tot_chilenos, 'name': '1 Dosis', 'kwargs': { 'hovertemplate':'<i>%{y:.1%}</i> - '+'<b>%{text:,}</b>', 'text': df_vacunas[df_vacunas['Dosis']=='Primera']['Total'].to_list() }, 'type': 'Scatter'},
            {'x': df_vacunas[df_vacunas['Dosis']=='Segunda'].datetime, 'y': df_vacunas[df_vacunas['Dosis']=='Segunda']['Total']/tot_chilenos, 'name': '2 Dosis', 'kwargs': { 'hovertemplate':'<i>%{y:.1%}</i> - '+'<b>%{text:,}</b>', 'text': df_vacunas[df_vacunas['Dosis']=='Segunda']['Total'].to_list() }, 'type': 'Scatter'}
        ],
        'layout': {'xaxis': {'showgrid': False},'xaxis_tickformat' : '%d %B <br>%Y', 'yaxis_tickformat' : ',.1%', 'legend': {'yanchor': 'top', 'y': 0.99, 'xanchor': 'left', 'x': 0.01}, 'margin' : {'l': 50, 'r': 10, 't': 10, 'b': 50}, }
    },
    {
        'name': 'vacunas-edad',
        'data': [
            {'x': df_vacunas[df_vacunas['Dosis']=='Primera'].datetime, 'y': df_vacunas[df_vacunas['Dosis']=='Primera']['Menores de 60 (%)'], 'name': '< 60 - 1 Dosis', 'kwargs': { 'hovertemplate':'<i>%{y:.1%}</i>', 'line': {'color': '#1f77b4'}, 'opacity': 0.4 }, 'type': 'Scatter'},
            {'x': df_vacunas[df_vacunas['Dosis']=='Segunda'].datetime, 'y': df_vacunas[df_vacunas['Dosis']=='Segunda']['Menores de 60 (%)'], 'name': '< 60 - 2 Dosis', 'kwargs': { 'hovertemplate':'<i>%{y:.1%}</i>', 'line': {'color': '#1f77b4'} }, 'type': 'Scatter'},
            {'x': df_vacunas[df_vacunas['Dosis']=='Primera'].datetime, 'y': df_vacunas[df_vacunas['Dosis']=='Primera']['60 o mas (%)'], 'name': '>= 60 - 1 Dosis', 'kwargs': { 'hovertemplate':'<i>%{y:.1%}</i>', 'line': {'color': '#ff7f0e'}, 'opacity': 0.4}, 'type': 'Scatter'},
            {'x': df_vacunas[df_vacunas['Dosis']=='Segunda'].datetime, 'y': df_vacunas[df_vacunas['Dosis']=='Segunda']['60 o mas (%)'], 'name': '>= 60 - 2 Dosis', 'kwargs': { 'hovertemplate':'<i>%{y:.1%}</i>','line': {'color': '#ff7f0e'}}, 'type': 'Scatter'},
        ],
        'layout': {'xaxis': {'showgrid': False}, 'xaxis_tickformat' : '%d %B <br>%Y', 'yaxis_tickformat' : ',.1%', 'legend': {'yanchor': 'top', 'y': 0.99, 'xanchor': 'left', 'x': 0.01}, 'margin' : {'l': 50, 'r': 10, 't': 10, 'b': 50} }
    },
    {
        'name': 'inc-contagios-edad',
        'data': [
            {'x': df_casos_diarios.date, 'y': df_casos_diarios['Menores de 60'], 'name': 'Menores de 60', 'kwargs': { 'hovertemplate':'<i>%{y}</i> - ' }, 'type': 'Scatter'},
            {'x': df_casos_diarios.date, 'y': df_casos_diarios['60 o mas'], 'name': '60 o más', 'kwargs': { 'hovertemplate':'<i>%{y}</i> - ' }, 'type': 'Scatter'}
        ],
        'layout': {'xaxis': {'showgrid': False},'xaxis_tickformat': '%d %B <br>%Y', 'legend': {'yanchor': 'top', 'y': 0.99, 'xanchor': 'left', 'x': 0.01}, 'margin' : {'l': 50, 'r': 10, 't': 10, 'b': 50}}
    },
    {
        'name': 'inc-contagios-base100',
        'data': [
            {'x': df_casos_diarios.date, 'y': df_casos_diarios['Menores de 60']/df_casos_diarios[df_casos_diarios['date']=='2021-02-03']['Menores de 60'].iloc[0]*100, 'name': 'Menores de 60', 'kwargs': { 'hovertemplate':'<i>%{y:.1f}</i>' }, 'type': 'Scatter'},
            {'x': df_casos_diarios.date, 'y': df_casos_diarios['60 o mas']/df_casos_diarios[df_casos_diarios['date']=='2021-02-03']['60 o mas'].iloc[0]*100, 'name': '60 o más', 'kwargs': { 'hovertemplate':'<i>%{y:.1f}</i>' }, 'type': 'Scatter'}
        ],
        'layout': {'xaxis': {'showgrid': False},'xaxis_tickformat' : '%d %B <br>%Y', 'legend': {'yanchor': 'top', 'y': 0.99, 'xanchor': 'left', 'x': 0.01}, 'margin' : {'l': 50, 'r': 10, 't': 10, 'b': 50}}
    },
    {
        'name': 'uci-edad',
        'data': [
            {'x': df_uci.date, 'y': df_uci['Menores de 60'], 'name': 'Menores de 60', 'kwargs': { 'hovertemplate':'<i>%{y}</i>', 'stackgroup': 'one' }, 'type': 'Scatter'},
            {'x': df_uci.date, 'y': df_uci['60 o mas'], 'name': '60 o más', 'kwargs': { 'hovertemplate':'<i>%{y}</i>', 'stackgroup': 'one' }, 'type': 'Scatter'},
            {'x': df_camas_uci.date, 'y': df_camas_uci['Camas no Covid-19 ocupadas'], 'name': "Camas no Covid-19 ocupadas", 'kwargs': { 'hovertemplate':'<i>%{y}</i>', 'stackgroup': 'one', 'line': {'color': 'red'} }, 'type': 'Scatter'},
            {'x': df_camas_uci.date, 'y': df_camas_uci['Camas UCI Habilitadas'], 'name': "Total camas UCI Habilitadas", 'type': 'Scatter', 'kwargs': {'line': {'width': 0.5, 'color': 'black', 'dash': 'dash'}}}
        ],
        'layout': {'xaxis': {'showgrid': False},'xaxis_tickformat' : '%d %B <br>%Y', 'legend': {'yanchor': 'bottom', 'y': 0.99, 'xanchor': 'left', 'x': 0.01}, 'margin' : {'l': 50, 'r': 10, 't': 10, 'b': 50}}
    },
    {
        'name': 'uci-dist-edad',
        'data': [
            {'x': df_uci.date, 'y': df_uci['Menores de 60']/df_uci['Totales'], 'name': 'Menores de 60', 'kwargs': { 'hovertemplate':'<i>%{y}</i>', 'stackgroup': 'one' }, 'type': 'Scatter'},
            {'x': df_uci.date, 'y': df_uci['60 o mas']/df_uci['Totales'], 'name': '60 o más', 'kwargs': { 'hovertemplate':'<i>%{y}</i>', 'stackgroup': 'one' }, 'type': 'Scatter'},
        ],
        'layout': {'xaxis': {'showgrid': False}, 'xaxis_tickformat' : '%d %B <br>%Y', 'legend': {'yanchor': 'top', 'y': 0.99, 'xanchor': 'left', 'x': 0.01}, 'margin' : {'l': 50, 'r': 10, 't': 10, 'b': 50}}
    },
    {
        'name': 'uci-edad-base-100-60',
        'data': [
            {'x': df_uci.date, 'y': df_uci['Menores de 60']/df_uci[df_uci['date']=='2021-02-03']['Menores de 60'].iloc[0]*100, 'name': 'Menores de 60', 'kwargs': { 'hovertemplate':'<i>%{y}</i>' }, 'type': 'Scatter'},
            {'x': df_uci.date, 'y': df_uci['60 o mas']/df_uci[df_uci['date']=='2021-02-03']['60 o mas'].iloc[0]*100, 'name': '60 o más', 'kwargs': { 'hovertemplate':'<i>%{y}</i>',  'fill': 'tonexty' }, 'type': 'Scatter'},
        ],
        'layout': {'xaxis': {'showgrid': False}, 'xaxis_tickformat' : '%d %B <br>%Y', 'legend': {'yanchor': 'top', 'y': 0.99, 'xanchor': 'left', 'x': 0.01}, 'margin' : {'l': 50, 'r': 10, 't': 10, 'b': 50}}
    },
    {
        'name': 'uci-edad-base-100-70',
        'data': [
            {'x': df_uci.date, 'y': df_uci[['<=39','40-49']].sum(axis=1)/df_uci[df_uci['date']=='2021-02-03'][['<=39','40-49']].sum(axis=1).iloc[0]*100, 'name': 'Menores de 50', 'kwargs': { 'hovertemplate':'<i>%{y}</i>'}, 'type': 'Scatter'},
            {'x': df_uci.date, 'y': df_uci['>=70']/df_uci[df_uci['date']=='2021-02-03']['>=70'].iloc[0]*100, 'name': '70 o más', 'kwargs': { 'hovertemplate':'<i>%{y}</i>', 'fill': 'tonexty' }, 'type': 'Scatter'},
        ],
        'layout': {'xaxis': {'showgrid': False}, 'xaxis_tickformat' : '%d %B <br>%Y', 'legend': {'yanchor': 'top', 'y': 0.99, 'xanchor': 'left', 'x': 0.01}, 'margin' : {'l': 50, 'r': 10, 't': 10, 'b': 50}}
    },
    {
        'name': 'fallecidos-edad',
        'data': [
            {'x': df_muertes_diarias.date, 'y': df_muertes_diarias['Menores de 60'], 'name': 'Menores de 60', 'kwargs': { 'hovertemplate':'<i>%{y}</i>', 'opacity': 0.4 }, 'type': 'Scatter'},
            {'x': df_muertes_diarias.date, 'y': df_muertes_diarias['60 o mas'], 'name': '60 o más', 'kwargs': { 'hovertemplate':'<i>%{y}</i>', 'opacity': 0.4 }, 'type': 'Scatter'},
            {'x': df_muertes_diarias.date, 'y': df_muertes_diarias['Menores de 60 (SMA-7)'], 'name': 'Menores de 60 (Promedio 7 días)', 'kwargs': { 'hovertemplate':'<i>%{y}</i>','line': {'color': '#1f77b4', 'dash': 'dash'} }, 'type': 'Scatter'},
            {'x': df_muertes_diarias.date, 'y': df_muertes_diarias['60 o mas (SMA-7)'], 'name': '60 o más (Promedio 7 días)', 'kwargs': { 'hovertemplate':'<i>%{y}</i>', 'line': {'color': '#ff7f0e', 'dash': 'dash'} }, 'type': 'Scatter'}
        ],
        'layout': {'xaxis': {'showgrid': False}, 'xaxis_tickformat': '%d %B <br>%Y', 'legend': {'yanchor': 'top', 'y': 0.99, 'xanchor': 'left', 'x': 0.01}, 'margin' : {'l': 50, 'r': 10, 't': 10, 'b': 50}},
        'kwargs': {'initial_min': '2021-01-01'}
    },
    {
        'name': 'fallecidos-edad-base100',
        'data': [
            {'x': df_muertes_diarias.date, 'y': df_muertes_diarias['Menores de 60 (SMA-7)']/df_muertes_diarias[df_muertes_diarias['date']=='2021-02-03']['Menores de 60 (SMA-7)'].iloc[0]*100, 'name': 'Menores de 60', 'kwargs': { 'hovertemplate':'<i>%{y:.1f}</i>' }, 'type': 'Scatter'},
            {'x': df_muertes_diarias.date, 'y': df_muertes_diarias['60 o mas (SMA-7)']/df_muertes_diarias[df_muertes_diarias['date']=='2021-02-03']['60 o mas (SMA-7)'].iloc[0]*100, 'name': '60 o más', 'kwargs': { 'hovertemplate':'<i>%{y:.1f}</i>' }, 'type': 'Scatter'}
        ],
        'layout': {'xaxis': {'showgrid': False}, 'xaxis_tickformat' : '%d %B <br>%Y', 'legend': {'yanchor': 'top', 'y': 0.99, 'xanchor': 'left', 'x': 0.01}, 'margin' : {'l': 50, 'r': 10, 't': 10, 'b': 50}},
        'kwargs': {'initial_min': '2021-01-01'}
    },
    {
        'name': 'fallecidos-edad-70',
        'data': [
            {'x': df_muertes_diarias.date, 'y': df_muertes_diarias['Menores de 50'], 'name': 'Menores de 50', 'kwargs': { 'hovertemplate':'<i>%{y}</i>', 'opacity': 0.4 }, 'type': 'Scatter'},
            {'x': df_muertes_diarias.date, 'y': df_muertes_diarias['70 o más'], 'name': '70 o más', 'kwargs': { 'hovertemplate':'<i>%{y}</i>', 'opacity': 0.4 }, 'type': 'Scatter'},
            {'x': df_muertes_diarias.date, 'y': df_muertes_diarias['Menores de 50 (SMA-7)'], 'name': 'Menores de 50 (Promedio 7 días)', 'kwargs': { 'hovertemplate':'<i>%{y}</i>','line': {'color': '#1f77b4', 'dash': 'dash'} }, 'type': 'Scatter'},
            {'x': df_muertes_diarias.date, 'y': df_muertes_diarias['70 o más (SMA-7)'], 'name': '70 o más (Promedio 7 días)', 'kwargs': { 'hovertemplate':'<i>%{y}</i>', 'line': {'color': '#ff7f0e', 'dash': 'dash'} }, 'type': 'Scatter'}
        ],
        'layout': {'xaxis': {'showgrid': False}, 'xaxis_tickformat': '%d %B <br>%Y', 'legend': {'yanchor': 'top', 'y': 0.99, 'xanchor': 'left', 'x': 0.01}, 'margin' : {'l': 50, 'r': 10, 't': 10, 'b': 50}},
        'kwargs': {'initial_min': '2021-01-01'}
    },
    {
        'name': 'fallecidos-edad-70-base100',
        'data': [
            {'x': df_muertes_diarias.date, 'y': df_muertes_diarias['Menores de 50 (SMA-7)']/df_muertes_diarias[df_muertes_diarias['date']=='2021-02-03']['Menores de 50 (SMA-7)'].iloc[0]*100, 'name': 'Menores de 50', 'kwargs': { 'hovertemplate':'<i>%{y:.1f}</i>' }, 'type': 'Scatter'},
            {'x': df_muertes_diarias.date, 'y': df_muertes_diarias['70 o más (SMA-7)']/df_muertes_diarias[df_muertes_diarias['date']=='2021-02-03']['70 o más (SMA-7)'].iloc[0]*100, 'name': '70 o más', 'kwargs': { 'hovertemplate':'<i>%{y:.1f}</i>' }, 'type': 'Scatter'}
        ],
        'layout': {'xaxis': {'showgrid': False}, 'xaxis_tickformat' : '%d %B <br>%Y', 'legend': {'yanchor': 'top', 'y': 0.99, 'xanchor': 'left', 'x': 0.01}, 'margin' : {'l': 50, 'r': 10, 't': 10, 'b': 50}},
        'kwargs': {'initial_min': '2021-01-01'}
    },

]

# con un solo registro por dia
df_vacunas_fix = df_vacunas.copy()
df_vacunas_fix['date'] = df_vacunas_fix['datetime'].dt.date
df_vacunas_fix.drop_duplicates(subset=['date','Dosis'], keep='last', inplace=True)
df_vacunas_fix['date'] = pd.to_datetime(df_vacunas_fix['date'])
df_vacunas_fix.reset_index(inplace=True)

# para ahorrar problemas con el filtro, que ambas se manejen en la misma escala
df_uci_inner_join = df_uci.set_index('date').join(df_vacunas_fix.set_index('date')[['datetime']], how='inner')
df_uci_inner_join.reset_index(inplace=True)

completion_graph_data ={
    'name': 'completados-segmentos',
    'data': [
        {'x': df_uci_inner_join.date, 'y': df_uci_inner_join['<=39']/df_uci_inner_join[df_uci_inner_join['date']>='2021-02-03']['<=39'].max(), 'name': '<=39', 'kwargs': { 'hovertemplate':'<i>%{y:.1%}</i>', 'line': {'color': 'red'}}, 'type': 'Scatter'},
        {'x': df_uci_inner_join.date, 'y': df_uci_inner_join['40-49']/df_uci_inner_join[df_uci_inner_join['date']>='2021-02-03']['40-49'].max(), 'name': '40-49', 'kwargs': { 'hovertemplate':'<i>%{y:.1%}</i>', 'line': {'color': '#ff7f0e'}}, 'type': 'Scatter'},
        {'x': df_uci_inner_join.date, 'y': df_uci_inner_join['50-59']/df_uci_inner_join[df_uci_inner_join['date']>='2021-02-03']['50-59'].max(), 'name': '50-59', 'kwargs': { 'hovertemplate':'<i>%{y:.1%}</i>', 'line': {'color': 'blue'}}, 'type': 'Scatter'},
        {'x': df_uci_inner_join.date, 'y': df_uci_inner_join['>=70']/df_uci_inner_join[df_uci_inner_join['date']>='2021-02-03']['>=70'].max(), 'name': '>=70', 'kwargs': { 'hovertemplate':'<i>%{y:.1%}</i>', 'line': {'color': 'purple'}}, 'type': 'Scatter'},
        {'x': df_uci_inner_join.date, 'y': df_uci_inner_join['60-69']/df_uci_inner_join[df_uci_inner_join['date']>='2021-02-03']['60-69'].max(), 'name': '60-69', 'kwargs': { 'hovertemplate':'<i>%{y:.1%}</i>', 'line': {'color': 'green'}}, 'type': 'Scatter'},
    ],
    'progress_data': [
        {'x': df_vacunas_fix[df_vacunas_fix['Dosis']=='Primera'].date, 'y': df_vacunas_fix[df_vacunas_fix['Dosis']=='Primera']['<=39']/df_demo.iloc[0:8][['M','F']].sum().sum(), 'name': '<= 39 : 1 Dosis', 'kwargs': { 'marker': {'color': 'red'}, 'opacity': 0.4  }},
        {'x': df_vacunas_fix[df_vacunas_fix['Dosis']=='Segunda'].date, 'y': df_vacunas_fix[df_vacunas_fix['Dosis']=='Segunda']['<=39']/df_demo.iloc[0:8][['M','F']].sum().sum(), 'name': '<= 39 : 2 Dosis', 'kwargs': { 'marker': {'color': 'red'}}},
        {'x': df_vacunas_fix[df_vacunas_fix['Dosis']=='Primera'].date, 'y': df_vacunas_fix[df_vacunas_fix['Dosis']=='Primera']['40-49']/df_demo.iloc[8:10][['M','F']].sum().sum(), 'name': '40-49 : 1 Dosis', 'kwargs': { 'marker': {'color': '#ff7f0e'}, 'opacity': 0.4}},
        {'x': df_vacunas_fix[df_vacunas_fix['Dosis']=='Segunda'].date, 'y': df_vacunas_fix[df_vacunas_fix['Dosis']=='Segunda']['40-49']/df_demo.iloc[8:10][['M','F']].sum().sum(), 'name': '40-49 : 2 Dosis', 'kwargs': { 'marker': {'color': '#ff7f0e'}}},
        {'x': df_vacunas_fix[df_vacunas_fix['Dosis']=='Primera'].date, 'y': df_vacunas_fix[df_vacunas_fix['Dosis']=='Primera']['50-59']/df_demo.iloc[10:12][['M','F']].sum().sum(), 'name': '50-59 : 1 Dosis', 'kwargs': { 'marker': {'color': 'blue'}, 'opacity': 0.4}},
        {'x': df_vacunas_fix[df_vacunas_fix['Dosis']=='Segunda'].date, 'y': df_vacunas_fix[df_vacunas_fix['Dosis']=='Segunda']['50-59']/df_demo.iloc[10:12][['M','F']].sum().sum(), 'name': '50-59 : 2 Dosis', 'kwargs': { 'marker': {'color': 'blue'}}},
        {'x': df_vacunas_fix[df_vacunas_fix['Dosis']=='Primera'].date, 'y': df_vacunas_fix[df_vacunas_fix['Dosis']=='Primera']['60-69']/df_demo.iloc[12:14][['M','F']].sum().sum(), 'name': '60-69 : 1 Dosis', 'kwargs': { 'marker': {'color': 'green'}, 'opacity': 0.4}},
        {'x': df_vacunas_fix[df_vacunas_fix['Dosis']=='Segunda'].date, 'y': df_vacunas_fix[df_vacunas_fix['Dosis']=='Segunda']['60-69']/df_demo.iloc[12:14][['M','F']].sum().sum(), 'name': '60-69 : 2 Dosis', 'kwargs': { 'marker': {'color': 'green'}}},
        {'x': df_vacunas_fix[df_vacunas_fix['Dosis']=='Primera'].date, 'y': df_vacunas_fix[df_vacunas_fix['Dosis']=='Primera']['>=70']/df_demo.iloc[14:][['M','F']].sum().sum(), 'name': '>=70 : 1 Dosis', 'kwargs': { 'marker': {'color': 'purple'}, 'opacity': 0.4}},
        {'x': df_vacunas_fix[df_vacunas_fix['Dosis']=='Segunda'].date, 'y': df_vacunas_fix[df_vacunas_fix['Dosis']=='Segunda']['>=70']/df_demo.iloc[14:][['M','F']].sum().sum(), 'name': '>=70 : 2 Dosis', 'kwargs': { 'marker': {'color': 'purple'}}},
    ],
    'layout': {'xaxis_tickformat' : '%d %B <br>%Y', 'legend': {'yanchor': 'top', 'y': 0.99, 'xanchor': 'left', 'x': 0.01}, 'margin' : {'l': 50, 'r': 10, 't': 10, 'b': 50}},
}