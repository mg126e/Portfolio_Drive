from flask import (Flask, render_template, make_response, url_for, request,
                   redirect, flash, session, send_from_directory, jsonify)
from werkzeug.utils import secure_filename
app = Flask(__name__)

import secrets
import cs304dbi as dbi
print(dbi.conf('projectdrive_db'))
import login_register_helpers as lrh
import search as sch

# we need a secret_key to use flash() and sessions
app.secret_key = secrets.token_hex()


# This gets us better error messages for certain common request errors
app.config['TRAP_BAD_REQUEST_ERRORS'] = True

@app.route('/')
def home():
    return render_template('main.html', page_title='Main Page')

@app.route('/about/')
def about():
    return render_template('about.html', page_title='About Page')

"""
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


@app.route('/register/', methods=['POST'])
def register():
    if request.method == 'POST':
        # Process the registration form
        pass
    return render_template('register.html')
"""
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
                results = sch.get_tag(conn, query, sid)
            #search for the title
            elif query_type == 'title':
                results = sch.get_title(conn, query, sid)
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

@app.route('/display_tag/')
def display_tag():
    """Display a user's existing tags, optionally update a tag's name or description"""
    #get current user
    sid = session.get('sid')
    if sid is None:
        flash('Please log in to display tags.')
        return redirect(url_for('home'))


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
