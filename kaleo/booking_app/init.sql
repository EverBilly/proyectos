CREATE DATABASE IF NOT EXISTS booking_db;
CREATE USER IF NOT EXISTS 'booking_user'@'%' IDENTIFIED BY 'booking_pass';
GRANT ALL PRIVILEGES ON booking_db.* TO 'booking_user'@'%';
FLUSH PRIVILEGES;