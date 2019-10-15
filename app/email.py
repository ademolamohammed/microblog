from flask_mail import Message
from app import app, mail
from flask import render_template
from threading import Thread

def send_async_email(app, msg):
    with app.app_context():
        mail.send(msg)

'''
APPLICATION CONTEXTS:
#we send application instance alongside the msg object:
EXPLANATION: Flask uses app. context to avoind having to pass 
arguments across functions. There are 2 types of contexts:
a)applic. context and 2) request context
Flask framework normally manages these 2 automatically; but 
there may be a need to do so manually when we start creating
custom threads.

Many Flask extensions require an applic. context in order to work -
bcos that allows them them to find the Flask applic. instance without
it being passed as an argument.
The extensns need to know the applic. instance bcos they have their 
configuratn stored in the app.config object.
### mail.send() needs to access config values for the email server - so
it needs to know what d application is
### we created the applicatn context by doing 'with app.app_context()'.
This makes the applic. instance accessible via the 'current_app' variable
from Flask 
'''
'''
send_async_email() was invoked via the Thread class in the last line 
of send_email() and it runs in a background thread. In this way, the 
app will not slow down in the process of sending email. 
'''

def send_email(subject, sender, recipients, text_body, html_body):
    msg=Message(subject, sender=sender, recipients=recipients)
    msg.body=text_body
    msg.html=html_body
    mail.send(msg)
    Thread(target=send_async_email, args=(app, msg)).start()

def send_password_reset_email(user):
    token = user.get_reset_password_token()
    send_email('[Microblog] Reset Your Password',
               sender=app.config['ADMINS'][0],
               recipients=[user.email],
               text_body=render_template('email/reset_password.txt',
                                         user=user, token=token),
               html_body=render_template('email/reset_password.html',
                                         user=user, token=token))

'''
INTERESTING!!! The text and html contents of the email is generated from the 
template using render_template() function. The template uses 'user' and 'token' 
arguments for generating personalised email
'''


