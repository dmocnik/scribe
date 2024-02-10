-- MySQL Workbench Forward Engineering

SET @OLD_UNIQUE_CHECKS=@@UNIQUE_CHECKS, UNIQUE_CHECKS=0;
SET @OLD_FOREIGN_KEY_CHECKS=@@FOREIGN_KEY_CHECKS, FOREIGN_KEY_CHECKS=0;
SET @OLD_SQL_MODE=@@SQL_MODE, SQL_MODE='ONLY_FULL_GROUP_BY,STRICT_TRANS_TABLES,NO_ZERO_IN_DATE,NO_ZERO_DATE,ERROR_FOR_DIVISION_BY_ZERO,NO_ENGINE_SUBSTITUTION';

-- -----------------------------------------------------
-- Schema mydb
-- -----------------------------------------------------
-- -----------------------------------------------------
-- Schema scribe
-- -----------------------------------------------------

-- -----------------------------------------------------
-- Schema scribe
-- -----------------------------------------------------
CREATE SCHEMA IF NOT EXISTS `scribe` DEFAULT CHARACTER SET utf8mb4 COLLATE utf8mb4_0900_ai_ci ;
USE `scribe` ;

-- -----------------------------------------------------
-- Table `scribe`.`user`
-- -----------------------------------------------------
CREATE TABLE IF NOT EXISTS `scribe`.`user` (
  `id` INT NOT NULL,
  `email` VARCHAR(30) NULL DEFAULT NULL,
  `password` VARCHAR(30) NULL DEFAULT NULL,
  `name` VARCHAR(30) NULL DEFAULT NULL,
  `disabled` TINYINT(1) NULL DEFAULT NULL,
  PRIMARY KEY (`id`))
ENGINE = InnoDB
DEFAULT CHARACTER SET = utf8mb4
COLLATE = utf8mb4_0900_ai_ci;


-- -----------------------------------------------------
-- Table `scribe`.`codes`
-- -----------------------------------------------------
CREATE TABLE IF NOT EXISTS `scribe`.`codes` (
  `id` INT NOT NULL,
  `user_ID` INT NULL DEFAULT NULL,
  `code_hash` VARCHAR(256) NULL DEFAULT NULL,
  `code_expiry` DATETIME NULL DEFAULT NULL,
  PRIMARY KEY (`id`),
  INDEX `user_ID` (`user_ID` ASC) VISIBLE,
  CONSTRAINT `codes_ibfk_1`
    FOREIGN KEY (`user_ID`)
    REFERENCES `scribe`.`user` (`id`))
ENGINE = InnoDB
DEFAULT CHARACTER SET = utf8mb4
COLLATE = utf8mb4_0900_ai_ci;


-- -----------------------------------------------------
-- Table `scribe`.`media`
-- -----------------------------------------------------
CREATE TABLE IF NOT EXISTS `scribe`.`media` (
  `id` INT NOT NULL,
  `name` VARCHAR(20) NULL DEFAULT NULL,
  `type` VARCHAR(20) NULL DEFAULT NULL,
  `content` LONGBLOB NULL DEFAULT NULL,
  PRIMARY KEY (`id`))
ENGINE = InnoDB
DEFAULT CHARACTER SET = utf8mb4
COLLATE = utf8mb4_0900_ai_ci;


-- -----------------------------------------------------
-- Table `scribe`.`project`
-- -----------------------------------------------------
CREATE TABLE IF NOT EXISTS `scribe`.`project` (
  `id` INT NOT NULL,
  `name` VARCHAR(20) NULL DEFAULT NULL,
  `video_id` INT NULL DEFAULT NULL,
  `transcript_id` INT NULL DEFAULT NULL,
  `notes_id` INT NULL DEFAULT NULL,
  `audio_id` INT NULL DEFAULT NULL,
  `highlights_id` INT NULL DEFAULT NULL,
  PRIMARY KEY (`id`),
  INDEX `video_id` (`video_id` ASC) VISIBLE,
  INDEX `transcript_id` (`transcript_id` ASC) VISIBLE,
  INDEX `notes_id` (`notes_id` ASC) VISIBLE,
  INDEX `audio_id` (`audio_id` ASC) VISIBLE,
  INDEX `highlights_id` (`highlights_id` ASC) VISIBLE,
  CONSTRAINT `project_ibfk_1`
    FOREIGN KEY (`video_id`)
    REFERENCES `scribe`.`user` (`id`),
  CONSTRAINT `project_ibfk_2`
    FOREIGN KEY (`transcript_id`)
    REFERENCES `scribe`.`user` (`id`),
  CONSTRAINT `project_ibfk_3`
    FOREIGN KEY (`notes_id`)
    REFERENCES `scribe`.`user` (`id`),
  CONSTRAINT `project_ibfk_4`
    FOREIGN KEY (`audio_id`)
    REFERENCES `scribe`.`user` (`id`),
  CONSTRAINT `project_ibfk_5`
    FOREIGN KEY (`highlights_id`)
    REFERENCES `scribe`.`user` (`id`))
ENGINE = InnoDB
DEFAULT CHARACTER SET = utf8mb4
COLLATE = utf8mb4_0900_ai_ci;


SET SQL_MODE=@OLD_SQL_MODE;
SET FOREIGN_KEY_CHECKS=@OLD_FOREIGN_KEY_CHECKS;
SET UNIQUE_CHECKS=@OLD_UNIQUE_CHECKS;
