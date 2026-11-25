-- This SQL file inserts sample data into our shared database
-- to test user login, tag search, title search, and other features.

insert into student (sid, username, email, institution, graduation_year,
    major1, major2, password_hash)
values
    (1, 'hannah', 'sz108@wellesley.edu', 'Wellesley', 2028,
     'Computer Science', 'Mathematics',
     '$argon2id$v=19$m=65536,t=3,p=4$fW/tnXOOcY4xZuw9R8iZ8w$DjZ5FZRwYfQ'),
    (2, 'alex', 'alex@example.com', 'Wellesley', 2026,
     'History', NULL,
     '$argon2id$v=19$m=65536,t=3,p=4$fW/tnXOOcY4xZuw9R8iZ8w$DjZ5FZRwYfQ'),
    (3, 'professor_lee', 'morgan@example.com', 'Wellesley', NULL,
     NULL, NULL,
     '$argon2id$v=19$m=65536,t=3,p=4$fW/tnXOOcY4xZuw9R8iZ8w$DjZ5FZRwYfQ'),
    (5, 'marin', 'mg126@example.com', 'Wellesley', 2027,
     'Computer Science', NULL,
     '$argon2id$v=19$m=65536,t=3,p=4$fW/tnXOOcY4xZuw9R8iZ8w$DjZ5FZRwYfQ'),
    (6, 'angela', 'an130@wellesley.edu', 'Wellesley', 2029,
     'Computer Science', 'Biochemistry',
     '$argon2id$v=19$m=65536,t=3,p=4$fW/tnXOOcY4xZuw9R8iZ8w$DjZ5FZRwYfQ'),
    (100, 'tester', 'ww100@wellesley.edu', 'Wellesley', 2028,
     'Computer Science', 'Mathematics',
     '$argon2id$v=19$m=65536,t=3,p=4$QQtAuXroM4OC4s/quJJQaw$n2m+OtHrbnOldC1q+2Dhl5uwy0PlSne9HZ69Xof1xxA');

insert into course (course_id, course_code, course_name, institution)
values
    (1, 'CS304', 'Databases with Web Interfaces', 'Wellesley'),
    (101, '6.1', 'Intro to CS', 'MIT');

insert into course_membership
    (membership_id, sid, course_id, role, term, date_taken)
values
    (1, 1, 1, 'student', 'Fall 2026', '2026-09-01'),
    (2, 2, 1, 'student', 'Fall 2026', '2026-09-01'),
    (3, 3, 1, 'professor', 'Fall 2026', NULL),
    (100, 100, 1, 'student', 'Fall 2026', '2026-09-01'),
    (101, 100, 101, 'student', 'Fall 2026', '2026-09-01');

insert into input
    (input_id, sid, course_id, title, document, permission,
     created_at, updated_at)
values
    (1, 1, 1, 'Database Design',
     'Designed tables for PortfolioDrive.', 'public',
     CURRENT_TIMESTAMP, CURRENT_TIMESTAMP),
    (2, 1, NULL, 'Internship Notes',
     'Examples of skills for applications.', 'private',
     CURRENT_TIMESTAMP, CURRENT_TIMESTAMP),
    (100, 100, 101, 'Neural Network Design',
     'Notes on neural networks and activation functions.', 'public',
     CURRENT_TIMESTAMP, CURRENT_TIMESTAMP),
    (101, 100, NULL, 'Internship Preparation',
     'Resume, interview questions, and application materials.', 'private',
     CURRENT_TIMESTAMP, CURRENT_TIMESTAMP),
    (102, 100, NULL, 'Personal Website Design',
     'Ideas for designing a personal portfolio website.', 'public',
     CURRENT_TIMESTAMP, CURRENT_TIMESTAMP);

insert into file_attachment
    (file_id, input_id, original_filename, storage_key,
     content_type, file_size, time_uploaded)
values
    (1, 1, 'database-design.pdf', 'demo/hannah/database-design.pdf',
     'application/pdf', 48000, CURRENT_TIMESTAMP);

insert into auth_users (sid, input_id)
values
    (2, 2);

insert into tag (tag_id, sid, name, description)
values
    (1, 1, 'CS304', 'Database coursework.'),
    (2, 1, 'applications', 'Internship application materials.'),
    (100, 100, 'AI', 'Artificial intelligence.'),
    (102, 100, 'Design', 'Design-related projects.'),
    (103, 100, 'Projects', 'Personal and academic projects.'),
    (104, 100, 'Career', 'Internship and career preparation.'),
    (105, 100, 'Unused', 'A tag without any associated inputs.');

insert into input_to_tag (input_id, tag_id)
values
    (1, 1),
    (2, 2),
    (100, 100),
    (100, 102),
    (100, 103),
    (101, 104),
    (102, 102),
    (102, 103);