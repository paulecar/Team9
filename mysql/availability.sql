CREATE TABLE `availability` (
  `idavailability` int(11) NOT NULL AUTO_INCREMENT,
  `Player_ID` int(11) NOT NULL,
  `Match_ID` int(11) NOT NULL,
  `Season_ID` int(11) NOT NULL,
  PRIMARY KEY (`idavailability`),
  KEY `fk_Match_idx` (`Match_ID`),
  KEY `fk_Avail_Player_idx` (`Player_ID`),
  KEY `fk_Avail_Season_idx` (`Season_ID`),
  CONSTRAINT `fk_Avail_Match` FOREIGN KEY (`Match_ID`) REFERENCES `match` (`idmatch`),
  CONSTRAINT `fk_Avail_Player` FOREIGN KEY (`Player_ID`) REFERENCES `player` (`idplayer`),
  CONSTRAINT `fk_Avail_Season` FOREIGN KEY (`Season_ID`) REFERENCES `season` (`idseason`)
);