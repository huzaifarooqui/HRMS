-- MySQL dump 10.13  Distrib 8.0.46, for Win64 (x86_64)
--
-- Host: localhost    Database: game_db
-- ------------------------------------------------------
-- Server version	8.4.10

/*!40101 SET @OLD_CHARACTER_SET_CLIENT=@@CHARACTER_SET_CLIENT */;
/*!40101 SET @OLD_CHARACTER_SET_RESULTS=@@CHARACTER_SET_RESULTS */;
/*!40101 SET @OLD_COLLATION_CONNECTION=@@COLLATION_CONNECTION */;
/*!50503 SET NAMES utf8 */;
/*!40103 SET @OLD_TIME_ZONE=@@TIME_ZONE */;
/*!40103 SET TIME_ZONE='+00:00' */;
/*!40014 SET @OLD_UNIQUE_CHECKS=@@UNIQUE_CHECKS, UNIQUE_CHECKS=0 */;
/*!40014 SET @OLD_FOREIGN_KEY_CHECKS=@@FOREIGN_KEY_CHECKS, FOREIGN_KEY_CHECKS=0 */;
/*!40101 SET @OLD_SQL_MODE=@@SQL_MODE, SQL_MODE='NO_AUTO_VALUE_ON_ZERO' */;
/*!40111 SET @OLD_SQL_NOTES=@@SQL_NOTES, SQL_NOTES=0 */;

--
-- Table structure for table `admins`
--

DROP TABLE IF EXISTS `admins`;
/*!40101 SET @saved_cs_client     = @@character_set_client */;
/*!50503 SET character_set_client = utf8mb4 */;
CREATE TABLE `admins` (
  `id` int NOT NULL AUTO_INCREMENT,
  `username` varchar(50) NOT NULL,
  `password` varchar(255) NOT NULL,
  `full_name` varchar(100) DEFAULT NULL,
  `must_change_password` tinyint(1) DEFAULT '1',
  `created_at` timestamp NULL DEFAULT CURRENT_TIMESTAMP,
  `last_login` datetime DEFAULT NULL,
  PRIMARY KEY (`id`),
  UNIQUE KEY `username` (`username`)
) ENGINE=InnoDB AUTO_INCREMENT=3 DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_0900_ai_ci;
/*!40101 SET character_set_client = @saved_cs_client */;

--
-- Dumping data for table `admins`
--

LOCK TABLES `admins` WRITE;
/*!40000 ALTER TABLE `admins` DISABLE KEYS */;
INSERT INTO `admins` VALUES (1,'admin','Admin@123','System Administrator',1,'2026-07-13 07:15:01',NULL);
/*!40000 ALTER TABLE `admins` ENABLE KEYS */;
UNLOCK TABLES;

--
-- Table structure for table `attendance`
--

DROP TABLE IF EXISTS `attendance`;
/*!40101 SET @saved_cs_client     = @@character_set_client */;
/*!50503 SET character_set_client = utf8mb4 */;
CREATE TABLE `attendance` (
  `id` int NOT NULL AUTO_INCREMENT,
  `employee_id` int NOT NULL,
  `attendance_date` date NOT NULL,
  `check_in` datetime DEFAULT NULL,
  `check_out` datetime DEFAULT NULL,
  `working_minutes` int DEFAULT '0',
  `late_minutes` int DEFAULT '0',
  `overtime_minutes` int DEFAULT '0',
  `status` enum('Present','Late','Half Day','Absent','Leave','Holiday') DEFAULT 'Present',
  `remarks` varchar(255) DEFAULT NULL,
  `created_at` timestamp NULL DEFAULT CURRENT_TIMESTAMP,
  `updated_at` timestamp NULL DEFAULT CURRENT_TIMESTAMP ON UPDATE CURRENT_TIMESTAMP,
  PRIMARY KEY (`id`),
  UNIQUE KEY `unique_attendance` (`employee_id`,`attendance_date`),
  CONSTRAINT `fk_attendance_employee` FOREIGN KEY (`employee_id`) REFERENCES `employees` (`id`) ON DELETE CASCADE
) ENGINE=InnoDB AUTO_INCREMENT=28 DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_0900_ai_ci;
/*!40101 SET character_set_client = @saved_cs_client */;

--
-- Dumping data for table `attendance`
--

