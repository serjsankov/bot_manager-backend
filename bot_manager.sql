-- MySQL dump 10.13  Distrib 9.4.0, for macos15.4 (arm64)
--
-- Host: localhost    Database: test_chg_auto_trade_db
-- ------------------------------------------------------
-- Server version	9.4.0

/*!40101 SET @OLD_CHARACTER_SET_CLIENT=@@CHARACTER_SET_CLIENT */;
/*!40101 SET @OLD_CHARACTER_SET_RESULTS=@@CHARACTER_SET_RESULTS */;
/*!40101 SET @OLD_COLLATION_CONNECTION=@@COLLATION_CONNECTION */;
/*!50503 SET NAMES utf8mb4 */;
/*!40103 SET @OLD_TIME_ZONE=@@TIME_ZONE */;
/*!40103 SET TIME_ZONE='+00:00' */;
/*!40014 SET @OLD_UNIQUE_CHECKS=@@UNIQUE_CHECKS, UNIQUE_CHECKS=0 */;
/*!40014 SET @OLD_FOREIGN_KEY_CHECKS=@@FOREIGN_KEY_CHECKS, FOREIGN_KEY_CHECKS=0 */;
/*!40101 SET @OLD_SQL_MODE=@@SQL_MODE, SQL_MODE='NO_AUTO_VALUE_ON_ZERO' */;
/*!40111 SET @OLD_SQL_NOTES=@@SQL_NOTES, SQL_NOTES=0 */;

--
-- Table structure for table `car_model`
--

DROP TABLE IF EXISTS `car_model`;
/*!40101 SET @saved_cs_client     = @@character_set_client */;
/*!50503 SET character_set_client = utf8mb4 */;
CREATE TABLE `car_model` (
  `id` int NOT NULL AUTO_INCREMENT,
  `model` varchar(100) NOT NULL,
  PRIMARY KEY (`id`)
) ENGINE=InnoDB AUTO_INCREMENT=12 DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_0900_ai_ci;
/*!40101 SET character_set_client = @saved_cs_client */;

--
-- Dumping data for table `car_model`
--

LOCK TABLES `car_model` WRITE;
/*!40000 ALTER TABLE `car_model` DISABLE KEYS */;
INSERT INTO `car_model` VALUES (1,'ALSVIN'),(2,'EADO PLUS'),(3,'CS35PLUS'),(4,'CS55PLUS'),(5,'LAMORE'),(6,'UNI-K'),(7,'UNI-T'),(8,'UNI-V'),(9,'HUNTER PLUS'),(10,'CS95PLUS');
/*!40000 ALTER TABLE `car_model` ENABLE KEYS */;
UNLOCK TABLES;

--
-- Table structure for table `chats`
--

DROP TABLE IF EXISTS `chats`;
/*!40101 SET @saved_cs_client     = @@character_set_client */;
/*!50503 SET character_set_client = utf8mb4 */;
CREATE TABLE `chats` (
  `id` int unsigned NOT NULL AUTO_INCREMENT,
  `value` varchar(100) CHARACTER SET utf8mb4 COLLATE utf8mb4_0900_ai_ci DEFAULT NULL,
  `created_at` timestamp NULL DEFAULT CURRENT_TIMESTAMP,
  `group_id` varchar(255) CHARACTER SET utf8mb4 COLLATE utf8mb4_0900_ai_ci DEFAULT NULL,
  `link` varchar(255) DEFAULT NULL,
  PRIMARY KEY (`id`)
) ENGINE=InnoDB AUTO_INCREMENT=16 DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_0900_ai_ci;
/*!40101 SET character_set_client = @saved_cs_client */;

--
-- Dumping data for table `chats`
--

LOCK TABLES `chats` WRITE;
/*!40000 ALTER TABLE `chats` DISABLE KEYS */;
/*!40000 ALTER TABLE `chats` ENABLE KEYS */;
UNLOCK TABLES;

--
-- Table structure for table `damage_codes`
--

DROP TABLE IF EXISTS `damage_codes`;
/*!40101 SET @saved_cs_client     = @@character_set_client */;
/*!50503 SET character_set_client = utf8mb4 */;
CREATE TABLE `damage_codes` (
  `id` int NOT NULL AUTO_INCREMENT,
  `code` varchar(10) NOT NULL,
  `damage` varchar(100) NOT NULL,
  PRIMARY KEY (`id`)
) ENGINE=InnoDB AUTO_INCREMENT=12 DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_0900_ai_ci;
/*!40101 SET character_set_client = @saved_cs_client */;

--
-- Dumping data for table `damage_codes`
--

LOCK TABLES `damage_codes` WRITE;
/*!40000 ALTER TABLE `damage_codes` DISABLE KEYS */;
INSERT INTO `damage_codes` VALUES (1,'B','Сломано, разбито'),(2,'C','Скол'),(3,'D','Вмятина'),(4,'F','Потёрто'),(5,'G','Повреждение стекла'),(6,'I','Загрязнение'),(7,'M','Отсутствует'),(8,'N','Проколото'),(9,'P','Порез'),(10,'S','Царапина'),(11,'T','Неисправно');
/*!40000 ALTER TABLE `damage_codes` ENABLE KEYS */;
UNLOCK TABLES;

