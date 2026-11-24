from flask import (Flask, render_template, make_response, url_for, request,
                   redirect, flash, session, send_from_directory, jsonify)
from werkzeug.utils import secure_filename
app = Flask(__name__)

import secrets
import cs304dbi as dbi
dbi.conf('projectdrive_db')
import login_register_helpers as lrh

# we need a secret_key to use flash() and sessions
app.secret_key = secrets.token_hex()


# This gets us better error messages for certain common request errors
app.config['TRAP_BAD_REQUEST_ERRORS'] = True

@app.route('/')
def home():
    if 'username' in session:
        username = session['username']
        sid = session['sid']
        session['visits'] = 1+int(session.get('visits',0))
        return render_template('main.html', page_title='Main', username=session['username'])
    else:
        return render_template('login.html', page_title='Login')

@app.route('/logout/')
def logout():
    session.clear()
    return redirect(url_for('home'))


@app.route('/login/', methods=['POST', 'GET'])
def login():
    if request.method == 'GET':
        return render_template('login.html')
    else:
        if request.form.get('email') != '' and request.form.get('password') != '':
            if lrh.login_helper(request.form.get('email'), request.form.get('password'), dbi):
                return redirect(url_for('home'))
            else:
                return redirect(url_for('login'))
        else:
            flash('enter all fields', 'error')
            return redirect(url_for('login'))

@app.route('/register/', methods=['POST', 'GET'])
def register():
    if request.method == 'GET':
        return render_template('register.html')
    else:
        if request.form.get('email') != '' and request.form.get('password1') != '' and request.form.get('password2') != '':
            if password1 := request.form.get('password1') != request.form.get('password2'):
                flash('passwords do not match', 'error')
                return redirect(url_for('register'))
            else:
                if lrh.register_helper(request.form.get('email'), request.form.get('username'), request.form.get('password1'), request.form.get('password2'), dbi):
                    return redirect(url_for('home'))
                else:
                    return redirect(url_for('register'))
        else:
            flash('enter all fields', 'error')
            return redirect(url_for('register'))

if __name__ == '__main__':
    import sys, os
    if len(sys.argv) > 1:
        port = int(sys.argv[1])
        assert(port>1024)
    else:
        port = os.getuid()
    app.debug = True
    app.run('0.0.0.0',port)
