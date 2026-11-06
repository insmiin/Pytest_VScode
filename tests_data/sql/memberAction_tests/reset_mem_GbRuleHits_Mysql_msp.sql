WITH mem_gbruleid_list AS (
    SELECT m.memberid, m.companyid, msp.gbruleid, msp.id
    FROM members m
    INNER JOIN memberscoreprofiles msp ON m.memberid = msp.memberid  -- should only return 1 record
    where lower(m.membercode) = lower(%(memberCode)s) and m.companyID = %(companyID)s
)
UPDATE  memberscores ms
INNER JOIN mem_gbruleid_list mgl ON ms.memberid = mgl.memberid AND ms.gbruleid = mgl.gbruleid
INNER JOIN memberscoreprofiles msp ON msp.id = mgl.id AND msp.gbruleid = ms.gbruleid
SET
    ms.updatedAt = %(date_to_change_UTC)s,
    msp.updatedAt = %(date_to_change_UTC)s,
    msp.laUpdatedAt = CASE  -- if updateAt is expired, it also makes sense for lastAction to expire
        WHEN msp.laUpdatedAt IS NOT NULL THEN %(date_to_change_UTC)s
        ELSE msp.laUpdatedAt
    END