from flask import render_template, flash, redirect, url_for, request
from app import app, db
from app.forms import LoginForm, RegistrationForm, EditProfileForm, PostForm
from flask_login import current_user, login_user, logout_user, login_required
from app.models import User, Post
from werkzeug.urls import url_parse
from datetime import datetime
from app.forms import ResetPasswordForm, ResetPasswordRequestForm
from app.email import send_password_reset_email

@app.route('/', methods=['GET', 'POST']) #@app.route decorator creates an association between the URL given as an argument and the function
@app.route('/index', methods=['GET', 'POST'])
@login_required #a decorator to protect login() function from users that are not authenticated
def index():
    #user = {'username':'Bolaji'}
    form = PostForm()
    if form.validate_on_submit():
        post = Post(body=form.post.data, author=current_user)
        db.session.add(post)
        db.session.commit()
        flash('Your post is now live!')
#POST/REDIRECT/GET Pattern: after processing d form data, we redirect to home page -
#to help mitigate how refresh command is implemented in browsers
#if the post request only did a submissn, a refresh will resubmit d form -
#in such case, the user to confirm a duplicate submission.
#but if the post request is answered with a redirect, the browser will
#simply send a GET request to grab the argument page, so the last request
#is not a POST anymore
        return redirect(url_for('index'))
#we use Flask's request.args object to access access arguments given in the query string
    page=request.args.get('page',1,type=int)
# the followed_posts() method returns a SQLAlchemy query object. This object will grab
# the posts the user is following from the database.
    #posts = current_user.followed_posts().all()
#we add pagination to the home() and explore() view functions
    posts=current_user.followed_posts().paginate(
        page, app.config['POSTS_PER_PAGE'], False)
    next_url=url_for('index', page=posts.next_num) \
        if posts.has_next else None
    prev_url=url_for('index', page=posts.prev_num) \
        if posts.has_prev else None
    #return render_template('index.html', title='Home', form=form, posts=posts)
    return render_template('index.html', title='Home', form=form, posts=posts.items,
                           next_url=next_url, prev_url=prev_url)
'''
    posts = [
        {
            'author': {'username':'Man'},
            'body' : 'Beautiful times are here!'
        },
        {
            'author': {'username': 'God'},
            'body': 'Good times have come!'
        }
    ]
    return render_template('index.html', title='Home Page', posts=posts)
'''


#logging in users
@app.route('/login', methods=['GET', 'POST'])
def login():
    if current_user.is_authenticated:
        return redirect(url_for('index'))
    form = LoginForm()
    if form.validate_on_submit():
        user = User.query.filter_by(username=form.username.data).first()
        if user is None or not user.check_password(form.password.data):
            flash('Invalid user name or password!')
            return redirect(url_for('login'))
        login_user(user, remember=form.remember_me.data)
        next_page = request.args.get('next')

#There are actually three possible cases that need to be considered to determine where to redirect after a successful login:
#   If the login URL does not have a next argument:
#       then the user is redirected to the index page.
#
#    If the login URL includes a next argument that is set to a relative path (or in other words, a URL without the domain portion)
#       then the user is redirected to that URL.
#
#   If the login URL includes a next argument that is set to a full URL that includes a domain name:
#       then the user is redirected to the index page. This is to discourage an attacker from insering a URL leading to a malicious site

        if not next_page or url_parse(next_page).netloc != '':  #url_parse() determines whether the URL is relative or absoluts; and then check if netloc component is set or not
            next_page = url_for('index')
        return redirect(next_page)
    return render_template('login.html', title='Sign In', form=form)

@app.route('/logout')
def logout():
    logout_user()
    return redirect(url_for('index'))

@app.route('/register', methods=['GET', 'POST'])
def register():
    if current_user.is_authenticated:
        return redirect(url_for('index'))
    form = RegistrationForm()
    if form.validate_on_submit():
        user = User(username=form.username.data, email=form.email.data)
        user.set_password(form.password.data)
        db.session.add(user)
        db.session.commit()
        flash('Congratulations, you are now a registered user!')
        return redirect(url_for('login'))
    return render_template('register.html', title='Register', form=form)

@app.route('/user/<username>')  #<> implies a dynamic component
@login_required
def user(username):
    #given the username, load the user from the database
    #if the username does not exist, the fxn will not return, and instead a 404 exception will be raised
    user = User.query.filter_by(username=username).first_or_404()
    #we create a fake list of posts for the returned(or unreturned) user

    page=request.args.get('page', 1, type=int)
    posts=user.posts.order_by(Post.timestamp.desc()).paginate(
        page, app.config['POSTS_PER_PAGE'], False)
    next_url=url_for('user', username=user.username, page=posts.next_num) \
        if posts.next_num else None
    prev_url=url_for('user', username=user.username, page=posts.prev_num) \
        if posts.prev_num else None
    #we render a new 'user.html' template to which we pass the user object and the list of posts
    return render_template('user.html', user=user, posts=posts.items,
                           prev_url=prev_url, next_url=next_url)
#the paginatn links that are generated by the url_for() fxn uses the username argum., bcos they are pointing
#back at the user profile page, which has d username as a dynamic component of the URL.

@app.before_request #registers the decorated fxn to be executed right before the view fxn below
def before_request():
    if current_user.is_authenticated:
        current_user.last_seen = datetime.utcnow()
