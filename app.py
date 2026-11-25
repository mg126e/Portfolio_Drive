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

from datetime import date 
@app.route('/upload/', methods=['POST', 'GET'])
def file_upload():
    if request.method == 'GET':
        return render_template('inputform.html')

    # the keys match the name attributes in inputform.html
    course_number = request.form['course_number']
    semester = request.form['semester']
    year = request.form['year']
    name = request.form['name']
    description = request.form.get('description', '') # Get description, default to empty string if not provided
    text_content = request.form.get('text_content', '') # Get text content, default to empty string if not provided
    tags = sorted({t.strip().lower()
                for t in request.form.get('tags', '').split(',') if t.strip()}) # Get tags, default to empty string if not provided, split by commas, strip whitespace, convert to lowercase, and sort
    f = request.files.get('file') 
    has_file = f is not None and f.filename != ''

    if not has_file and not text_content:
        flash('Upload a file or paste some text.', 'error')
        return redirect(url_for('file_upload'))

    original_name = None
    stored_name = None

    if has_file:
        original_name = secure_filename(f.filename)
        # random stored name so that two items with the same file name don't collide
        stored_name = secrets.token_hex(8) + os.path.splitext(f.filename)[1].lower()
        f.save(os.path.join(app.config['UPLOADS'], stored_name))

    conn = dbi.connect()
    curs = dbi.dict_cursor(conn)
    # ADJUST table and column names
    curs.execute('''insert into item(course_number, semester, year, name, description,
                                     text_content, original_filename, stored_filename)
                    values (%s, %s, %s, %s, %s, %s, %s, %s)''',
                 [course_number, semester, int(year), name, description,
                  text_content or None, original_name, stored_name])
    item_id = curs.lastrowid
    for tag in tags:
        curs.execute('insert into item_tag(item_id, tag) values (%s, %s)', [item_id, tag])
    conn.commit()

    flash('Successfully created item')
    return redirect(url_for('file_upload'))  # point this at the item's page once it exists

if __name__ == '__main__':
    import sys, os
    if len(sys.argv) > 1:
        port = int(sys.argv[1])
        assert(port>1024)
    else:
        port = os.getuid()
    app.debug = True
    app.run('0.0.0.0',port)