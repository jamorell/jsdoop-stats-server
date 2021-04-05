CREATE DATABASE IF NOT EXISTS jsdoop;
USE jsdoop;

CREATE TABLE `stats` (
 `id` bigint NOT NULL AUTO_INCREMENT,
 `infoWorker` varchar(300) NOT NULL,
 `remoteAddr` varchar(200) NOT NULL,
 `timeRequest` bigint NOT NULL,
 `timeResponse` bigint NOT NULL,
 `ageModel` int DEFAULT NULL,
 `idJob` bigint NOT NULL,
 `typeTask` varchar(200) NOT NULL,
 `other` varchar(300) DEFAULT NULL,
 `username` varchar(50) NOT NULL,
 `idTask` bigint NOT NULL,
 `executionTime` bigint NOT NULL,
 PRIMARY KEY (`id`),
 UNIQUE KEY `UK_VALUES` (`infoWorker`,`remoteAddr`,`timeRequest`)
) ENGINE=InnoDB AUTO_INCREMENT=4731473 DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_0900_ai_ci;


CREATE TABLE `test_acc_loss` (
 `id` bigint NOT NULL AUTO_INCREMENT,
 `idJob` bigint NOT NULL,
 `ageModel` int NOT NULL,
 `confusion_matrix` varchar(5000) NOT NULL,
 `loss` decimal(20,15) NOT NULL,
 `acc` decimal(20,15) NOT NULL,
 `requestTime` bigint NOT NULL,
 `responseTime` bigint NOT NULL,
 PRIMARY KEY (`id`),
 UNIQUE KEY `UK_VARS` (`idJob`,`ageModel`)
) ENGINE=InnoDB AUTO_INCREMENT=63706 DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_0900_ai_ci;
