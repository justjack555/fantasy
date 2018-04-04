#!/usr/bin/env python2.7
'''
python server.py [user] [password]
http://localhost:8111
'''

import os
import sys
import datetime
from sqlalchemy import *
from sqlalchemy.pool import NullPool
from flask import Flask, request, render_template, g, redirect, Response, session

#client_folder = os.path.join(os.path.dirname(os.path.abspath(__file__)), 'client')
app = Flask(__name__)
app.secret_key = 'ABZr98j/3yX R~XHH!jmx]LWX/,7RT'
DATABASEURI = 'postgresql://%s:%s@35.227.79.146/proj1part2' % (sys.argv[3], sys.argv[4])
engine = create_engine(DATABASEURI)

@app.before_request
def before_request():
	'''
	Setup a database connection that can be used throughout the request.
	'''
	try:
		g.conn = engine.connect()
	except:
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
		return render_template('signup.html')
	else:
		if 'login' in session:
			session.pop('login', None)
		cursor = g.conn.execute('SELECT MAX(user_id) FROM users')
		max_user_id = cursor.fetchone()[0]
		try:
			g.conn.execute('INSERT INTO users VALUES (%d, %s, %s, 0)', max_user_id + 1, request.form['login'], request.form['password'])
		except:
			return render_template('signup.html')
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
		return render_template('login.html')
	else:
		cursor = g.conn.execute('SELECT login, password FROM users')
		for row in cursor:
			if row['login'] == request.form['login'] and row['password'] == request.form['password']:
				session['login'] = request.form['login']
				return redirect('/teams/')
		return render_template('login.html')

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
		return redirect('/login/')

	context = {'player_names': [], 'positions': [], 'prices': []}
	cursor1 = g.conn.execute('SELECT u.user_id FROM users u WHERE u.login = %s', session['login'])
	user_id = cursor1.fetchone()['user_id']
	cursor2 = g.conn.execute('SELECT o.player_id FROM own o WHERE o.user_id = %s', user_id)
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
	return render_template('teams.html', **context)

'''
@app.route('/teams/claim/', methods=['POST'])
def claim():
'''
'''
	POST: Process team claim of a player and redirect to team page
	      Form should contain player_name key
'''
'''	if 'login' not in session:
		return redirect('/login/')

	cursor = g.conn.execute('SELECT p.player_id FROM players p WHERE p.player_name = %s', request.form['player_name'])
	player_id = cursor.fetchone()['player_id']
	cursor = g.conn.execute('SELECT u.user_id FROM users u WHERE u.login = %s', session['login'])
	user_id = cursor.fetchone()['user_id']
	if not claimed(user_id, player_id):
		try:
			g.conn.execute('INSERT INTO owns VALUES (%d, %s)', user_id, player_id)
		except:
			pass
		cursor = g.conn.execute('SELECT MAX(transaction_id) FROM transactions')
		max_transaction_id = cursor.fetchone()[0]
'''
#		g.conn.execute('''INSERT INTO transactions VALUES (%d, %d, %s, %s, 'CLAIM')''', max_transaction_id + 1, user_id, player_id,datetime.datetime.now().strftime('%Y-%m-%d'))
#	return redirect('/teams/')


def claimed(user_id, player_id):
	players = []
	cursor1 = g.conn.execute('SELECT o.player_id FROM own o WHERE o.user_id = %s', user_id)
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

#@app.route('/teams/waive/', methods=['POST'])
#def waive():
'''
	POST: Process team waive of a player and redirect to team page
'''
'''	if 'login' not in session:
		return redirect('/login/')

	cursor = g.conn.execute('SELECT p.player_id FROM players p WHERE p.player_name = %s', request.form['player_name'])
	player_id = cursor.fetchone()['player_id']
	cursor = g.conn.execute('SELECT u.user_id FROM users u WHERE u.login = %s', session['login'])
	user_id = cursor.fetchone()['user_id']
	if claimed(user_id, player_id):
		cursor = g.conn.execute('SELECT MAX(transaction_id) FROM transactions')
		max_transaction_id = cursor.fetchone()[0]
'''
#		g.conn.execute('''INSERT INTO transactions VALUES (%d, %d, %s, %s, 'WAIVE')''', max_transaction_id + 1, user_id, player_id,datetime.datetime.now().strftime('%Y-%m-%d'))
#	return redirect('/teams/')


