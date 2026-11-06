with getMemberid as (
select memberid,membercode,companyid from members
where lower(membercode) = lower(%(memberCode)s) and companyID = %(companyID)s
)
,MemHitGbRules as (
select m.membercode,m.companyid,ms.memberid,ms.batchID as scr_batchID ,ms.gbRuleID as scr_gbRuleID,gbRuleName as src_gbruleName,' ' as prof_moduleID,' ' as prof_featureName,actionStatusID,eAct.displayName as displayName,
msp.createdAt,msp.createdBy,msp.updatedAt,DATE_SUB(msp.updatedAt, INTERVAL 4 HOUR) updatedAt_GMTMinus4,msp.updatedby,ms.gbRuleBandID as scr_gbRuleBandID,scoreProfileID as scr_scoreProfileID, ' ' as prof_profileGroupID,
msp.score latest_score,msp.lascore lastWfActn_score, msp.laUpdatedAt lastWfActn_updatedAt,
case when -- use ms.updateAt to filter GBrule & egon validityperiod
         (
			(ms.gbRuleID =11 and DATE_SUB(ms.updatedAt, INTERVAL 4 HOUR) >= DATE_SUB(DATE_SUB(current_timestamp(), INTERVAL 4 HOUR), INTERVAL 24 HOUR) )  -- tally with PP_EgonValidityPeriod
				or
			(ms.gbRuleID !=11 and DATE_SUB(ms.updatedAt, INTERVAL 4 HOUR) >= DATE_SUB(DATE_SUB(current_timestamp(), INTERVAL 4 HOUR), INTERVAL 24 HOUR)  )  -- tally with PP_RuleValidityPeriod
         )
     and (
           (actionStatusID Not in ({action_disallowed}))
             or
		   (actionstatusID = 100 and
				(
					(ms.gbRuleID =11 and DATE_SUB(msp.laUpdatedAt, INTERVAL 4 HOUR) >= DATE_SUB(DATE_SUB(current_timestamp(), INTERVAL 4 HOUR), INTERVAL 24 HOUR)  )  -- tally with PP_EgonValidityPeriod
						or
					(ms.gbRuleID !=11 and DATE_SUB(msp.laUpdatedAt, INTERVAL 4 HOUR) >= DATE_SUB(DATE_SUB(current_timestamp(), INTERVAL 4 HOUR), INTERVAL 24 HOUR)  ) -- tally with PP_RuleValidityPeriod
                )
			)
		 )
     then 'true' else 'false' end as has_action_to_verify
from memberscores ms inner join getMemberid m on ms.memberid=m.memberid
inner join memberscoreprofiles msp  on ms.memberid = msp.memberid and  ms.gbruleid=msp.gbruleid -- (Uniq key)
left join GB_Qat.gbrules gr on ms.gbruleid = gr.id
left join  displaynameenum eAct on msp.actionStatusID = eAct.enumID and eAct.enumName = 'GBActionStatusEnum'
-- include only hits that are within validity period  AND Include hits except status 95, 96, 98, 99, and 100 —but allow status 100 if the updatedate of lasthitWithAction is within validityPeriod
where
    (
		(ms.gbRuleID =11 and DATE_SUB(ms.updatedAt, INTERVAL 4 HOUR) >= DATE_SUB(DATE_SUB(current_timestamp(), INTERVAL 4 HOUR), INTERVAL 24 HOUR) ) -- tally with PP_EgonValidityPeriod
				or
		(ms.gbRuleID !=11 and DATE_SUB(ms.updatedAt, INTERVAL 4 HOUR) >= DATE_SUB(DATE_SUB(current_timestamp(), INTERVAL 4 HOUR), INTERVAL 24 HOUR)  ) -- tally with PP_RuleValidityPeriod
	)
and (
      (actionStatusID Not in ({actionID_to_filter}))
       or
      (actionstatusID = 100 and
				(
					(ms.gbRuleID =11 and DATE_SUB(msp.laUpdatedAt, INTERVAL 4 HOUR) >= DATE_SUB(DATE_SUB(current_timestamp(), INTERVAL 4 HOUR), INTERVAL 24 HOUR) ) -- tally with PP_EgonValidityPeriod
						or
					(ms.gbRuleID !=11 and DATE_SUB(msp.laUpdatedAt, INTERVAL 4 HOUR) >= DATE_SUB(DATE_SUB(current_timestamp(), INTERVAL 4 HOUR), INTERVAL 24 HOUR) ) -- tally with PP_RuleValidityPeriod
                )
	  )
	)
)
,MemHitGbFeatures as (
select m.membercode,m.companyid,mpg.memberid,' ' as scr_batchID ,' ' as scr_gbRuleID,' ' as src_gbruleName,moduleID as prof_moduleID,emod.name as prof_featureName,actionStatusID,eAct.displayName as displayName,
 mpg.createdAt,mpg.createdBy,mpg.updatedAt,DATE_SUB(mpg.updatedAt, INTERVAL 4 HOUR) updatedAt_GMTMinus4,mpg.updatedby,' ' as scr_gbRuleBandID,' ' as scr_scoreProfileID, ' ' as prof_profileGroupID,
 ' ' as latest_score, ' ' as lastWfActn_score, ' ' as lastWfActn_updatedAt,
case when DATE_SUB(mpg.updatedAt, INTERVAL 4 HOUR) >= DATE_FORMAT(DATE_SUB(DATE_SUB(current_timestamp(), INTERVAL 4 HOUR), INTERVAL 3 MONTH), '%Y-%m-01 00:00:00') -- mz tally with PP_FeatureValidityPeriod
     and actionStatusID Not in ({action_disallowed})
     then 'true' else 'false' end as has_action_to_verify
from memberprofilegroups mpg inner join getMemberid m on mpg.memberid=m.memberid
left join  displaynameenum emod on mpg.moduleid = emod.enumID and emod.enumName = 'GBFeatureModuleEnum'
left join  displaynameenum eAct on mpg.actionStatusID = eAct.enumID and eAct.enumName = 'GBActionStatusEnum'
where DATE_SUB(mpg.updatedAt, INTERVAL 4 HOUR) >= DATE_FORMAT(DATE_SUB(DATE_SUB(current_timestamp(), INTERVAL 4 HOUR), INTERVAL 3 MONTH), '%Y-%m-01 00:00:00') -- mz tally with PP_FeatureValidityPeriod
and actionStatusID Not in ({actionID_to_filter}) -- GBfeature has no 100 anyway
)
,MemHitGbRulesActions as (
SELECT   ' ' gbmoduleid, msp.gbruleid,  -- gbmoduleid=prof_moduleID, gbruleid = src_gbRuleID
max(case when actionName = 'ScoreType' then actionValue end ) as latest_ScoreType,
max(case when actionName = 'UpdateMemberBetDelay' then actionValue end)  as latest_BetDelay,
max(case when actionName = 'UpdateMemberProfile' then actionValue end ) as latest_MemberProfile,
max(case when actionName = 'UpdateMemberSpreadGroup' then actionValue end)  as latest_SpreadGroup,
max(case when actionName = 'UpdateMemberCategory' then actionValue end)  as latest_MemberCategory,
max(case when actionName = 'UpdateMemberIsAdvised' then actionValue end)  as latest_IsAdvised,
max(case when actionName = 'UpdateMemberBetDelay' then ActionValue2 end) as latest_BDSportGroups,   -- @@change ActionValue2
max(case when actionName = 'UpdateNotifyMerchant' then actionValue end)  as latest_NotifyMerchant,
'||' as split1,
max(case when actionName = 'ScoreType' then laactionValue end ) as lastWfActn_ScoreType,
max(case when actionName = 'UpdateMemberBetDelay' then laactionValue end)  as lastWfActn_BetDelay,
max(case when actionName = 'UpdateMemberProfile' then laactionValue end ) as lastWfActn_MemberProfile,
max(case when actionName = 'UpdateMemberSpreadGroup' then laactionValue end)  as lastWfActn_SpreadGroup,
max(case when actionName = 'UpdateMemberCategory' then laactionValue end)  as lastWfActn_MemberCategory,
max(case when actionName = 'UpdateMemberIsAdvised' then laactionValue end)  as lastWfActn_IsAdvised,
max(case when actionName = 'UpdateMemberBetDelay' then laActionValue2 end) as lastWfActn_BDSportGroups,   -- @@change  laActionValue2
max(case when actionName = 'UpdateNotifyMerchant' then laactionValue end)  as lastWfActn_NotifyMerchant
from memberscoreprofiles msp
inner join memberscoreprofileactions msa on  msp.id = msa.memberScoreProfileID
inner join getMemberid m on msp.memberid=m.memberid
group by   msp.gbruleid
)
,MemHitGbFeaturesActions as(
SELECT   mpg.moduleID , ' 'gbruleid,   -- gbmoduleid=prof_moduleID, gbruleid = src_gbRuleID
max(case when actionName = 'ScoreType' then ' ' end ) as latest_ScoreType,
max(case when actionName = 'UpdateMemberBetDelay' then actionValue end)  as latest_BetDelay,
max(case when actionName = 'UpdateMemberProfile' then actionValue end ) as latest_MemberProfile,
max(case when actionName = 'UpdateMemberSpreadGroup' then actionValue end)  as latest_SpreadGroup,
max(case when actionName = 'UpdateMemberCategory' then actionValue end)  as latest_MemberCategory,
max(case when actionName = 'UpdateMemberIsAdvised' then actionValue end)  as latest_IsAdvised,
max(case when actionName = 'UpdateMemberBetDelay' then ActionValue2 end) as latest_BDSportGroups,   -- @@change ActionValue2
max(case when actionName = 'UpdateNotifyMerchant' then actionValue end)  as latest_NotifyMerchant,
'||' as split1,
' ' as lastWfActn_ScoreType,
' ' as lastWfActn_BetDelay,
' ' as lastWfActn_MemberProfile,
' ' as lastWfActn_SpreadGroup,
' '  as lastWfActn_MemberCategory,
' '  as lastWfActn_IsAdvised,
' ' as lastWfActn_BDSportGroups,   -- @change done
' ' as lastWfActn_NotifyMerchant
from memberprofilegroups mpg
inner join memberprofilegroupactions mpga on mpg.id = mpga.memberProfileGroupID
inner join getMemberid m on mpg.memberid=m.memberid
group by  mpg.moduleID
)
-- ,MemHitModules as (
select * from
(
select gr.*,gra.*,'||' as split2,
case when gr.actionStatusID = 100 and gr.lastWfActn_score <= gr.latest_score then gr.lastWfActn_score else gr.latest_score end as score, -- makesure null work properly with operator <=
case when gr.actionStatusID = 100 and gr.lastWfActn_score <= gr.latest_score then gra.lastWfActn_ScoreType else gra.latest_ScoreType end as ScoreType,
case when gr.actionStatusID = 100 and gr.lastWfActn_score <= gr.latest_score then gra.lastWfActn_BetDelay else gra.latest_BetDelay end as UpdateMemberBetDelay,
case when gr.actionStatusID = 100 and gr.lastWfActn_score <= gr.latest_score then gra.lastWfActn_MemberProfile else gra.latest_MemberProfile end as UpdateMemberProfile,
case when gr.actionStatusID = 100 and gr.lastWfActn_score <= gr.latest_score then gra.lastWfActn_SpreadGroup else gra.latest_SpreadGroup end as UpdateMemberSpreadGroup,
case when gr.actionStatusID = 100 and gr.lastWfActn_score <= gr.latest_score then gra.lastWfActn_MemberCategory else gra.latest_MemberCategory end as UpdateMemberCategory,
case when gr.actionStatusID = 100 and gr.lastWfActn_score <= gr.latest_score then gra.lastWfActn_IsAdvised else gra.latest_IsAdvised end as UpdateMemberIsAdvised,
case when gr.actionStatusID = 100 and gr.lastWfActn_score <= gr.latest_score then gra.lastWfActn_BDSportGroups else gra.latest_BDSportGroups end as UpdateBDSportGroups,  -- @@change
gra.latest_NotifyMerchant  as UpdateNotifyMerchant  -- notifyMerchant still using latesthit value
 from MemHitGbRules gr inner join MemHitGbRulesActions gra on  gr.scr_gbRuleID=gra.gbruleid
union all
select gf.*,gfa.*,'||',
' ' as score,
latest_ScoreType as ScoreType,   -- gbfeature always use latest hitAction. no special handiling for 'noActionConditionMet' which only apply for score band
latest_BetDelay as UpdateMemberBetDelay,
latest_MemberProfile as UpdateMemberProfile,
latest_SpreadGroup as UpdateMemberSpreadGroup,
latest_MemberCategory as UpdateMemberCategory,
latest_IsAdvised as UpdateMemberIsAdvised,
latest_BDSportGroups as UpdateBDSportGroups,  -- @@change
latest_NotifyMerchant as UpdateNotifyMerchant
 from MemHitGbFeatures gf  inner join MemHitGbFeaturesActions gfa on gf.prof_moduleID =gfa.moduleid
) t
where  {filter_statement}






/**** OLD
,MemHitGbRules as (
select m.membercode,m.companyid,ms.memberid,ms.batchID as scr_batchID ,ms.gbRuleID as scr_gbRuleID,gbRuleName as src_gbruleName,' ' as prof_moduleID,' ' as prof_featureName,actionStatusID,eAct.displayName as displayName,
msp.createdAt,msp.createdBy,msp.updatedAt,DATE_SUB(msp.updatedAt, INTERVAL 4 HOUR) updatedAt_GMTMinus4,msp.updatedby,ms.gbRuleBandID as scr_gbRuleBandID,scoreProfileID as scr_scoreProfileID, ' ' as prof_profileGroupID,
msp.score latest_score,msp.lascore lastWfActn_score, msp.laUpdatedAt lastWfActn_updatedAt,
case when DATE_SUB(ms.updatedAt, INTERVAL 4 HOUR) >= DATE_FORMAT(DATE_SUB(DATE_SUB(current_timestamp(), INTERVAL 4 HOUR), INTERVAL 3 MONTH), '%Y-%m-01 00:00:00')
     and (
           (actionStatusID Not in ({action_disallowed}))
             or
		   (actionstatusID = 100 and DATE_SUB(msp.laUpdatedAt, INTERVAL 4 HOUR) >= DATE_FORMAT(DATE_SUB(DATE_SUB(current_timestamp(), INTERVAL 4 HOUR), INTERVAL 3 MONTH), '%Y-%m-01 00:00:00'))
		 )
     then 'true' else 'false' end as has_action_to_verify
from memberscores ms inner join getMemberid m on ms.memberid=m.memberid
inner join memberscoreprofiles msp  on ms.memberid = msp.memberid and  ms.gbruleid=msp.gbruleid -- (Uniq key)
left join GB_Qat.gbrules gr on ms.gbruleid = gr.id
left join  displaynameenum eAct on msp.actionStatusID = eAct.enumID and eAct.enumName = 'GBActionStatusEnum'
-- include only hits that are within validity period  AND Include hits except status 95, 96, 98, 99, and 100 —but allow status 100 if the updatedate of lasthitWithAction is within validityPeriod
where DATE_SUB(ms.updatedAt, INTERVAL 4 HOUR) >= DATE_FORMAT(DATE_SUB(DATE_SUB(current_timestamp(), INTERVAL 4 HOUR), INTERVAL 3 MONTH), '%Y-%m-01 00:00:00')
and (
      (actionStatusID Not in ({actionID_to_filter}))
       or
      (actionstatusID = 100 and DATE_SUB(msp.laUpdatedAt, INTERVAL 4 HOUR) >= DATE_FORMAT(DATE_SUB(DATE_SUB(current_timestamp(), INTERVAL 4 HOUR), INTERVAL 3 MONTH), '%Y-%m-01 00:00:00'))
	)
)
,MemHitGbFeatures as (
select m.membercode,m.companyid,mpg.memberid,' ' as scr_batchID ,' ' as scr_gbRuleID,' ' as src_gbruleName,moduleID as prof_moduleID,emod.name as prof_featureName,actionStatusID,eAct.displayName as displayName,
 mpg.createdAt,mpg.createdBy,mpg.updatedAt,DATE_SUB(mpg.updatedAt, INTERVAL 4 HOUR) updatedAt_GMTMinus4,mpg.updatedby,' ' as scr_gbRuleBandID,' ' as scr_scoreProfileID, ' ' as prof_profileGroupID,
 ' ' as latest_score, ' ' as lastWfActn_score, ' ' as lastWfActn_updatedAt,
case when DATE_SUB(mpg.updatedAt, INTERVAL 4 HOUR) >= DATE_FORMAT(DATE_SUB(DATE_SUB(current_timestamp(), INTERVAL 4 HOUR), INTERVAL 3 MONTH), '%Y-%m-01 00:00:00')
     and actionStatusID Not in ({action_disallowed})
     then 'true' else 'false' end as has_action_to_verify
from memberprofilegroups mpg inner join getMemberid m on mpg.memberid=m.memberid
left join  displaynameenum emod on mpg.moduleid = emod.enumID and emod.enumName = 'GBFeatureModuleEnum'
left join  displaynameenum eAct on mpg.actionStatusID = eAct.enumID and eAct.enumName = 'GBActionStatusEnum'
where DATE_SUB(mpg.updatedAt, INTERVAL 4 HOUR) >= DATE_FORMAT(DATE_SUB(DATE_SUB(current_timestamp(), INTERVAL 4 HOUR), INTERVAL 3 MONTH), '%Y-%m-01 00:00:00')
and actionStatusID Not in ({actionID_to_filter}) -- GBfeature has no 100 anyway
)
,MemHitGbRulesActions as (
SELECT   ' ' gbmoduleid, msp.gbruleid,  -- gbmoduleid=prof_moduleID, gbruleid = src_gbRuleID
max(case when actionName = 'ScoreType' then actionValue end ) as latest_ScoreType,
max(case when actionName = 'UpdateMemberBetDelay' then actionValue end)  as latest_BetDelay,
max(case when actionName = 'UpdateMemberProfile' then actionValue end ) as latest_MemberProfile,
max(case when actionName = 'UpdateMemberSpreadGroup' then actionValue end)  as latest_SpreadGroup,
max(case when actionName = 'UpdateMemberCategory' then actionValue end)  as latest_MemberCategory,
max(case when actionName = 'UpdateMemberIsAdvised' then actionValue end)  as latest_IsAdvised,
max(case when actionName = 'UpdateMemberBetDelay' then ActionValue2 end) as latest_BDSportGroups,
max(case when actionName = 'UpdateNotifyMerchant' then actionValue end)  as latest_NotifyMerchant,
'||' as split1,
max(case when actionName = 'ScoreType' then laactionValue end ) as lastWfActn_ScoreType,
max(case when actionName = 'UpdateMemberBetDelay' then laactionValue end)  as lastWfActn_BetDelay,
max(case when actionName = 'UpdateMemberProfile' then laactionValue end ) as lastWfActn_MemberProfile,
max(case when actionName = 'UpdateMemberSpreadGroup' then laactionValue end)  as lastWfActn_SpreadGroup,
max(case when actionName = 'UpdateMemberCategory' then laactionValue end)  as lastWfActn_MemberCategory,
max(case when actionName = 'UpdateMemberIsAdvised' then laactionValue end)  as lastWfActn_IsAdvised,
max(case when actionName = 'UpdateMemberBetDelay' then laActionValue2 end) as lastWfActn_BDSportGroups,
max(case when actionName = 'UpdateNotifyMerchant' then laactionValue end)  as lastWfActn_NotifyMerchant
from memberscoreprofiles msp
inner join memberscoreprofileactions msa on  msp.id = msa.memberScoreProfileID
inner join getMemberid m on msp.memberid=m.memberid
group by   msp.gbruleid
)
,MemHitGbFeaturesActions as(
SELECT   mpg.moduleID , ' 'gbruleid,   -- gbmoduleid=prof_moduleID, gbruleid = src_gbRuleID
max(case when actionName = 'ScoreType' then ' ' end ) as latest_ScoreType,
max(case when actionName = 'UpdateMemberBetDelay' then actionValue end)  as latest_BetDelay,
max(case when actionName = 'UpdateMemberProfile' then actionValue end ) as latest_MemberProfile,
max(case when actionName = 'UpdateMemberSpreadGroup' then actionValue end)  as latest_SpreadGroup,
max(case when actionName = 'UpdateMemberCategory' then actionValue end)  as latest_MemberCategory,
max(case when actionName = 'UpdateMemberIsAdvised' then actionValue end)  as latest_IsAdvised,
max(case when actionName = 'UpdateMemberBetDelay' then ActionValue2 end) as latest_BDSportGroups,
max(case when actionName = 'UpdateNotifyMerchant' then actionValue end)  as latest_NotifyMerchant,
'||' as split1,
' ' as lastWfActn_ScoreType,
' ' as lastWfActn_BetDelay,
' ' as lastWfActn_MemberProfile,
' ' as lastWfActn_SpreadGroup,
' '  as lastWfActn_MemberCategory,
' '  as lastWfActn_IsAdvised,
' ' as lastWfActn_BDSportGroups,   -- @change done
' ' as lastWfActn_NotifyMerchant
from memberprofilegroups mpg
inner join memberprofilegroupactions mpga on mpg.id = mpga.memberProfileGroupID
inner join getMemberid m on mpg.memberid=m.memberid
group by  mpg.moduleID
)
-- ,MemHitModules as (
select * from
(
select gr.*,gra.*,'||' as split2,
case when gr.actionStatusID = 100 and gr.lastWfActn_score <= gr.latest_score then gr.lastWfActn_score else gr.latest_score end as score, -- makesure null work properly with operator <=
case when gr.actionStatusID = 100 and gr.lastWfActn_score <= gr.latest_score then gra.lastWfActn_ScoreType else gra.latest_ScoreType end as ScoreType,
case when gr.actionStatusID = 100 and gr.lastWfActn_score <= gr.latest_score then gra.lastWfActn_BetDelay else gra.latest_BetDelay end as UpdateMemberBetDelay,
case when gr.actionStatusID = 100 and gr.lastWfActn_score <= gr.latest_score then gra.lastWfActn_MemberProfile else gra.latest_MemberProfile end as UpdateMemberProfile,
case when gr.actionStatusID = 100 and gr.lastWfActn_score <= gr.latest_score then gra.lastWfActn_SpreadGroup else gra.latest_SpreadGroup end as UpdateMemberSpreadGroup,
case when gr.actionStatusID = 100 and gr.lastWfActn_score <= gr.latest_score then gra.lastWfActn_MemberCategory else gra.latest_MemberCategory end as UpdateMemberCategory,
case when gr.actionStatusID = 100 and gr.lastWfActn_score <= gr.latest_score then gra.lastWfActn_IsAdvised else gra.latest_IsAdvised end as UpdateMemberIsAdvised,
case when gr.actionStatusID = 100 and gr.lastWfActn_score <= gr.latest_score then gra.lastWfActn_BDSportGroups else gra.latest_BDSportGroups end as UpdateBDSportGroups,
gra.latest_NotifyMerchant  as UpdateNotifyMerchant  -- notifyMerchant still using latesthit value
 from MemHitGbRules gr inner join MemHitGbRulesActions gra on  gr.scr_gbRuleID=gra.gbruleid
union all
select gf.*,gfa.*,'||',
' ' as score,
latest_ScoreType as ScoreType,   -- gbfeature always use latest hitAction. no special handiling for 'noActionConditionMet' which only apply for score band
latest_BetDelay as UpdateMemberBetDelay,
latest_MemberProfile as UpdateMemberProfile,
latest_SpreadGroup as UpdateMemberSpreadGroup,
latest_MemberCategory as UpdateMemberCategory,
latest_IsAdvised as UpdateMemberIsAdvised,
latest_BDSportGroups as UpdateBDSportGroups,
latest_NotifyMerchant as UpdateNotifyMerchant
 from MemHitGbFeatures gf  inner join MemHitGbFeaturesActions gfa on gf.prof_moduleID =gfa.moduleid
) t
where  {filter_statement}

***/