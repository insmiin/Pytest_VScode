select m.membercode,m.memberid,m.companyid,m.sfMemberCategoryID,m.sfisAdvised,m.isManualRevised,mex.revisedValueUpdatedDate,mex.sfMemberCategoryLastUpdatedBy,mex.sfMemberCategoryUpdatedDate,
'||',mcs.suggestedCreditScore,mcs.isManualRevised isManualRevised_CS,mcs.appliedCreditScore,
'||',m.defaultSfMemberSettingProfileID,m.sfMemberSettingProfileID,mex.sfMemberProfileSettingLastUpdatedID mexsfMemberProfileSettingLastUpdatedID, mex.sfMemberProfileSettingUpdatedDate,mex.sfMemberProfileSettingLastUpdatedBy,mex.sfMemberProfileSettingIDUpdatedByUser,mex.sfMemberProfileSettingUpdatedDateByUser,
mex.sfMemberProfileSettingIDUpdatedByMerchant,mex.sfMemberProfileSettingUpdatedDateByMerchant,mex.revisedMemberProfileSettingID,
'||', m.defaultSfSpreadGroupID,m.sfSpreadGroupID,mex.sfSpreadGroupLastUpdatedID mexsfSpreadGroupLastUpdatedID,mex.sfSpreadGroupUpdatedDate,mex.sfSpreadGroupLastUpdatedBy,mex.sfSpreadGroupIDUpdatedByUser,mex.sfSpreadGroupUpdatedDateByUser,
mex.sfSpreadGroupIDUpdatedByMerchant, mex.sfSpreadGroupUpdatedDateByMerchant,mex.revisedSpreadGroupID
FROM GB_Qat.memberextrainfos mex inner join members m on mex.memberid = m.memberid
left join membercreditscores mcs on m.memberid=mcs.memberid
where lower(m.membercode) = lower(%(memberCode)s) and m.companyID = %(companyID)s