#@app.route('/players/batters/', methods=['GET'])
#def batters():
'''
	GET: Using arguments with player_name key, render the batters page with batter info
'''
'''	if 'login' not in session:
		return redirect('/login/')

	search = ''
	if 'player_name' in request.args:
		search = ' AND p.player_name = %s' % (request.args['player_name'])

	context = {'player_names': [], 'positions': [], 'prices': [], 'atbats': [], 'averages': [], 'hits': [], 'b_walks': [], 'runs': [], 'rbis': [], 'homeruns': []}
	cursor = g.conn.execute('SELECT * FROM players p, batters b WHERE p.player_id = b.player_id%s', search)
	for row in cursor:
		context['player_names'].append(row['player_name'])
		context['positions'].append(row['player_name'])
		context['prices'].append(row['player_name'])
		context['atbats'].append(row['player_name'])
		context['averages'].append(row['player_name'])
		context['hits'].append(row['player_name'])
		context['b_walks'].append(row['player_name'])
		context['runs'].append(row['player_name'])
		context['rbis'].append(row['player_name'])
		context['homeruns'].append(row['player_name'])
	return render_template('batters.html', **context)
'''

# @app.route('/players/pitchers/', methods=['GET'])
# def pitchers():
'''
	GET: Using arguments with player_name key, render the pitchers page with pitcher info
'''
'''	if 'login' not in session:
		return redirect('/login/')

	search = ''
	if 'player_name' in request.args:
		search = ' AND p1.player_name = %s' % (request.args['player_name'])

	context = {'player_names': [], 'positions': [], 'prices': [], 'innings': [], 'eras': [], 'p_walks': [], 'strikeouts': [], 'wins': [], 'losses': [], 'saves': []}
	cursor = g.conn.execute('SELECT * FROM players p1, pitchers p2 WHERE p1.player_id = p2.player_id%s', search)
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
	return render_template('pitchers.html', **context)
'''
@app.route('/leagues/', methods=['GET'])
def leagues():
	'''
	GET: If arguments have league_name key, render the individual league page with specific league standings
	GET: If arguments do not have league_name key, render the leagues page with list of user's leagues
	'''
	if 'login' not in session:
		return redirect('/login/')

	if 'league_name' in request.args:
		context = {'logins': [], 'points': []}
		cursor1 = g.conn.execute('SELECT * FROM leagues l WHERE l.league_name = %s', request.args['league_name'])
		row1 = cursor1.fetchone()
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
		
		cursor2 = g.conn.execute('SELECT p.user_id FROM plays p WHERE p.league_id = %s', row1['league_id'])
		for row2 in cursor2:
			#for each user_id
			points = 0
			cursor3 = g.conn.execute('SELECT o.player_id FROM own o WHERE o.user_id = %s', row1['user_id'])
			for row3 in cursor3:
				#for each player_id
				cursor4 = g.conn.execute('SELECT MAX(timestamp) FROM transactions t WHERE t.user_id = %s AND t.player_id = %s', row2['user_id'], row3['player_id'])
				max_timestamp = cursor4.fetchone()[0]
				cursor5 = g.conn.execute('''SELECT t.player_id FROM transactions t WHERE t.user_id = %s AND t.type = 'CLAIM' AND t.timestamp = %s''', row2['user_id'], max_timestamp)
				row5 = cursor5.fetchone()
				if row5:
					#for each player currently on the team
					cursor6 = g.conn.execute('SELECT * FROM batters b WHERE b.player_id = %s', row5['player_id'])
					row6 = cursor6.fetchone()
					if row6:
						points += calculate_points(row6, row1)
					cursor7 = g.conn.execute('SELECT * FROM pitchers p WHERE p.player_id = %s', row5['player_id'])
					row7 = cursor7.fetchone()
					if row7:
						points += calculate_points(row7, row1)
			context['points'].append(points)
		return render_template('league.html', **context)
	else:
		context = {'league_names': []}
		cursor = g.conn.execute('SELECT l.league_name FROM users u, plays p, leagues l WHERE u.user_id = p.user_id AND p.league_id = l.league_id')
		for row in cursor:
			context['league_names'].append(row['league_name'])
		return render_template('leagues.html', **context)

