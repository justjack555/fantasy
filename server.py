#!/usr/bin/env python2.7
'''
python server.py [HOST] [PORT] [user] [password]
http://localhost:[PORT]
'''

import os
import sys
import datetime
from sqlalchemy import *
from sqlalchemy.pool import NullPool
from flask import Flask, request, render_template, g, redirect, Response, session

app = Flask(__name__)
app.secret_key = 'ABZr98j/3yX R~XHH!jmx]LWX/,7RT'
DATABASEURI = 'postgresql://jr3663:JustJackForrest555@35.227.79.146/proj1part2'
engine = create_engine(DATABASEURI)

@app.before_request
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

@app.teardown_request
def teardown_request(exception):
	'''
	Close the database connection.
	'''
	try:
		g.conn.close()
	except Exception as e:
		pass

@app.route('/', methods=['GET'])
def index():
	'''
	GET: Render the index page with static data only
	'''
	return render_template('index.html')

@app.route('/users/signup/', methods=['GET', 'POST'])
def signup():
	'''
	GET: Render the signup page with static data only
	POST: Process user signup and user login and redirect to team page
	      Form should contain login key and password key
	'''
	if request.method == 'GET':
		return render_template('sessions/signup.html')
	else:
		if 'login' in session:
			session.pop('login', None)
		cursor = g.conn.execute('SELECT MAX(user_id) FROM users')
		row = cursor.fetchone()
		user_id = row[0] + 1 if row[0] is not None else 0

		try:
			g.conn.execute('INSERT INTO users VALUES (%s, %s, %s, %s)', user_id, request.form['login'], request.form['password'], 0)
		except Exception as e:
			print(e)
			return render_template('sessions/signup.html')

		session['login'] = request.form['login']
		return redirect('/teams/')

@app.route('/users/login/', methods=['GET', 'POST'])
def login():
	'''
	GET: Render the login page with static data only
	POST: Process user login and redirect to team page
	      Form should contain login key and password key
	'''
	if request.method == 'GET':
		if 'login' in session:
			return redirect('/teams/')
		return render_template('sessions/login.html')
	else:
		cursor = g.conn.execute('SELECT login, password FROM users')
		for row in cursor:
			if row['login'] == request.form['login'] and row['password'] == request.form['password']:
				session['login'] = request.form['login']
				return redirect('/teams/')
		return render_template('sessions/login.html')

@app.route('/users/logout/', methods=['GET'])
def logout():
	'''
	GET: Process user logout and redirect to index page
	'''
	if 'login' in session:
		session.pop('login', None)
	return redirect('/')

@app.route('/teams/', methods=['GET'])
def teams():
	'''
	GET: Render the team page with team's player info
	'''
	if 'login' not in session:
		return redirect('/users/login/')

	context = {'player_names': [], 'positions': [], 'prices': []}
	cursor1 = g.conn.execute('SELECT u.user_id FROM users u WHERE u.login = %s', session['login'])
	user_id = cursor1.fetchone()['user_id']
	cursor2 = g.conn.execute('SELECT o.player_id FROM owns o WHERE o.user_id = %s', user_id)
	for row2 in cursor2:
		cursor3 = g.conn.execute('SELECT MAX(timestamp) FROM transactions t WHERE t.user_id = %s AND t.player_id = %s', user_id, row2['player_id'])
		max_timestamp = cursor3.fetchone()[0]
		cursor4 = g.conn.execute('''SELECT t.player_id FROM transactions t WHERE t.user_id = %s AND t.type = 'CLAIM' AND t.timestamp = %s''', user_id, max_timestamp)
		row4 = cursor4.fetchone()
		if row4:
			cursor5 = g.conn.execute('SELECT * FROM players p WHERE p.player_id = %s', row4['player_id'])
			row5 = cursor5.fetchone()
			context['player_names'].append(row5['player_name'])
			context['positions'].append(row5['position'])
			context['prices'].append(row5['price'])
	return render_template('teams/teams.html', **context)

