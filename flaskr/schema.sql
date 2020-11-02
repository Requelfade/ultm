CREATE TABLE `Player` (
	`idplayers` INT NOT NULL AUTO_INCREMENT,
	`riotpuuid` TEXT NOT NULL,
    `summonerid` TEXT NOT NULL,
	`nickname` TEXT NOT NULL,
	`idposition` INT,
	`idteams` INT,
	`level` INT,
	`issub` BOOLEAN,
	`rankedrank` TEXT,
	`lastupdate` DATETIME NOT NULL,
    `iconid` TEXT,
    `isverified` BOOLEAN,
	PRIMARY KEY (`idplayers`)
);

CREATE TABLE `Users` (
	`idusers` INT NOT NULL AUTO_INCREMENT,
	`username` TEXT NOT NULL,
	`password` TEXT NOT NULL,
	`email` TEXT NOT NULL,
	`permissionslevel` INT,
	`displayedname` TEXT,
	`idplayers` INT,
	`discordid` TEXT,
	`name` TEXT,
	`surname` TEXT,
	`idschools` INT,
	`idclass` INT,
	PRIMARY KEY (`idusers`)
);

CREATE TABLE `Positions` (
	`idpositions` INT NOT NULL AUTO_INCREMENT,
	`position` TEXT NOT NULL,
	PRIMARY KEY (`idpositions`)
);

CREATE TABLE `Schools` (
	`idschools` INT NOT NULL AUTO_INCREMENT,
	`name` TEXT NOT NULL,
	`shortname` TEXT NOT NULL,
	PRIMARY KEY (`idschools`)
);

CREATE TABLE `Classes` (
	`idclass` INT NOT NULL AUTO_INCREMENT,
	`classname` TEXT NOT NULL,
	PRIMARY KEY (`idclass`)
);

CREATE TABLE `Teams` (
	`idteams` INT NOT NULL AUTO_INCREMENT,
	`name` TEXT NOT NULL,
	`tag` TEXT NOT NULL,
	`wins` INT,
	`loses` INT,
	`idgroups` INT,
	PRIMARY KEY (`idteams`)
);

CREATE TABLE `Matches` (
	`idmatches` INT NOT NULL AUTO_INCREMENT,
	`idteams1` INT NOT NULL,
	`idteams2` INT NOT NULL,
	`matchdata` JSON,
	`result` TEXT,
	`matchcode` TEXT,
	`playdate` DATE,
	PRIMARY KEY (`idmatches`)
);

CREATE TABLE `Groups` (
	`idgroups` INT NOT NULL AUTO_INCREMENT,
	`name` VARCHAR(255) NOT NULL,
	`idphase` INT,
	PRIMARY KEY (`idgroups`)
);

CREATE TABLE `Phases` (
	`idphase` INT NOT NULL AUTO_INCREMENT,
	`name` TEXT NOT NULL,
	PRIMARY KEY (`idphase`)
);

CREATE TABLE `Tournament` (
	`idtournament` INT NOT NULL AUTO_INCREMENT,
	`idprovider` INT NOT NULL,
	`tournament` TEXT NOT NULL,
	PRIMARY KEY (`idtournament`)
);

CREATE TABLE `Provider` (
	`idprovider` INT NOT NULL AUTO_INCREMENT,
	`provider` TEXT NOT NULL,
	PRIMARY KEY (`idprovider`)
);

ALTER TABLE `Player` ADD CONSTRAINT `Player_fk0` FOREIGN KEY (`idposition`) REFERENCES `Positions`(`idpositions`);

ALTER TABLE `Player` ADD CONSTRAINT `Player_fk1` FOREIGN KEY (`idteams`) REFERENCES `Teams`(`idteams`);

ALTER TABLE `Users` ADD CONSTRAINT `Users_fk0` FOREIGN KEY (`idplayers`) REFERENCES `Player`(`idplayers`);

ALTER TABLE `Users` ADD CONSTRAINT `Users_fk1` FOREIGN KEY (`idschools`) REFERENCES `Schools`(`idschools`);

ALTER TABLE `Users` ADD CONSTRAINT `Users_fk2` FOREIGN KEY (`idclass`) REFERENCES `Classes`(`idclass`);

ALTER TABLE `Teams` ADD CONSTRAINT `Teams_fk0` FOREIGN KEY (`idgroups`) REFERENCES `Groups`(`idgroups`);

ALTER TABLE `Matches` ADD CONSTRAINT `Matches_fk0` FOREIGN KEY (`idteams1`) REFERENCES `Teams`(`idteams`);

ALTER TABLE `Matches` ADD CONSTRAINT `Matches_fk1` FOREIGN KEY (`idteams2`) REFERENCES `Teams`(`idteams`);

ALTER TABLE `Groups` ADD CONSTRAINT `Groups_fk0` FOREIGN KEY (`idphase`) REFERENCES `Phases`(`idphase`);

ALTER TABLE `Tournament` ADD CONSTRAINT `Tournament_fk0` FOREIGN KEY (`idprovider`) REFERENCES `Provider`(`idprovider`);