#so we needn't add to session bcos when we reference current_user, Flask-Login will invoke the user
#loader callback fxn, which will run a database query that will put the target user in the database
#session. So it's not necessary to add the user again in this function
        db.session.commit()

@app.route('/edit_profile', methods=['GET', 'POST'])
@login_required
def edit_profile():
    '''
        to use def validate_username() of forms.py, we will add original username argument
        where the form object is created
    '''
    form = EditProfileForm(current_user.username)
    if form.validate_on_submit():
#if the above test returns true, i copy the data from the form into the user object and then write
#the object to the database. LOOK BELOW RETURN FOR MORE COMMENT

        current_user.username = form.username.data
        current_user.about_me = form.about_me.data
        db.session.commit()
        flash('Your changes have been saves')
        return redirect(url_for('edit_profile'))
    elif request.method == 'GET':

        form.username.data = current_user.username
        form.about_me.data = current_user.about_me
    return render_template('edit_profile.html', title='Edit Profile', form=form)


'''validate_on_submit() could returns a False :
    A)bcos the browser sent a 'GET'(i.e form is being requested gor the first time) or
    B)bcos the browser sent a 'POST' request with some form data is invalid:
i)FOR CASE A: prepopulate the form with data that's stored in the db
we respond by providing an initial version of the form template. This is the reverse
of what we did during submission - move data stored in the user field to the form.
Those form fields will have the current data stored for the user.
ii)FOR CASE B: 'POST' is automatically checked for a submission with failed validation 
 we don't want to write anything on the form fields(which ia already populated by WTForms)
'''

@app.route('/follow/<username>')
@login_required
def follow(username):
    user = User.query.filter_by(username=username).first()
    if user is None:
        flash('User {} not found.'.format(username))
        return redirect(url_for('index'))
    if user == current_user:
        flash('You cannot follow yourself!')
        return redirect(url_for('user', username=username))
    current_user.follow(user)
    db.session.commit()
    flash('You are following {}!'.format(username))
    return redirect(url_for('user', username=username))

@app.route('/unfollow/<username>')
@login_required
def unfollow(username):
    user = User.query.filter_by(username=username).first()
    if user is None:
        flash('User {} not found.'.format(username))
        return redirect(url_for('index'))
    if user == current_user:
        flash('You cannot unfollow yourself!')
        return redirect(url_for('user', username=username))
    current_user.unfollow(user)
    db.session.commit()
    flash('You are not following {}.'.format(username))
    return redirect(url_for('user', username=username))
'''
@app.route('/', methods=['GET', 'POST'])
@app.route('/index', methods=['GET', 'POST'])
@login_required
def index():
    form=PostForm()
    if form.validate_on_submit():
        post=Post(body=form.posst.data, author=current_user)
        db.session.add(post)
        db.session.commit()
        flash('Your post has been published')
        return redirect(url_for('index'))
'''
'''
        posts=[
            {
                'author':{'username':'John'},
                'body':'Beautiful day in Portland!'
            },
            {
                'author':{'username':'Susan'},
                'body':'The course is really interesting!'
            }
        ]
    '''
'''
    posts = current_user.followed_posts().all()
    return render_template("index.html", title='Home Page', form=form, posts=posts)
'''

#shows a stream of all users, including those not followed
@app.route('/explore')
@login_required
def explore():
    page=request.args.get('page',1,type=int)    #request.args exposes the content of the query string in a friendly format
    #posts = Post.query.order_by(Post.timestamp.desc()).all()
    posts=Post.query.order_by(Post.timestamp.desc()).paginate(
        page, app.config['POSTS_PER_PAGE'], False)
    next_url=url_for('explore', page=posts.next_num) \
        if posts.has_next else None
    prev_url=url_for('explore', posts=posts.prev_num) \
        if posts.has_prev else None
    #return render_template('index.html', title='Explore', posts=posts)
    return render_template('index.html', title='Explore', posts=posts.items,
                           next_url=next_url, prev_url=prev_url)
'''
The render_template() call references index.html. Here, simply I reuse the index template.
However, in the explore page, we don't want a form to write blog posts, so in this view fxn, 
we didn't include the 'form' argument in render_template. 
We can pass any keyword argum. to url_for() if the name of the argum is not referenced in 
the URL directly.
'''

#password reset request form

@app.route('/reset_password_request', methods=['GET', 'POST'])
def reset_password_request():
    if current_user.is_authenticated:
        return redirect(url_for('index'))
    form=ResetPasswordRequestForm()
    if form.validate_on_submit():
        user=User.query.filter_by(email=form.email.data).first()
        if user:
            send_password_reset_email(user)
        flash('Check your mail to reset your password')
        return redirect(url_for('login'))
    return render_template('reset_password_request.html', title='Reset Password', form=form)
#the flashed message is displayed even when the email supplied by the user is unknown:
#This is so that user cannot use this form to figure out if a given user is a member or not

@app.route('/reset_password/<token>', methods=['GET', 'POST'])
def reset_password(token):
    if current_user.is_authenticated:
        return redirect(url_for('index'))
    user = User.verify_reset_password_token(token)
    if not user:
        return redirect(url_for('index'))
    form = ResetPasswordForm()
    if form.validate_on_submit():
        user.set_password(form.password.data)
        db.session.commit()
        flash('Your password has been reset.')
        return redirect(url_for('login'))
    return render_template('reset_password.html', form=form)
