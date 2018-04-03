#!/usr/bin/env python2.7
'''
python server.py [user] [password]
http://localhost:8111
'''

import os
import sys
from sqlalchemy import *
from sqlalchemy.pool import NullPool
from flask import Flask, request, render_template, g, redirect, Response, session

client_folder = os.path.join(os.path.dirname(os.path.abspath(__file__)), 'client')
app = Flask(__name__, template_folder=client_folder)
app.secret_key = 'ABZr98j/3yX R~XHH!jmx]LWX/,7RT'
DATABASEURI = 'postgresql://%s:%s@35.227.79.146/proj1part2' % (sys.argv[1], sys.argv[2])
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
	#TODO
	if 'login' not in session:
		return redirect('/login/')

	#SQL QUERY
	context = {'player_names': [], 'positions': [], 'prices': []}
	cursor = g.conn.execute()
	for row in cursor:
		context['player_names'].append(row['player_name'])
		context['positions'].append(row['position'])
		context['prices'].append(row['price'])
	return render_template('teams.html', **context)

@app.route('/teams/claim/', methods=['POST'])
def claim():
	'''
	POST: Process team claim of a player and redirect to team page
	'''
	#TODO
	if 'login' not in session:
		return redirect('/login/')
	#check if already on team then update user's team after player was claimed
	pass

@app.route('/teams/waive/', methods=['POST'])
def waive():
	'''
	POST: Process team waive of a player and redirect to team page
	'''
	#TODO
	if 'login' not in session:
		return redirect('/login/')
	#check if already not on team then update user's team after player was waived
	pass

@app.route('/players/batters/', methods=['GET'])
def batters():
	'''
	GET: Using arguments with player_name key, render the batters page with batter info
	'''
	if 'login' not in session:
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

@app.route('/players/pitchers/', methods=['GET'])
def pitchers():
	'''
	GET: Using arguments with player_name key, render the pitchers page with pitcher info
	'''
	if 'login' not in session:
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

@app.route('/leagues/', methods=['GET'])
def leagues():
	'''
	GET: If arguments do not have league_name key, render the leagues page with list of user's leagues
	GET: If arguments have league_name key, render the individual league page with specific league standings
	'''
	#TODO
	if 'login' not in session:
		return redirect('/login/')
	pass

@app.route('/leagues/transactions/', methods=['GET'])
def leagues_transactions():
	'''
	GET: Using arguments with league_name key, render the league transactions page with league transactions
	'''
	#TODO
	if 'login' not in session:
		return redirect('/login/')
	pass

@app.route('/leagues/add/', methods=['POST'])
def leagues_add():
	'''
	POST: Process league add and redirect to leagues page
	'''
	#TODO
	if 'login' not in session:
		return redirect('/login/')
	pass

@app.route('/leagues/create/', methods=['GET', 'POST'])
def leagues_create():
	'''
	GET: Render the create league page with static data only
	POST: Process league create and redirect to individual league page
	'''
	#TODO
	if 'login' not in session:
		return redirect('/login/')
	pass

@app.route('/leagues/modify/', methods=['POST'])
def leagues_modify():
	#TODO
	if 'login' not in session:
		return redirect('/login/')
	pass

if __name__ == '__main__':
	import click

	@click.command()
	@click.option('--debug', is_flag=True)
	@click.option('--threaded', is_flag=True)
	@click.argument('HOST', default='0.0.0.0')
	@click.argument('PORT', default=8111, type=int)
	def run(debug, threaded, host, port):
		HOST, PORT = host, port
		print('running on %s:%d' % (HOST, PORT))
		app.run(host=HOST, port=PORT, debug=debug, threaded=threaded)

	run()