--
-- Table structure for table `department`
--

DROP TABLE IF EXISTS `department`;
/*!40101 SET @saved_cs_client     = @@character_set_client */;
/*!50503 SET character_set_client = utf8mb4 */;
CREATE TABLE `department` (
  `id` int unsigned NOT NULL AUTO_INCREMENT,
  `value` varchar(255) CHARACTER SET utf8mb4 COLLATE utf8mb4_0900_ai_ci NOT NULL,
  PRIMARY KEY (`id`)
) ENGINE=InnoDB AUTO_INCREMENT=10 DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_0900_ai_ci;
/*!40101 SET character_set_client = @saved_cs_client */;

--
-- Dumping data for table `department`
--

LOCK TABLES `department` WRITE;
/*!40000 ALTER TABLE `department` DISABLE KEYS */;
/*!40000 ALTER TABLE `department` ENABLE KEYS */;
UNLOCK TABLES;

--
-- Table structure for table `employees`
--

DROP TABLE IF EXISTS `employees`;
/*!40101 SET @saved_cs_client     = @@character_set_client */;
/*!50503 SET character_set_client = utf8mb4 */;
CREATE TABLE `employees` (
  `id` int NOT NULL AUTO_INCREMENT,
  `full_name` varchar(255) DEFAULT NULL,
  `phone` varchar(255) DEFAULT NULL,
  `username` varchar(255) DEFAULT NULL,
  `tg_id` bigint DEFAULT NULL,
  PRIMARY KEY (`id`)
) ENGINE=InnoDB AUTO_INCREMENT=3 DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_0900_ai_ci;
/*!40101 SET character_set_client = @saved_cs_client */;

--
-- Dumping data for table `employees`
--

LOCK TABLES `employees` WRITE;
/*!40000 ALTER TABLE `employees` DISABLE KEYS */;
/*!40000 ALTER TABLE `employees` ENABLE KEYS */;
UNLOCK TABLES;

--
-- Table structure for table `list_accepts_cars`
--

DROP TABLE IF EXISTS `list_accepts_cars`;
/*!40101 SET @saved_cs_client     = @@character_set_client */;
/*!50503 SET character_set_client = utf8mb4 */;
CREATE TABLE `list_accepts_cars` (
  `id` int NOT NULL AUTO_INCREMENT,
  `status` varchar(20) NOT NULL,
  `tg_username` varchar(20) NOT NULL,
  `name_folder` varchar(200) NOT NULL,
  `car_model` varchar(100) NOT NULL,
  `car_vin` varchar(20) DEFAULT NULL,
  `url_ya_folder` varchar(300) NOT NULL,
  `message_id` varchar(100) DEFAULT NULL,
  `created_at` timestamp NOT NULL DEFAULT CURRENT_TIMESTAMP,
  `updated_at` timestamp NULL DEFAULT NULL ON UPDATE CURRENT_TIMESTAMP,
  `telegram_id` bigint DEFAULT NULL,
  PRIMARY KEY (`id`),
  UNIQUE KEY `list_accept_car_unique` (`name_folder`)
) ENGINE=InnoDB AUTO_INCREMENT=204 DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_0900_ai_ci;
/*!40101 SET character_set_client = @saved_cs_client */;

--
-- Dumping data for table `list_accepts_cars`
--

