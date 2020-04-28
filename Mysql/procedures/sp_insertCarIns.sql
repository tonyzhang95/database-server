DELIMITER $$
CREATE DEFINER=`root`@`localhost` PROCEDURE `sp_insertCarIns`(in p_insstartdate varchar(20), in p_insenddate varchar(20),
						in p_inspremium decimal(10,2), in p_vin varchar(20), in p_vmake varchar(30), in p_vmodel varchar(30),
                        in p_vyear int, in p_vstatus char(1), in p_licenseno varchar(10), in p_driverfirstname varchar(30),
                        in p_driverlastname varchar(30), in p_driverbirthdate varchar(20), in p_user_name varchar(45))
BEGIN
	set @temp_cid := (select c.cid from WDS.user u join WDS.customer c on u.user_id=c.user_id
					where u.user_username = p_user_name);
	insert into insurance(insstartdate, insenddate, inspremium, cid)
		values (p_insstartdate, p_insenddate, p_inspremium, @temp_cid);

    set @temp_ins_id := (select m.insid from (select i.insid from insurance i where i.insid not in (select insid from auto_ins)) m where m.insid not in (select insid from home_ins));
	insert into auto_ins(insid, vin, vmake, vmodel, vyear, vstatus, licenseno, driverfirstname, driverlastname, driverbirthdate)
		values (@temp_ins_id, p_vin, p_vmake, p_vmodel, p_vyear, p_vstatus, p_licenseno, p_driverfirstname, p_driverlastname,
        p_driverbirthdate);
END$$
DELIMITER ;