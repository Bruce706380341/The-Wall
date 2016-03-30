from flask import Flask, render_template, redirect, session, flash, request
import re
from flask.ext.bcrypt import Bcrypt
from mysqlconnection import MySQLConnector
app = Flask(__name__)
b = Bcrypt(app)
app.secret_key = "ThisIsMySecret"
mysql = MySQLConnector('oscarwall')

@app.route('/')
def index():
	return render_template('index.html')

@app.route('/register', methods=['POST'])
def register():
	first_name = request.form['first_name']
	last_name = request.form['last_name']
	email = request.form['email']
	password = request.form['password']
	pw_hash = b.generate_password_hash(password)

	sql = "INSERT INTO Users (first_name, last_name, email, password) values('{}', '{}', '{}', '{}')".format(first_name, last_name, email, pw_hash)
	mysql.run_mysql_query(sql)

	return redirect('/')


@app.route('/login', methods=['post'])
def login():
	email = request.form['email']
	password = request.form['password']

	sql = "select * from users where email = '{}'".format(email)
	user = mysql.fetch(sql)
	if len(user) > 0:
		if b.check_password_hash(user[0]['password'], password):
			session['user_id'] = user[0]['id']
			print session['user_id']
			return redirect('/wall')
		else:
			return redirect('/')
	else:
		return redirect('/')

@app.route('/wall')
def wall():
	sql = "select id, first_name, last_name from users where id = '{}'".format(session['user_id'])
	user = mysql.fetch(sql)
	messql = "SELECT messages.id, users.first_name, messages.message, messages.created_at from messages join users on messages.users_id = users.id"

	messages = mysql.fetch(messql)
	comsql = "SELECT comments.comment, comments.created_at, comments.updated_at, comments.messages_id, comments.users_id, users.first_name from comments join users on comments.users_id = users.id"
	comments = mysql.fetch(comsql)
	return render_template('wall.html', user=user[0], messages = messages, comments = comments)

@app.route('/messages', methods=["post"])
def message():
	sql = "INSERT INTO messages (message, users_id, created_at, updated_at) values('{}', '{}', NOW(), NOW())".format(re.escape(request.form['message']), request.form['user_id'])
	mysql.run_mysql_query(sql)
	return redirect('/wall')

@app.route('/comments', methods=["post"])
def comment():
	sql = "INSERT INTO comments (comment, messages_id, users_id, created_at, updated_at) values ('{}', '{}', '{}', NOW(), NOW())".format(request.form['comment'], request.form['mes_id'], request.form['user_id'])
	mysql.run_mysql_query(sql)
	return redirect('/wall')

@app.route('/logout')
def logout():
	session.clear()
	return redirect('/')

app.run(debug=True)