-- [Init main]
SET SQL_MODE = "NO_AUTO_VALUE_ON_ZERO";
START TRANSACTION;
SET time_zone = "+00:00";

-- [ Create main db ]
-- Create the database titled "EEEEEEEEEE" if it does not exist
CREATE DATABASE IF NOT EXISTS EEEEEEEEEE;
-- Use the database titled "EEEEEEEEEE"
USE EEEEEEEEEE;

-- [Create primary user]
-- Create the user "AAAAAAAAAA" with the password "BBBBBBBBBB" if it does not exist, restricted to localhost
CREATE USER IF NOT EXISTS AAAAAAAAAA@'localhost' IDENTIFIED BY 'BBBBBBBBBB';
-- Grant the user "AAAAAAAAAA" all privileges on the database "EEEEEEEEEE", restricted to localhost
GRANT ALL PRIVILEGES ON EEEEEEEEEE.* TO AAAAAAAAAA@'localhost';

-- [Set preferences]
-- Enable large packets for database
SET GLOBAL max_allowed_packet=268435456;
-- Enable local data loading
SET GLOBAL local_infile = 1;

-- [Create tables]
DROP TABLE IF EXISTS `bruh`;
CREATE TABLE IF NOT EXISTS `bruh` (
  `id` int NOT NULL AUTO_INCREMENT,
  `power_level` int NOT NULL,
  PRIMARY KEY (`id`)
) ENGINE=InnoDB DEFAULT CHARSET=latin1;