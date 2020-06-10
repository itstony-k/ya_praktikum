#!/usr/bin/python
# -*- coding: utf-8 -*-

# импортируем библиотеки
import pandas as pd
from datetime import datetime

import dash
import dash_core_components as dcc
import dash_html_components as html
from dash.dependencies import Input, Output

import plotly.graph_objs as go

# задаём данные для отрисовки
from sqlalchemy import create_engine

# параметры подключения к БД
db_config = {'user': 'my_user',         # имя пользователя
             'pwd': 'my_user_password', # пароль
             'host': 'localhost',       # адрес сервера
             'port': 5432,              # порт подключения
             'db': 'zen'}               # название базы данных

engine = create_engine('postgresql://{}:{}@{}:{}/{}'.format(db_config['user'],
															db_config['pwd'],
															db_config['host'],
															db_config['port'],
															db_config['db']))

# sql-запрос.
query = '''SELECT *
           FROM dash_visits
        '''

dash_visits = pd.io.sql.read_sql(query, con = engine)

# sql-запрос.
query = '''SELECT *
           FROM dash_engagement
        '''

dash_engagement = pd.io.sql.read_sql(query, con = engine)

# приводим столбцы к типу datetime
dash_visits['dt'] = pd.to_datetime(dash_visits['dt'])
dash_engagement['dt'] = pd.to_datetime(dash_engagement['dt'])

# заголовок дашборда
dash_title = 'Взаимодействие пользователей с карточками Яндекс.Дзен'

# описание дашборда
dash_description = '''
                    Этот дашборд показывает взаимодействие пользователей Яндекс.Дзен с карточками:
                    	историю событий по темам карточек;
                    	разбивку событий по темам источников;
                    	глубину взаимодействия пользователей с карточками (воронка: показ — клик — просмотр).
                    Используйте выбор интервала даты, возрастной категории и темы карточек для управления дашбордом.
                   '''

# задаём лейаут
external_stylesheets = ['https://codepen.io/chriddyp/pen/bWLwgP.css']
app = dash.Dash(__name__, external_stylesheets=external_stylesheets, compress=False)
app.layout = html.Div(children=[  
    
	# название
	html.H1(children = dash_title,
				style={'font-weight': 'bold'}),

	# описание
	html.Label(dash_description),

	html.Br(),
	
	# начало блока с фильтрами
	html.Div([

		# фильтры даты/времени и возраста (левый блок)
		html.Div([

			# фильтр даты и времени
			html.Label('Выбор временного промежутка'),

			dcc.DatePickerRange(
				start_date = dash_visits['dt'].min(),
				end_date = dash_visits['dt'].max(),
				display_format = 'YYYY-MM-DD',
				id = 'dt_selector',
				),

			html.Br(),
			html.Br(),

			# фильтр возраста
			html.Label('Выбор возрастной категории'),

			# составляем список
			dcc.Dropdown(
				options = [{'label': x, 'value': x} for x in dash_visits['age_segment'].unique()],
				value = dash_visits['age_segment'].unique(),
				multi = True, 
				id = 'age-dropdown'
				),
				
		], className = 'six columns'),  # конец левого блока

		# блок с пикером тем (правый блок)
		html.Div([

			# фильтр тем
			html.Label('Выбор темы карточек'),

			# составляем список
			dcc.Dropdown(
				options = [{'label': x, 'value': x} for x in dash_visits['item_topic'].unique()],
				value = dash_visits['item_topic'].unique(),
				multi = True,
				id = 'item-topic-dropdown'
				),

		], className = 'six columns'), # конец правого блока

	], className = 'row'), # конец блока фильтров

	# начало блока графиков
	html.Div([

		# блок графика истории событий (левый блок)
		html.Div([

			html.Br(),

			html.Label('График истории событий по темам карточек',
				style={'textAlign': 'center', 'color': 'Black', 'font-weight': 'bold'}),

			dcc.Graph(
				style = {'height': '50vw'},
				id = 'history-absolute-visits'
				),

		], className = 'six columns'), # конец левого блока

		# правый блок графиков
		html.Div([

			html.Br(),

			html.Label('График разбивки событий по темам источников',
				style={'textAlign': 'center', 'color': 'Black', 'font-weight': 'bold'}),

			dcc.Graph(
				style = {'height': '25vw'},
				id = 'pie-visits'
				),

			html.Br(),		

			html.Label('График средней глубины взаимодействия',
				style={'textAlign': 'center', 'color': 'Black', 'font-weight': 'bold'}),

			dcc.Graph(
				style = {'height': '25vw'},
				id = 'engagement-graph'
				),

		], className = 'six columns'), # конец правого блока

	], className = 'row'), # конец блока графиков



]) # конец лейаута

# логика дашборда
@app.callback(
	
	# выход
	[Output('history-absolute-visits', 'figure'),
	Output('pie-visits', 'figure'),
	Output('engagement-graph', 'figure'),
	],

	# входные параметры
	[Input('item-topic-dropdown', 'value'),
	Input('age-dropdown', 'value'),
	Input('dt_selector', 'start_date'),
	Input('dt_selector', 'end_date'),
	])

def update_figures(selected_item_topics, selected_ages, start_date, end_date):

	dash_visits_filtered = dash_visits.query(
		'item_topic.isin(@selected_item_topics)\
		 and dt >= @start_date and dt <= @end_date\
		  and age_segment.isin(@selected_ages)'
		)
	
	# scatter		
	scatter_agg = dash_visits_filtered.groupby(['item_topic', 'dt'])\
			.agg({'visits': 'sum'})\
			.reset_index()

	scatter = []
	for topic in scatter_agg['item_topic'].unique():
		scatter += [go.Scatter(x = scatter_agg.query('item_topic == @topic')['dt'],
							y = scatter_agg.query('item_topic == @topic')['visits'],
							mode = 'lines',
							stackgroup = 'one',
							name = topic)]

	# pie
	pie_agg = dash_visits_filtered.groupby('source_topic', as_index = False).agg({'visits': 'sum'})

	pie = [go.Pie(labels = pie_agg['source_topic'],
			values = pie_agg['visits'])]

	# bar
	dash_engagement_filtered = dash_engagement.query(
		  'item_topic.isin(@selected_item_topics) and \
		  dt >= @start_date and dt <= @end_date \
		  and age_segment.isin(@selected_ages)'
		  )

	bar_agg = dash_engagement_filtered.groupby('event', as_index = False)\
		.agg({'unique_users': 'mean'})\

	# нормируем
	bar_agg['avg_unique_users'] = bar_agg['unique_users'] / bar_agg['unique_users'].max()

	bar_agg = bar_agg.sort_values('avg_unique_users', ascending = False)

	bar = [go.Bar(x = bar_agg['event'],
			y = bar_agg['avg_unique_users'])]



	return (
		{
		'data': scatter,
		'layout': go.Layout(xaxis = {'title': 'Дата и время'},
							yaxis = {'title': 'Доля уникальных <br> пользователей'})
		},

		{
		'data': pie
		},

		{'data': bar,
		'layout': go.Layout(xaxis = {'title': 'Событие'},
							yaxis = {'title': 'Уникальные пользователи'})
		},

		)
	
if __name__ == '__main__':
	app.run_server(host='0.0.0.0', port=3000)
