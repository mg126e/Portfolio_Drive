''' This implements item creation and searching '''

from flask import (Flask, render_template, make_response, url_for, request,
                   redirect, flash, session, send_from_directory, jsonify)
from werkzeug.utils import secure_filename
app = Flask(__name__)

import sys, os
import secrets
import cs304dbi as dbi
print(dbi.conf('projectdrive_db'))
import login_register_helpers as lrh # handles login and register logic
import search as sch # handles search tag and titles
import file_upload as fuh # handles create input and upload files
import edit_profile as eph # handles edit profile

# we need a secret_key to use flash() and sessions
app.secret_key = secrets.token_hex()

# This gets us better error messages for certain common request errors
app.config['TRAP_BAD_REQUEST_ERRORS'] = True

app.config['UPLOADS'] = 'uploads'
app.config['MAX_CONTENT_LENGTH'] = 16 * 1024 * 1024  # 16 MB limit

@app.route('/')
def home():
    '''Displays the home page when user logs in, otherwise displays the login page.'''
    if 'username' in session:
        username = session['username']
        sid = session['sid']
        session['visits'] = 1+int(session.get('visits',0))
        sql = '''SELECT * FROM student WHERE sid = %s'''
        with dbi.connect() as conn:
            with dbi.dict_cursor(conn) as curs:
                curs.execute(sql, [sid])
                row = curs.fetchone()
                if row is None:
                    flash('user not found')
                    return redirect(url_for('logout'))
                else:
                    return render_template('main.html', 
                        page_title='Main', 
                        username=session['username'], 
                        info=row)
    else:
        return render_template('login.html', page_title='Login')

@app.route('/about/')
def about():
    return render_template('about.html', page_title='About Page')

@app.route('/login/', methods=['POST', 'GET'])
def login():
    '''Displays the login page and handles login requests.'''
    if request.method == 'GET':
        return render_template('login.html', page_title='Login')
    else:
        if request.form.get('email') != '' and request.form.get('password') != '':
            if lrh.login_helper(request.form.get('email'), 
            request.form.get('password'), dbi):
                return redirect(url_for('home'))
            else:
                return redirect(url_for('login'))
        else:
            flash('enter all fields', 'error')
            return redirect(url_for('login'))

@app.route('/register/', methods=['POST', 'GET'])
def register():
    """Displays the registration page and handles registration requests. 
    Each user must have a unique email but may have the same username as others. 
    Email must be a college/university email address."""
    if request.method == 'GET':
        return render_template('register.html', page_title='Register')
    else:
        if (request.form.get('email') != ''and request.form.get('password1') != ''
        and request.form.get('password2') != ''):
            if password1 := request.form.get('password1') != request.form.get('password2'):
                flash('passwords do not match', 'error')
                return redirect(url_for('register'))
            else:
                if lrh.register_helper(
                    request.form.get('email'), request.form.get('username'), 
                    request.form.get('password1'), request.form.get('password2'), dbi):
                    return redirect(url_for('home'))
                else:
                    return redirect(url_for('register'))
        else:
            flash('enter all fields', 'error')
            return redirect(url_for('register'))

@app.route('/logout/')
def logout():
    """Logs out the user and clears the session. Directing to home redirects to login page"""
    session.clear()
    return redirect(url_for('home'))

@app.route('/home/editProfile/', methods=['POST', 'GET'])
def editProfile():
    '''Edit the profile info'''
    if 'username' not in session:
        flash('Please login to edit your profile.')
        return redirect(url_for('logout'))
    if request.method == 'GET':
        sid = session.get('sid')
        with dbi.connect() as conn:
            row = eph.get_profile(conn, sid)
            if row is None:
                flash('user not found')
                return redirect(url_for('logout'))
            else:
                major1 = row['major1']
                major2 = row['major2']
                if major1 == None or major1 == "none":
                    major1 = ''
                if major2 is None or major2 == "none":
                    major2 = ''
                return render_template('editProfile.html',
                    page_title='Edit Profile', info=row,
                    major1=major1, major2=major2)
    else:
        sid = session.get('sid')
        if sid is None:
            flash('Please log in to edit your profile.')
            return redirect(url_for('logout'))
        major1 = request.form.get('major1')
        major2 = request.form.get('major2')
        if major1 == '':
            major1 = None
        if major2 == '':
            major2 = None
        institution = request.form.get('institution')
        with dbi.connect() as conn:
            eph.update_profile(conn, sid, major1, major2, institution)
            conn.commit()
            flash('Profile updated successfully.')
            return redirect(url_for('home'))


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
            #for testing: flash(results)
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
    return render_template('viewInput.html', page_title='View Item')

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
    return 'Tag deletion is not implemented in this draft.'


from datetime import date 
@app.route('/upload/', methods=['POST', 'GET'])
def file_upload():
    '''Display the creation form and handle item submissions.'''
    # the item needs an owner, so the user must be logged in
    sid = session.get('sid')
    if sid is None:
        flash('Please log in to create an item')
        return redirect(url_for('home'))

    if request.method == 'GET':
        return render_template('inputform.html', page_title='Create an Item')

    # the keys match the name attributes in inputform.html
    course_number = request.form['course_number']
    semester = request.form['semester']
    year = request.form['year']
    name = request.form['name']
    # Get text content, default to empty string if not provided
    text_content = request.form.get('text_content', '')
    # Get tags, default to empty string if not provided, split by commas, strip whitespace, convert to lowercase, and sort
    tags = sorted({t.strip().lower()
        for t in request.form.get('tags', '').split(',') if t.strip()})
    
    f = request.files.get('file') 
    has_file = f is not None and f.filename != ''
    if not has_file and not text_content:
        flash('Upload a file or paste some text.', 'error')
        return redirect(url_for('file_upload'))

    term = f'{semester} {year}'
    conn = dbi.connect()
    try:
        with dbi.dict_cursor(conn) as curs:
            if has_file:
                original_name, stored_name = fuh.save_file(
                    f, app.config['UPLOADS'])

            # find the course or create a new one
            course_id = fuh.get_or_create_course(
                curs, sid, course_number)

            # record the term
            fuh.add_course_membership(curs, sid, course_id, term)

            #item goes into the input table
            input_id = fuh.create_item(
                curs, sid, course_id, name, text_content)

            # uploaded file gets its own row in file_attachment
            if has_file:
                fuh.add_file_attachment(
                    curs, input_id, original_name, stored_name,
                    f.mimetype, app.config['UPLOADS'])

            # link the tags to the item
            fuh.add_tags(curs, sid, input_id, tags)
            conn.commit()
    except Exception:
        conn.rollback()
        conn.close()
        raise

    conn.close()
    flash('Successfully created item')
    return redirect(url_for('file_upload'))# point this at the item's page once it exists

if __name__ == '__main__':
    import sys, os
    if len(sys.argv) > 1:
        port = int(sys.argv[1])
        assert(port>1024)
    else:
        port = os.getuid()
    app.debug = True
    app.run('0.0.0.0',port)