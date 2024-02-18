-- scribe.media definition

CREATE TABLE `media` (
  `id` int(11) NOT NULL,
  `name` varchar(64) NOT NULL,
  `type` varchar(20) NOT NULL,
  `content` longblob NOT NULL,
  PRIMARY KEY (`id`)
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_unicode_520_ci;


-- scribe.`user` definition

CREATE TABLE `user` (
  `id` int(11) NOT NULL AUTO_INCREMENT,
  `email` varchar(64) NOT NULL,
  `password_hash` varchar(256) NOT NULL,
  `name` varchar(30) DEFAULT NULL,
  `disabled` tinyint(1) NOT NULL DEFAULT 1,
  PRIMARY KEY (`id`)
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_unicode_520_ci;


-- scribe.codes definition

CREATE TABLE `codes` (
  `id` int(11) NOT NULL AUTO_INCREMENT,
  `user_ID` int(11) NOT NULL,
  `code_hash` varchar(256) NOT NULL,
  `code_expiry` datetime NOT NULL,
  PRIMARY KEY (`id`),
  KEY `user_ID` (`user_ID`),
  CONSTRAINT `codes_ibfk_1` FOREIGN KEY (`user_ID`) REFERENCES `user` (`id`)
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_unicode_520_ci;


-- scribe.project definition

CREATE TABLE `project` (
  `id` int(11) NOT NULL AUTO_INCREMENT,
  `name` varchar(64) NOT NULL,
  `video_id` int(11) DEFAULT NULL,
  `transcript_id` int(11) DEFAULT NULL,
  `aitranscript_id` int(11) DEFAULT NULL,
  `aisummary_id` int(11) DEFAULT NULL,
  `aiaudio_id` int(11) DEFAULT NULL,
  `aivideo_id` int(11) DEFAULT NULL,
  PRIMARY KEY (`id`),
  KEY `video_id` (`video_id`),
  KEY `transcript_id` (`transcript_id`),
  KEY `notes_id` (`aitranscript_id`),
  KEY `audio_id` (`aisummary_id`),
  KEY `highlights_id` (`aiaudio_id`),
  KEY `project_media_FK` (`aivideo_id`),
  CONSTRAINT `project_ibfk_1` FOREIGN KEY (`video_id`) REFERENCES `user` (`id`),
  CONSTRAINT `project_ibfk_2` FOREIGN KEY (`transcript_id`) REFERENCES `user` (`id`),
  CONSTRAINT `project_ibfk_3` FOREIGN KEY (`aitranscript_id`) REFERENCES `user` (`id`),
  CONSTRAINT `project_ibfk_4` FOREIGN KEY (`aisummary_id`) REFERENCES `user` (`id`),
  CONSTRAINT `project_ibfk_5` FOREIGN KEY (`aiaudio_id`) REFERENCES `user` (`id`),
  CONSTRAINT `project_media_FK` FOREIGN KEY (`aivideo_id`) REFERENCES `media` (`id`)
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_unicode_520_ci;