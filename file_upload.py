"""Helpers for saving uploaded files and creating item records."""

import os
import secrets
from werkzeug.utils import secure_filename
import cs304dbi as dbi

def save_file(uploaded_file, upload_folder):
    '''Save a file and return its original and stored filenames.'''
    original_name = secure_filename(f.filename)
    # random stored name so that two items with the same file name don't collide
    stored_name = secrets.token_hex(8) + os.path.splitext(original_name)[1].lower()
    os.makedirs(upload_folder, exist_ok=True) # create uploads/ if it's missing
    f.save(os.path.join(upload_folder, stored_name))

    return original_name, stored_name

def get_or_create_course(curs, sid, course_number):
    '''Finds the course at the student's institution or creates it.'''
    curs.execute('select institution from student where sid = %s', [sid])
    institution = curs.fetchone()['institution']
    course_code = course_number.strip().upper()

    curs.execute('''select course_id from course
        where institution = %s and course_code = %s''',
        [institution, course_code])
    row = curs.fetchone()

    if row:
        course_id = row['course_id']
    else:
        # the form has no course name field so the code is used as the name
        curs.execute('''insert into course(course_code, course_name, institution)
            values (%s, %s, %s)''',
            [course_code, course_code, institution])
        course_id = curs.lastrowid

    return course_id

def add_course_membership(curs, sid, course_id, term):
    '''Records a student's course and term.'''
    curs.execute('''
        insert into course_membership(sid, course_id, role, term)
        values (%s, %s, 'student', %s)
        on duplicate key update membership_id = membership_id''',
        [sid, course_id, term])
    return

def create_item(curs, sid, course_id, name, text_content):
    '''adds the item to the input table and returns its id.'''
    curs.execute('''
        insert into input(sid, course_id, title, document, created_at, updated_at)
        values (%s, %s, %s, %s, now(), now())''',
        [sid, course_id, name, text_content or None])
    return curs.lastrowid

def add_file_attachment(
    curs, input_id, original_name, stored_name, content_type, upload_folder):
    '''Adds the uploaded file's information to file_attachment.'''

    file_size = os.path.getsize(os.path.join(upload_folder, stored_name))
    curs.execute('''insert into file_attachment(input_id, original_filename, storage_key, content_type, file_size, time_uploaded)
        values (%s, %s, %s, %s, %s, now())''',
        [input_id, original_name[:100], stored_name, content_type, file_size])
    return

def add_tags(curs, sid, input_id, tags):
    '''Finds or creates tags and links them to the item.'''
    for tag in tags:
        curs.execute('select tag_id from tag where sid = %s and name = %s',
            [sid, tag])
        row = curs.fetchone()

        if row:
            tag_id = row['tag_id']
        else:
            curs.execute('insert into tag(sid, name) values (%s, %s)',
                [sid, tag])
            tag_id = curs.lastrowid

        # link the tag to the item through input_to_tag
        curs.execute('insert into input_to_tag(input_id, tag_id) values (%s, %s)',
            [input_id, tag_id])
        return
    