WITH mem_toUpd_BD AS (
    SELECT DISTINCT m.memberid
    FROM members m
    INNER JOIN membersportsettings mbd ON m.memberid = mbd.memberid
    where lower(m.membercode) = lower(%(memberCode)s) and m.companyID = %(companyID)s
)
UPDATE membersportsettings mbd
INNER JOIN mem_toUpd_BD m ON mbd.memberid = m.memberid
SET mbd.gbmemberbetdelay = NULL,
    mbd.updatedAt = %(date_to_change_UTC)s


/* OLDDDDDDDDD
with mem_toUpd_BD as
(
select distinct m.memberid,m.companyid FROM members m
inner join membersportsettings mbd on m.memberid = mbd.memberid
where lower(m.membercode) = lower(%(memberCode)s) and m.companyID = %(companyID)s
)
update  membersportsettings mbd, mem_toUpd_BD m
set mbd.gbmemberbetdelay = 0,
    mbd.updatedAt = %(date_to_change_UTC)s
where mbd.memberid = m.memberid
*/