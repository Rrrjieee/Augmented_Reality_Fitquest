INSERT INTO USER_PROFILE (USER_ID, NAME)
VALUES (?, ?)
ON DUPLICATE KEY UPDATE
    NAME = VALUES(column1),