from flask import render_template
from app import app, db

@app.errorhandler(404)
def not_found_error(error):
    return render_template('404.html'), 404

@app.errorhandler(500)
def internal_error(error):
    db.session.rollback()
    return render_template('500.html'), 500
'''
- The second value returned is the error status code
- If a username duplicate error occurs in the db, the 
handlers for the 500 errors will be invoked. We simply
ensured that such did not interfere with other db request 
by issuing a session rollback. THIS RESETS THE SESSION TO 
A CLEAN STATE 
'''
