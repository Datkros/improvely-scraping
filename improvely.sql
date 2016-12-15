-- phpMyAdmin SQL Dump
-- version 4.5.1
-- http://www.phpmyadmin.net
--
-- Servidor: 127.0.0.1
-- Tiempo de generación: 15-12-2016 a las 00:54:56
-- Versión del servidor: 10.1.10-MariaDB
-- Versión de PHP: 7.0.2

SET SQL_MODE = "NO_AUTO_VALUE_ON_ZERO";
SET time_zone = "+00:00";


/*!40101 SET @OLD_CHARACTER_SET_CLIENT=@@CHARACTER_SET_CLIENT */;
/*!40101 SET @OLD_CHARACTER_SET_RESULTS=@@CHARACTER_SET_RESULTS */;
/*!40101 SET @OLD_COLLATION_CONNECTION=@@COLLATION_CONNECTION */;
/*!40101 SET NAMES utf8mb4 */;

--
-- Base de datos: `improvely`
--

-- --------------------------------------------------------

--
-- Estructura de tabla para la tabla `activity_timeline`
--

CREATE TABLE `activity_timeline` (
  `id` int(11) NOT NULL,
  `user_id` varchar(40) NOT NULL,
  `activity_id` int(11) NOT NULL,
  `timestamp` datetime NOT NULL,
  `activity_type_id` int(11) NOT NULL
) ENGINE=InnoDB DEFAULT CHARSET=latin1;

-- --------------------------------------------------------

--
-- Estructura de tabla para la tabla `activity_type`
--

CREATE TABLE `activity_type` (
  `id` int(11) NOT NULL,
  `name` varchar(10) NOT NULL
) ENGINE=InnoDB DEFAULT CHARSET=latin1;

--
-- Volcado de datos para la tabla `activity_type`
--

INSERT INTO `activity_type` (`id`, `name`) VALUES
(1, 'Conversion'),
(2, 'Ad Click');

-- --------------------------------------------------------

--
-- Estructura de tabla para la tabla `ad_click`
--

CREATE TABLE `ad_click` (
  `id` int(11) NOT NULL,
  `url_clicked` varchar(200) NOT NULL,
  `location` varchar(30) NOT NULL,
  `referrer` varchar(200) NOT NULL,
  `tracking_link` varchar(200) NOT NULL,
  `ad` varchar(200) NOT NULL,
  `location_ip` varchar(20) NOT NULL
) ENGINE=InnoDB DEFAULT CHARSET=latin1;

-- --------------------------------------------------------

--
-- Estructura de tabla para la tabla `conversion`
--

CREATE TABLE `conversion` (
  `id` int(11) NOT NULL,
  `revenue` int(12) NOT NULL,
  `conversion_url` varchar(200) NOT NULL,
  `source` varchar(200) NOT NULL,
  `reference` int(20) DEFAULT NULL
) ENGINE=InnoDB DEFAULT CHARSET=latin1;

-- --------------------------------------------------------

--
-- Estructura de tabla para la tabla `person_details`
--

CREATE TABLE `person_details` (
  `id` int(11) NOT NULL,
  `conversions` int(10) NOT NULL,
  `visits` int(10) NOT NULL,
  `lifetime_value` float NOT NULL,
  `user_id` varchar(40) NOT NULL,
  `time_conversions` int(5) NOT NULL,
  `last_seen` datetime NOT NULL
) ENGINE=InnoDB DEFAULT CHARSET=latin1;

--
-- Índices para tablas volcadas
--

--
-- Indices de la tabla `activity_timeline`
--
ALTER TABLE `activity_timeline`
  ADD PRIMARY KEY (`id`);

--
-- Indices de la tabla `activity_type`
--
ALTER TABLE `activity_type`
  ADD PRIMARY KEY (`id`);

--
-- Indices de la tabla `ad_click`
--
ALTER TABLE `ad_click`
  ADD PRIMARY KEY (`id`);

--
-- Indices de la tabla `conversion`
--
ALTER TABLE `conversion`
  ADD PRIMARY KEY (`id`);

--
-- Indices de la tabla `person_details`
--
ALTER TABLE `person_details`
  ADD PRIMARY KEY (`id`),
  ADD UNIQUE KEY `user_id` (`user_id`);

--
-- AUTO_INCREMENT de las tablas volcadas
--

--
-- AUTO_INCREMENT de la tabla `activity_timeline`
--
ALTER TABLE `activity_timeline`
  MODIFY `id` int(11) NOT NULL AUTO_INCREMENT, AUTO_INCREMENT=9714;
--
-- AUTO_INCREMENT de la tabla `activity_type`
--
ALTER TABLE `activity_type`
  MODIFY `id` int(11) NOT NULL AUTO_INCREMENT, AUTO_INCREMENT=3;
--
-- AUTO_INCREMENT de la tabla `ad_click`
--
ALTER TABLE `ad_click`
  MODIFY `id` int(11) NOT NULL AUTO_INCREMENT, AUTO_INCREMENT=5641;
--
-- AUTO_INCREMENT de la tabla `conversion`
--
ALTER TABLE `conversion`
  MODIFY `id` int(11) NOT NULL AUTO_INCREMENT, AUTO_INCREMENT=4074;
--
-- AUTO_INCREMENT de la tabla `person_details`
--
ALTER TABLE `person_details`
  MODIFY `id` int(11) NOT NULL AUTO_INCREMENT, AUTO_INCREMENT=4223;
/*!40101 SET CHARACTER_SET_CLIENT=@OLD_CHARACTER_SET_CLIENT */;
/*!40101 SET CHARACTER_SET_RESULTS=@OLD_CHARACTER_SET_RESULTS */;
/*!40101 SET COLLATION_CONNECTION=@OLD_COLLATION_CONNECTION */;
