from flask import (Flask, render_template, make_response, url_for, request,
                   redirect, flash, session, send_from_directory, jsonify)
from werkzeug.utils import secure_filename
app = Flask(__name__)

import secrets
import cs304dbi as dbi
dbi.conf('projectdrive_db')

# we need a secret_key to use flash() and sessions
app.secret_key = secrets.token_hex()


# This gets us better error messages for certain common request errors
app.config['TRAP_BAD_REQUEST_ERRORS'] = True

@app.route('/')
def home():
    return render_template('main.html', page_title='Main Page')


@app.route('/login/', methods=['POST', 'GET'])
def login():
    if request.method == 'GET':
        return render_template('login.html')
    else:
        if request.form.get('username') != '' and request.form.get('password') != '':
            sql = 'select sid, username from student where username = %s and password_hash = %s;'
            with dbi.dict_cursor(dbi.connect()) as curs:
                curs.execute(sql, [request.form.get('username'), request.form.get('password_hash')])
                user = curs.fetchone()
            if user is not None:
                session['uid'] = user['uid']
                flash('You were successfully logged in', 'success')
                return redirect(url_for('home'))
            else:
                flash('Invalid username or password', 'error')
                return redirect(url_for('login'))
        else:
            flash('enter username and password', 'error')
            return redirect(url_for('login'))

@app.route('/register/', methods=['POST'])
def register():
    if request.method == 'POST':
        # Process the registration form
        pass
    return render_template('register.html')

if __name__ == '__main__':
    import sys, os
    if len(sys.argv) > 1:
        port = int(sys.argv[1])
        assert(port>1024)
    else:
        port = os.getuid()
    app.debug = True
    app.run('0.0.0.0',port)
