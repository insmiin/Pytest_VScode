select m.membercode,m.memberid,m.companyid,m.sfMemberCategoryID,m.sfisAdvised,m.isManualRevised,mex.revisedValueUpdatedDate,mex.sfMemberCategoryLastUpdatedBy,mex.sfMemberCategoryUpdatedDate,
'||',mcs.suggestedCreditScore,mcs.isManualRevised isManualRevised_CS,mcs.appliedCreditScore,
'||',m.defaultSfMemberSettingProfileID,m.sfMemberSettingProfileID,mex.sfMemberProfileSettingLastUpdatedID mexsfMemberProfileSettingLastUpdatedID, mex.sfMemberProfileSettingUpdatedDate,mex.sfMemberProfileSettingLastUpdatedBy,mex.sfMemberProfileSettingIDUpdatedByUser,mex.sfMemberProfileSettingUpdatedDateByUser,
mex.sfMemberProfileSettingIDUpdatedByMerchant,mex.sfMemberProfileSettingUpdatedDateByMerchant,mex.revisedMemberProfileSettingID,
'||', m.defaultSfSpreadGroupID,m.sfSpreadGroupID,mex.sfSpreadGroupLastUpdatedID mexsfSpreadGroupLastUpdatedID,mex.sfSpreadGroupUpdatedDate,mex.sfSpreadGroupLastUpdatedBy,mex.sfSpreadGroupIDUpdatedByUser,mex.sfSpreadGroupUpdatedDateByUser,
mex.sfSpreadGroupIDUpdatedByMerchant, mex.sfSpreadGroupUpdatedDateByMerchant,mex.revisedSpreadGroupID
FROM GB_Qat.memberextrainfos mex inner join members m on mex.memberid = m.memberid
left join membercreditscores mcs on m.memberid=mcs.memberid
where lower(m.membercode) = lower(%(memberCode)s) and m.companyID = %(companyID)s

/* OLD
select m.membercode,m.memberid,m.companyid,m.sfMemberCategoryID,m.sfisAdvised,m.isManualRevised,mex.revisedValueUpdatedDate,mex.sfMemberCategoryLastUpdatedBy,mex.sfMemberCategoryUpdatedDate,
DATE_SUB(mex.sfMemberCategoryUpdatedDate, INTERVAL 4 HOUR) >= DATE_FORMAT(DATE_SUB(DATE_SUB(current_timestamp(), INTERVAL 4 HOUR), INTERVAL 3 MONTH), '%Y-%m-01 00:00:00') memCat_withinValidityPeriod,
'||',mcs.suggestedCreditScore,mcs.isManualRevised isManualRevised_CS,mcs.appliedCreditScore,
'||',m.defaultSfMemberSettingProfileID,m.sfMemberSettingProfileID,mex.sfMemberProfileSettingLastUpdatedID mexsfMemberProfileSettingLastUpdatedID, mex.sfMemberProfileSettingUpdatedDate,mex.sfMemberProfileSettingLastUpdatedBy,mex.sfMemberProfileSettingIDUpdatedByUser,mex.sfMemberProfileSettingUpdatedDateByUser,
mex.sfMemberProfileSettingIDUpdatedByMerchant,mex.sfMemberProfileSettingUpdatedDateByMerchant,mex.revisedMemberProfileSettingID,
DATE_SUB(mex.sfMemberProfileSettingUpdatedDate, INTERVAL 4 HOUR) >= DATE_FORMAT(DATE_SUB(DATE_SUB(current_timestamp(), INTERVAL 4 HOUR), INTERVAL 3 MONTH), '%Y-%m-01 00:00:00') msp_withinValidityPeriod,
'||', m.defaultSfSpreadGroupID,m.sfSpreadGroupID,mex.sfSpreadGroupLastUpdatedID mexsfSpreadGroupLastUpdatedID,mex.sfSpreadGroupUpdatedDate,mex.sfSpreadGroupLastUpdatedBy,mex.sfSpreadGroupIDUpdatedByUser,mex.sfSpreadGroupUpdatedDateByUser,
mex.sfSpreadGroupIDUpdatedByMerchant, mex.sfSpreadGroupUpdatedDateByMerchant,mex.revisedSpreadGroupID,
DATE_SUB(mex.sfSpreadGroupUpdatedDate, INTERVAL 4 HOUR) >= DATE_FORMAT(DATE_SUB(DATE_SUB(current_timestamp(), INTERVAL 4 HOUR), INTERVAL 3 MONTH), '%Y-%m-01 00:00:00') spread_withinValidityPeriod
FROM GB_Qat.memberextrainfos mex inner join members m on mex.memberid = m.memberid
left join membercreditscores mcs on m.memberid=mcs.memberid
where lower(m.membercode) = lower(%(memberCode)s) and m.companyID = %(companyID)s
*/
/* OLD
select m.membercode,m.memberid,m.companyid,m.sfMemberCategoryID,m.sfisAdvised,m.isManualRevised,mex.revisedValueUpdatedDate,mex.sfMemberCategoryLastUpdatedBy,mex.sfMemberCategoryUpdatedDate,
DATE_SUB(mex.sfMemberCategoryUpdatedDate, INTERVAL 4 HOUR) >= DATE_FORMAT(DATE_SUB(DATE_SUB(current_timestamp(), INTERVAL 4 HOUR), INTERVAL 3 MONTH), '%Y-%m-01 00:00:00') memCat_withinValidityPeriod,
'||',m.defaultSfMemberSettingProfileID,m.sfMemberSettingProfileID,mex.sfMemberProfileSettingLastUpdatedID mexsfMemberProfileSettingLastUpdatedID, mex.sfMemberProfileSettingUpdatedDate,mex.sfMemberProfileSettingLastUpdatedBy,mex.sfMemberProfileSettingIDUpdatedByUser,mex.sfMemberProfileSettingUpdatedDateByUser,
mex.sfMemberProfileSettingIDUpdatedByMerchant,mex.sfMemberProfileSettingUpdatedDateByMerchant,mex.revisedMemberProfileSettingID,
DATE_SUB(mex.sfMemberProfileSettingUpdatedDate, INTERVAL 4 HOUR) >= DATE_FORMAT(DATE_SUB(DATE_SUB(current_timestamp(), INTERVAL 4 HOUR), INTERVAL 3 MONTH), '%Y-%m-01 00:00:00') msp_withinValidityPeriod,
'||', m.defaultSfSpreadGroupID,m.sfSpreadGroupID,mex.sfSpreadGroupLastUpdatedID mexsfSpreadGroupLastUpdatedID,mex.sfSpreadGroupUpdatedDate,mex.sfSpreadGroupLastUpdatedBy,mex.sfSpreadGroupIDUpdatedByUser,mex.sfSpreadGroupUpdatedDateByUser,
mex.sfSpreadGroupIDUpdatedByMerchant, mex.sfSpreadGroupUpdatedDateByMerchant,mex.revisedSpreadGroupID,
DATE_SUB(mex.sfSpreadGroupUpdatedDate, INTERVAL 4 HOUR) >= DATE_FORMAT(DATE_SUB(DATE_SUB(current_timestamp(), INTERVAL 4 HOUR), INTERVAL 3 MONTH), '%Y-%m-01 00:00:00') spread_withinValidityPeriod
FROM GB_Qat.memberextrainfos mex inner join members m on mex.memberid = m.memberid
where lower(m.membercode) = lower(%(memberCode)s) and m.companyID = %(companyID)s
*/
