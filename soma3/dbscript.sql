SET @OLD_UNIQUE_CHECKS=@@UNIQUE_CHECKS, UNIQUE_CHECKS=0;
SET @OLD_FOREIGN_KEY_CHECKS=@@FOREIGN_KEY_CHECKS, FOREIGN_KEY_CHECKS=0;
SET @OLD_SQL_MODE=@@SQL_MODE, SQL_MODE='TRADITIONAL,ALLOW_INVALID_DATES';

CREATE SCHEMA IF NOT EXISTS `urqa` DEFAULT CHARACTER SET utf8 ;
USE `urqa` ;

-- -----------------------------------------------------
-- Table `urqa`.`users`
-- -----------------------------------------------------
CREATE  TABLE IF NOT EXISTS `urqa`.`users` (
  `uid` INT NOT NULL AUTO_INCREMENT ,
  `email` VARCHAR(45) NOT NULL ,
  `passwd` VARCHAR(20) NOT NULL ,
  `nickname` VARCHAR(45) NOT NULL ,
  `company` VARCHAR(45) NOT NULL ,
  `image_path` VARCHAR(45) NULL DEFAULT 'null.png' ,
  PRIMARY KEY (`uid`) ,
  UNIQUE INDEX `email_UNIQUE` (`email` ASC) )
ENGINE = InnoDB;


-- -----------------------------------------------------
-- Table `urqa`.`auth_user`
-- -----------------------------------------------------
CREATE  TABLE IF NOT EXISTS `urqa`.`auth_user` (
  `id` INT NOT NULL AUTO_INCREMENT ,
  `password` VARCHAR(128) NOT NULL ,
  `last_login` DATETIME NOT NULL ,
  `is_superuser` TINYINT(1) NOT NULL ,
  `username` VARCHAR(30) NOT NULL ,
  `first_name` VARCHAR(30) NOT NULL ,
  `last_name` VARCHAR(30) NOT NULL ,
  `email` VARCHAR(75) NOT NULL ,
  `is_staff` TINYINT(1) NOT NULL ,
  `is_active` TINYINT(1) NOT NULL ,
  `date_joined` DATETIME NOT NULL ,
  `image_path` VARCHAR(260) NULL ,
  PRIMARY KEY (`id`) ,
  UNIQUE INDEX `username` (`username` ASC) )
ENGINE = InnoDB
AUTO_INCREMENT = 2
DEFAULT CHARACTER SET = utf8;


-- -----------------------------------------------------
-- Table `urqa`.`projects`
-- -----------------------------------------------------
CREATE  TABLE IF NOT EXISTS `urqa`.`projects` (
  `pid` INT NOT NULL AUTO_INCREMENT ,
  `apikey` VARCHAR(10) NOT NULL ,
  `platform` INT NOT NULL ,
  `name` VARCHAR(45) NOT NULL ,
  `stage` INT NOT NULL ,
  `owner_uid` INT NOT NULL ,
  `category` INT NULL ,
  `timezone` VARCHAR(45) NULL ,
  PRIMARY KEY (`pid`) ,
  UNIQUE INDEX `apikey_UNIQUE` (`apikey` ASC) ,
  INDEX `user_projects_idx` (`owner_uid` ASC) ,
  CONSTRAINT `user_projects`
    FOREIGN KEY (`owner_uid` )
    REFERENCES `urqa`.`auth_user` (`id` )
    ON DELETE NO ACTION
    ON UPDATE NO ACTION)
ENGINE = InnoDB;


-- -----------------------------------------------------
-- Table `urqa`.`viewer`
-- -----------------------------------------------------
CREATE  TABLE IF NOT EXISTS `urqa`.`viewer` (
  `idviewer` INT NOT NULL AUTO_INCREMENT ,
  `uid` INT NOT NULL ,
  `pid` INT NOT NULL ,
  INDEX `projects_idx` (`pid` ASC) ,
  INDEX `users_viewer_idx` (`uid` ASC) ,
  PRIMARY KEY (`idviewer`) ,
  CONSTRAINT `users_viewer`
    FOREIGN KEY (`uid` )
    REFERENCES `urqa`.`auth_user` (`id` )
    ON DELETE NO ACTION
    ON UPDATE NO ACTION,
  CONSTRAINT `projects_viewer`
    FOREIGN KEY (`pid` )
    REFERENCES `urqa`.`projects` (`pid` )
    ON DELETE NO ACTION
    ON UPDATE NO ACTION)
