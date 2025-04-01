-- phpMyAdmin SQL Dump
-- version 4.7.4
-- https://www.phpmyadmin.net/
--
-- Host: 127.0.0.1:3306
-- Generation Time: Jan 14, 2019 at 06:42 AM
-- Server version: 5.7.19
-- PHP Version: 7.1.9

SET SQL_MODE = "NO_AUTO_VALUE_ON_ZERO";
SET AUTOCOMMIT = 0;
START TRANSACTION;
SET time_zone = "+00:00";


/*!40101 SET @OLD_CHARACTER_SET_CLIENT=@@CHARACTER_SET_CLIENT */;
/*!40101 SET @OLD_CHARACTER_SET_RESULTS=@@CHARACTER_SET_RESULTS */;
/*!40101 SET @OLD_COLLATION_CONNECTION=@@COLLATION_CONNECTION */;
/*!40101 SET NAMES utf8mb4 */;

--
-- Database: `expenses`
--
CREATE DATABASE IF NOT EXISTS `expenses` DEFAULT CHARACTER SET utf8 COLLATE utf8_general_ci;
USE `expenses`;

-- --------------------------------------------------------

--
-- Table structure for table `expenses`
--

DROP TABLE IF EXISTS `expenses`;
CREATE TABLE IF NOT EXISTS `expenses` (
  `trip_id` varchar(64) NOT NULL,
  `user_id` varchar(64) NOT NULL,
  `date` date NOT NULL,
  `location` varchar(64) NOT NULL,
  `amount` decimal(10,2) NOT NULL,
  `base_currency` varchar(3) NOT NULL,
  `description` varchar(64),
  `is_paid` boolean,
  PRIMARY KEY (`trip_id`, `user_id`, `date`, `location`, `amount`, `base_currency`)
) ENGINE=InnoDB DEFAULT CHARSET=utf8;

--
-- Dumping data for table `expenses`
--

INSERT INTO `expenses` (`trip_id`, `user_id`, `date`, `location`, `amount`, `base_currency`, `description`, `is_paid`) VALUES
('TRIP001', 'USER01', '2023-03-15', 'Singapore', 150.00, 'SGD', 'Hotel Accommodation', TRUE),
('TRIP001', 'USER01', '2023-03-16', 'Singapore', 25.50, 'SGD', 'Hawker Meal', TRUE),
('TRIP001', 'USER02', '2023-03-15', 'Singapore', 80.00, 'SGD', 'Taxi Fare', FALSE),
('TRIP001', 'USER03', '2023-03-17', 'Malaysia', 200.00, 'SGD', 'Bus Tickets', TRUE),
('TRIP002', 'USER01', '2023-04-10', 'Japan', 300.00, 'SGD', 'Shinkansen Ticket', TRUE),
('TRIP002', 'USER02', '2023-04-11', 'Tokyo', 45.75, 'SGD', 'Sushi Dinner', TRUE),
('TRIP002', 'USER02', '2023-04-12', 'Osaka', 1200.00, 'SGD', 'Team Activity', FALSE),
('TRIP003', 'USER03', '2023-05-05', 'Bangkok', 180.00, 'SGD', 'Hotel Payment', TRUE),
('TRIP003', 'USER01', '2023-05-06', 'Chiang Mai', 75.25, 'SGD', 'Local Transport', TRUE),
('TRIP003', 'USER02', '2023-05-07', 'Phuket', 550.00, 'SGD', 'Boat Tour', FALSE),
('TRIP004', 'USER04', '2023-06-01', 'Sydney', 420.00, 'SGD', 'Conference Fee', TRUE),
('TRIP004', 'USER04', '2023-06-02', 'Sydney', 35.00, 'SGD', 'Museum Ticket', TRUE),
('TRIP004', 'USER05', '2023-06-03', 'Melbourne', 90.00, 'SGD', 'Team Lunch', FALSE);
COMMIT;

/*!40101 SET CHARACTER_SET_CLIENT=@OLD_CHARACTER_SET_CLIENT */;
/*!40101 SET CHARACTER_SET_RESULTS=@OLD_CHARACTER_SET_RESULTS */;
/*!40101 SET COLLATION_CONNECTION=@OLD_COLLATION_CONNECTION */;
