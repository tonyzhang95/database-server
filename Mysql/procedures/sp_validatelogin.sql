drop procedure sp_validatelogin;

DELIMITER $$
CREATE DEFINER=`root`@`localhost` PROCEDURE `sp_validatelogin`(
 IN p_username VARCHAR(45)
    )
BEGIN
 SELECT * FROM WDS.user WHERE user_username=p_username;
END$$
DELIMITER ;
