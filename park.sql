CREATE DATABASE park_system;
USE park_system;

CREATE TABLE park_records (
    id INT AUTO_INCREMENT PRIMARY KEY,
    timestamp DATETIME,
    status VARCHAR(20),
    video_path VARCHAR(255)
);
CREATE TABLE line_positions (
    id INT AUTO_INCREMENT PRIMARY KEY,
    position_1 INT NOT NULL,
    position_2 INT NOT NULL,
    position_3 INT NOT NULL,
    timestamp TIMESTAMP DEFAULT CURRENT_TIMESTAMP
);




