--This SQL file inserts a few sample data into our database to show how each table works.

insert into student (sid, username, email, institution, graduation_year,
     major1, major2, password_hash)
values
    (1, 'hannah', 'sz108@wellesley.edu', 'Wellesley', 2028,
     'Computer Science', 'Mathematics', '$argon2id$v=19$m=65536,t=3,p=4$fW/tnXOOcY4xZuw9R8iZ8w$DjZ5FZRwYfQ'),
    (2, 'alex', 'alex@example.com', 'Wellesley', 2026,
     'History', NULL, '$argon2id$v=19$m=65536,t=3,p=4$fW/tnXOOcY4xZuw9R8iZ8w$DjZ5FZRwYfQ'),
    (3, 'professor_lee', 'morgan@example.com', 'Wellesley', NULL,
     NULL, NULL, '$argon2id$v=19$m=65536,t=3,p=4$fW/tnXOOcY4xZuw9R8iZ8w$DjZ5FZRwYfQ'),
    (5, 'marin', 'mg126@example.com', 'Wellesley', 2027,
     'Computer Science', NULL, '$argon2id$v=19$m=65536,t=3,p=4$fW/tnXOOcY4xZuw9R8iZ8w$DjZ5FZRwYfQ'),
    (6, 'angela', 'an130@wellesley.edu', 'Wellesley', 2029,
     'Computer Science', 'Biochemistry', '$argon2id$v=19$m=65536,t=3,p=4$fW/tnXOOcY4xZuw9R8iZ8w$DjZ5FZRwYfQ');

insert into course (course_id, course_code, course_name, institution)
values (1, 'CS304', 'Databases with Web Interfaces', 'Wellesley');

insert into course_membership (membership_id, sid, course_id, role, term, date_taken)
values
    (1, 1, 1, 'student', 'Fall 2026', '2026-09-01'),
    (2, 2, 1, 'student', 'Fall 2026', '2026-09-01'),
    (3, 3, 1, 'professor', 'Fall 2026', NULL);

insert into input
    (input_id, sid, course_id, title, document, permission, created_at, updated_at)
values
    (1, 1, 1, 'Database Design',
     'Designed tables for PortfolioDrive.', 'public',
     CURRENT_TIMESTAMP, CURRENT_TIMESTAMP),
    (2, 1, NULL, 'Internship Notes',
     'Examples of skills for applications.', 'private',
     CURRENT_TIMESTAMP, CURRENT_TIMESTAMP);

insert into file_attachment (file_id, input_id, original_filename, storage_key,
     content_type, file_size, time_uploaded)
values
    (1, 1, 'database-design.pdf', 'demo/hannah/database-design.pdf',
     'application/pdf', 48000, CURRENT_TIMESTAMP);

insert into auth_users (sid, input_id)
values (2, 2);

insert into tag (tag_id, sid, name, description)
values
    (1, 1, 'CS304', 'Database coursework.'),
    (2, 1, 'applications', 'Internship application materials.');

insert into input_to_tag (input_id, tag_id)
values
    (1, 1),
    (2, 2);