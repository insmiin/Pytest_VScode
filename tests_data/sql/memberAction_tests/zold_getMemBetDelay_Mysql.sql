 SELECT m.membercode,m.companyid,mss.sportid,mss.gbMemberBetDelay,mss.updatedBy,mss.updatedAt
 FROM GB_Qat.membersportsettings mss
inner join members m on m.memberid = mss.memberid
where m.membercode = lower(%(memberCode)s) and m.companyid = %(companyID)s

/*
 SELECT m.membercode,m.companyid,mss.sportid,mss.gbMemberBetDelay,mss.updatedBy,mss.updatedAt,
 DATE_SUB(mss.updatedAt, INTERVAL 4 HOUR) >= DATE_FORMAT(DATE_SUB(DATE_SUB(current_timestamp(), INTERVAL 4 HOUR), INTERVAL 3 MONTH), '%Y-%m-01 00:00:00') Bdelay_withinValidityPeriod
 FROM GB_Qat.membersportsettings mss
inner join members m on m.memberid = mss.memberid
where m.membercode = lower(%(memberCode)s) and m.companyid = %(companyID)s
*/
/*
SELECT m.membercode,m.companyid,mss.sportid,mss.sportTypeID,mss.gbMemberBetDelay FROM GB_Qat.membersportsettings mss
inner join members m on m.memberid = mss.memberid
where m.membercode = lower(%(memberCode)s) and m.companyid = %(companyID)s
-- and mss.updatedby like 'GB_%' and mss.updatedBy not like 'GB_MemberList%';
*/