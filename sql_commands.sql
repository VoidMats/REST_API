
CREATE TABLE tbl_temperature (
    id INTEGER PRIMARY KEY AUTOINCREMENT, 
    int_sensor INT NOT NULL,
    real_value REAL NOT NULL,
    str_date CHAR(30),
    str_comment CHAR(50)
);

CREATE TABLE tbl_sensor (
    id INTEGER PRIMARY KEY AUTOINCREMENT, 
    str_name CHAR(50),
    str_folder CHAR(50),
    str_postition CHAR(50),
    str_unit CHAR(1),
    str_date_created CHAR(30),
    str_comment CHAR(50)
);

INSERT INTO tbl_temperature (int_sensor, real_value, str_date, str_comment) 
VALUES 
    (1, 12.23, '2020-07-01 12:01:01', 'CORRECT VALUE'),
    (1, 13.23, '2020-07-01 23:01:00', 'NO ERROR'),
    (1, 11.13, '2020-07-02 12:00:00 ', 'FAULTY VALUE'),
    (1, 14.73, '2020-07-02 23:00:00', 'SPRING TIMe'),
    (1, 9.23, '2020-07-03 12:00:00', 'CORRECT VALUE');