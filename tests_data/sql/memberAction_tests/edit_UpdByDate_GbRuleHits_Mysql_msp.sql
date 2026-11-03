WITH mem_gbruleid_list AS (
    SELECT m.memberid, m.companyid, msp.gbruleid, msp.id
    FROM members m
    INNER JOIN memberscoreprofiles msp ON m.memberid = msp.memberid  -- should only return 1 record
    where lower(m.membercode) = lower(%(memberCode)s) and m.companyID = %(companyID)s and msp.gbruleid = %(use_ruleID_to_update)s
)
UPDATE  memberscores ms
INNER JOIN mem_gbruleid_list mgl ON ms.memberid = mgl.memberid AND ms.gbruleid = mgl.gbruleid
INNER JOIN memberscoreprofiles msp ON msp.id = mgl.id AND msp.gbruleid = ms.gbruleid
SET
    ms.updatedAt = %(date_to_change_UTC)s,
    msp.updatedAt = %(date_to_change_UTC)s,
    msp.laUpdatedAt = CASE  -- if updateAt is expired, it also makes sense for lastAction to expire
        WHEN msp.laUpdatedAt IS NOT NULL THEN @date_to_change_UTC
        ELSE msp.laUpdatedAt
    END


/* OLDDDD
WITH mem_gbruleid_list AS (
    SELECT m.memberid, m.companyid, msp.gbruleid, msp.id
    FROM members m
    INNER JOIN memberscoreprofiles msp ON m.memberid = msp.memberid
    where lower(m.membercode) = lower(%(memberCode)s) and m.companyID = %(companyID)s and msp.gbruleid = %(use_ruleID_to_update)s
)
UPDATE memberscores ms
INNER JOIN mem_gbruleid_list mgl ON ms.memberid = mgl.memberid AND ms.gbruleid = mgl.gbruleid
INNER JOIN memberscoreprofiles msp ON msp.id = mgl.id and msp.gbruleid = ms.gbruleid
INNER JOIN memberscoreprofileactions mspa ON msp.id = mspa.memberScoreProfileID
SET
    ms.updatedAt = %(date_to_change_UTC)s,
    msp.updatedAt = %(date_to_change_UTC)s,
    msp.laUpdatedAt = CASE
        WHEN msp.laUpdatedAt IS NOT NULL THEN %(date_to_change_UTC)s
        ELSE msp.laUpdatedAt
    END,
    mspa.updatedAt = %(date_to_change_UTC)s,
    mspa.laUpdatedAt = CASE
        WHEN mspa.laUpdatedAt IS NOT NULL THEN %(date_to_change_UTC)s
        ELSE mspa.laUpdatedAt
    END
*/

/* OLDDDDDDD
with mem_gbruleid_list as
(
select m.memberid,m.companyid, gbruleid ,msp.id FROM members m
inner join memberscoreprofiles msp on m.memberid = msp.memberid   -- should only return 1 record
where lower(m.membercode) = lower(%(memberCode)s) and m.companyID = %(companyID)s and msp.gbruleid = %(use_ruleID_to_update)s
)
update
 memberscores ms, memberscoreprofiles msp, memberscoreprofileactions mspa ,mem_gbruleid_list mgl
 SET ms.updatedAt = %(date_to_change_UTC)s,    --
    msp.updatedAt = %(date_to_change_UTC)s,
    msp.laUpdatedAt = CASE                  -- if updateAt is expired, it also makes sense for lastAction to expire
        WHEN msp.laUpdatedAt IS NOT NULL
        THEN %(date_to_change_UTC)s
        ELSE msp.laUpdatedAt
    END,
	mspa.updatedAt = %(date_to_change_UTC)s,
    mspa.laUpdatedAt = CASE                  -- if updateAt is expired, it also makes sense for lastAction to expire
        WHEN msp.laUpdatedAt IS NOT NULL
        THEN %(date_to_change_UTC)s
        ELSE msp.laUpdatedAt
    END
WHERE
    mgl.memberid = ms.memberid
    and ms.memberid = msp.memberid and ms.gbruleid=msp.gbruleid
    and msp.id = mspa.memberScoreProfileID
    AND msp.gbruleid in (mgl.gbruleid)

*/