def claimed(user_id, player_id):
	players = []
	cursor1 = g.conn.execute('SELECT o.player_id FROM owns o WHERE o.user_id = %s', user_id)
	for row1 in cursor1:
		cursor2 = g.conn.execute('SELECT MAX(timestamp) FROM transactions t WHERE t.user_id = %s AND t.player_id = %s', user_id, row1['player_id'])
		max_timestamp = cursor2.fetchone()[0]
		cursor3 = g.conn.execute('''SELECT t.player_id FROM transactions t WHERE t.user_id = %s AND t.type = 'CLAIM' AND t.timestamp = %s''', user_id, max_timestamp)
		row3 = cursor3.fetchone()
		if row3:
			cursor4 = g.conn.execute('SELECT * FROM players p WHERE p.player_id = %s', row3['player_id'])
			row4 = cursor4.fetchone()
			players.append(row4['player_id'])
	return player_id in players

def budget(payroll, user_id):
	cursor = g.conn.execute('SELECT l.max_payroll FROM leagues l, plays p, users u WHERE p.league_id = l.league_id AND p.user_id = u.user_id AND u.user_id = %s', user_id)
	for row in cursor:
		if payroll > row['max_payroll']:
			print('TOO EXPENSIVE')
			return False
	return True

@app.route('/teams/claim/', methods=['POST'])
def claim():
	'''
	POST: Process team claim of a player and redirect to team page
	      Form should contain player_name key
	'''
	if 'login' not in session:
		return redirect('/users/login/')

	cursor = g.conn.execute('SELECT p.player_id FROM players p WHERE p.player_name = %s', request.form['player_name'])
	player_id = cursor.fetchone()['player_id']
	cursor = g.conn.execute('SELECT u.user_id FROM users u WHERE u.login = %s', session['login'])
	user_id = cursor.fetchone()['user_id']
	if not claimed(user_id, player_id):
		price = g.conn.execute('SELECT p.price FROM players p WHERE p.player_id = %s', player_id).fetchone()[0]
		payroll = g.conn.execute('SELECT u.payroll FROM users u WHERE u.user_id = %s', user_id).fetchone()[0]
		payroll += price
		if budget(payroll, user_id):
			try:
				g.conn.execute('INSERT INTO owns VALUES (%s, %s)', user_id, player_id)
			except Exception as e:
				pass
			cursor = g.conn.execute('SELECT MAX(transaction_id) FROM transactions')
			row = cursor.fetchone()
			transaction_id = row[0] + 1 if row[0] is not None else 0
			try:
				g.conn.execute('''INSERT INTO transactions VALUES (%s, %s, %s, %s, 'CLAIM')''', transaction_id, user_id, player_id, datetime.datetime.now().strftime('%Y-%m-%d %H:%M:%S'))
				g.conn.execute('UPDATE users SET payroll = %s WHERE user_id = %s', payroll, user_id)
			except Exception as e:
				print(e)
	return redirect('/teams/')

@app.route('/teams/waive/', methods=['POST'])
def waive():
	'''
	POST: Process team waive of a player and redirect to team page
	      Form should contain player_name key
	'''
	if 'login' not in session:
		return redirect('/users/login/')

	cursor = g.conn.execute('SELECT p.player_id FROM players p WHERE p.player_name = %s', request.form['player_name'])
	player_id = cursor.fetchone()['player_id']
	cursor = g.conn.execute('SELECT u.user_id FROM users u WHERE u.login = %s', session['login'])
	user_id = cursor.fetchone()['user_id']
	if claimed(user_id, player_id):
		price = g.conn.execute('SELECT p.price FROM players p WHERE p.player_id = %s', player_id).fetchone()[0]
		payroll = g.conn.execute('SELECT u.payroll FROM users u WHERE u.user_id = %s', user_id).fetchone()[0]
		payroll -= price

		cursor = g.conn.execute('SELECT MAX(transaction_id) FROM transactions')
		row = cursor.fetchone()
		transaction_id = row[0] + 1 if row[0] is not None else 0
		
		g.conn.execute('''INSERT INTO transactions VALUES (%s, %s, %s, %s, 'WAIVE')''', transaction_id, user_id, player_id,datetime.datetime.now().strftime('%Y-%m-%d %H:%M:%S'))
		g.conn.execute('UPDATE users SET payroll = %s WHERE user_id = %s', payroll, user_id)
	return redirect('/teams/')


