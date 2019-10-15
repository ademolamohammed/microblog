from flask import Flask
from config import Config
from flask_sqlalchemy import SQLAlchemy
from flask_migrate import Migrate
from flask_login import LoginManager
import logging
from logging.handlers import  SMTPHandler, RotatingFileHandler
import os
from flask_mail import Mail
from flask_bootstrap import Bootstrap


app = Flask(__name__)
app.config.from_object(Config)
db = SQLAlchemy(app)
migrate = Migrate(app,db)
login=LoginManager(app)  #this is for your flaslogin
login.login_view = 'login'
mail=Mail(app)
bootstrap=Bootstrap(app)

from app import routes, models, errors

if not app.debug:
    if app.config['MAIL_SERVER']:
        auth=None
        if app.config['MAIL_USERNAME'] or app.config['MAIL_PASSWORD']:
            auth=(app.config['MAIL_USERNAME'], app.config["MAIL_PASSWORD"])
        secure=None
        if app.config['MAIL_USE_TLS']:
            secure=()
        mail_handler=SMTPHandler(
            mailhost=(app.config['MAIL_SERVER'],app.config['MAIL_PORT']),
            fromaddr='no-reply@'+app.config['MAIL_SERVER'],
            toaddrs=app.config['ADMINS'], subject='Microblog Failure',
            credentials=auth, secure=secure)
        mail_handler.setLevel(logging.ERROR)
        app.logger.addHandler(mail_handler)
    if not os.path.exists('logs'):
        os.mkdir('logs')
    file_handler=RotatingFileHandler('logs/microblog.log', maxBytes=10240, backupCount=10)
    file_handler.setFormatter(logging.Formatter('%(asctime)s %(levelname)s: %(message)s [in %(pathname)s:%(lineno)d]'))
    file_handler.setLevel(logging.INFO)
    app.logger.addHandler(file_handler)

    app.logger.setLevel(logging.INFO)
    app.logger.info('Microblog startup')




'''the RotatingFileHandler class used below is cool: it rotates the logs to ensure 
that the log files the log files don't grow too large when the app runs 
for a long time. We keep the last 10 log files as backup and limit the size of the 
log file to 10KB.
The logging.Formatter class provides custom formatting for the log msges.
The format used include timestamp, logging level, message and its source, and line 
number from where the log entry originated.
We also lower the logging level to the INFO categories(DEBUG, INFO, WARNING, ERROR and CRITICAL) 
both in the applicatn logger and the logger handler, in increasing order of severity. 
'''

'''
In the first use of the log file, the server will write a line to the logs each time it 
starts. When the applic runs on a prod. server, these log entries will tell u when the 
server was restarted.
'''




