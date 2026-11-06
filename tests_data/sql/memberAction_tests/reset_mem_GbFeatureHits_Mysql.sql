-- BLOCK 1: Update Groups and Actions
WITH mem_pgModuleid_list AS (
    SELECT m.memberid, mpg.moduleID, mpg.id
    FROM members m
    INNER JOIN memberprofilegroups mpg ON m.memberid = mpg.memberid
    where lower(m.membercode) = lower(%(memberCode)s) and m.companyID = %(companyID)s
)
UPDATE memberprofilegroups mpg
INNER JOIN mem_pgModuleid_list pgl ON mpg.id = pgl.id and mpg.moduleid=pgl.moduleid
INNER JOIN memberprofilegroupactions mpga ON mpg.id = mpga.memberProfileGroupID
SET mpg.updatedAt = %(date_to_change_UTC)s,
    mpga.updatedAt = %(date_to_change_UTC)s

