import pandas as pd
from environs import Env

env = Env()
env.read_env()

tot_chilenos = 19116208

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


# graficos a hacer con datos y layout
graphs_data = [
    {
        'name': 'vacunas-totales',
        'data': [
            {'x': df_vacunas[df_vacunas['Dosis']=='Primera'].datetime, 'y': df_vacunas[df_vacunas['Dosis']=='Primera']['Total']/tot_chilenos, 'name': '1 Dosis', 'kwargs': { 'hovertemplate':'<i>%{y:.1%}</i> - '+'<b>%{text:,}</b>', 'text': df_vacunas[df_vacunas['Dosis']=='Primera']['Total'].to_list() }, 'type': 'Scatter'},
            {'x': df_vacunas[df_vacunas['Dosis']=='Segunda'].datetime, 'y': df_vacunas[df_vacunas['Dosis']=='Segunda']['Total']/tot_chilenos, 'name': '2 Dosis', 'kwargs': { 'hovertemplate':'<i>%{y:.1%}</i> - '+'<b>%{text:,}</b>', 'text': df_vacunas[df_vacunas['Dosis']=='Segunda']['Total'].to_list() }, 'type': 'Scatter'}
        ],
        'layout': {'xaxis_tickformat' : '%d %B <br>%Y', 'yaxis_tickformat' : ',.1%', 'legend': {'yanchor': 'top', 'y': 0.99, 'xanchor': 'left', 'x': 0.01}, 'margin' : {'l': 50, 'r': 10, 't': 10, 'b': 50}, }
    },
    {
        'name': 'vacunas-edad',
        'data': [
            {'x': df_vacunas[df_vacunas['Dosis']=='Primera'].datetime, 'y': df_vacunas[df_vacunas['Dosis']=='Primera']['Menores de 60 (%)'], 'name': '< 60 - 1 Dosis', 'kwargs': { 'hovertemplate':'<i>%{y:.1%}</i>', 'line': {'color': '#1f77b4'}, 'opacity': 0.4 }, 'type': 'Scatter'},
            {'x': df_vacunas[df_vacunas['Dosis']=='Segunda'].datetime, 'y': df_vacunas[df_vacunas['Dosis']=='Segunda']['Menores de 60 (%)'], 'name': '< 60 - 2 Dosis', 'kwargs': { 'hovertemplate':'<i>%{y:.1%}</i>', 'line': {'color': '#1f77b4'} }, 'type': 'Scatter'},
            {'x': df_vacunas[df_vacunas['Dosis']=='Primera'].datetime, 'y': df_vacunas[df_vacunas['Dosis']=='Primera']['60 o mas (%)'], 'name': '>= 60 - 1 Dosis', 'kwargs': { 'hovertemplate':'<i>%{y:.1%}</i>', 'line': {'color': '#ff7f0e'}, 'opacity': 0.4}, 'type': 'Scatter'},
            {'x': df_vacunas[df_vacunas['Dosis']=='Segunda'].datetime, 'y': df_vacunas[df_vacunas['Dosis']=='Segunda']['60 o mas (%)'], 'name': '>= 60 - 2 Dosis', 'kwargs': { 'hovertemplate':'<i>%{y:.1%}</i>','line': {'color': '#ff7f0e'}}, 'type': 'Scatter'},
        ],
        'layout': {'xaxis_tickformat' : '%d %B <br>%Y', 'yaxis_tickformat' : ',.1%', 'legend': {'yanchor': 'top', 'y': 0.99, 'xanchor': 'left', 'x': 0.01}, 'margin' : {'l': 50, 'r': 10, 't': 10, 'b': 50} }
    },
    {
        'name': 'inc-contagios-edad',
        'data': [
            {'x': df_casos_diarios.date, 'y': df_casos_diarios['Menores de 60'], 'name': 'Menores de 60', 'kwargs': { 'hovertemplate':'<i>%{y}</i> - ' }, 'type': 'Scatter'},
            {'x': df_casos_diarios.date, 'y': df_casos_diarios['60 o mas'], 'name': '60 o más', 'kwargs': { 'hovertemplate':'<i>%{y}</i> - ' }, 'type': 'Scatter'}
        ],
        'layout': {'xaxis_tickformat': '%d %B <br>%Y', 'legend': {'yanchor': 'top', 'y': 0.99, 'xanchor': 'left', 'x': 0.01}, 'margin' : {'l': 50, 'r': 10, 't': 10, 'b': 50}}
    },
    {
        'name': 'inc-contagios-base100',
        'data': [
            {'x': df_casos_diarios.date, 'y': df_casos_diarios['Menores de 60']/df_casos_diarios[df_casos_diarios['date']=='2021-02-03']['Menores de 60'].iloc[0]*100, 'name': 'Menores de 60', 'kwargs': { 'hovertemplate':'<i>%{y:.1f}</i>' }, 'type': 'Scatter'},
            {'x': df_casos_diarios.date, 'y': df_casos_diarios['60 o mas']/df_casos_diarios[df_casos_diarios['date']=='2021-02-03']['60 o mas'].iloc[0]*100, 'name': '60 o más', 'kwargs': { 'hovertemplate':'<i>%{y:.1f}</i>' }, 'type': 'Scatter'}
        ],
        'layout': {'xaxis_tickformat' : '%d %B <br>%Y', 'legend': {'yanchor': 'top', 'y': 0.99, 'xanchor': 'left', 'x': 0.01}, 'margin' : {'l': 50, 'r': 10, 't': 10, 'b': 50}}
    },
    {
        'name': 'uci-edad',
        'data': [
            {'x': df_uci.date, 'y': df_uci['Menores de 60'], 'name': 'Menores de 60', 'kwargs': { 'hovertemplate':'<i>%{y}</i>', 'stackgroup': 'one' }, 'type': 'Scatter'},
            {'x': df_uci.date, 'y': df_uci['60 o mas'], 'name': '60 o más', 'kwargs': { 'hovertemplate':'<i>%{y}</i>', 'stackgroup': 'one' }, 'type': 'Scatter'},
            {'x': df_camas_uci.date, 'y': df_camas_uci['Camas no Covid-19 ocupadas'], 'name': "Camas no Covid-19 ocupadas", 'kwargs': { 'hovertemplate':'<i>%{y}</i>', 'stackgroup': 'one', 'line': {'color': 'red'} }, 'type': 'Scatter'},
            {'x': df_camas_uci.date, 'y': df_camas_uci['Camas UCI Habilitadas'], 'name': "Total camas UCI Habilitadas", 'type': 'Scatter', 'kwargs': {'line': {'width': 0.5, 'color': 'black', 'dash': 'dash'}}}
        ],
        'layout': {'xaxis_tickformat' : '%d %B <br>%Y', 'legend': {'yanchor': 'bottom', 'y': 0.99, 'xanchor': 'left', 'x': 0.01}, 'margin' : {'l': 50, 'r': 10, 't': 10, 'b': 50}}
    },
    {
        'name': 'uci-dist-edad',
        'data': [
            {'x': df_uci.date, 'y': df_uci['Menores de 60']/df_uci['Totales'], 'name': 'Menores de 60', 'kwargs': { 'hovertemplate':'<i>%{y}</i>', 'stackgroup': 'one' }, 'type': 'Scatter'},
            {'x': df_uci.date, 'y': df_uci['60 o mas']/df_uci['Totales'], 'name': '60 o más', 'kwargs': { 'hovertemplate':'<i>%{y}</i>', 'stackgroup': 'one' }, 'type': 'Scatter'},
        ],
        'layout': {'xaxis_tickformat' : '%d %B <br>%Y', 'legend': {'yanchor': 'top', 'y': 0.99, 'xanchor': 'left', 'x': 0.01}, 'margin' : {'l': 50, 'r': 10, 't': 10, 'b': 50}}
    },
    {
        'name': 'uci-edad-base-100-60',
        'data': [
            {'x': df_uci.date, 'y': df_uci['Menores de 60']/df_uci[df_uci['date']=='2021-02-03']['Menores de 60'].iloc[0]*100, 'name': 'Menores de 60', 'kwargs': { 'hovertemplate':'<i>%{y}</i>' }, 'type': 'Scatter'},
            {'x': df_uci.date, 'y': df_uci['60 o mas']/df_uci[df_uci['date']=='2021-02-03']['60 o mas'].iloc[0]*100, 'name': '60 o más', 'kwargs': { 'hovertemplate':'<i>%{y}</i>',  'fill': 'tonexty' }, 'type': 'Scatter'},
        ],
        'layout': {'xaxis_tickformat' : '%d %B <br>%Y', 'legend': {'yanchor': 'top', 'y': 0.99, 'xanchor': 'left', 'x': 0.01}, 'margin' : {'l': 50, 'r': 10, 't': 10, 'b': 50}}
    },
    {
        'name': 'uci-edad-base-100-70',
        'data': [
            {'x': df_uci.date, 'y': df_uci[['<=39','40-49']].sum(axis=1)/df_uci[df_uci['date']=='2021-02-03'][['<=39','40-49']].sum(axis=1).iloc[0]*100, 'name': 'Menores de 50', 'kwargs': { 'hovertemplate':'<i>%{y}</i>'}, 'type': 'Scatter'},
            {'x': df_uci.date, 'y': df_uci['>=70']/df_uci[df_uci['date']=='2021-02-03']['>=70'].iloc[0]*100, 'name': '70 o más', 'kwargs': { 'hovertemplate':'<i>%{y}</i>', 'fill': 'tonexty' }, 'type': 'Scatter'},
        ],
        'layout': {'xaxis_tickformat' : '%d %B <br>%Y', 'legend': {'yanchor': 'top', 'y': 0.99, 'xanchor': 'left', 'x': 0.01}, 'margin' : {'l': 50, 'r': 10, 't': 10, 'b': 50}}
    },
    {
        'name': 'fallecidos-edad',
        'data': [
            {'x': df_muertes_diarias.date, 'y': df_muertes_diarias['Menores de 60'], 'name': 'Menores de 60', 'kwargs': { 'hovertemplate':'<i>%{y}</i>', 'opacity': 0.4 }, 'type': 'Scatter'},
            {'x': df_muertes_diarias.date, 'y': df_muertes_diarias['60 o mas'], 'name': '60 o más', 'kwargs': { 'hovertemplate':'<i>%{y}</i>', 'opacity': 0.4 }, 'type': 'Scatter'},
            {'x': df_muertes_diarias.date, 'y': df_muertes_diarias['Menores de 60 (SMA-7)'], 'name': 'Menores de 60 (Promedio 7 días)', 'kwargs': { 'hovertemplate':'<i>%{y}</i>','line': {'color': '#1f77b4', 'dash': 'dash'} }, 'type': 'Scatter'},
            {'x': df_muertes_diarias.date, 'y': df_muertes_diarias['60 o mas (SMA-7)'], 'name': '60 o más (Promedio 7 días)', 'kwargs': { 'hovertemplate':'<i>%{y}</i>', 'line': {'color': '#ff7f0e', 'dash': 'dash'} }, 'type': 'Scatter'}
        ],
        'layout': {'xaxis_tickformat': '%d %B <br>%Y', 'legend': {'yanchor': 'top', 'y': 0.99, 'xanchor': 'left', 'x': 0.01}, 'margin' : {'l': 50, 'r': 10, 't': 10, 'b': 50}},
        'kwargs': {'initial_min': '2021-01-01'}
    },
    {
        'name': 'fallecidos-edad-base100',
        'data': [
            {'x': df_muertes_diarias.date, 'y': df_muertes_diarias['Menores de 60 (SMA-7)']/df_muertes_diarias[df_muertes_diarias['date']=='2021-02-03']['Menores de 60 (SMA-7)'].iloc[0]*100, 'name': 'Menores de 60', 'kwargs': { 'hovertemplate':'<i>%{y:.1f}</i>' }, 'type': 'Scatter'},
            {'x': df_muertes_diarias.date, 'y': df_muertes_diarias['60 o mas (SMA-7)']/df_muertes_diarias[df_muertes_diarias['date']=='2021-02-03']['60 o mas (SMA-7)'].iloc[0]*100, 'name': '60 o más', 'kwargs': { 'hovertemplate':'<i>%{y:.1f}</i>' }, 'type': 'Scatter'}
        ],
        'layout': {'xaxis_tickformat' : '%d %B <br>%Y', 'legend': {'yanchor': 'top', 'y': 0.99, 'xanchor': 'left', 'x': 0.01}, 'margin' : {'l': 50, 'r': 10, 't': 10, 'b': 50}},
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
        'layout': {'xaxis_tickformat': '%d %B <br>%Y', 'legend': {'yanchor': 'top', 'y': 0.99, 'xanchor': 'left', 'x': 0.01}, 'margin' : {'l': 50, 'r': 10, 't': 10, 'b': 50}},
        'kwargs': {'initial_min': '2021-01-01'}
    },
    {
        'name': 'fallecidos-edad-70-base100',
        'data': [
            {'x': df_muertes_diarias.date, 'y': df_muertes_diarias['Menores de 50 (SMA-7)']/df_muertes_diarias[df_muertes_diarias['date']=='2021-02-03']['Menores de 50 (SMA-7)'].iloc[0]*100, 'name': 'Menores de 50', 'kwargs': { 'hovertemplate':'<i>%{y:.1f}</i>' }, 'type': 'Scatter'},
            {'x': df_muertes_diarias.date, 'y': df_muertes_diarias['70 o más (SMA-7)']/df_muertes_diarias[df_muertes_diarias['date']=='2021-02-03']['70 o más (SMA-7)'].iloc[0]*100, 'name': '70 o más', 'kwargs': { 'hovertemplate':'<i>%{y:.1f}</i>' }, 'type': 'Scatter'}
        ],
        'layout': {'xaxis_tickformat' : '%d %B <br>%Y', 'legend': {'yanchor': 'top', 'y': 0.99, 'xanchor': 'left', 'x': 0.01}, 'margin' : {'l': 50, 'r': 10, 't': 10, 'b': 50}},
        'kwargs': {'initial_min': '2021-01-01'}
    },

]