ENGINE = InnoDB;


-- -----------------------------------------------------
-- Table `urqa`.`errors`
-- -----------------------------------------------------
CREATE  TABLE IF NOT EXISTS `urqa`.`errors` (
  `iderror` INT NOT NULL AUTO_INCREMENT ,
  `pid` INT NOT NULL ,
  `rank` INT NOT NULL ,
  `autodetermine` INT NOT NULL ,
  `status` INT NULL ,
  `numofinstances` INT NOT NULL ,
  `createdate` DATETIME NOT NULL ,
  `lastdate` DATETIME NOT NULL ,
  `callstack` MEDIUMTEXT NOT NULL ,
  `errorname` VARCHAR(500) NOT NULL ,
  `errorclassname` VARCHAR(300) NOT NULL ,
  `linenum` VARCHAR(45) NOT NULL ,
  `errorweight` INT NULL ,
  `recur` INT NULL ,
  `eventpath` BLOB NULL ,
  `wifion` INT NOT NULL ,
  `gpson` INT NOT NULL ,
  `mobileon` INT NOT NULL ,
  `totalmemusage` INT NOT NULL ,
  `gain1` FLOAT NULL ,
  `gain2` FLOAT NULL ,
  PRIMARY KEY (`iderror`) ,
  INDEX `projects_idx` (`pid` ASC) ,
  CONSTRAINT `projects_errors`
    FOREIGN KEY (`pid` )
    REFERENCES `urqa`.`projects` (`pid` )
    ON DELETE NO ACTION
    ON UPDATE NO ACTION)
ENGINE = InnoDB;


-- -----------------------------------------------------
-- Table `urqa`.`appstatistics`
-- -----------------------------------------------------
CREATE  TABLE IF NOT EXISTS `urqa`.`appstatistics` (
  `idappstatistics` INT NOT NULL AUTO_INCREMENT ,
  `iderror` INT NOT NULL ,
  `appversion` VARCHAR(45) NOT NULL ,
  `count` INT NOT NULL ,
  PRIMARY KEY (`idappstatistics`) ,
  CONSTRAINT `errors_appstatistics`
    FOREIGN KEY (`iderror` )
    REFERENCES `urqa`.`errors` (`iderror` )
    ON DELETE NO ACTION
    ON UPDATE NO ACTION)
ENGINE = InnoDB;


-- -----------------------------------------------------
-- Table `urqa`.`osstatistics`
-- -----------------------------------------------------
CREATE  TABLE IF NOT EXISTS `urqa`.`osstatistics` (
  `idosstatistics` INT NOT NULL AUTO_INCREMENT ,
  `iderror` INT NOT NULL ,
  `osversion` VARCHAR(10) NOT NULL ,
  `count` INT NOT NULL ,
  PRIMARY KEY (`idosstatistics`) ,
  CONSTRAINT `errors_osstatistics`
    FOREIGN KEY (`iderror` )
    REFERENCES `urqa`.`errors` (`iderror` )
    ON DELETE NO ACTION
    ON UPDATE NO ACTION)
ENGINE = InnoDB;


-- -----------------------------------------------------
-- Table `urqa`.`devicestatistics`
-- -----------------------------------------------------
CREATE  TABLE IF NOT EXISTS `urqa`.`devicestatistics` (
  `iddevicestatistics` INT NOT NULL AUTO_INCREMENT ,
  `iderror` INT NOT NULL ,
  `devicename` VARCHAR(45) NOT NULL ,
  `count` INT NOT NULL ,
  PRIMARY KEY (`iddevicestatistics`) ,
  CONSTRAINT `errors_devicestatistics`
    FOREIGN KEY (`iderror` )
    REFERENCES `urqa`.`errors` (`iderror` )
    ON DELETE NO ACTION
    ON UPDATE NO ACTION)
ENGINE = InnoDB;


-- -----------------------------------------------------
-- Table `urqa`.`countrystatistics`
-- -----------------------------------------------------
CREATE  TABLE IF NOT EXISTS `urqa`.`countrystatistics` (
  `idcountrystatistics` INT NOT NULL AUTO_INCREMENT ,
  `iderror` INT NOT NULL ,
  `countryname` VARCHAR(45) NOT NULL ,
  `count` INT NOT NULL ,
  PRIMARY KEY (`idcountrystatistics`) ,
  CONSTRAINT `errors_countrystatistics`
    FOREIGN KEY (`iderror` )
    REFERENCES `urqa`.`errors` (`iderror` )
    ON DELETE NO ACTION
    ON UPDATE NO ACTION)
