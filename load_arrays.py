#!/usr/bin/env python2.7
'''
python server.py [HOST] [PORT] [user] [password]
http://localhost:[PORT]
'''

import os
import sys
import datetime
import random
from sqlalchemy import *
from sqlalchemy.pool import NullPool
from flask import Flask, request, render_template, g, redirect, Response, session


DATABASEURI = 'postgresql://jr3663:JustJackForrest555@35.227.79.146/proj1part2'
engine = create_engine(DATABASEURI)

def before_request():
	'''
	Setup a database connection that can be used throughout the request.
	'''
	try:
		g.conn = engine.connect()
	except Exception as e:
		print(e)
		print('Error connecting to database.')
		import traceback
		traceback.print_exc()
		g.conn = None

def teardown_request():
	'''
	Close the database connection.
	'''
	try:
		g.conn.close()
	except Exception as e:
		pass

def load_arrays():
	'''
	Setup a database connection that can be used throughout the request.
	'''

	random.seed()

	metadata = MetaData()
	players_tbl = Table('players', metadata,
						Column('player_id', String(20) , primary_key=True),
						Column('player_name', String(50)),
						Column('position', String(5)),
						Column('price', Integer ),
						Column('years_played', ARRAY(Integer)))
	try:
		new_conn = engine.connect()
	except Exception as e:
		print(e)
		print('Error connecting to database.')
		return

	# SELECT TO GET EACH PLAYER's player_id INTO ARRAY
	cursor = new_conn.execute('SELECT p.player_id FROM players p')

	# FOR EACH ENTRY IN ARRAY
	for row in cursor:
		# RANDOMLY ADD YEARS TO PLAYER_YEARS ARRAY
		player_years = []
		for yr in range(2000, 2017):
			if random.randint(0, 1) == 1:
				player_years.append(yr)

		# UPDATE PLAYER'S years_played ATTRIBUTE VALUE
		stmt = players_tbl.update().where(players_tbl.c.player_id==row['player_id']).values(years_played=player_years)
		try:
			new_conn.execute(stmt)
			#	new_conn.execute('UPDATE players SET years_played = array([2005, 2007]) WHERE player_name = %s')
		except Exception as e:
			print(e)
			return

	try:
		new_conn.close()
	except Exception as e:
		pass


if __name__ == '__main__':
	load_arrays()
