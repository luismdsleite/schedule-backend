DROP DATABASE IF EXISTS schedule;
CREATE DATABASE IF NOT EXISTS schedule;

USE schedule;

CREATE TABLE `EVENT` (
  `Id` int NOT NULL AUTO_INCREMENT,
  `Subject` varchar(255) NOT NULL,
  `SubjectAbbr` varchar(255) NOT NULL,
  `LecturerId` int,
  `RoomId` int,
  `StartTime` time,
  `EndTime` time,
  `WeekDay` tinyint,
  `Hide` boolean NOT NULL,
  PRIMARY KEY (`Id`)
);

CREATE TABLE `LECTURER` (
  `Id` int NOT NULL AUTO_INCREMENT,
  `Name` varchar(255) NOT NULL,
  `NameAbbr` varchar(255) NOT NULL,
  `Office` varchar(255) NOT NULL,
  `Hide` boolean NOT NULL,
  PRIMARY KEY (`Id`)
);

CREATE TABLE `ROOM` (
  `Id` int NOT NULL AUTO_INCREMENT,
  `Name` varchar(255) NOT NULL,
  `NameAbbr` varchar(255) NOT NULL,
  `Number` varchar(255) NOT NULL,
  `Capacity` int NOT NULL,
  `Hide` boolean NOT NULL,
  PRIMARY KEY (`Id`)
);

CREATE TABLE `BLOCK` (
  `Id` int NOT NULL AUTO_INCREMENT,
  `Name` varchar(255) NOT NULL,
  `NameAbbr` varchar(255) NOT NULL,
  `Hide` boolean NOT NULL,
  PRIMARY KEY (`Id`)
);

CREATE TABLE `BLOCK_TO_EVENT` (
  `BlockId` int NOT NULL,
  `EventId` int NOT NULL,
  PRIMARY KEY (`BlockId`, `EventId`)
);

CREATE TABLE `RESTRICTION` (
  `Id` int NOT NULL AUTO_INCREMENT,
  `LecturerId` int NOT NULL,
  `Type` int NOT NULL,
  `StartTime` time NOT NULL,
  `EndTime` time NOT NULL,
  `WeekDay` tinyint NOT NULL,
  PRIMARY KEY (`Id`)
);

CREATE TABLE `OCCUPATION` (
  `Id` int NOT NULL AUTO_INCREMENT,
  `RoomId` int NOT NULL,
  `StartTime` time NOT NULL,
  `EndTime` time NOT NULL,
  `WeekDay` tinyint NOT NULL,
  PRIMARY KEY (`Id`)
);

ALTER TABLE `EVENT` ADD FOREIGN KEY (`LecturerId`) REFERENCES `LECTURER` (`Id`);

ALTER TABLE `EVENT` ADD FOREIGN KEY (`RoomId`) REFERENCES `ROOM` (`Id`);

ALTER TABLE `BLOCK_TO_EVENT` ADD FOREIGN KEY (`BlockId`) REFERENCES `BLOCK` (`Id`);

ALTER TABLE `BLOCK_TO_EVENT` ADD FOREIGN KEY (`EventId`) REFERENCES `EVENT` (`Id`);

ALTER TABLE `RESTRICTION` ADD FOREIGN KEY (`LecturerId`) REFERENCES `LECTURER` (`Id`);

ALTER TABLE `OCCUPATION` ADD FOREIGN KEY (`RoomId`) REFERENCES `ROOM` (`Id`);

CREATE TABLE `USER` (
  `Username` varchar(255) NOT NULL,
  `Hash` VARCHAR(255) NOT NULL,
  `PasswordHash` varbinary(72) NOT NULL,
  `Salt` varbinary(29) NOT NULL,
  PRIMARY KEY (`Username`)
);