@app.route('/players/batters/', methods=['GET'])
def batters():
	'''
	GET: Using arguments with player_name key, render the batters page with batter info
	'''
	if 'login' not in session:
		return redirect('/users/login/')

	cursor = None
	if 'player_name' in request.args:
		regex = '%' + request.args['player_name'].lower() + '%'
		cursor = g.conn.execute('SELECT * FROM players p, batters b WHERE p.player_id = b.player_id AND lower(p.player_name) LIKE %s', regex)
	else:
		cursor = g.conn.execute('SELECT * FROM players p, batters b WHERE p.player_id = b.player_id')
	context = {'player_names': [], 'positions': [], 'prices': [], 'atbats': [], 'averages': [], 'hits': [], 'b_walks': [], 'runs': [], 'rbis': [], 'homeruns': []}
	for row in cursor:
		context['player_names'].append(row['player_name'])
		context['positions'].append(row['position'])
		context['prices'].append(row['price'])
		context['atbats'].append(row['atbats'])
		context['averages'].append(row['average'])
		context['hits'].append(row['hits'])
		context['b_walks'].append(row['b_walks'])
		context['runs'].append(row['runs'])
		context['rbis'].append(row['rbi'])
		context['homeruns'].append(row['homeruns'])
	return render_template('players/batters.html', **context)


@app.route('/players/pitchers/', methods=['GET'])
def pitchers():
	'''
	GET: Using arguments with player_name key, render the pitchers page with pitcher info
	'''
	if 'login' not in session:
		return redirect('/users/login/')

	cursor = None
	if 'player_name' in request.args:
		regex = '%' + request.args['player_name'].lower() + '%'
		cursor = g.conn.execute('SELECT * FROM players p1, pitchers p2 WHERE p1.player_id = p2.player_id AND lower(p1.player_name) LIKE %s', regex)
	else:
		cursor = g.conn.execute('SELECT * FROM players p1, pitchers p2 WHERE p1.player_id = p2.player_id')
	
	context = {'player_names': [], 'positions': [], 'prices': [], 'innings': [], 'eras': [], 'p_walks': [], 'strikeouts': [], 'wins': [], 'losses': [], 'saves': []}
	for row in cursor:
		context['player_names'].append(row['player_name'])
		context['positions'].append(row['position'])
		context['prices'].append(row['price'])
		context['innings'].append(row['innings'])
		context['eras'].append(row['era'])
		context['p_walks'].append(row['p_walks'])
		context['strikeouts'].append(row['strikeouts'])
		context['wins'].append(row['wins'])
		context['losses'].append(row['losses'])
		context['saves'].append(row['saves'])
	return render_template('players/pitchers.html', **context)