ENGINE = InnoDB;


-- -----------------------------------------------------
-- Table `urqa`.`comments`
-- -----------------------------------------------------
CREATE  TABLE IF NOT EXISTS `urqa`.`comments` (
  `idcomment` INT NOT NULL AUTO_INCREMENT ,
  `uid` INT NOT NULL ,
  `iderror` INT NOT NULL ,
  `datetime` DATETIME NOT NULL ,
  `comment` VARCHAR(200) NOT NULL ,
  PRIMARY KEY (`idcomment`) ,
  INDEX `users_comments_idx` (`uid` ASC) ,
  CONSTRAINT `errors_comments`
    FOREIGN KEY (`iderror` )
    REFERENCES `urqa`.`errors` (`iderror` )
    ON DELETE NO ACTION
    ON UPDATE NO ACTION,
  CONSTRAINT `users_comments`
    FOREIGN KEY (`uid` )
    REFERENCES `urqa`.`auth_user` (`id` )
    ON DELETE NO ACTION
    ON UPDATE NO ACTION)
ENGINE = InnoDB;


-- -----------------------------------------------------
-- Table `urqa`.`instances`
-- -----------------------------------------------------
CREATE  TABLE IF NOT EXISTS `urqa`.`instances` (
  `idinstance` INT NOT NULL AUTO_INCREMENT ,
  `iderror` INT NOT NULL ,
  `ins_count` INT NULL ,
  `sdkversion` VARCHAR(45) NULL ,
  `appversion` VARCHAR(45) NULL ,
  `osversion` VARCHAR(45) NULL ,
  `kernelversion` VARCHAR(45) NULL ,
  `appmemmax` VARCHAR(45) NULL ,
  `appmemfree` VARCHAR(45) NULL ,
  `appmemtotal` VARCHAR(45) NULL ,
  `country` VARCHAR(45) NULL ,
  `datetime` DATETIME NULL ,
  `locale` VARCHAR(45) NULL ,
  `mobileon` INT NULL ,
  `gpson` INT NULL ,
  `wifion` INT NULL ,
  `device` VARCHAR(45) NULL ,
  `rooted` INT NULL ,
  `scrheight` INT NULL ,
  `scrwidth` INT NULL ,
  `scrorientation` INT NULL ,
  `sysmemlow` VARCHAR(45) NULL ,
  `log_path` VARCHAR(260) NULL ,
  `batterylevel` INT NULL ,
  `availsdcard` INT NULL ,
  `xdpi` DOUBLE NULL ,
  `ydpi` DOUBLE NULL ,
  `callstack` MEDIUMTEXT NULL ,
  `dump_path` VARCHAR(260) NULL ,
  `lastactivity` VARCHAR(300) NULL ,
  PRIMARY KEY (`idinstance`) ,
  INDEX `errors_idx` (`iderror` ASC) ,
  CONSTRAINT `errors_instances`
    FOREIGN KEY (`iderror` )
    REFERENCES `urqa`.`errors` (`iderror` )
    ON DELETE NO ACTION
    ON UPDATE NO ACTION)
ENGINE = InnoDB;


-- -----------------------------------------------------
-- Table `urqa`.`eventpaths`
-- -----------------------------------------------------
CREATE  TABLE IF NOT EXISTS `urqa`.`eventpaths` (
  `ideventpaths` INT NOT NULL AUTO_INCREMENT ,
  `idinstance` INT NOT NULL ,
  `iderror` INT NOT NULL ,
  `ins_count` INT NULL ,
  `datetime` DATETIME NULL ,
  `classname` VARCHAR(300) NULL ,
  `methodname` VARCHAR(300) NULL ,
  `linenum` INT NULL ,
  `depth` INT NULL ,
  `label` VARCHAR(300) NULL ,
  PRIMARY KEY (`ideventpaths`) ,
  INDEX `errors_eventpaths_idx` (`iderror` ASC) ,
  CONSTRAINT `instances_eventpaths`
    FOREIGN KEY (`idinstance` )
    REFERENCES `urqa`.`instances` (`idinstance` )
    ON DELETE NO ACTION
    ON UPDATE NO ACTION,
  CONSTRAINT `errors_eventpaths`
    FOREIGN KEY (`iderror` )
    REFERENCES `urqa`.`errors` (`iderror` )
    ON DELETE NO ACTION
    ON UPDATE NO ACTION)
