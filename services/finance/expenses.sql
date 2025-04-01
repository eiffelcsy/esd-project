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
  `is_paid` boolean
  PRIMARY KEY (`trip_id`, `user_id`, `date`, `location`, `amount`, `base_currency`)
) ENGINE=InnoDB DEFAULT CHARSET=utf8;

--
-- Dumping data for table `expenses`
--

INSERT INTO `expenses` (`trip_id`, `user_id`, `date`, `location`, `amount`, `base_currency`, `description`, `is_paid`) VALUES

COMMIT;

/*!40101 SET CHARACTER_SET_CLIENT=@OLD_CHARACTER_SET_CLIENT */;
/*!40101 SET CHARACTER_SET_RESULTS=@OLD_CHARACTER_SET_RESULTS */;
/*!40101 SET COLLATION_CONNECTION=@OLD_COLLATION_CONNECTION */;