@app.route('/leagues/', methods=['GET'])
def leagues():
	'''
	GET: If arguments have league_name key, render the individual league page with specific league standings
	GET: If arguments do not have league_name key, render the leagues page with list of user's leagues
	'''
	if 'login' not in session:
		return redirect('/users/login/')

	if 'league_name' in request.args:
		context = {'logins': [], 'points': []}
		cursor1 = g.conn.execute('SELECT * FROM leagues l WHERE l.league_name = %s', request.args['league_name'])
		row1 = cursor1.fetchone()
		if row1 is None:
			return redirect('/leagues/')
		context['league_name'] = row1['league_name']
		context['max_payroll'] = row1['max_payroll']
		context['atbats_weight'] = row1['atbats_weight']
		context['average_weight'] = row1['average_weight']
		context['hits_weight'] = row1['hits_weight']
		context['b_walks_weight'] = row1['b_walks_weight']
		context['runs_weight'] = row1['runs_weight']
		context['rbi_weight'] = row1['rbi_weight']
		context['homeruns_weight'] = row1['homeruns_weight']
		context['innings_weight'] = row1['innings_weight']
		context['era_weight'] = row1['era_weight']
		context['p_walks_weight'] = row1['p_walks_weight']
		context['strikeouts_weight'] = row1['strikeouts_weight']
		context['wins_weight'] = row1['wins_weight']
		context['losses_weight'] = row1['losses_weight']
		context['saves_weight'] = row1['saves_weight']
		
		cursor2 = g.conn.execute('SELECT u.user_id, u.login FROM users u, plays p WHERE u.user_id = p.user_id AND p.league_id = %s', row1['league_id'])
		for row2 in cursor2:
			context['logins'].append(row2['login'])
			points = 0
			cursor3 = g.conn.execute('SELECT o.player_id FROM owns o WHERE o.user_id = %s', row2['user_id'])
			for row3 in cursor3:
				cursor4 = g.conn.execute('SELECT MAX(timestamp) FROM transactions t WHERE t.user_id = %s AND t.player_id = %s', row2['user_id'], row3['player_id'])
				max_timestamp = cursor4.fetchone()[0]
				cursor5 = g.conn.execute('''SELECT t.player_id FROM transactions t WHERE t.user_id = %s AND t.type = 'CLAIM' AND t.timestamp = %s''', row2['user_id'], max_timestamp)
				row5 = cursor5.fetchone()
				if row5:
					cursor6 = g.conn.execute('SELECT * FROM batters b WHERE b.player_id = %s', row5['player_id'])
					row6 = cursor6.fetchone()
					if row6:
						points += calculate_points(row1, row6)
					cursor7 = g.conn.execute('SELECT * FROM pitchers p WHERE p.player_id = %s', row5['player_id'])
					row7 = cursor7.fetchone()
					if row7:
						points += calculate_points(row1, row7)
			context['points'].append(points)
		return render_template('leagues/league.html', **context)
	else:
		cursor = g.conn.execute('SELECT u.user_id FROM users u WHERE u.login = %s', session['login'])
		user_id = cursor.fetchone()['user_id']
		
		context = {'user_league_names': [], 'all_league_names': []}
		cursor = g.conn.execute('SELECT l.league_name FROM users u, plays p, leagues l WHERE u.user_id = p.user_id AND p.league_id = l.league_id AND u.user_id = %s', user_id)
		for row in cursor:
			context['user_league_names'].append(row['league_name'])
		cursor = g.conn.execute('SELECT l.league_name FROM leagues l')
		for row in cursor:
			context['all_league_names'].append(row['league_name'])
		return render_template('leagues/leagues.html', **context)

def calculate_points(weights, values):
	points = 0
	stats = ['atbats', 'average', 'hits', 'b_walks', 'runs', 'rbi', 'homeruns', 'innings', 'era', 'p_walks', 'strikeouts', 'wins', 'losses', 'saves']
	for stat in stats:
		try:
			points += weights[stat + '_weight'] * values[stat]
		except Exception as e:
			continue
	return points

