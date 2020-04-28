DELIMITER $$
CREATE DEFINER=`root`@`localhost` PROCEDURE `sp_insertHomeIns`(in p_insstartdate varchar(20), in p_insenddate varchar(20),
						in p_inspremium decimal(10,2), in p_hpurchasedate varchar(20), in p_hvalue decimal(10,2),
                        in p_harea decimal(8,2), in p_htype char(1), in p_hfire char(1), in p_hsecurity char(1),
                        in p_hpool char(1), in p_hbasement char(1), in p_user_name varchar(45))
BEGIN
	set @temp_cid := (select c.cid from WDS.user u join WDS.customer c on u.user_id=c.user_id
					where u.user_username = p_user_name);
	insert into insurance(insstartdate, insenddate, inspremium, cid)
		values (p_insstartdate, p_insenddate, p_inspremium, @temp_cid);

    set @temp_ins_id := (select m.insid from (select i.insid from insurance i where i.insid not in (select insid from auto_ins)) m where m.insid not in (select insid from home_ins));
    insert into home_ins(insid, hpurchasedate, hvalue, harea, htype, hfire, hsecurity, hpool, hbasement)
		values (@temp_ins_id, p_hpurchasedate, p_hvalue, p_harea, p_htype, p_hfire, p_hsecurity,
        p_hpool, p_hbasement);
END$$
DELIMITER ;