ENGINE = InnoDB;


-- -----------------------------------------------------
-- Table `urqa`.`tags`
-- -----------------------------------------------------
CREATE  TABLE IF NOT EXISTS `urqa`.`tags` (
  `idtag` INT NOT NULL AUTO_INCREMENT ,
  `iderror` INT NOT NULL ,
  `tag` VARCHAR(45) NOT NULL ,
  `pid` INT NOT NULL ,
  PRIMARY KEY (`idtag`) ,
  INDEX `errors_tags_idx` (`iderror` ASC) ,
  INDEX `projects_tags_idx` (`pid` ASC) ,
  CONSTRAINT `errors_tags`
    FOREIGN KEY (`iderror` )
    REFERENCES `urqa`.`errors` (`iderror` )
    ON DELETE NO ACTION
    ON UPDATE NO ACTION,
  CONSTRAINT `projects_tags`
    FOREIGN KEY (`pid` )
    REFERENCES `urqa`.`projects` (`pid` )
    ON DELETE NO ACTION
    ON UPDATE NO ACTION)
ENGINE = InnoDB;


-- -----------------------------------------------------
-- Table `urqa`.`session`
-- -----------------------------------------------------
CREATE  TABLE IF NOT EXISTS `urqa`.`session` (
  `idsession` BIGINT NOT NULL ,
  `pid` INT NOT NULL ,
  `appversion` VARCHAR(45) NOT NULL ,
  PRIMARY KEY (`idsession`) ,
  INDEX `projects_session_idx` (`pid` ASC) ,
  CONSTRAINT `projects_session`
    FOREIGN KEY (`pid` )
    REFERENCES `urqa`.`projects` (`pid` )
    ON DELETE NO ACTION
    ON UPDATE NO ACTION)
ENGINE = InnoDB;


-- -----------------------------------------------------
-- Table `urqa`.`sessionevent`
-- -----------------------------------------------------
CREATE  TABLE IF NOT EXISTS `urqa`.`sessionevent` (
  `idsessionevent` INT NOT NULL AUTO_INCREMENT ,
  `idsession` BIGINT NOT NULL ,
  `datetime` DATETIME NULL ,
  `classname` VARCHAR(300) NULL ,
  `methodname` VARCHAR(300) NULL ,
  `linenum` INT NULL ,
  PRIMARY KEY (`idsessionevent`) ,
  CONSTRAINT `session_sessionevent`
    FOREIGN KEY (`idsession` )
    REFERENCES `urqa`.`session` (`idsession` )
    ON DELETE NO ACTION
    ON UPDATE NO ACTION)
ENGINE = InnoDB;


-- -----------------------------------------------------
-- Table `urqa`.`appruncount`
-- -----------------------------------------------------
CREATE  TABLE IF NOT EXISTS `urqa`.`appruncount` (
  `idappruncount` INT NOT NULL AUTO_INCREMENT ,
  `pid` INT NOT NULL ,
  `date` DATE NULL ,
  `appversion` VARCHAR(45) NULL ,
  `runcount` BIGINT NULL ,
  PRIMARY KEY (`idappruncount`) ,
  INDEX `projects_appruncount_idx` (`pid` ASC) ,
  CONSTRAINT `projects_appruncount`
    FOREIGN KEY (`pid` )
    REFERENCES `urqa`.`projects` (`pid` )
    ON DELETE NO ACTION
    ON UPDATE NO ACTION)
ENGINE = InnoDB;


-- -----------------------------------------------------
-- Table `urqa`.`auth_group`
-- -----------------------------------------------------
CREATE  TABLE IF NOT EXISTS `urqa`.`auth_group` (
  `id` INT NOT NULL AUTO_INCREMENT ,
  `name` VARCHAR(80) NOT NULL ,
  PRIMARY KEY (`id`) ,
  UNIQUE INDEX `name` (`name` ASC) )
ENGINE = InnoDB
DEFAULT CHARACTER SET = utf8;


