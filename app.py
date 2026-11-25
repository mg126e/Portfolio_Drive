from flask import (Flask, render_template, make_response, url_for, request,
                   redirect, flash, session, send_from_directory, jsonify)
from werkzeug.utils import secure_filename
app = Flask(__name__)

import secrets
import cs304dbi as dbi
print(dbi.conf('projectdrive_db'))
import login_register_helpers as lrh # handles login and register logic
import search as sch

# we need a secret_key to use flash() and sessions
app.secret_key = secrets.token_hex()


# This gets us better error messages for certain common request errors
app.config['TRAP_BAD_REQUEST_ERRORS'] = True

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
                    return render_template('main.html', page_title='Main', username=session['username'], info=row)
    else:
        return render_template('login.html', page_title='Login')

@app.route('/logout/')
def logout():
    """Logs out the user and clears the session. Directing to home redirects to login page"""
    session.clear()
    return redirect(url_for('home'))

@app.route('/home/editProfile/', methods=['POST', 'GET'])
def editProfile():
    if 'username' not in session:
            flash('Please login to edit your profile.')
            return redirect(url_for('logout'))
    if request.method == 'GET':
        sql = '''SELECT major1, major2, institution FROM student WHERE sid = %s'''
        sid = session.get('sid')
        with dbi.connect() as conn:
            with dbi.dict_cursor(conn) as curs:
                curs.execute(sql, [sid])
                row = curs.fetchone()
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
                    return render_template('editProfile.html', page_title='Edit Profile', info=row, major1=major1, major2=major2)
        return render_template('editProfile.html', page_title='Edit Profile')
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
            with dbi.cursor(conn) as curs:
                sql = '''UPDATE student SET major1 = %s, major2 = %s, institution = %s WHERE sid = %s'''
                curs.execute(sql, [major1, major2, institution, sid])
                conn.commit()
                flash('Profile updated successfully.')
                return redirect(url_for('home'))

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
            if lrh.login_helper(request.form.get('email'), request.form.get('password'), dbi):
                return redirect(url_for('home'))
            else:
                return redirect(url_for('login'))
        else:
            flash('enter all fields', 'error')
            return redirect(url_for('login'))

@app.route('/register/', methods=['POST', 'GET'])
def register():
    """Displays the registration page and handles registration requests. Each user must have a unique email
    but may have the same username as others. Email must be a college/university email address."""
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


if __name__ == '__main__':
    import sys, os
    if len(sys.argv) > 1:
        port = int(sys.argv[1])
        assert(port>1024)
    else:
        port = os.getuid()
    app.debug = True
    app.run('0.0.0.0',port)
