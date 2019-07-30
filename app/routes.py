from app import app
from flask import render_template, flash, redirect, url_for, request
from app.forms import LoginForm , RegistrationForm, EditprofileForm
from app.models import User
from app import db
from flask_login import login_user, current_user, logout_user, login_required
from werkzeug.urls import url_parse
from datetime import datetime

@app.route('/')
@app.route('/index')
@login_required
def index():
	user = {'username':'Bolaji'}
	posts = [
		{
			'author':{'username':'Bola'},
			'body':'you guys eat too much eba!'

		},

		{
			'author':{'username':'Mohammed'},
			'body': 'life is easy,all is well'
		},
	]
	return render_template('index.html', title='Home Page', posts=posts)


@app.route('/login', methods=['GET', 'POST'])
def login():
	if current_user.is_authenticated:
		return redirect(url_for('index'))
	form = LoginForm()
	if form .validate_on_submit():
		user = User.query.filter_by(username=form.username.data).first()
		if user is None or not user.check_password(form.password.data):
			flash('invalid username or password')
			return redirect(url_for('login'))
		login_user(user,remember=True) #form.remember_me.data  #once a user is authenticated you log them in with login_user
		next_page = request.args.get('next')
		if not next_page or url_parse(next_page).netloc != '':
			next_page=url_for('index')

		return redirect(url_for('index'))
	return render_template('login.html', title='sign in', form=form)


@app.route('/logout')
def logout():
	logout_user()
	return redirect(url_for('index'))

@app.route('/register', methods=['GET','POST'])
def register():
	if current_user.is_authenticated:
		return redirect(url_for('index'))
	form = RegistrationForm()
	if form.validate_on_submit():
		user=User(username=form.username.data, email=form.email.data)
		user.set_password(form.password.data)
		db.session.add(user)
		db.session.commit()
		flash('congratulations, you have sucessfully reistered')
		return redirect(url_for('login'))
	return render_template('register.html', title='register', form=form)

@app.route('/user/<username>')
@login_required
def user(username):
	user = User.query.filter_by(username=username).first_or_404()
	posts = [
		{'author':user, 'body':'Test post 1'},
		{'author':user, 'body':'Test post 2'}
	]
	return render_template('user.html', user=user, posts=posts)

@app.before_request
def defore_request():
	if current_user.is_authenticated:
		current_user.last_seen = datetime.utcnow()
		db.session.commit()


@app.route('/edit_profile.html', methods=['GET', 'POST'])
@login_required
def edit_profile():
		form=EditprofileForm(current_user.username)
		if  form.validate_on_submit():
			current_user.username = form.username.data
			current_user.about_me = form.about_me.data
			db.session.commit()
			flash ('your changes have been saved.')
			return redirect(url_for('edit_profile'))

		elif request.method == 'GET':
			 form.username.data = current_user.username
			 form.about_me.data = current_user.about_me
		return render_template('edit_profile.html', title='edit profile', form=form)
'''
@app.route('/request-info')
def request_info():
	geoip_url = 'http://freegeoip.net/json/{}'.format(request.remote_addr)
	client_location = requests.get(geoip_url).json()
	return render_template('info.html', title='request_info', gets=gets)

'''

@app.route('/follow/<username>')
@login_required
def follow(username):
	user=User.query.filter_by(username=username).first()
	if user is None:
		flash('user {} not found'. format(username))  #this will return user buhari is not found. if the person type buhari in the /follow/buhari
		return redirect(url_for('index'))
	if user == current_user:
		flash('please you can\'t follow yourself')
		return redirect(url_for('user', username=username))
	current_user.follow(user)
	db.session.commit()
	flash('you have successfully followed {}'.format(username))
	return redirect(url_for('user', username=username))

@app.route('/unfollow/<username>')
@login_required
def unfollow(username):
	user= User.query.filter_by(username=username).first()
	if user is None:
		flash('user {} not found'. format(username))
		return redirect(url_for('index'))
	if user == current_user:
		flash('please you can\'t unfollow yourself')
		return redirect(url_for('user', username=username))
	current_user.unfollow(user)
	db.session.commit()
	flash('you have successfully unfollowed {}'.format(username))
	return redirect(url_for('user', username=username))
