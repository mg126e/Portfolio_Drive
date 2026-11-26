'''helper functions for editing profiles '''
import cs304dbi as dbi

def get_profile(conn, sid):
    '''Gets a student majors and institution.'''
    with dbi.dict_cursor(conn) as curs:
        curs.execute('''
            SELECT major1, major2, institution
            FROM student WHERE sid = %s''',
            [sid])
        return curs.fetchone()

def update_profile(conn, sid, major1, major2, institution):
    '''Updates a student majors and institution.'''
    with dbi.cursor(conn) as curs:
        curs.execute('''
            UPDATE student
            SET major1 = %s, major2 = %s, institution = %s
            WHERE sid = %s''',
            [major1, major2, institution, sid])