#!/usr/bin/python
# -*- coding: utf-8 -*-

# импортируем библиотеки
import sys
import getopt
import pandas as pd
from sqlalchemy import create_engine
from datetime import datetime

if __name__ == "__main__":

	#входные параметры
	unixOptions = "s:e"
	gnuOptions = ["start_dt=", "end_dt="]

	fullCmdArguments = sys.argv
	argumentList = fullCmdArguments[1:]

	try:
		arguments, values = getopt.getopt(argumentList, unixOptions, gnuOptions)
	except getopt.error as err:
		print (str(err))
		sys.exit(2)

	start_dt = ''
	end_dt = ''

	for currentArgument, currentValue in arguments:
		if currentArgument in ("-s", "--start_dt"):
			start_dt = currentValue
		elif currentArgument in ("-e", "--end_dt"):
			end_dt = currentValue

    # параметры подключения к БД
	db_config = {'user': 'my_user',         # имя пользователя
	             'pwd': 'my_user_password', # пароль
	             'host': 'localhost',       # адрес сервера
	             'port': 5432,              # порт подключения
	             'db': 'zen'}               # название базы данных

	# формируем строку соединения с БД
	connection_string = 'postgresql://{}:{}@{}:{}/{}'.format(db_config['user'],
	                                                         db_config['pwd'],
	                                                         db_config['host'],
	                                                         db_config['port'],
	                                                         db_config['db'])
	# подключаемся к БД
	engine = create_engine(connection_string)

	# sql-запрос.
	query = '''SELECT *, TO_TIMESTAMP(ts / 1000) AT TIME ZONE 'Etc/UTC' AS dt
	           FROM log_raw
	           WHERE TO_TIMESTAMP(ts / 1000) AT TIME ZONE 'Etc/UTC' BETWEEN '{}'::TIMESTAMP AND '{}'::TIMESTAMP
	        '''.format(start_dt, end_dt)

	# выполняем запрос и сохраняем результат
	log_raw = pd.io.sql.read_sql(query, con = engine)

	# округляем дату/время до минут
	log_raw['dt'] = pd.to_datetime(log_raw['dt']).dt.round('min')

	# формируем агрегированные таблицы
	# визиты
	dash_visits = log_raw.groupby(['item_topic', 'source_topic', 'age_segment', 'dt'], as_index=False)\
	    .agg({'event_id':'count'})
	
	dash_visits.columns = ['item_topic', 'source_topic', 'age_segment', 'dt', 'visits']
	# просмотры
	dash_engagement = log_raw.groupby(['dt', 'item_topic', 'event', 'age_segment'], as_index=False)\
	    .agg({'user_id':'nunique'})
	
	dash_engagement.columns = ['dt', 'item_topic', 'event', 'age_segment', 'unique_users']
	# формируем словарь для цикла
	table_list = {'dash_visits': dash_visits, 
	              'dash_engagement': dash_engagement}

	for table_name, table_data in table_list.items():
		query = '''DELETE FROM {}
	               WHERE dt BETWEEN '{}'::TIMESTAMP AND '{}'::TIMESTAMP
	            '''.format(table_name, start_dt, end_dt)
		engine.execute(query)

	    # записываем агрегированные таблицы в базу данных
		table_data.to_sql(name = table_name, con = engine, if_exists = 'append', index = False)