LOCK TABLES `attendance` WRITE;
/*!40000 ALTER TABLE `attendance` DISABLE KEYS */;
INSERT INTO `attendance` VALUES (1,1,'2026-07-13','2026-07-13 19:19:38','2026-07-13 19:19:56',0,0,0,'Present',NULL,'2026-07-13 13:49:38','2026-07-13 13:49:56'),(2,1,'2026-07-14','2026-07-14 01:41:04','2026-07-14 01:41:08',0,0,0,'Present',NULL,'2026-07-13 20:11:04','2026-07-13 20:11:08'),(3,1,'2026-07-15','2026-07-15 11:36:55','2026-07-15 11:37:00',0,0,0,'Present',NULL,'2026-07-15 06:06:55','2026-07-15 06:07:00'),(5,1,'2026-07-16','2026-07-16 16:03:17',NULL,0,0,0,'Present',NULL,'2026-07-16 10:33:17','2026-07-16 10:33:17'),(8,1,'2026-07-17','2026-07-17 12:39:10','2026-07-17 12:39:13',0,0,0,'Present',NULL,'2026-07-17 07:09:10','2026-07-17 07:09:13'),(9,16,'2026-07-17','2026-07-17 20:03:46','2026-07-17 20:03:50',0,0,0,'Present',NULL,'2026-07-17 14:33:46','2026-07-17 14:33:50'),(10,1,'2026-07-18','2026-07-18 01:36:04','2026-07-18 01:36:06',0,0,0,'Present',NULL,'2026-07-17 20:06:04','2026-07-17 20:06:06'),(12,16,'2026-07-18','2026-07-18 01:36:27','2026-07-18 01:36:29',0,0,0,'Present',NULL,'2026-07-17 20:06:27','2026-07-17 20:06:29'),(14,21,'2026-07-18','2026-07-18 15:41:14','2026-07-18 15:41:17',0,0,0,'Present',NULL,'2026-07-18 10:11:14','2026-07-18 10:11:17'),(16,21,'2026-07-20','2026-07-20 00:42:52','2026-07-20 00:42:58',0,0,0,'Present',NULL,'2026-07-19 19:12:52','2026-07-19 19:12:58'),(17,23,'2026-07-21','2026-07-21 11:51:32','2026-07-21 11:51:41',0,121,0,'Late',NULL,'2026-07-21 06:21:32','2026-07-21 06:21:41'),(18,1,'2026-07-21','2026-07-21 11:57:34','2026-07-21 11:57:36',0,127,0,'Late',NULL,'2026-07-21 06:27:34','2026-07-21 06:27:36'),(20,18,'2026-07-21','2026-07-21 12:57:40','2026-07-21 12:57:47',0,187,0,'Late',NULL,'2026-07-21 07:27:40','2026-07-21 07:27:47'),(21,16,'2026-07-21','2026-07-21 13:06:45','2026-07-21 13:06:53',0,196,0,'Late',NULL,'2026-07-21 07:36:45','2026-07-21 07:36:53'),(22,21,'2026-07-21','2026-07-21 17:13:46','2026-07-21 17:56:07',0,443,0,'Late',NULL,'2026-07-21 11:43:46','2026-07-21 12:26:07'),(23,19,'2026-07-21','2026-07-21 20:56:54','2026-07-21 20:57:05',0,666,0,'Late',NULL,'2026-07-21 15:26:54','2026-07-21 15:27:05'),(24,1,'2026-07-22','2026-07-22 00:58:14',NULL,0,0,0,'Present',NULL,'2026-07-21 19:28:14','2026-07-21 19:28:14'),(26,1,'2026-07-23','2026-07-23 08:30:33',NULL,0,0,0,'Present',NULL,'2026-07-23 03:00:33','2026-07-23 03:00:33'),(27,21,'2026-07-23','2026-07-23 09:58:47',NULL,0,8,0,'Late',NULL,'2026-07-23 04:28:47','2026-07-23 04:28:47');
/*!40000 ALTER TABLE `attendance` ENABLE KEYS */;
UNLOCK TABLES;

--
-- Table structure for table `company_settings`
--

