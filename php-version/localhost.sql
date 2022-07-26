-- phpMyAdmin SQL Dump
-- version 4.8.5
-- https://www.phpmyadmin.net/
--
-- Värd: localhost
-- Tid vid skapande: 27 jan 2022 kl 12:13
-- Serverversion: 5.5.68-MariaDB
-- PHP-version: 7.1.33

SET SQL_MODE = "NO_AUTO_VALUE_ON_ZERO";
SET AUTOCOMMIT = 0;
START TRANSACTION;
SET time_zone = "+00:00";


/*!40101 SET @OLD_CHARACTER_SET_CLIENT=@@CHARACTER_SET_CLIENT */;
/*!40101 SET @OLD_CHARACTER_SET_RESULTS=@@CHARACTER_SET_RESULTS */;
/*!40101 SET @OLD_COLLATION_CONNECTION=@@COLLATION_CONNECTION */;
/*!40101 SET NAMES utf8mb4 */;

--
-- Database: `sqlpixels`
--
CREATE DATABASE IF NOT EXISTS `sqlpixels` DEFAULT CHARACTER SET utf8 COLLATE utf8_unicode_ci;
USE `sqlpixels`;

CREATE TABLE `counters` (
  `counter_name` varchar(255) CHARACTER SET latin1 COLLATE latin1_general_ci NOT NULL,
  `counter_value` int NOT NULL
) ENGINE=InnoDB DEFAULT CHARSET=latin1 COLLATE=latin1_general_ci;
INSERT INTO `counters` (`counter_name`, `counter_value`) VALUES
('example', 0);


