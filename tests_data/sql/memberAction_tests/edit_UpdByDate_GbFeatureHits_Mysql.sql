-- BLOCK 1: Update Groups and Actions
WITH mem_pgModuleid_list AS (
    SELECT m.memberid, mpg.moduleID, mpg.id
    FROM members m
    INNER JOIN memberprofilegroups mpg ON m.memberid = mpg.memberid
    where lower(m.membercode) = lower(%(memberCode)s) and m.companyID = %(companyID)s and mpg.moduleid = %(use_ruleID_to_update)s -- membercode&coyid is unique,  memberid&moduleID is unique.this should return only 1 rec
)
UPDATE memberprofilegroups mpg
INNER JOIN mem_pgModuleid_list pgl ON mpg.id = pgl.id and mpg.moduleid=pgl.moduleid
INNER JOIN memberprofilegroupactions mpga ON mpg.id = mpga.memberProfileGroupID
SET mpg.updatedAt = %(date_to_change_UTC)s,
    mpga.updatedAt = %(date_to_change_UTC)s


/*
-- i comment out this block to save execution time, as it is just to update the score of issbr on UI,which wont impact the action processing
-- if this block is needed, a new script will need to be created. as my py code can only 1 statement in a script
-- BLOCK 2: Update Features table
WITH mem_pgModuleid_list AS (
    SELECT m.memberid, mpg.moduleID
    FROM members m
    INNER JOIN memberprofilegroups mpg ON m.memberid = mpg.memberid
    where lower(m.membercode) = lower(%(memberCode)s) and m.companyID = %(companyID)s and mpg.moduleid = %(use_ruleID_to_update)s -- membercode&coyid is unique,  memberid&moduleID is unique.this should return only 1 rec
)
UPDATE memberfeatures mf
INNER JOIN mem_pgModuleid_list pgl ON mf.memberid = pgl.memberid AND mf.moduleID = pgl.moduleID
SET mf.updatedAt = %(date_to_change_UTC)s;
*/

/*  OLDDDDDDDDDDDD
with mem_pgModuleid_list as
(
select m.memberid,m.companyid, mpg.moduleID,mpg.id FROM members m
inner join memberprofilegroups mpg on m.memberid = mpg.memberid
where lower(m.membercode) = lower(%(memberCode)s) and m.companyID = %(companyID)s  and mpg.moduleid = %(use_ruleID_to_update)s -- membercode&coyid is unique,  memberid&moduleID is unique.this should return only 1 rec
)
update   --
   memberprofilegroups mpg, memberprofilegroupactions mpga, mem_pgModuleid_list pgl
   SET mpg.updatedAt = %(date_to_change_UTC)s,  --
   mpga.updatedAt = %(date_to_change_UTC)s
WHERE
    pgl.memberid = mpg.memberid
    and mpg.id = mpga.memberProfileGroupID
    AND mpg.moduleID in (pgl.moduleID)
*/