LOCK TABLES `list_accepts_cars` WRITE;
/*!40000 ALTER TABLE `list_accepts_cars` DISABLE KEYS */;
INSERT INTO `list_accepts_cars` VALUES (54,'удалена','lobot24','25-04-19 ALSVIN VIN11111','ALSVIN','11111','https://yadi.sk/d/R7NC136da3tm5w','642','2025-04-19 12:54:15','2025-07-28 12:53:25',NULL),(55,'новая','bladwor','25-04-22 LAMORE VIN667','LAMORE','667','https://yadi.sk/d/oRTLbcPa9WMvxw','822','2025-04-22 14:27:42','2025-04-22 14:27:45',NULL),(59,'новая','Monareich','25-04-23 UNI-T VIN89632','UNI-T','89632','https://yadi.sk/d/GrEq5Bj327IcWA','966','2025-04-23 07:18:15','2025-04-23 07:18:17',NULL),(61,'закрыта','Monareich','25-04-23 LAMORE VIN678906','LAMORE','678906','https://yadi.sk/d/xg-IwSC-HnVLDA','1112','2025-04-23 09:07:40','2025-04-29 12:32:02',NULL),(64,'закрыта','Monareich','25-04-23 HUNTER PLUS VIN678907','HUNTER PLUS','678907','https://yadi.sk/d/s14USjUG9mTJ_g','1188','2025-04-23 12:31:36','2025-05-06 08:48:32',NULL),(80,'закрыта','Monareich','25-04-25 EADO PLUS VIN123456','EADO PLUS','123456','https://yadi.sk/d/KVHMAF7McNbHhg','1369','2025-04-25 09:05:13','2025-05-06 08:47:49',NULL),(83,'закрыта','Monareich','25-04-25 CS35PLUS VIN236589','CS35PLUS','236589','https://yadi.sk/d/bmrt1aZxKUaPug','1391','2025-04-25 13:12:03','2025-04-29 11:56:17',NULL),(90,'новая','lobot24','25-04-28 ALSVIN VIN22222','ALSVIN','22222','https://yadi.sk/d/KaFWa7JfSCEhwA','254','2025-04-28 14:20:06','2025-04-28 14:20:52',NULL),(92,'удалена','Monareich','25-04-29 UNI-V VIN258369','UNI-V','258369','https://yadi.sk/d/4GLIopxkNjBUuw','1515','2025-04-29 09:45:50','2025-04-29 12:32:22',NULL),(94,'закрыта','bladwor','25-05-06 LAMORE VIN67876','LAMORE','67876','https://yadi.sk/d/w5aNwFjie3Nodw','1697','2025-05-06 11:56:26','2025-05-06 13:32:04',NULL),(97,'удалена','Monareich','25-05-06 CS55PLUS VIN925275','CS55PLUS','925275','https://yadi.sk/d/IhSohVS0efay_Q','1978','2025-05-06 14:40:03','2025-08-01 15:57:03',NULL),(98,'новая','Monareich','25-05-06 CS55PLUS VIN925230','CS55PLUS','925230','https://yadi.sk/d/hbZRzMTdxiAe6A','1831','2025-05-06 14:43:04','2025-05-06 14:43:06',NULL),(99,'новая','Monareich','25-05-06 CS55PLUS VIN959885','CS55PLUS','959885','https://yadi.sk/d/6hY3JmTe_zio0w','1885','2025-05-06 14:46:08','2025-05-06 14:46:10',NULL),(103,'новая','Monareich','25-05-06 CS55PLUS VIN958419','CS55PLUS','958419','https://yadi.sk/d/RPbMoZ3HCdc4UQ','2046','2025-05-06 15:00:05','2025-05-06 15:00:07',NULL),(104,'новая','Monareich','25-05-06 CS55PLUS VIN954561','CS55PLUS','954561','https://yadi.sk/d/44K--dPqr9F1Bg','2262','2025-05-06 15:02:44','2025-05-06 15:19:00',NULL),(106,'новая','Monareich','25-05-06 CS55PLUS VIN920406','CS55PLUS','920406','https://yadi.sk/d/J3kd2qj3N4Ew0A','2168','2025-05-06 15:06:30','2025-05-06 15:06:33',NULL),(107,'новая','Monareich','25-05-06 CS55PLUS VIN922709','CS55PLUS','922709','https://yadi.sk/d/_A6MSntp1wc6-g','2222','2025-05-06 15:10:15','2025-05-06 15:10:16',NULL),(109,'новая','as_popovich','25-05-23 ALSVIN VIN666633','ALSVIN','666633','https://yadi.sk/d/bnnW5raR0O4r8w','2376','2025-05-23 12:54:56','2025-05-23 12:57:18',NULL),(112,'новая','as_popovich','25-05-23 LAMORE VIN346688','LAMORE','346688','https://yadi.sk/d/pLHjamJX4fL8Lw','2454','2025-05-23 12:58:12','2025-05-23 13:21:38',NULL),(114,'закрыта','Monareich','25-05-23 LAMORE VIN34569','LAMORE','34569','https://yadi.sk/d/p2ZjtETYXmEcVQ','2477','2025-05-23 13:31:23','2025-05-23 14:07:35',NULL),(115,'новая','as_popovich','25-05-24 CS35PLUS VIN975664','CS35PLUS','975664','https://yadi.sk/d/bzrYlhZZ7-Cn0Q','2591','2025-05-24 13:38:02','2025-05-24 13:38:04',NULL),(116,'новая','as_popovich','25-05-24 CS55PLUS VIN924664','CS55PLUS','924664','https://yadi.sk/d/FMwpcyWOZj5wjQ','2984','2025-05-24 13:42:22','2025-05-24 14:14:03',NULL),(118,'новая','as_popovich','25-05-24 CS55PLUS VIN957989','CS55PLUS','957989','https://yadi.sk/d/tW_syK4fXDqL5w','2734','2025-05-24 13:49:31','2025-05-24 13:49:33',NULL),(119,'новая','as_popovich','25-05-24 CS55PLUS VIN959241','CS55PLUS','959241','https://yadi.sk/d/Ss0ZwtveLA4C5g','2792','2025-05-24 13:53:58','2025-05-24 13:54:01',NULL),(120,'новая','as_popovich','25-05-24 CS35PLUS VIN974793','CS35PLUS','974793','https://yadi.sk/d/YnLZZodX5JIYFA','2850','2025-05-24 13:59:19','2025-05-24 13:59:21',NULL),(121,'новая','as_popovich','25-05-24 CS35PLUS VIN973470','CS35PLUS','973470','https://yadi.sk/d/eUuc8IwzLWPyuw','3008','2025-05-24 14:03:39','2025-05-24 14:31:07',NULL),(122,'новая','as_popovich','25-05-24 CS35PLUS VIN975706','CS35PLUS','975706','https://yadi.sk/d/h78h7az2zX63Ww','2960','2025-05-24 14:06:29','2025-05-24 14:06:31',NULL),(125,'новая','as_popovich','25-06-20 CS95PLUS VIN911543','CS95PLUS','911543','https://yadi.sk/d/nyRSKgwpwpNW_g','3104','2025-06-20 08:59:16','2025-06-20 08:59:19',NULL),(126,'новая','as_popovich','25-06-20 CS55PLUS VIN957286','CS55PLUS','957286','https://yadi.sk/d/-zsXB7WaTDJ0GQ','3162','2025-06-20 09:03:40','2025-06-20 09:03:41',NULL),(127,'новая','as_popovich','25-06-20 UNI-T VIN993143','UNI-T','993143','https://yadi.sk/d/5rmU-w1DiZT7Eg','3220','2025-06-20 09:08:46','2025-06-20 09:08:48',NULL),(128,'новая','as_popovich','25-06-20 CS55PLUS VIN956942','CS55PLUS','956942','https://yadi.sk/d/0uMQE2VqcUYYsw','3283','2025-06-20 09:14:03','2025-06-20 09:14:06',NULL),(129,'новая','as_popovich','25-06-20 CS35PLUS VIN975300','CS35PLUS','975300','https://yadi.sk/d/taNkbliTyIHm0Q','3341','2025-06-20 09:18:12','2025-06-20 09:18:13',NULL),(130,'новая','as_popovich','25-06-20 CS35PLUS VIN974885','CS35PLUS','974885','https://yadi.sk/d/AGFT9KjHoLWxhA','3399','2025-06-20 09:24:55','2025-06-20 09:24:57',NULL),(131,'новая','as_popovich','25-06-20 CS55PLUS VIN952647','CS55PLUS','952647','https://yadi.sk/d/Eh6_4SLpk-GEjQ','3457','2025-06-20 13:12:11','2025-06-20 13:12:13',NULL),(132,'новая','as_popovich','25-06-20 CS55PLUS VIN952535','CS55PLUS','952535','https://yadi.sk/d/3KIk6GiGbobLpQ','3836','2025-06-20 13:29:51','2025-06-20 14:19:50',NULL),(133,'новая','as_popovich','25-06-20 CS55PLUS VIN924835','CS55PLUS','924835','https://yadi.sk/d/ZmhMN3nYLx9LYA','3630','2025-06-20 13:37:46','2025-06-20 13:37:48',NULL),(134,'новая','as_popovich','25-06-20 CS55PLUS VIN952339','CS55PLUS','952339','https://yadi.sk/d/hPxq0gMri5XJUQ','3688','2025-06-20 13:54:06','2025-06-20 13:54:08',NULL),(135,'новая','as_popovich','25-06-20 CS55PLUS VIN922539','CS55PLUS','922539','https://yadi.sk/d/P-qU0h0iRlsKoQ','3746','2025-06-20 13:59:10','2025-06-20 13:59:12',NULL),(136,'новая','as_popovich','25-06-20 CS55PLUS VIN922685','CS55PLUS','922685','https://yadi.sk/d/SqRXOIrz7NN-7g','3804','2025-06-20 14:06:31','2025-06-20 14:06:33',NULL),(138,'новая','as_popovich','25-06-20 CS55PLUS VINРррро','CS55PLUS','Рррро','https://yadi.sk/d/fGEpALAPKz3CjA','3868','2025-07-01 12:21:59','2025-07-01 12:22:02',NULL),(139,'новая','as_popovich','25-07-01 CS55PLUS VIN957191','CS55PLUS','957191','https://yadi.sk/d/dZ37pneX_i-mQQ','3931','2025-07-01 12:28:41','2025-07-01 12:28:44',NULL),(140,'новая','as_popovich','25-07-01 CS55PLUS VIN959821','CS55PLUS','959821','https://yadi.sk/d/nwXpypcA5OwcJw','3989','2025-07-01 12:35:27','2025-07-01 12:35:32',NULL),(141,'новая','as_popovich','25-07-01 CS95PLUS VIN912062','CS95PLUS','912062','https://yadi.sk/d/xftzG4Tei4yTxQ','4047','2025-07-01 12:43:06','2025-07-01 12:43:09',NULL),(142,'новая','as_popovich','25-07-01 CS35PLUS VIN973639','CS35PLUS','973639','https://yadi.sk/d/E3ZP9tDX1Zn0Gg','4155','2025-07-01 13:21:18','2025-07-01 13:31:02',NULL),(144,'новая','as_popovich','25-07-06 UNI-T VIN706211','UNI-T','706211','https://yadi.sk/d/ZlXhieCfnyfpcA','4247','2025-07-06 06:17:59','2025-07-06 06:18:02',NULL),(145,'новая','as_popovich','25-07-06 CS55PLUS VIN956845','CS55PLUS','956845','https://yadi.sk/d/Gyqt_2KEY6LCng','4305','2025-07-06 06:22:50','2025-07-06 06:22:52',NULL),(146,'новая','as_popovich','25-07-06 CS55PLUS VIN958103','CS55PLUS','958103','https://yadi.sk/d/yqIH9GQ64RCAsA','4381','2025-07-06 06:31:14','2025-07-06 06:31:16',NULL),(147,'новая','as_popovich','25-07-06 CS55PLUS VIN958084','CS55PLUS','958084','https://yadi.sk/d/xFqQckryB9EbDA','4439','2025-07-06 06:37:59','2025-07-06 06:38:01',NULL),(148,'закрыта','Dmitry200611','25-06-08 CS55PLUS VIN59885','CS55PLUS','59885','https://yadi.sk/d/_0IrywaVANBZHw','4455','2025-07-07 07:10:30','2025-07-07 07:28:19',NULL),(149,'новая','Dmitry200611','25-07-07 CS35PLUS VIN70873','CS35PLUS','70873','https://yadi.sk/d/1vzuQ1pukF90BA','4543','2025-07-07 07:23:43','2025-07-07 07:23:45',NULL),(150,'новая','as_popovich','25-07-09 UNI-K VIN996945','UNI-K','996945','https://yadi.sk/d/J4E8GlYwkOCrPg','4746','2025-07-09 10:25:03','2025-07-09 10:31:57',NULL),(151,'новая','lobot24','25-08-01 ALSVIN VIN15648','ALSVIN','15648','https://yadi.sk/d/n17DZA2SEw3XxA','4816','2025-08-01 12:41:40','2025-08-01 12:41:42',NULL),(152,'новая','as_popovich','25-08-04 CS55PLUS VIN956878','CS55PLUS','956878','https://yadi.sk/d/a3polcPoNYlRcw','4907','2025-08-04 11:20:14','2025-08-04 11:20:16',NULL),(153,'новая','Monareich','25-08-20 ALSVIN VIN25362','ALSVIN','25362','https://yadi.sk/d/OXL0IVvrvn_hjg','5549','2025-08-20 16:13:44','2025-08-20 16:14:57',NULL),(155,'новая','KirillOrekhov','25-08-22 UNI-K VIN67890','UNI-K','67890','https://yadi.sk/d/NVSsLs3suPXHXg','5674','2025-08-22 08:32:22','2025-08-22 08:33:31',NULL),(157,'новая','as_popovich','25-08-22 ALSVIN VIN123456','ALSVIN','123456','https://yadi.sk/d/eDqcSxtwnXY4BQ','5684','2025-08-22 08:33:42','2025-08-22 08:33:43',NULL),(158,'новая','it_sir','25-08-22 CS95PLUS VIN89856','CS95PLUS','89856','https://yadi.sk/d/FTooX7kfphY1Ug',NULL,'2025-08-22 17:40:21',NULL,NULL),(159,'новая','it_sir96','25-08-22 CS95PLUS VINTEST','CS95PLUS','TEST','https://yadi.sk/d/cWg4o4TCJPr2Rg',NULL,'2025-08-22 17:53:07','2025-08-22 19:04:18',1179174103),(164,'в работе','it_sir96','25-08-22 ALSVIN VINTEST1','ALSVIN','TEST1','https://yadi.sk/d/Lf4EzCRCyXdZwg','139','2025-08-22 18:03:09','2025-08-24 10:20:53',1179174103),(173,'закрыта','serj_sankov','25-08-24 ALSVIN VINtest','ALSVIN','test','https://yadi.sk/d/w7GRhhHIwB4qug','19','2025-08-24 08:06:52','2025-08-24 08:55:23',704861909),(177,'закрыта','serj_sankov','25-08-24 LAMORE VIN33333','LAMORE','33333','https://yadi.sk/d/dLY221O8eRSc3w','20','2025-08-24 08:57:09','2025-08-24 08:57:40',704861909),(178,'закрыта','Alla_sankova','25-08-24 ALSVIN VINtest333','ALSVIN','test333','https://yadi.sk/d/QMOFwjU6gRT8dA','21','2025-08-24 09:13:31','2025-08-24 09:14:40',1164835766),(179,'в работе','frontend_top','25-08-24 LAMORE VINtest3','LAMORE','test3','https://yadi.sk/d/3OUnLTLy4aoZvA','22','2025-08-24 10:29:09','2025-08-25 06:37:58',704861909),(180,'новая','serj_sankov','25-08-29 UNI-K VIN22222','UNI-K','22222','https://yadi.sk/d/i0qn6bly-6Mlrg','25','2025-08-29 09:14:50','2025-08-29 09:14:53',704861909),(181,'новая','serj_sankov','25-08-30 UNI-V VINтест0','UNI-V','тест0','https://yadi.sk/d/Bw0p3POH6MpTEg','26','2025-08-30 11:41:49','2025-08-30 11:41:52',704861909),(182,'новая','serj_sankov','25-09-01 EADO PLUS VINтест000','EADO PLUS','тест000','https://yadi.sk/d/X1tW9g3HUXGxvg','27','2025-09-01 08:24:52','2025-09-01 08:24:55',704861909),(183,'новая','serj_sankov','25-09-04 ALSVIN VINtest3333','ALSVIN','test3333','https://yadi.sk/d/SXJe227wdEuhjA','28','2025-09-04 00:09:15','2025-09-04 00:09:18',704861909),(184,'новая','serj_sankov','25-09-04 ALSVIN VINtest','ALSVIN','test','https://yadi.sk/d/fJCLiEQupD-y4w','29','2025-09-04 00:24:16','2025-09-04 00:24:20',704861909),(185,'новая','serj_sankov','25-09-04 ALSVIN VINtest02','ALSVIN','test02','https://yadi.sk/d/x0SCUmwFJanv8Q','30','2025-09-04 00:29:06','2025-09-04 00:29:09',704861909),(186,'новая','serj_sankov','25-09-04 LAMORE VINtest03','LAMORE','test03','https://yadi.sk/d/LDKmi8YoOOHMpA','31','2025-09-04 00:31:25','2025-09-04 00:31:27',704861909),(187,'новая','serj_sankov','25-09-04 CS35PLUS VINtest04','CS35PLUS','test04','https://yadi.sk/d/ysbaY_8pd7PtMg','32','2025-09-04 00:42:02','2025-09-04 00:42:04',704861909),(188,'новая','serj_sankov','25-09-04 LAMORE VINtest05','LAMORE','test05','https://yadi.sk/d/sqUgk39vws2Vmg','33','2025-09-04 00:43:20','2025-09-04 00:43:23',704861909),(189,'новая','serj_sankov','25-09-04 LAMORE VINtest06','LAMORE','test06','https://yadi.sk/d/uLSdzZki4Ktn5A','34','2025-09-04 00:47:45','2025-09-04 00:47:47',704861909),(190,'новая','KirillBukhtenko','25-09-04 LAMORE VIN56842','LAMORE','56842','https://yadi.sk/d/3ov7evp80ZA1eQ','35','2025-09-04 12:24:23','2025-09-04 12:24:26',466255064),(191,'новая','serj_sankov','25-09-05 ALSVIN VINtest01','ALSVIN','test01','https://yadi.sk/d/A9J2OzVz1BFuPg','36','2025-09-04 22:18:52','2025-09-04 22:18:55',704861909),(194,'новая','serj_sankov','25-09-05 CS95PLUS VINtest02','CS95PLUS','test02','https://yadi.sk/d/3zfQw3wJLSXnHg','39','2025-09-04 23:40:26','2025-09-04 23:40:30',704861909),(195,'новая','serj_sankov','25-09-05 HUNTER PLUS VINtest03','HUNTER PLUS','test03','https://yadi.sk/d/Hi21QeViC8gyFw','40','2025-09-04 23:54:28','2025-09-04 23:54:30',704861909),(196,'новая','serj_sankov','25-09-05 ALSVIN VINtest0001','ALSVIN','test0001','https://yadi.sk/d/uQW4XjB-RKrHPQ','41','2025-09-05 08:52:05','2025-09-05 08:52:08',704861909),(197,'новая','serj_sankov','25-09-05 UNI-K VINtest009','UNI-K','test009','https://yadi.sk/d/-Q4foCIV1r6HvQ','42','2025-09-05 09:24:25','2025-09-05 09:24:28',704861909),(198,'новая','serj_sankov','25-09-05 HUNTER PLUS VINtest333','HUNTER PLUS','test333','https://yadi.sk/d/K6Iz9Xd2lMVaQw','43','2025-09-05 10:59:34','2025-09-05 10:59:37',704861909),(199,'новая','serj_sankov','25-09-05 UNI-T VINtest333','UNI-T','test333','https://yadi.sk/d/SOgxk2HoD4o8Gw','44','2025-09-05 11:02:36','2025-09-05 11:02:40',704861909),(200,'новая','serj_sankov','25-09-05 UNI-V VINtest89898','UNI-V','test89898','https://yadi.sk/d/s3w-pvE-m6lsgQ','45','2025-09-05 14:41:09','2025-09-05 14:41:11',704861909),(201,'новая','KirillBukhtenko','25-09-05 EADO PLUS VIN66754','EADO PLUS','66754','https://yadi.sk/d/5RSKON7_-ufxOQ','46','2025-09-05 15:33:28','2025-09-05 15:33:37',466255064),(202,'новая','serj_sankov','25-09-10 CS55PLUS VINtest000','CS55PLUS','test000','https://yadi.sk/d/nDRBMFkYRS07Hw','47','2025-09-10 09:29:14','2025-09-10 09:29:17',704861909),(203,'новая','serj_sankov','25-09-10 ALSVIN VINtest000','ALSVIN','test000','https://yadi.sk/d/GevCI1axPXnT6A','48','2025-09-10 12:43:07','2025-09-10 12:43:10',704861909);
/*!40000 ALTER TABLE `list_accepts_cars` ENABLE KEYS */;
UNLOCK TABLES;

