CREATE DATABASE IF NOT EXISTS studentdb;
USE studentdb;

CREATE TABLE IF NOT EXISTS students (
    id INT PRIMARY KEY AUTO_INCREMENT,
    student_id VARCHAR(10),
    fullname VARCHAR(100),
    dob DATE,
    major VARCHAR(50)
);

INSERT INTO students (student_id, fullname, dob, major) VALUES
    ('52200139', 'Chau Thi Tram', '2004-07-25', 'Computer Science'),
    ('52200809', 'Dinh Thi Nguyet', '2004-08-25', 'Computer Science'),
    ('52200810', 'Nguyen Thanh Ha', '2004-08-01', 'Software Engineer');
