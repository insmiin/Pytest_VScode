WITH mem_gbruleid_list AS (
    SELECT m.memberid, m.companyid, msp.gbruleid, msp.id
    FROM members m
    INNER JOIN memberscoreprofiles msp ON m.memberid = msp.memberid  -- should only return 1 record
    where lower(m.membercode) = lower(%(memberCode)s) and m.companyID = %(companyID)s and msp.gbruleid = %(use_ruleID_to_update)s
)
UPDATE mem_gbruleid_list mgl
INNER JOIN memberscoreprofiles msp ON msp.id = mgl.id and msp.gbruleid = mgl.gbruleid and msp.memberid = mgl.memberid
INNER JOIN memberscoreprofileactions mspa ON msp.id = mspa.memberScoreProfileID
SET
    mspa.updatedAt = %(date_to_change_UTC)s,
    mspa.laUpdatedAt = CASE  -- if updateAt is expired, it also makes sense for lastAction to expire
        WHEN mspa.laUpdatedAt IS NOT NULL THEN %(date_to_change_UTC)s
        ELSE mspa.laUpdatedAt
    END