--This SQL files creates tables for out shared group database.

-- Drop existing tables
drop table if exists input_to_tag;
drop table if exists auth_users;
drop table if exists file_attachment;
drop table if exists tag;
drop table if exists input;
drop table if exists course_membership;
drop table if exists course;
drop table if exists student;

-- Create tables
create table student (
    sid int auto_increment primary key,
    name varchar(100) not null,
    username varchar(50) not null,
    email varchar(100) not null,
    institution varchar(100) not null,
    graduation_year int,
    major1 varchar(50), 
    major2 varchar(50),
    password_hash varchar(200) not null
) engine=InnoDB;

create table course (
    course_id int auto_increment primary key,
    course_code varchar(30) not null,
    course_name varchar(30) not null,
    institution varchar(30) not null,
    -- unique institute and course name pair
    unique(institution, course_name) 
) engine=InnoDB;

create table course_membership (
    membership_id int auto_increment primary key,
    sid int not null,
    course_id int not null,
    role enum('student', 'professor', 'staff') not null,
    term varchar(30) not null,
    date_taken date,

    unique (sid, course_id, term),
    foreign key (sid) references student(sid),
    foreign key (course_id) references course(course_id)
) engine=InnoDB;

create table input (
    input_id int auto_increment primary key,
    sid int not null,
    course_id int,
    title varchar(200) not null,
    document text,
    permission enum('private', 'public') not null default 'private',
    created_at timestamp not null,
    updated_at timestamp not null,

    foreign key (sid) references student(sid),
    foreign key (course_id) references course(course_id)
) engine=InnoDB;

create table file_attachment (
    file_id int auto_increment primary key,
    input_id int not null,
    original_filename varchar(100) not null,
    storage_key varchar(100) not null unique,
    content_type varchar(100),
    file_size int,
    time_uploaded timestamp not null,

    foreign key (input_id) references input(input_id)
) engine=InnoDB;

create table auth_users (
    sid int not null,
    input_id int not null,

    primary key (sid, input_id),
    foreign key (sid) references student(sid),
    foreign key (input_id) references input(input_id)
) engine=InnoDB;

create table tag (
    tag_id int auto_increment primary key,
    sid int not null,
    name varchar(50) not null,
    description text,

    foreign key(sid) references student(sid)
) engine=InnoDB;

create table input_to_tag (
    input_id int not null,
    tag_id int not null,

    primary key (tag_id, input_id),
    foreign key (input_id) references input(input_id),
    foreign key (tag_id) references tag(tag_id)
) engine=InnoDB;