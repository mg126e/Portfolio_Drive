SELECT email, COUNT(*)
FROM student
GROUP BY email
HAVING COUNT(*) > 1;

SELECT sid, name, COUNT(*)
FROM tag
GROUP BY sid, name
HAVING COUNT(*) > 1;

SELECT institution, course_code, COUNT(*)
FROM course
GROUP BY institution, course_code
HAVING COUNT(*) > 1;