update  memberextrainfos mex
                                  set
mex.sfMemberProfileSettingIDUpdatedByMerchant = %(mspID)s,
                 mex.sfMemberProfileSettingUpdatedDateByMerchant=%(mspUpdatedDt)s,mex.sfMemberProfileSettingIDUpdatedByMerchant = %(mspID)s,
                 mex.IsSfMemberProfileSettingUpdatedByMerchant = %(IsMSPByMerchant)s,
  mex.IsUpdatedByInternalCompany = %(IsUpdatedByInternalCompany)s where memberid = %(memberID)s