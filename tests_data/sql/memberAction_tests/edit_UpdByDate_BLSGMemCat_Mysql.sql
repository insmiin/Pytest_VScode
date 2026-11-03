WITH affected_member AS (
    SELECT DISTINCT m.memberid
    FROM members m
    INNER JOIN memberextrainfos mei ON m.memberid = mei.memberid
    where lower(m.membercode) = lower(%(memberCode)s) and m.companyID = %(companyID)s
)
UPDATE memberextrainfos mei
INNER JOIN affected_member am ON mei.memberid = am.memberid
SET mei.sfMemberProfileSettingUpdatedDate = %(date_to_change_UTC)s,
    mei.sfSpreadGroupUpdatedDate = %(date_to_change_UTC)s,
    mei.sfMemberCategoryUpdatedDate = %(date_to_change_UTC)s


/* OLDDDDDDDDD
with affected_member as
(select distinct m.memberid
FROM members m
inner join memberextrainfos mei on m.memberid = mei.memberid
where lower(m.membercode) = lower(%(memberCode)s) and m.companyID = %(companyID)s
)
update memberextrainfos mei, affected_member am
    SET mei.sfMemberProfileSettingUpdatedDate = %(date_to_change_UTC)s,
    mei.sfSpreadGroupUpdatedDate = %(date_to_change_UTC)s,
    mei.sfMemberCategoryUpdatedDate = %(date_to_change_UTC)s
    where mei.memberid = am.memberid
    */