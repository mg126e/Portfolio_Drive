import cs304dbi as dbi

def get_input_from_tag(conn, sid, tag):
    '''Returns all the file objects that matches the given tag name'''
    with dbi.dict_cursor(conn) as curs:
        curs.execute('''
            select input.title, input.input_id, input.course_id, input.updated_at
            from input_to_tag
                inner join input using (input_id)
                inner join tag using (tag_id)
            where input.sid = %s and tag.sid = %s and tag.name = %s
            order by input.updated_at desc''',
            [sid, sid, tag])
        return curs.fetchall()

def get_input_from_title(conn, sid, title):
    '''Returns all the file objects that matches the given title'''
    with dbi.dict_cursor(conn) as curs:
        curs.execute('''
            select input.input_id, input.title, input.course_id, input.updated_at
            from input
            where sid = %s and title like %s
            order by updated_at desc''',
            [sid, '%' + title + '%'])
        return curs.fetchall()
    
def get_this_user_tag(conn, sid):
    '''Returns all the tags(id, name, descriptions) given a user'''
    with dbi.dict_cursor(conn) as curs:
        curs.execute('''
            select tag_id, name, description
            from tag
            where sid = %s''',
            [sid])
        return curs.fetchall()
        