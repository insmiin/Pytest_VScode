WITH mem_toUpd_BD AS (
    SELECT DISTINCT m.memberid, mbd.updatedBy
    FROM members m
    INNER JOIN membersportsettings mbd ON m.memberid = mbd.memberid
    where lower(m.membercode) = lower(%(memberCode)s) and m.companyID = %(companyID)s  and mbd.updatedBy like %(use_ruleUpdByName_to_update_BD)s
)
UPDATE membersportsettings mbd
INNER JOIN mem_toUpd_BD m ON mbd.memberid = m.memberid
                          AND mbd.updatedBy = m.updatedBy
SET mbd.updatedAt = %(date_to_change_UTC)s

/*OLD
with mem_toUpd_BD as
(
select distinct m.memberid,m.companyid,mbd.updatedBy
FROM members m
inner join membersportsettings mbd on m.memberid = mbd.memberid
where lower(m.membercode) = lower(%(memberCode)s) and m.companyID = %(companyID)s  and mbd.updatedBy like %(use_ruleUpdByName_to_update_BD)s
)
update  membersportsettings mbd, mem_toUpd_BD m
set mbd.updatedAt = %(date_to_change_UTC)s
where mbd.memberid = m.memberid and mbd.updatedby = m.updatedby
*/