DROP DATABASE schedule;
CREATE DATABASE IF NOT EXISTS schedule;

USE schedule;

CREATE TABLE `EVENT` (
  `Id` int NOT NULL AUTO_INCREMENT,
  `Subject` varchar(255),
  `SubjectAbbr` varchar(255),
  `LecturerId` int,
  `RoomId` int,
  `StartTime` time,
  `EndTime` time,
  `WeekDay` tinyint,
  `Hide` boolean,
  PRIMARY KEY (`Id`)
);

CREATE TABLE `LECTURER` (
  `Id` int NOT NULL AUTO_INCREMENT,
  `Name` varchar(255),
  `NameAbbr` varchar(255),
  `Office` varchar(255),
  `Hide` boolean,
  PRIMARY KEY (`Id`)
);

CREATE TABLE `ROOM` (
  `Id` int NOT NULL AUTO_INCREMENT,
  `Name` varchar(255),
  `NameAbbr` varchar(255),
  `Number` varchar(255),
  `Capacity` int,
  `Hide` boolean,
  PRIMARY KEY (`Id`)
);

CREATE TABLE `BLOCK` (
  `Id` int NOT NULL AUTO_INCREMENT,
  `Name` varchar(255),
  `NameAbbr` varchar(255),
  `Hide` boolean,
  PRIMARY KEY (`Id`)
);

CREATE TABLE `BLOCK_TO_EVENT` (
  `BlockId` int,
  `EventId` int,
  PRIMARY KEY (`BlockId`, `EventId`)
);

CREATE TABLE `RESTRICTION` (
  `Id` int NOT NULL AUTO_INCREMENT,
  `LecturerId` int,
  `Type` int,
  `StartTime` time,
  `EndTime` time,
  `WeekDay` tinyint,
  PRIMARY KEY (`Id`)
);

CREATE TABLE `OCUPATION` (
  `Id` int NOT NULL AUTO_INCREMENT,
  `RoomId` int,
  `Type` int,
  `StartTime` time,
  `EndTime` time,
  `WeekDay` tinyint,
  PRIMARY KEY (`Id`)
);

ALTER TABLE `EVENT` ADD FOREIGN KEY (`LecturerId`) REFERENCES `LECTURER` (`Id`);

ALTER TABLE `EVENT` ADD FOREIGN KEY (`RoomId`) REFERENCES `ROOM` (`Id`);

ALTER TABLE `BLOCK_TO_EVENT` ADD FOREIGN KEY (`BlockId`) REFERENCES `BLOCK` (`Id`);

ALTER TABLE `BLOCK_TO_EVENT` ADD FOREIGN KEY (`EventId`) REFERENCES `EVENT` (`Id`);

ALTER TABLE `RESTRICTION` ADD FOREIGN KEY (`LecturerId`) REFERENCES `LECTURER` (`Id`);

ALTER TABLE `OCUPATION` ADD FOREIGN KEY (`RoomId`) REFERENCES `ROOM` (`Id`);
