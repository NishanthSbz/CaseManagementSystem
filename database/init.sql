-- Initialize the database with proper settings
CREATE DATABASE IF NOT EXISTS case_management CHARACTER SET utf8mb4 COLLATE utf8mb4_unicode_ci;

-- Create application user
CREATE USER IF NOT EXISTS 'app_user'@'%' IDENTIFIED BY 'app_password';
GRANT ALL PRIVILEGES ON case_management.* TO 'app_user'@'%';

-- Use the database
USE case_management;

-- Ensure proper timezone and character set
SET time_zone = '+00:00';
SET character_set_client = utf8mb4;
SET character_set_connection = utf8mb4;
SET character_set_results = utf8mb4;

FLUSH PRIVILEGES;