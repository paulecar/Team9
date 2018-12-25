CREATE TABLE `amsterdamteam9`.`kvm` (
  `key` varchar(32) NOT NULL,
  `value` VARCHAR(240) NULL,
  PRIMARY KEY (`key`),
  UNIQUE INDEX `key_UNIQUE` (`key` ASC));