--
-- Table structure for table `photo_angles`
--

DROP TABLE IF EXISTS `photo_angles`;
/*!40101 SET @saved_cs_client     = @@character_set_client */;
/*!50503 SET character_set_client = utf8mb4 */;
CREATE TABLE `photo_angles` (
  `id` int NOT NULL AUTO_INCREMENT,
  `angle` varchar(50) NOT NULL,
  PRIMARY KEY (`id`)
) ENGINE=InnoDB AUTO_INCREMENT=13 DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_0900_ai_ci;
/*!40101 SET character_set_client = @saved_cs_client */;

--
-- Dumping data for table `photo_angles`
--

LOCK TABLES `photo_angles` WRITE;
/*!40000 ALTER TABLE `photo_angles` DISABLE KEYS */;
INSERT INTO `photo_angles` VALUES (1,'Вид спереди'),(2,'Вид сзади'),(8,'Крыша'),(9,'Вид слева'),(10,'Вид справа'),(11,'Пробег авто'),(12,'vin номер авто на фоне водит.удостоверения');
/*!40000 ALTER TABLE `photo_angles` ENABLE KEYS */;
UNLOCK TABLES;

--
-- Table structure for table `role_chat`
--

DROP TABLE IF EXISTS `role_chat`;
/*!40101 SET @saved_cs_client     = @@character_set_client */;
/*!50503 SET character_set_client = utf8mb4 */;
CREATE TABLE `role_chat` (
  `role_id` int unsigned NOT NULL,
  `chat_id` int NOT NULL,
  PRIMARY KEY (`role_id`,`chat_id`),
  CONSTRAINT `role_chat_ibfk_1` FOREIGN KEY (`role_id`) REFERENCES `roles` (`id`) ON DELETE CASCADE
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_0900_ai_ci;
/*!40101 SET character_set_client = @saved_cs_client */;

--
-- Dumping data for table `role_chat`
--

LOCK TABLES `role_chat` WRITE;
/*!40000 ALTER TABLE `role_chat` DISABLE KEYS */;
/*!40000 ALTER TABLE `role_chat` ENABLE KEYS */;
UNLOCK TABLES;

--
-- Table structure for table `role_dep`
--

DROP TABLE IF EXISTS `role_dep`;
/*!40101 SET @saved_cs_client     = @@character_set_client */;
/*!50503 SET character_set_client = utf8mb4 */;
CREATE TABLE `role_dep` (
  `role_id` int unsigned NOT NULL,
  `dep_id` int NOT NULL,
  PRIMARY KEY (`role_id`,`dep_id`),
  CONSTRAINT `role_dep_ibfk_1` FOREIGN KEY (`role_id`) REFERENCES `roles` (`id`) ON DELETE CASCADE
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_0900_ai_ci;
/*!40101 SET character_set_client = @saved_cs_client */;

--
-- Dumping data for table `role_dep`
--

LOCK TABLES `role_dep` WRITE;
/*!40000 ALTER TABLE `role_dep` DISABLE KEYS */;
/*!40000 ALTER TABLE `role_dep` ENABLE KEYS */;
UNLOCK TABLES;

--
-- Table structure for table `roles`
--

DROP TABLE IF EXISTS `roles`;
/*!40101 SET @saved_cs_client     = @@character_set_client */;
/*!50503 SET character_set_client = utf8mb4 */;
CREATE TABLE `roles` (
  `id` int unsigned NOT NULL AUTO_INCREMENT,
  `value` varchar(255) CHARACTER SET utf8mb4 COLLATE utf8mb4_0900_ai_ci DEFAULT NULL,
  PRIMARY KEY (`id`)
) ENGINE=InnoDB AUTO_INCREMENT=29 DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_0900_ai_ci;
/*!40101 SET character_set_client = @saved_cs_client */;

--
-- Dumping data for table `roles`
--

LOCK TABLES `roles` WRITE;
/*!40000 ALTER TABLE `roles` DISABLE KEYS */;
/*!40000 ALTER TABLE `roles` ENABLE KEYS */;
UNLOCK TABLES;

--
-- Table structure for table `user_chats`
--

DROP TABLE IF EXISTS `user_chats`;
/*!40101 SET @saved_cs_client     = @@character_set_client */;
/*!50503 SET character_set_client = utf8mb4 */;
CREATE TABLE `user_chats` (
  `user_id` int unsigned NOT NULL,
  `chat_id` int unsigned NOT NULL,
  `joined_at` timestamp NULL DEFAULT CURRENT_TIMESTAMP,
  PRIMARY KEY (`user_id`,`chat_id`),
  KEY `chat_id` (`chat_id`),
  CONSTRAINT `user_chats_ibfk_1` FOREIGN KEY (`user_id`) REFERENCES `users_managers` (`id`) ON DELETE CASCADE,
  CONSTRAINT `user_chats_ibfk_2` FOREIGN KEY (`chat_id`) REFERENCES `chats` (`id`) ON DELETE CASCADE
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_0900_ai_ci;
/*!40101 SET character_set_client = @saved_cs_client */;

--
-- Dumping data for table `user_chats`
--

LOCK TABLES `user_chats` WRITE;
/*!40000 ALTER TABLE `user_chats` DISABLE KEYS */;
/*!40000 ALTER TABLE `user_chats` ENABLE KEYS */;
UNLOCK TABLES;

--
-- Table structure for table `users`
--

DROP TABLE IF EXISTS `users`;
/*!40101 SET @saved_cs_client     = @@character_set_client */;
/*!50503 SET character_set_client = utf8mb4 */;
CREATE TABLE `users` (
  `id` bigint unsigned NOT NULL AUTO_INCREMENT,
  `type_user` varchar(20) DEFAULT NULL,
  `full_name` varchar(255) NOT NULL,
  `username` varchar(255) NOT NULL,
  `telegram_id` bigint DEFAULT NULL,
  `created_at` timestamp NOT NULL DEFAULT CURRENT_TIMESTAMP,
  PRIMARY KEY (`id`),
  UNIQUE KEY `id` (`id`),
  UNIQUE KEY `telegram_id` (`telegram_id`)
) ENGINE=InnoDB AUTO_INCREMENT=48 DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_0900_ai_ci;
/*!40101 SET character_set_client = @saved_cs_client */;

--
-- Dumping data for table `users`
--

LOCK TABLES `users` WRITE;
/*!40000 ALTER TABLE `users` DISABLE KEYS */;
INSERT INTO `users` VALUES (20,'receiver','Буслаков Кирилл Игоревич','spiker0777',NULL,'2025-02-22 15:02:25'),(21,'receiver','Орехов Кирилл Алексеевич','KirillOrekhov',NULL,'2025-02-22 15:02:25'),(22,'receiver','Маляров Кирилл Валерьевич','Kirill_Mzp',NULL,'2025-02-22 15:02:25'),(23,'receiver','Крупенский Дмитрий Александрович','Dmitry200611',NULL,'2025-02-22 15:02:26'),(24,'receiver','Апарышев Артем Дмитриевич','Glyba2343',NULL,'2025-02-22 15:02:26'),(25,'receiver','Попович Алексей Сергеевич','as_popovich',NULL,'2025-02-22 15:02:26'),(26,'boss','Гурьева Полина Сергеевна','PolinaElenich',NULL,'2025-02-22 15:11:35'),(27,'boss','Коршунова Валерия Валерьевна','n_valeri27',NULL,'2025-02-22 15:11:35'),(28,'receiver','Позднякова Екатерина Владимировна','Monareich',NULL,'2025-02-22 15:11:36'),(32,'receiver','Станислав','bladwor',NULL,'2025-02-27 15:38:55'),(33,'boss','Вячеслав','digitparts',NULL,'2025-02-27 15:38:55'),(40,'admin','Лоик Андрей','lobot24',NULL,'2025-05-25 07:59:21'),(41,'receiver','Лоик Андрей','lobot24',NULL,'2025-05-25 08:00:08'),(43,'receiver','Кирилл','KirillBukhtenko',466255064,'2025-08-14 21:39:12'),(44,'receiver','Павел','it_sir',1179174103,'2025-08-14 21:40:05'),(46,'admin','Test','Alla_sankova',1164835766,'2025-08-24 09:12:20'),(47,'receiver','Serj','serj_sankov',704861909,'2025-08-26 14:41:18');
/*!40000 ALTER TABLE `users` ENABLE KEYS */;
UNLOCK TABLES;

--
-- Table structure for table `users_managers`
--

DROP TABLE IF EXISTS `users_managers`;
/*!40101 SET @saved_cs_client     = @@character_set_client */;
/*!50503 SET character_set_client = utf8mb4 */;
CREATE TABLE `users_managers` (
  `id` int unsigned NOT NULL AUTO_INCREMENT,
  `created_at` timestamp NOT NULL DEFAULT CURRENT_TIMESTAMP,
  `gender` varchar(255) NOT NULL,
  `phone_director` varchar(20) DEFAULT NULL,
  `director` varchar(255) NOT NULL,
  `phone_manager` varchar(20) DEFAULT NULL,
  `manager` varchar(255) NOT NULL,
  `department` varchar(255) NOT NULL,
  `role` varchar(255) NOT NULL,
  `birth_date` date DEFAULT NULL,
  `phone` varchar(20) DEFAULT NULL,
  `full_name` varchar(255) NOT NULL,
  `username` varchar(255) NOT NULL,
  `tg_id` bigint DEFAULT NULL,
  `status` enum('pending','approved','rejected') NOT NULL DEFAULT 'pending',
  PRIMARY KEY (`id`),
  UNIQUE KEY `id` (`id`),
  UNIQUE KEY `telegram_id` (`tg_id`)
) ENGINE=InnoDB AUTO_INCREMENT=66 DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_0900_ai_ci;
/*!40101 SET character_set_client = @saved_cs_client */;

--
-- Dumping data for table `users_managers`
--

LOCK TABLES `users_managers` WRITE;
/*!40000 ALTER TABLE `users_managers` DISABLE KEYS */;
INSERT INTO `users_managers` VALUES (1,'2025-09-29 08:49:10','',NULL,'',NULL,'','','директор','1997-12-14','79000000000','Алла','Alla_sankova',1164835766,'approved');
/*!40000 ALTER TABLE `users_managers` ENABLE KEYS */;
UNLOCK TABLES;
/*!40103 SET TIME_ZONE=@OLD_TIME_ZONE */;

/*!40101 SET SQL_MODE=@OLD_SQL_MODE */;
/*!40014 SET FOREIGN_KEY_CHECKS=@OLD_FOREIGN_KEY_CHECKS */;
/*!40014 SET UNIQUE_CHECKS=@OLD_UNIQUE_CHECKS */;
/*!40101 SET CHARACTER_SET_CLIENT=@OLD_CHARACTER_SET_CLIENT */;
/*!40101 SET CHARACTER_SET_RESULTS=@OLD_CHARACTER_SET_RESULTS */;
/*!40101 SET COLLATION_CONNECTION=@OLD_COLLATION_CONNECTION */;
/*!40111 SET SQL_NOTES=@OLD_SQL_NOTES */;

-- Dump completed on 2025-10-13 22:52:43