def calculate_points(weights, values):
	points = 0
	stats = ['atbats', 'average', 'hits', 'b_walks', 'runs', 'rbi', 'homeruns', 'innings', 'era', 'p_walks', 'strikeouts', 'wins', 'losses', 'saves']
	for stat in stats:
		points += weights[stat + '_weight'] * values[stat]
	return points

#@app.route('/leagues/transactions/', methods=['GET'])
#def leagues_transactions():
'''
	GET: Using arguments with league_name key, render the league transactions page with league transactions
'''
'''	if 'login' not in session:
		return redirect('/login/')

	context = {'logins': [], 'player_names': [], 'timestamps': [], 'types': []}
	cursor1 = g.conn.execute('SELECT p.user_id FROM plays p WHERE p.league_id = %s', request.args['league_name'])
	for row1 in cursor1:
		cursor2 = g.conn.execute('SELECT t.timestamp, t.type, u.login, p.player_name FROM transactions t, users u, players p WHERE t.user_id = u.user_id AND t.player_id = p.player_id AND t.user_id = %s ORDER BY t.timestamp DESC', row1['user_id'])
		for row2 in cursor2:
			context['logins'].append(row2['login'])
			context['player_names'].append(row2['player_name'])
			context['timestamps'].append(row2['timestamp'])
			context['types'].append(row2['type'])
	return render_template('leagues_transactions.html', **context)
'''
#@app.route('/leagues/add/', methods=['POST'])
#def leagues_add():
'''
	POST: Process league add and redirect to leagues page
	      Form should contain league_name key
'''
'''	if 'login' not in session:
		return redirect('/login/')

	cursor = g.conn.execute('SELECT u.payroll FROM users u WHERE u.user_id = %s', session['login'])
	payroll = cursor.fetchone()[0]
	cursor = g.conn.execute('SELECT l.league_id, l.max_payroll FROM leagues l WHERE l.league_name = %s', request.form['league_name'])
	league_id = cursor.fetchone()['league_id']
	max_payroll = cursor.fetchone()['max_payroll']
	if payroll <= max_payroll:
		try:
			g.conn.execute('INSERT INTO plays VALUES (%d, %d)', session['login'], league_id)
		except:
			pass
	return redirect('/leagues/')
'''
#@app.route('/leagues/create/', methods=['GET', 'POST'])
#def leagues_create():
'''
	GET: Render the create league page with static data only
	POST: Process league create and redirect to individual league page
	      Form should contain keys for all league values except for league_id and user_id
'''
'''	if 'login' not in session:
		return redirect('/login/')

	if request.method == 'GET':
		return render_template('leagues_create.html')
	else:
		cursor = g.conn.execute('SELECT MAX(league_id) FROM leagues')
		max_league_id = cursor.fetchone()[0]
		cursor = g.conn.execute('SELECT u.user_id FROM users u WHERE u.login = %s', session['login'])
		user_id = cursor.fetchone()[0]
		try:
			g.conn.execute('INSERT INTO leagues VALUES (%d, %d, %s, %s, %d, %f, %f, %f, %f, %f, %f, %f, %f, %f, %f, %f, %f, %f)', max_league_id + 1, request.form['login'], request.form['league_name'], request.form['max_payroll'], request.form['atbats_weight'], , request.form['average_weight'], request.form['hits_weight'], request.form['b_walks_weight'], request.form['runs_weight'], request.form['rbi_weight'], request.form['homeruns_weight'], request.form['innings_weight'], request.form['era_weight'], request.form['p_walks_weight'], request.form['strikeouts_weight'], request.form['wins_weight'], request.form['losses_weight'], request.form['saves_weight'])
			g.conn.execute('INSERT INTO plays VALUES (%d, %d)', session['login'], max_league_id + 1)
		except:
			pass
		return redirect('/leagues/')
'''
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
