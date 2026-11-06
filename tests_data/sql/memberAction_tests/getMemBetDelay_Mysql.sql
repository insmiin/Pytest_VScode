SELECT * FROM EXTERNAL_QUERY("ghostbuster-dev.asia-east1.GB_MySQL", 
"""
 SELECT m.membercode,m.companyid,mss.sportid,mss.gbMemberBetDelay,mss.updatedBy,mss.updatedAt,
 mss.gbBetDelayByUser,mss.gbBetDelayByUserUpdatedDate,mss.revisedGBBetDelay,mss.revisedGBBetDelayUpdatedDate
 FROM GB_Qat.membersportsettings mss
inner join members m on m.memberid = mss.memberid
where m.membercode = lower(@memberCode) and m.companyid = @companyID
""")