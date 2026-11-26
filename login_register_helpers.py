from passlib.context import CryptContext
import pymysql
from flask import (Flask, render_template, url_for,
                   redirect, flash, session)

pwd_context = CryptContext(
    schemes=["argon2", "bcrypt"],
    default="argon2",
    deprecated=["bcrypt"],

    bcrypt__rounds=12,
    bcrypt__ident="2b",
    bcrypt__truncate_error=True,

    argon2__memory_cost=65536,
    argon2__time_cost=3,
    argon2__parallelism=4,
)

def hash_password(password):
    return pwd_context.hash(password)

def verify_password(password, stored_hash):
    """
    Returns (ok, new_hash_or_none) The caller is expected
    to update the stored_hash if there's a new_hash
    """
    if not pwd_context.verify(password, stored_hash):
        return False, None
    # Password is okay, but does it need updating?
    if pwd_context.needs_update(stored_hash):
        return True, pwd_context.hash(password)
    # Password is okay and does not need updating
    return True, None

def login_helper(email, passwd, dbi):
    with dbi.connect() as conn:
        with dbi.dict_cursor(conn) as curs:
            curs.execute('''SELECT sid, username, email, password_hash
                            FROM student
                            WHERE email = %s''',
                            [email])
            row = curs.fetchone()
            if row is None:
                # Same response as wrong password,
                # so no information about what went wrong
                flash('login incorrect. Try again or register')
                return False
            stored = row['password_hash']
            username = row['username']
            print('ATTEMPT LOGIN', username)
            okay, new_hash = verify_password(passwd, stored)
            if okay:
                print('they match!')
                flash('successfully logged in as '+username)
                session['username'] = username
                session['sid'] = row['sid']
                session['logged_in'] = True
                session['visits'] = 1
                if new_hash is not None:
                    curs.execute(
                        'update student set password_hash = %s where sid = %s',
                        [new_hash, row['sid']]
                    )
                    conn.commit()
                # all done; go to user's page
                return True
            else:
                flash('login incorrect. Try again or register')
                return False

def register_helper(email, username, password1, password2, dbi):
    hashed = hash_password(password1)
    print('REGISTER', username)
    # should probably be a helper function
    with dbi.connect() as conn:
        with dbi.cursor(conn) as curs:
            sql = '''SELECT sid FROM student WHERE email = %s'''
            curs.execute(sql, [email])
            if curs.fetchone() is not None:
                flash('email already registered, login or use a different email')
                return False
            try:
                curs.execute('''INSERT INTO student(username,email,password_hash, institution)
                                VALUES(%s,%s,%s,%s)''',
                                [username, email, hashed, email.split('@')[1].split('.')[0]])
                conn.commit()
            except pymysql.IntegrityError as err:
                flash(f'try again: {err}')
                return False
            sid = curs.lastrowid
            session['username'] = username
            session['sid'] = sid
            session['logged_in'] = True
            session['visits'] = 1
            return True