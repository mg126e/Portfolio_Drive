''' This implements item creation and searching '''

from flask import (Flask, render_template, make_response, url_for, request,
                   redirect, flash, session, send_from_directory, jsonify)
from werkzeug.utils import secure_filename
app = Flask(__name__)

import sys, os
import secrets
import cs304dbi as dbi
print(dbi.conf('projectdrive_db'))
import login_register_helpers as lrh
import search as sch

# we need a secret_key to use flash() and sessions
app.secret_key = secrets.token_hex()


# This gets us better error messages for certain common request errors
app.config['TRAP_BAD_REQUEST_ERRORS'] = True

app.config['UPLOADS'] = 'uploads'
app.config['MAX_CONTENT_LENGTH'] = 16 * 1024 * 1024  # 16 MB limit

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

@app.route('/about/')
def about():
    return render_template('about.html', page_title='About Page')

@app.route('/login/', methods=['POST', 'GET'])
def login():
    if request.method == 'GET':
        return render_template('login.html', page_title='Login')
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
        return render_template('register.html', page_title='Register')
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

@app.route('/query/')
def search():
    """Search for a given tag or title and display all results.
    ***This function ONLY handles search tags and input titles owned by the 
    logged-in user for this phase"""
    #get current user
    sid = session.get('sid')
    if sid is None:
        flash('Please log in to search tags.')
        return redirect(url_for('home'))

    query_type = request.args.get('query_type')
    query = request.args.get('query', '').strip()
    results=[]
    #check the query, if valid, get the tags
    if query and query_type:
        with dbi.connect() as conn:
            #search for the tag
            if query_type == 'tag':
                results = sch.get_input_from_tag(conn, sid, query)
            #search for the title
            else:
                results = sch.get_input_from_title(conn, sid, query)
            flash(results)
    #if not valid, flash messages
    else:
        flash('Enter a valid query or type to search.')

    return render_template(
        'search.html',
        page_title='Search by Tag',
        query=query,
        query_type=query_type,
        results=results
    )

@app.route('/view_input/')
def view_input():
    """Display a specified user input"""
    return "This page not implememted but supposed to display an user input."

@app.route('/view_tag/')
def view_tag():
    """Display a user's existing tags, optionally update a tag's name or description"""
    #get current user
    sid = session.get('sid')
    if sid is None:
        flash('Please log in to display tags.')
        return redirect(url_for('home'))

    return "This page not implememted but supposed to display a tag."

@app.route('/delete_tag/')
def delete_tag():
    """Delete a tag and removes its links to all of a user's inputs."""
    #get current user
    sid = session.get('sid')
    if sid is None:
        flash('Please log in to delete tags.')
        return redirect(url_for('home'))


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