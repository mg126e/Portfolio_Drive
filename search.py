import cs304dbi as dbi

def get_tag(conn, tag, sid):
    '''Returns all the file objects that matches the given tag name'''
    with dbi.dict_cursor(conn) as curs:
        curs.execute('''
            select input.title, input.input_id, input.course_id, input.updated_at,
                tag.tag_id, tag.name
            from input_to_tag
                inner join input using (input_id)
                inner join tag using (tag_id)
            where input.sid = %s and tag.sid = %s and and tag.name = %s''',
            [sid, sid, tag])
        return curs.fetchall()

def get_title(conn, title, sid):
    '''Returns all the file objects that matches the given title'''
    with dbi.dict_cursor(conn) as curs:
        curs.execute('''
            select input.title, input.input_id, input.course_id, input.updated_at,
                tag.tag_id, tag.name
            from input_to_tag
                inner join input using (input_id)
                inner join tag using (tag_id)
            where sid = %s and tag.sid = %s and and input.title = %s''',
            [sid, sid, title])
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
        