-- -----------------------------------------------------
-- Table `urqa`.`django_content_type`
-- -----------------------------------------------------
CREATE  TABLE IF NOT EXISTS `urqa`.`django_content_type` (
  `id` INT(11) NOT NULL AUTO_INCREMENT ,
  `name` VARCHAR(100) NOT NULL ,
  `app_label` VARCHAR(100) NOT NULL ,
  `model` VARCHAR(100) NOT NULL ,
  PRIMARY KEY (`id`) ,
  UNIQUE INDEX `app_label` (`app_label` ASC, `model` ASC) )
ENGINE = InnoDB
AUTO_INCREMENT = 37
DEFAULT CHARACTER SET = utf8;


-- -----------------------------------------------------
-- Table `urqa`.`auth_permission`
-- -----------------------------------------------------
CREATE  TABLE IF NOT EXISTS `urqa`.`auth_permission` (
  `id` INT NOT NULL AUTO_INCREMENT ,
  `name` VARCHAR(50) NOT NULL ,
  `content_type_id` INT NOT NULL ,
  `codename` VARCHAR(100) NOT NULL ,
  PRIMARY KEY (`id`) ,
  UNIQUE INDEX `content_type_id` (`content_type_id` ASC, `codename` ASC) ,
  INDEX `auth_permission_37ef4eb4` (`content_type_id` ASC) ,
  CONSTRAINT `content_type_id_refs_id_d043b34a`
    FOREIGN KEY (`content_type_id` )
    REFERENCES `urqa`.`django_content_type` (`id` ))
ENGINE = InnoDB
AUTO_INCREMENT = 109
DEFAULT CHARACTER SET = utf8;


-- -----------------------------------------------------
-- Table `urqa`.`auth_group_permissions`
-- -----------------------------------------------------
CREATE  TABLE IF NOT EXISTS `urqa`.`auth_group_permissions` (
  `id` INT NOT NULL AUTO_INCREMENT ,
  `group_id` INT NOT NULL ,
  `permission_id` INT NOT NULL ,
  PRIMARY KEY (`id`) ,
  UNIQUE INDEX `group_id` (`group_id` ASC, `permission_id` ASC) ,
  INDEX `auth_group_permissions_5f412f9a` (`group_id` ASC) ,
  INDEX `auth_group_permissions_83d7f98b` (`permission_id` ASC) ,
  CONSTRAINT `group_id_refs_id_f4b32aac`
    FOREIGN KEY (`group_id` )
    REFERENCES `urqa`.`auth_group` (`id` ),
  CONSTRAINT `permission_id_refs_id_6ba0f519`
    FOREIGN KEY (`permission_id` )
    REFERENCES `urqa`.`auth_permission` (`id` ))
ENGINE = InnoDB
DEFAULT CHARACTER SET = utf8;


-- -----------------------------------------------------
-- Table `urqa`.`auth_user_groups`
-- -----------------------------------------------------
CREATE  TABLE IF NOT EXISTS `urqa`.`auth_user_groups` (
  `id` INT NOT NULL AUTO_INCREMENT ,
  `user_id` INT NOT NULL ,
  `group_id` INT NOT NULL ,
  PRIMARY KEY (`id`) ,
  UNIQUE INDEX `user_id` (`user_id` ASC, `group_id` ASC) ,
  INDEX `auth_user_groups_6340c63c` (`user_id` ASC) ,
  INDEX `auth_user_groups_5f412f9a` (`group_id` ASC) ,
  CONSTRAINT `user_id_refs_id_40c41112`
    FOREIGN KEY (`user_id` )
    REFERENCES `urqa`.`auth_user` (`id` ),
  CONSTRAINT `group_id_refs_id_274b862c`
    FOREIGN KEY (`group_id` )
    REFERENCES `urqa`.`auth_group` (`id` ))
ENGINE = InnoDB
DEFAULT CHARACTER SET = utf8;


-- -----------------------------------------------------
-- Table `urqa`.`auth_user_user_permissions`
-- -----------------------------------------------------
CREATE  TABLE IF NOT EXISTS `urqa`.`auth_user_user_permissions` (
  `id` INT NOT NULL AUTO_INCREMENT ,
  `user_id` INT NOT NULL ,
  `permission_id` INT NOT NULL ,
  PRIMARY KEY (`id`) ,
  UNIQUE INDEX `user_id` (`user_id` ASC, `permission_id` ASC) ,
  INDEX `auth_user_user_permissions_6340c63c` (`user_id` ASC) ,
  INDEX `auth_user_user_permissions_83d7f98b` (`permission_id` ASC) ,
  CONSTRAINT `user_id_refs_id_4dc23c39`
    FOREIGN KEY (`user_id` )
    REFERENCES `urqa`.`auth_user` (`id` ),
  CONSTRAINT `permission_id_refs_id_35d9ac25`
    FOREIGN KEY (`permission_id` )
    REFERENCES `urqa`.`auth_permission` (`id` ))