DROP TABLE IF EXISTS `company_settings`;
/*!40101 SET @saved_cs_client     = @@character_set_client */;
/*!50503 SET character_set_client = utf8mb4 */;
CREATE TABLE `company_settings` (
  `id` int NOT NULL,
  `company_name` varchar(200) DEFAULT NULL,
  `company_logo` varchar(255) DEFAULT NULL,
  `company_address` text,
  `company_phone` varchar(20) DEFAULT NULL,
  `company_email` varchar(150) DEFAULT NULL,
  `office_latitude` decimal(10,8) DEFAULT NULL,
  `office_longitude` decimal(11,8) DEFAULT NULL,
  `office_start` time DEFAULT NULL,
  `last_reporting` time DEFAULT NULL,
  `office_end` time DEFAULT NULL,
  `working_hours` int DEFAULT '9',
  `grace_minutes` int DEFAULT '15',
  `gps_radius` int DEFAULT '3',
  `created_at` timestamp NULL DEFAULT CURRENT_TIMESTAMP,
  `updated_at` timestamp NULL DEFAULT CURRENT_TIMESTAMP ON UPDATE CURRENT_TIMESTAMP,
  PRIMARY KEY (`id`)
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_0900_ai_ci;
/*!40101 SET character_set_client = @saved_cs_client */;

--
-- Dumping data for table `company_settings`
--

LOCK TABLES `company_settings` WRITE;
/*!40000 ALTER TABLE `company_settings` DISABLE KEYS */;
INSERT INTO `company_settings` VALUES (1,'Guru Ram Singh Ji Associates',NULL,NULL,NULL,NULL,NULL,NULL,'09:30:00','09:50:00','18:30:00',9,20,3,'2026-07-20 14:00:59','2026-07-20 14:00:59');
/*!40000 ALTER TABLE `company_settings` ENABLE KEYS */;
UNLOCK TABLES;

--
-- Table structure for table `departments`
--

DROP TABLE IF EXISTS `departments`;
/*!40101 SET @saved_cs_client     = @@character_set_client */;
/*!50503 SET character_set_client = utf8mb4 */;
CREATE TABLE `departments` (
  `id` int NOT NULL AUTO_INCREMENT,
  `department_name` varchar(100) NOT NULL,
  `description` varchar(255) DEFAULT NULL,
  `status` enum('Active','Inactive') DEFAULT 'Active',
  `created_at` timestamp NULL DEFAULT CURRENT_TIMESTAMP,
  PRIMARY KEY (`id`),
  UNIQUE KEY `department_name` (`department_name`)
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_0900_ai_ci;
/*!40101 SET character_set_client = @saved_cs_client */;

--
-- Dumping data for table `departments`
--

LOCK TABLES `departments` WRITE;
/*!40000 ALTER TABLE `departments` DISABLE KEYS */;
/*!40000 ALTER TABLE `departments` ENABLE KEYS */;
UNLOCK TABLES;

--
-- Table structure for table `employees`
--

DROP TABLE IF EXISTS `employees`;
/*!40101 SET @saved_cs_client     = @@character_set_client */;
/*!50503 SET character_set_client = utf8mb4 */;
CREATE TABLE `employees` (
  `id` int NOT NULL AUTO_INCREMENT,
  `employee_id` varchar(20) DEFAULT NULL,
  `login_id` varchar(20) NOT NULL,
  `first_name` varchar(50) NOT NULL,
  `last_name` varchar(50) DEFAULT NULL,
  `father_name` varchar(100) DEFAULT NULL,
  `mother_name` varchar(100) DEFAULT NULL,
  `dob` date DEFAULT NULL,
  `gender` enum('Male','Female','Other') DEFAULT NULL,
  `email` varchar(100) DEFAULT NULL,
  `address` text,
  `city` varchar(80) DEFAULT NULL,
  `state` varchar(80) DEFAULT NULL,
  `pincode` varchar(10) DEFAULT NULL,
  `phone` varchar(15) DEFAULT NULL,
  `alternate_phone` varchar(15) DEFAULT NULL,
  `aadhar` varchar(12) DEFAULT NULL,
  `pan` varchar(10) DEFAULT NULL,
  `department_id` int DEFAULT NULL,
  `department` varchar(100) DEFAULT NULL,
  `designation` varchar(100) DEFAULT NULL,
  `joining_date` date DEFAULT NULL,
  `salary` decimal(10,2) DEFAULT NULL,
  `password` varchar(255) DEFAULT NULL,
  `photo` varchar(255) DEFAULT NULL,
  `status` enum('Active','Inactive') DEFAULT 'Active',
  `created_at` timestamp NULL DEFAULT CURRENT_TIMESTAMP,
  `updated_at` timestamp NULL DEFAULT CURRENT_TIMESTAMP ON UPDATE CURRENT_TIMESTAMP,
  PRIMARY KEY (`id`),
  UNIQUE KEY `employee_code` (`login_id`),
  UNIQUE KEY `login_id` (`login_id`),
  UNIQUE KEY `email` (`email`),
  UNIQUE KEY `aadhar` (`aadhar`),
  UNIQUE KEY `pan` (`pan`),
  UNIQUE KEY `employee_id` (`employee_id`),
  KEY `fk_employee_department` (`department_id`),
  CONSTRAINT `fk_employee_department` FOREIGN KEY (`department_id`) REFERENCES `departments` (`id`) ON DELETE SET NULL
) ENGINE=InnoDB AUTO_INCREMENT=27 DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_0900_ai_ci;
/*!40101 SET character_set_client = @saved_cs_client */;

--
-- Dumping data for table `employees`
--

LOCK TABLES `employees` WRITE;
/*!40000 ALTER TABLE `employees` DISABLE KEYS */;
INSERT INTO `employees` VALUES (1,NULL,'GRSJ9457','Huzaifa','Farooqui',NULL,NULL,NULL,'Male','farooquihuzaifa59@gmail.com',NULL,NULL,NULL,NULL,'9457918378',NULL,NULL,NULL,NULL,NULL,'Developer','2026-07-13',50000.00,NULL,NULL,'Active','2026-07-13 10:23:25','2026-07-13 10:23:25'),(16,NULL,'AK651742','Ankush','Kashyap',NULL,NULL,NULL,'Male',NULL,NULL,NULL,NULL,NULL,'9457918393',NULL,NULL,NULL,NULL,NULL,'Telecaller','1990-01-01',10000.00,NULL,NULL,'Active','2026-07-17 14:32:57','2026-07-17 14:32:57'),(18,NULL,'MH667599','Ms.','Heena',NULL,NULL,NULL,'Female',NULL,NULL,NULL,NULL,NULL,'9457918395',NULL,NULL,NULL,NULL,NULL,'Telecaller','1937-03-09',10000.00,NULL,NULL,'Active','2026-07-17 20:13:20','2026-07-17 20:13:20'),(19,NULL,'MS823577','Ms.','Sonali',NULL,NULL,NULL,'Female',NULL,NULL,NULL,NULL,NULL,'9457918396',NULL,NULL,NULL,NULL,NULL,'Telecaller','1947-03-09',10000.00,NULL,NULL,'Active','2026-07-18 05:21:15','2026-07-18 05:21:15'),(21,NULL,'VS803539','Vikram Jeet','Singh',NULL,NULL,NULL,'Male',NULL,NULL,NULL,NULL,NULL,'9355501915',NULL,NULL,NULL,NULL,'','Owner','2025-06-02',500000.00,NULL,NULL,'Active','2026-07-18 10:10:40','2026-07-18 11:21:02'),(23,NULL,'MN930135','Mohd Huzaifa','Naseem',NULL,NULL,NULL,'Male',NULL,NULL,NULL,NULL,NULL,'9457918393',NULL,NULL,NULL,NULL,NULL,'Admin','2026-06-06',13000.00,NULL,NULL,'Active','2026-07-20 15:52:40','2026-07-20 15:52:40');
/*!40000 ALTER TABLE `employees` ENABLE KEYS */;
UNLOCK TABLES;
/*!40103 SET TIME_ZONE=@OLD_TIME_ZONE */;

/*!40101 SET SQL_MODE=@OLD_SQL_MODE */;
/*!40014 SET FOREIGN_KEY_CHECKS=@OLD_FOREIGN_KEY_CHECKS */;
/*!40014 SET UNIQUE_CHECKS=@OLD_UNIQUE_CHECKS */;
/*!40101 SET CHARACTER_SET_CLIENT=@OLD_CHARACTER_SET_CLIENT */;
/*!40101 SET CHARACTER_SET_RESULTS=@OLD_CHARACTER_SET_RESULTS */;
/*!40101 SET COLLATION_CONNECTION=@OLD_COLLATION_CONNECTION */;
/*!40111 SET SQL_NOTES=@OLD_SQL_NOTES */;

-- Dump completed on 2026-07-23 14:35:20
