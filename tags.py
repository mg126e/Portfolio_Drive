import cs304dbi as dbi

def get_tag(conn, tag, sid):
    '''Returns all the file objects that matches the given tag name'''
    with dbi.dict_cursor(conn) as curs:
        curs.execute('''
            select input.title, input.input_id, input.course_id, tag.tag_id
            from input_to_tag
                inner join input using (input_id)
                inner join tag using (tag_id)
            where sid = sid and tag.name like %s''',
            ['%' + tag + '%', ])
        return curs.fetchall