ENGINE = InnoDB
DEFAULT CHARACTER SET = utf8;


-- -----------------------------------------------------
-- Table `urqa`.`django_session`
-- -----------------------------------------------------
CREATE  TABLE IF NOT EXISTS `urqa`.`django_session` (
  `session_key` VARCHAR(40) NOT NULL ,
  `session_data` LONGTEXT NOT NULL ,
  `expire_date` DATETIME NOT NULL ,
  PRIMARY KEY (`session_key`) ,
  INDEX `django_session_b7b81f0c` (`expire_date` ASC) )
ENGINE = InnoDB
DEFAULT CHARACTER SET = utf8;


-- -----------------------------------------------------
-- Table `urqa`.`django_site`
-- -----------------------------------------------------
CREATE  TABLE IF NOT EXISTS `urqa`.`django_site` (
  `id` INT NOT NULL AUTO_INCREMENT ,
  `domain` VARCHAR(100) NOT NULL ,
  `name` VARCHAR(50) NOT NULL ,
  PRIMARY KEY (`id`) )
ENGINE = InnoDB
AUTO_INCREMENT = 2
DEFAULT CHARACTER SET = utf8;


-- -----------------------------------------------------
-- Table `urqa`.`sofiles`
-- -----------------------------------------------------
CREATE  TABLE IF NOT EXISTS `urqa`.`sofiles` (
  `idsofiles` INT NOT NULL AUTO_INCREMENT ,
  `pid` INT NOT NULL ,
  `appversion` VARCHAR(45) NOT NULL ,
  `versionkey` VARCHAR(45) NULL ,
  `filename` VARCHAR(45) NULL ,
  `uploaded` VARCHAR(45) NULL ,
  PRIMARY KEY (`idsofiles`) ,
  INDEX `projects_sofiles_idx` (`pid` ASC) ,
  CONSTRAINT `projects_sofiles`
    FOREIGN KEY (`pid` )
    REFERENCES `urqa`.`projects` (`pid` )
    ON DELETE NO ACTION
    ON UPDATE NO ACTION)
ENGINE = InnoDB;


-- -----------------------------------------------------
-- Table `urqa`.`activitystatistics`
-- -----------------------------------------------------
CREATE  TABLE IF NOT EXISTS `urqa`.`activitystatistics` (
  `idactivitystatistics` INT NOT NULL AUTO_INCREMENT ,
  `iderror` INT NOT NULL ,
  `activityname` VARCHAR(300) NOT NULL ,
  `count` INT NOT NULL ,
  PRIMARY KEY (`idactivitystatistics`) ,
  INDEX `errors_activitystatistics_idx` (`iderror` ASC) ,
  CONSTRAINT `errors_activitystatistics`
    FOREIGN KEY (`iderror` )
    REFERENCES `urqa`.`errors` (`iderror` )
    ON DELETE NO ACTION
    ON UPDATE NO ACTION)
ENGINE = InnoDB;


-- -----------------------------------------------------
-- Table `urqa`.`proguardmap`
-- -----------------------------------------------------
CREATE  TABLE IF NOT EXISTS `urqa`.`proguardmap` (
  `idproguardmap` INT NOT NULL AUTO_INCREMENT ,
  `pid` INT NOT NULL ,
  `appversion` VARCHAR(45) NULL ,
  `filename` VARCHAR(45) NULL ,
  `uploadtime` DATETIME NULL ,
  PRIMARY KEY (`idproguardmap`) ,
  INDEX `projects_proguardmap_idx` (`pid` ASC) ,
  CONSTRAINT `projects_proguardmap`
    FOREIGN KEY (`pid` )
    REFERENCES `urqa`.`projects` (`pid` )
    ON DELETE NO ACTION
    ON UPDATE NO ACTION)
ENGINE = InnoDB;

USE `urqa` ;


SET SQL_MODE=@OLD_SQL_MODE;
SET FOREIGN_KEY_CHECKS=@OLD_FOREIGN_KEY_CHECKS;
SET UNIQUE_CHECKS=@OLD_UNIQUE_CHECKS;
