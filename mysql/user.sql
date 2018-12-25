ALTER TABLE `amsterdamteam9`.`user`
ADD COLUMN `last_seen` DATETIME NULL DEFAULT NULL AFTER `Player_ID`;