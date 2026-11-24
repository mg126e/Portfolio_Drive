''' This implements item creation and searching '''

from flask import (Flask, render_template, make_response, url_for, request,
                   redirect, flash, session, send_from_directory, jsonify)
from werkzeug.utils import secure_filename
app = Flask(__name__)

import sys, os
import secrets
import cs304dbi as dbi
dbi.conf('projectdrive_db')
import login_register_helpers as lrh

# we need a secret_key to use flash() and sessions
app.secret_key = secrets.token_hex()


# This gets us better error messages for certain common request errors
app.config['TRAP_BAD_REQUEST_ERRORS'] = True

app.config['UPLOADS'] = 'uploads'
app.config['MAX_CONTENT_LENGTH'] = 16 * 1024 * 1024  # 16 MB limit

@app.route('/')
def home():
    return render_template('main.html', page_title='Main Page')


@app.route('/login/', methods=['POST', 'GET'])
def login():
    if request.method == 'GET':
        return render_template('login.html')
    else:
        if request.form.get('email') != '' and request.form.get('password') != '':
            lrh.login_helper(request.form.get('email'), request.form.get('password'), dbi)
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

def file_upload():
    if request.method == 'GET':
        # we explicitly clear the IMG src and the nm value
        return render_template('inputform.html', src='', nm='')
    else:
        try:
            nm = int(request.form['nm'])
            f = request.files['pic']
            user_filename = f.filename
            ext = user_filename.split('.')[-1]
            filename = secure_filename(f'{nm}.{ext}')
            pathname = os.path.join(app.config[UPLOADS'], filename)
            f.save(pathname)
            with dbi.connect as conn:
                with dbi.dict_cursor(conn) as curs:
                    curs.execute([nm,filename,filename])
                    conn.commit()
            flash('Successfully created item')
