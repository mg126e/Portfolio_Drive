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