@app.route('/leagues/transactions/', methods=['GET'])
def leagues_transactions():
	'''
	GET: Using arguments with league_name key, render the league transactions page with league transactions
	'''
	if 'login' not in session:
		return redirect('/users/login/')


	cursor = g.conn.execute('SELECT l.league_id FROM leagues l WHERE l.league_name = %s', request.args['league_name'])
	league_id = cursor.fetchone()['league_id']
	context = {'logins': [], 'player_names': [], 'timestamps': [], 'types': []}
	cursor1 = g.conn.execute('SELECT p.user_id FROM plays p WHERE p.league_id = %s', league_id)
	for row1 in cursor1:
		cursor2 = g.conn.execute('SELECT u.login, p.player_name, t.timestamp, t.type FROM users u, players p, transactions t WHERE u.user_id = t.user_id AND p.player_id = t.player_id AND u.user_id = %s ORDER BY t.timestamp DESC', row1['user_id'])
		for row2 in cursor2:
			context['logins'].append(row2['login'])
			context['player_names'].append(row2['player_name'])
			context['timestamps'].append(row2['timestamp'])
			context['types'].append(row2['type'])
	return render_template('leagues/leagues_transactions.html', **context)

@app.route('/leagues/add/', methods=['POST'])
def leagues_add():
	'''
	POST: Process league add and redirect to leagues page
	      Form should contain league_name key
	'''
	if 'login' not in session:
		return redirect('/users/login/')

	cursor = g.conn.execute('SELECT u.user_id FROM users u WHERE u.login = %s', session['login'])
	user_id = cursor.fetchone()['user_id']
	cursor = g.conn.execute('SELECT u.payroll FROM users u WHERE u.user_id = %s', user_id)
	payroll = cursor.fetchone()[0]
	cursor = g.conn.execute('SELECT l.league_id, l.max_payroll FROM leagues l WHERE l.league_name = %s', request.form['league_name'])
	row = cursor.fetchone()
	league_id = row['league_id']
	max_payroll = row['max_payroll']
	if payroll <= max_payroll:
		try:
			g.conn.execute('INSERT INTO plays VALUES (%s, %s)', user_id, league_id)
		except Exception as e:
			pass
	return redirect('/leagues/')

@app.route('/leagues/create/', methods=['GET', 'POST'])
def leagues_create():
	'''
	GET: Render the create league page with static data only
	POST: Process league create and redirect to individual league page
	      Form should contain keys for all league values except for league_id and user_id
	'''
	print('here')
	if 'login' not in session:
		return redirect('/users/login/')

	if request.method == 'GET':
		return render_template('leagues/leagues_create.html')
	else:
		print('post')
		cursor = g.conn.execute('SELECT u.user_id FROM users u WHERE u.login = %s', session['login'])
		user_id = cursor.fetchone()['user_id']
		cursor = g.conn.execute('SELECT MAX(league_id) FROM leagues')
		row = cursor.fetchone()
		league_id = row[0] + 1 if row[0] is not None else 0
		try:
			g.conn.execute('INSERT INTO leagues VALUES (%s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s)', league_id, user_id, request.form['league_name'], request.form['max_payroll'], request.form['atbats_weight'],  request.form['average_weight'], request.form['hits_weight'], request.form['b_walks_weight'], request.form['runs_weight'], request.form['rbi_weight'], request.form['homeruns_weight'], request.form['innings_weight'], request.form['era_weight'], request.form['p_walks_weight'], request.form['strikeouts_weight'], request.form['wins_weight'], request.form['losses_weight'], request.form['saves_weight'])
			g.conn.execute('INSERT INTO plays VALUES (%s, %s)', user_id, league_id)
		except Exception as e:
			print('error')
			print(e)
			pass
		return redirect('/leagues/')

if __name__ == '__main__':
	import click

	@click.command()
	@click.option('--debug', is_flag=True)
	@click.option('--threaded', is_flag=True)
	@click.argument('HOST', default='0.0.0.0')
	@click.argument('PORT', default=8111, type=int)
	@click.argument('UNAME', default='')
	@click.argument('PWORD', default='')
	def run(debug, threaded, host, port, uname, pword):
		HOST, PORT, UNAME, PWORD = host, port, uname, pword
		print('running on %s:%d' % (HOST, PORT))
		app.run(host=HOST, port=PORT, debug=debug, threaded=threaded)

	run()
