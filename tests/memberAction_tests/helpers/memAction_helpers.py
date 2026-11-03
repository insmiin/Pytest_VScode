
import tests.memberAction_tests.helpers.myHelperFunc as helper
from tests.utils.comparison_utils import is_match, is_LT
from tests.memberAction_tests.mappingModule import SpreadGroupMappers, MemberProfileSettingMappers, GbRuleMapper, GbFeatureMapper
import ast
import logging

logger = logging.getLogger(__name__)


def get_ranking_byID(value, type):
    if type == 'msp':
        rankNum = MemberProfileSettingMappers.get_ranking_by_ID(value)
    else:
        rankNum = SpreadGroupMappers.get_ranking_by_ID(value)
    return rankNum


def get_most_severe(rankNum, smallest_rankNum):
    if smallest_rankNum == None or is_LT(rankNum, smallest_rankNum):
        smallest_rankNum = rankNum
    return smallest_rankNum



def get_most_severe_value_from_all_moduleHits(hitObject, moduleHistory_after_hit, smallest_ranking_number_msp,
                                              smallest_ranking_number_spread, sportGroup_sportIDs_UImap_dict,
                                              betDelay_Severest_dict):
    memCategory_of_directEGON = None
    isAdvised_of_directEGON = None
    BetDelay_of_directEGON = None
    # loop thru each hits(history+current) to determine if need pick up to process or not
    for hitmodule in moduleHistory_after_hit:
        # rank1 is most severe/highest hierarchy.
        # each member can only hit either ML_UI_Level_Robot or ML_UI_Level_Arber in lifetime. do not trigger both in same member. will give unexpected result..
        # if (hitmodule['scr_gbRuleID'] == '7' and new_Hit_Action['prof_moduleID'] == '84') or (hitmodule['prof_moduleID'] == '84' and new_Hit_Action['scr_gbRuleID'] == '7'):
        #    continue

        # if GBBad & EGON good & newHit=EGON, noAction directly
        if (hitObject.cross_GB_Bad and hitObject.cross_EGON_Good and is_match(hitObject.HitID, 11)):
            break

        # if GBBad & EGON good & newHit=NonEGON, skip EGON (to use only GBrule/feature for comparison)
        # if GBGood & hasEGON,skip all non-EGON(gbrule/gbfeature) & process only EGON (EGON's BL,SG,BD straightaway become most severe since only got EGON)
        if (hitObject.cross_GB_Good and hitObject.cross_has_EGON and not is_match(hitmodule['scr_gbRuleID'], 11)) or \
                (hitObject.cross_GB_Bad and hitObject.cross_EGON_Good and is_match(hitmodule['scr_gbRuleID'], 11)):
            continue

        # skip hitModule that has memberSettingProfile/spreadGroup defined as 'NoAction'/null
        if hitmodule['UpdateMemberProfile'] is not None:  # i.e. has actionValue defined
            rankNum_msp = get_ranking_byID(hitmodule['UpdateMemberProfile'], 'msp')
            if smallest_ranking_number_msp == None or is_LT(rankNum_msp, smallest_ranking_number_msp):
                smallest_ranking_number_msp = rankNum_msp
        if hitmodule['UpdateMemberSpreadGroup'] is not None:  # has actionValue defined
            rankNum_spread = get_ranking_byID(hitmodule['UpdateMemberSpreadGroup'], 'spread')
            if smallest_ranking_number_spread == None or is_LT(rankNum_spread, smallest_ranking_number_spread):
                smallest_ranking_number_spread = rankNum_spread

        if hitmodule['UpdateMemberBetDelay'] is not None:  # i.e. has actionValue defined
            Module_BetDelay = int(hitmodule['UpdateMemberBetDelay'])
            # hitmodule['UpdateBDSportGroups'] contains SportGroup format, i.e ['1001','1003']
            # we convert it into individual sportID and store in BDsportIDs for processing, i.e [1,54,55]
            BDsportIDs = []
            thismodule_SportGroup_list = ast.literal_eval(
                hitmodule['UpdateBDSportGroups'])  # >reformat '[1001,1002]'  to [1001,1002]
            # print(f"hitmodule['UpdateBDSportGroups'] 111 is ,",thismodule_SportGroup_list)
            if thismodule_SportGroup_list == [-1]:
                for sportGroup in sportGroup_sportIDs_UImap_dict:  # get all from {1001: [1], 1002: [2], 1003: [54, 55], 1000: [3, 4, 5, 6, 7, 8,etc..]}
                    BDsportIDs.extend(sportGroup_sportIDs_UImap_dict.get(sportGroup, []))
            else:
                for sportGroup in thismodule_SportGroup_list:
                    BDsportIDs.extend(sportGroup_sportIDs_UImap_dict.get(sportGroup, []))
            # print(f"sportid 1 is ,",BDsportIDs)
            for sport in BDsportIDs:  # for each sport of current looping module,  #eg [1,2,54,55]
                # if this sportBD never exist in severest_list,directly update inside
                # if already exist(from other module), then compare new with existing and get the most severe one
                if sport in betDelay_Severest_dict:
                    if betDelay_Severest_dict[sport] < Module_BetDelay:
                        betDelay_Severest_dict[sport] = Module_BetDelay
                else:  # if no most severe yet, add this as most severe
                    betDelay_Severest_dict[sport] = Module_BetDelay
                # print(f"severest sport is ,",betDelay_Severest_dict)

        # only for crossModuleType: GBGood & hasEGON , saved (the only) EGON among moduleHits
        # if is_match(hitmodule['scr_gbRuleID'],11):
        if (hitObject.cross_GB_Good and hitObject.cross_has_EGON and is_match(hitmodule['scr_gbRuleID'], 11)):
            memCategory_of_directEGON = hitmodule['UpdateMemberCategory']
            isAdvised_of_directEGON = hitmodule['UpdateMemberIsAdvised']
            BetDelay_of_directEGON = thismodule_SportGroup_list

    return smallest_ranking_number_msp, smallest_ranking_number_spread, betDelay_Severest_dict, memCategory_of_directEGON, isAdvised_of_directEGON, BetDelay_of_directEGON

def to_apply_creditscore(creditScore_before_hit,msp_smallest_rankNum,msp_before_hit,p_CS_GT1_fullfill_otherConditions):
    # to change, right now i skip CSaction if noCS or CS>1 or memCat=molly,etc..(both BL & BD has same omit conditions)
    if not creditScore_before_hit or (creditScore_before_hit and creditScore_before_hit > 1 and p_CS_GT1_fullfill_otherConditions==False ):  # @@change . see if there is a need to retrieve minCS from general setting
        return False

    if msp_smallest_rankNum is not None:
        BL_ori_raw_percentage_value = MemberProfileSettingMappers.get_perc_by_ranking(msp_smallest_rankNum)
        existing_BL_raw_percentage_value = MemberProfileSettingMappers.get_perc_by_id(msp_before_hit)
        # for newAction BL or existing BL do not have raw_percentage value,
        # no need to apply creditScore. eg.Molly group, RMB1Group etc..return orig newActionBL
        if BL_ori_raw_percentage_value == None or existing_BL_raw_percentage_value == None:
            return False

    return True #apply creditScore/delayModifier action

def creditScore_application_BL(msp_smallest_rankNum, api_CalcBL_CSfinalBL_mapping, creditScore_before_hit,msp_before_hit,p_CS_GT1_fullfill_otherConditions):
    if to_apply_creditscore(creditScore_before_hit, msp_smallest_rankNum,msp_before_hit,p_CS_GT1_fullfill_otherConditions):
        BL_ori_raw_percentage_value = MemberProfileSettingMappers.get_perc_by_ranking(msp_smallest_rankNum)
        # retrieve the CS_finalBL rankNum if there is matching calculated_BL_raw_perc range
        calculated_BL_raw_perc = BL_ori_raw_percentage_value * creditScore_before_hit
        for mapping in api_CalcBL_CSfinalBL_mapping:
            # pass in argument(calculated_BL_raw_perc) into lambda function(that check if calculated_raw_BL is within defined range that map to CS_finalBL_ID)
            if mapping['func_within_defined_CalcBL_range'](float(calculated_BL_raw_perc)):
                return MemberProfileSettingMappers.get_ranking_by_ID(
                    mapping['CS_finalBL_ID']), True  # return newActionBL*CreditScore
    # if mapping between calculated_BL_raw_perc range and CS_FinalBL is not found/defined,  return newActionBL
    return msp_smallest_rankNum,False

def creditScore_application_BD(NewHit_BetDelay, api_assignedCS_delaymodifier_mapping, creditScore_before_hit,msp_before_hit,msp_smallest_rankNum,p_CS_GT1_fullfill_otherConditions):
    if to_apply_creditscore(creditScore_before_hit,msp_smallest_rankNum,msp_before_hit,p_CS_GT1_fullfill_otherConditions):
        if api_assignedCS_delaymodifier_mapping[creditScore_before_hit]:
            return NewHit_BetDelay + api_assignedCS_delaymodifier_mapping[creditScore_before_hit], True  # return NewHit_BetDelay*DelayModifier
    # if mapping between calculated_BL_raw_perc range and CS_FinalBL is not found/defined,  return newActionBL
    return NewHit_BetDelay,False


def BL_SG_Cross_Module_check(memSetting_before_hit, hitObject, smallest_rankNum, field_type):
    errMsg = None
    # this function is only used for special handling for EGON, so far
    if field_type == 'msp':
        value_before_hit = get_ranking_byID(memSetting_before_hit['sfMemberSettingProfileID'], 'msp')
        value_lastUpdatedBy, _ = helper.parse_updatedby(memSetting_before_hit['sfMemberProfileSettingLastUpdatedBy'])
    else:
        value_before_hit = get_ranking_byID(memSetting_before_hit['sfSpreadGroupID'], 'spread')
        value_lastUpdatedBy, _ = helper.parse_updatedby(memSetting_before_hit['sfSpreadGroupLastUpdatedBy'])

    # special handling for cross_GBBad_EGONGood
    # when upgrading(smallest_rankNum/most_severe_value  is better than existing value), lastupdatedby mz be EGON. if not dun take action.
    if (hitObject.cross_GBBad_EGONGood
            and smallest_rankNum > value_before_hit and value_lastUpdatedBy != 'GB_EGON'):
        errMsg = f'{field_type} only allowed to be upgraded if lastUpdby=EGON; behavour: {hitObject.cross_type}'
        smallest_rankNum = None
    return smallest_rankNum, errMsg


def BL_SG_Single_Module_check(memSetting_before_hit, hitObject, new_Hit_Action, smallest_rankNum, threshold_rankNum,
                              field_type):
    isWithinValidityPeriod = False
    updatedby_system = False
    if field_type == 'msp':
        lastUpdatedBy, lastScoreType = helper.parse_updatedby(memSetting_before_hit['sfMemberProfileSettingLastUpdatedBy'])
        updatedby_system = is_system(lastUpdatedBy)
        if updatedby_system:
            module_validFrom_utc = get_module_validFromDate_utc(lastUpdatedBy,'updatedby_module')
            isWithinValidityPeriod = check_if_within_validity_period(module_validFrom_utc,memSetting_before_hit['sfMemberProfileSettingUpdatedDate'])
        existing_valueID = memSetting_before_hit['sfMemberSettingProfileID']
    elif field_type == 'spread':
        lastUpdatedBy, lastScoreType = helper.parse_updatedby(memSetting_before_hit['sfSpreadGroupLastUpdatedBy'])
        updatedby_system = is_system(lastUpdatedBy)
        if updatedby_system:
            module_validFrom_utc = get_module_validFromDate_utc(lastUpdatedBy,'updatedby_module')
            isWithinValidityPeriod = check_if_within_validity_period(module_validFrom_utc,memSetting_before_hit['sfSpreadGroupUpdatedDate'])
        existing_valueID = memSetting_before_hit['sfSpreadGroupID']


    # process Single EGON
    if hitObject.single_EGON:
        # if lastUpdby=DiffModule & withinValidityPeriod & prevScoreType=Bad, use severity btw existing & new hit value.
        # else remain(use newHit)
        if updatedby_system and not is_match(lastUpdatedBy,
                                                 hitObject.UpdBy_Module) and isWithinValidityPeriod == True and lastScoreType == 'Bad':
            smallest_rankNum = get_most_severe(get_ranking_byID(existing_valueID, field_type), smallest_rankNum)
            errMsg = f'{field_type} failed to use most severe value btw new & existing value. behaviour Hit: singleEGON & LastUpdby=diffModule & withinValidity & LastScoreType !=good'
        else:
            errMsg = f'{field_type} failed to be updated with EGON action'
    # process Single Non-EGON
    else:
        # Hit Single GBrule & lastUpdatedby=User/null
        if hitObject.hitGbRule and not updatedby_system:
            # if GoodScore,noAction allowed
            if is_match(new_Hit_Action['ScoreType'], 1):
                smallest_rankNum = None  # action is not allowed
                errMsg = f'update to {field_type} is not allowed for GoodScore and lastupdatedby is user/null'
            #else:
                # (remove below in GBQAT-2384)
                # badScore & Action is less severe, then NOAction allowed
                # if is_GT(smallest_rankNum,threshold_rankNum):
                #     smallest_rankNum = None  # action is not allowed if badScore and newHit less severe than defaultValue
                #     errMsg = f'update to {field_type} is not allowed for BadScore and newHit less severe than threshold value'
                # else:
                #     errMsg = f'update to {field_type} has failed for  BadScore and newHit more severe than threshold value'
            elif lastUpdatedBy == None:  # lastupdated=null(usually newly created member,no action yet), remain(use newHit)
                errMsg = f'{field_type} failed to be updated with new GBrule action'
            else: #lastupdatedby=user
                # badScore , only downgrade is allowed(i.e get most sever between existing value vs newHit value)
                smallest_rankNum = get_most_severe(get_ranking_byID(existing_valueID, field_type), smallest_rankNum)
                errMsg = f'{field_type} can only downgrade from member existing value for BadScore,LastUpdby=user/null '

        # Hit SingleModule(GBrule & GBfeature) & LastUpdatedBy=DiffModule(due to reduce from cross)
        elif lastUpdatedBy and updatedby_system and not is_match(lastUpdatedBy, hitObject.UpdBy_Module):
            # if GoodScore,noAction allowed
            if is_match(new_Hit_Action['ScoreType'], 1):
                smallest_rankNum = None  # action is not allowed
                errMsg = f'update to {field_type} is not allowed for GoodScore and lastupdatedby is by diff Module'
            else:  # badScore & Within Validity period,then use most severe value between existing and new Hit
                # existing value is not possible to be Null/empty at this point
                if isWithinValidityPeriod == True:  #
                    smallest_rankNum = get_most_severe(get_ranking_byID(existing_valueID, field_type), smallest_rankNum)
                    errMsg = f'{field_type} failed to use most severe value btw new & existing value. behaviour Hit: singleModule,LstUpdBy=DiffModule,withinValidtityPeriod '
                else:
                    errMsg = f'update to {field_type} has failed'
        else:
            errMsg = f'this test case is not covered, please check'
    return smallest_rankNum, errMsg


def get_threshold_bd(hitObject,
                     memSetting_before_hit,memBetDelay_before_hit_fmt, sportid,to_apply_creditScore_BD):
    BD_threshold = None
    BD_priorValue_UpdDate = memBetDelay_before_hit_fmt.get(sportid, {}).get('revisedGBBetDelayUpdatedDate')
    BD_priorValue_Flag = memSetting_before_hit['isManualRevised']
    # if priorityflag=0(off)/1(BL/SG only), priorValue for BD will still remain in mysql so better to use flag to determine if BD prior is on or off
    # we default priorflagUpdateDate to null to exclude checking in threshold, if BD prior is off
    if BD_priorValue_Flag != 2: # 2= has BL/SG/BD priorValue, 1= has BL/SG prior value
        BD_priorValue_UpdDate = None
    BD_UserValue_UpdDate = memBetDelay_before_hit_fmt.get(sportid, {}).get('GBBetDelayByUserUpdatedDate')
    BD_UserValue = memBetDelay_before_hit_fmt.get(sportid, {}).get('GBBetDelayByUser') if BD_UserValue_UpdDate else None
    BD_PriorValue = memBetDelay_before_hit_fmt.get(sportid, {}).get('revisedGBBetDelay')  if BD_priorValue_UpdDate else None

    # === get threshold of BD (BD has no merchant,so no merchant checking is applied here)==
    # if got CreditScore, do not apply user limit, only prioritise flag(no checking of merchant limit here as BD has no merchant upd)======
    if (to_apply_creditScore_BD == True):
        if (BD_priorValue_UpdDate):  # apply threshold if got, else No threshold for BD
            BD_candidates = []
            if BD_priorValue_UpdDate:  # save down for further check only if flag is on, value exists and date exists
                BD_candidates.append((BD_priorValue_UpdDate, BD_PriorValue))
            _, BD_threshold = max(BD_candidates, key=lambda x: x[0])

    # if no creditScore,apply type of threshold accordingly depends on single/cross type
    else:
        # for  (1)singleEGON or (2)GBgood_hasEGON or  or (3)GBbad_EGONbad,
        #      use priorFlag or merchantValue(whichever latest) as cap
        if (hitObject.single_EGON or hitObject.cross_GBGood_hasEGON or hitObject.cross_GBBad_EGONBad):
            if (BD_priorValue_UpdDate):  # apply threshold if got, else No threshold
                BD_candidates = []
                if BD_priorValue_UpdDate:  # save down for further check only if flag is on, value exists and date exists
                    BD_candidates.append((BD_priorValue_UpdDate, BD_PriorValue))
                _, BD_threshold = max(BD_candidates, key=lambda x: x[0])
        # for (4)singleGBrule;SingleGBfeature or (5)GBonly_good (6)crossGBonly_bad ,
        #      use UserValue or PrioritiseValue(whichever latest) as cap
        elif ((
                      hitObject.singleModule and not hitObject.single_EGON) or hitObject.cross_onlyGBs_noEGON_GBGood or hitObject.cross_onlyGBs_noEGON_GBBad):
            if (BD_UserValue_UpdDate or BD_priorValue_UpdDate):  # apply threshold if there is, else initialValue
                BD_candidates = []
                if BD_UserValue_UpdDate:
                    BD_candidates.append((BD_UserValue_UpdDate, BD_UserValue))
                if BD_priorValue_UpdDate:
                    BD_candidates.append((BD_priorValue_UpdDate, BD_PriorValue))
                _, BD_threshold = max(BD_candidates, key=lambda x: x[0])
        # for (7)GBbad_egonGood,
        #     use UserValue or PrioritiseValue or MerchantValue(whichever latest)
        elif (hitObject.cross_GBBad_EGONGood):
            if (BD_UserValue_UpdDate or BD_priorValue_UpdDate):  # apply threshold if there is, else initial value
                BD_candidates = []
                if BD_UserValue_UpdDate:
                    BD_candidates.append((BD_UserValue_UpdDate, BD_UserValue))
                if BD_priorValue_UpdDate:
                    BD_candidates.append((BD_priorValue_UpdDate, BD_PriorValue))
                _, BD_threshold = max(BD_candidates, key=lambda x: x[0])

    # BD_threshold cannot be None/null, downstream must be able to handle None value
    return BD_threshold

def get_threshold(hitObject, memSetting_before_hit, to_apply_creditScore,type):
    threshold_rankNum = None
    priorValue_UpdDate = memSetting_before_hit['revisedValueUpdatedDate']
    priorValue_Flag = memSetting_before_hit['isManualRevised']
    # if priorityflag is off on UI, isManualRevised will be set to 0 and PriorValue will be delete(None) in mysql.
    # so, we default priorflagUpdateDate to null to exclude checking in threshold
    if priorValue_Flag not in (1,2):  #has BL/SG prior
        priorValue_UpdDate = None

    # !!! this part i hardcoded to cater for dirty data
    memSetting_before_hit['defaultSfMemberSettingProfileID'] = memSetting_before_hit[
        'defaultSfMemberSettingProfileID'] if memSetting_before_hit['defaultSfMemberSettingProfileID'] else 1
    memSetting_before_hit['revisedMemberProfileSettingID'] = memSetting_before_hit['revisedMemberProfileSettingID'] if (
                priorValue_UpdDate and memSetting_before_hit['revisedMemberProfileSettingID']) else 1
    memSetting_before_hit['defaultSfSpreadGroupID'] = memSetting_before_hit['defaultSfSpreadGroupID'] if \
    memSetting_before_hit['defaultSfSpreadGroupID'] else 1
    memSetting_before_hit['revisedSpreadGroupID'] = memSetting_before_hit['revisedSpreadGroupID'] if (
                priorValue_UpdDate and memSetting_before_hit['revisedSpreadGroupID']) else 1
    # !!!

    if type == 'msp':
        UserValue_UpdDate = memSetting_before_hit['sfMemberProfileSettingUpdatedDateByUser']
        MerchValue_UpdDate = memSetting_before_hit['sfMemberProfileSettingUpdatedDateByMerchant']
        UserValue_rankNum = get_ranking_byID(memSetting_before_hit['sfMemberProfileSettingIDUpdatedByUser'],
                                             'msp') if UserValue_UpdDate else None
        MerchValue_rankNum = get_ranking_byID(memSetting_before_hit['sfMemberProfileSettingIDUpdatedByMerchant'],
                                              'msp') if MerchValue_UpdDate else None
        PriorValue_rankNum = get_ranking_byID(
            memSetting_before_hit['revisedMemberProfileSettingID'], 'msp') if priorValue_UpdDate else None
        initial_rankNum = get_ranking_byID(
            memSetting_before_hit['defaultSfMemberSettingProfileID'], 'msp')
    else:
        UserValue_UpdDate = memSetting_before_hit['sfSpreadGroupUpdatedDateByUser']
        MerchValue_UpdDate = memSetting_before_hit['sfSpreadGroupUpdatedDateByMerchant']
        UserValue_rankNum = get_ranking_byID(
            memSetting_before_hit['sfSpreadGroupIDUpdatedByUser'], 'spread') if UserValue_UpdDate else None
        MerchValue_rankNum = get_ranking_byID(
            memSetting_before_hit['sfSpreadGroupIDUpdatedByMerchant'], 'spread') if MerchValue_UpdDate else None
        PriorValue_rankNum = get_ranking_byID(
            memSetting_before_hit['revisedSpreadGroupID'], 'spread') if priorValue_UpdDate else None
        initial_rankNum = get_ranking_byID(memSetting_before_hit['defaultSfSpreadGroupID'], 'spread')


    # =======GET THRESHOLD VALUE===================

    # if got CreditScore, apply merchant limit or prioritise Flag ===
    if (to_apply_creditScore == True and type == 'msp'):
        if(priorValue_UpdDate or MerchValue_UpdDate):  #apply threshold if there is, else initialValue(if initalvalue is not used, then comment out else statement)
            candidates = []
            if priorValue_UpdDate:  # save down for further check only if flag is on, value exists and date exists
                candidates.append((priorValue_UpdDate, PriorValue_rankNum))
            if MerchValue_UpdDate:
                candidates.append((MerchValue_UpdDate, MerchValue_rankNum))
            _, threshold_rankNum = max(candidates, key=lambda x: x[0])
        #else:
        #    threshold_rankNum = initial_rankNum          #system currently no use
    # if no CreditScore, type of threshold accordingly depends on single/cross type
    else:
        # for  (1)singleEGON or (2)GBgood_hasEGON or  or (3)GBbad_EGONbad,
        #      use priorFlag or merchantValue(whichever latest) as cap
        if (hitObject.single_EGON or hitObject.cross_GBGood_hasEGON or hitObject.cross_GBBad_EGONBad):
            if (priorValue_UpdDate or MerchValue_UpdDate): #apply threshold if got, else No threshold
                candidates = []
                if priorValue_UpdDate:  # save down for further check only if flag is on, value exists and date exists
                    candidates.append((priorValue_UpdDate, PriorValue_rankNum))
                if MerchValue_UpdDate:
                    candidates.append((MerchValue_UpdDate, MerchValue_rankNum))
                _, threshold_rankNum = max(candidates, key=lambda x: x[0])
        # for (4)singleGBrule;SingleGBfeature or (5)GBonly_good (6)crossGBonly_bad ,
        #      use UserValue or PrioritiseValue(whichever latest) as cap
        elif ((hitObject.singleModule and not hitObject.single_EGON) or hitObject.cross_onlyGBs_noEGON_GBGood or hitObject.cross_onlyGBs_noEGON_GBBad):
            if (UserValue_UpdDate or priorValue_UpdDate):  #apply threshold if there is, else initialValue
                candidates = []
                if UserValue_UpdDate:
                   candidates.append((UserValue_UpdDate, UserValue_rankNum))
                if priorValue_UpdDate:
                    candidates.append((priorValue_UpdDate, PriorValue_rankNum))
                _, threshold_rankNum = max(candidates, key=lambda x: x[0])
            else:
                threshold_rankNum = initial_rankNum
        # for (7)GBbad_egonGood,
        #     use UserValue or PrioritiseValue or MerchantValue(whichever latest)
        elif (hitObject.cross_GBBad_EGONGood):
            if (UserValue_UpdDate or priorValue_UpdDate or MerchValue_UpdDate): #apply threshold if there is, else initial value
                candidates = []
                if UserValue_UpdDate:
                    candidates.append((UserValue_UpdDate, UserValue_rankNum))
                if priorValue_UpdDate:
                    candidates.append((priorValue_UpdDate, PriorValue_rankNum))
                if MerchValue_UpdDate:
                    candidates.append((MerchValue_UpdDate, MerchValue_rankNum))
                _, threshold_rankNum = max(candidates, key=lambda x: x[0])
            else:
                threshold_rankNum = initial_rankNum


    return threshold_rankNum


'''
    # GET THRESHOLD VALUE
        #if singleEGON/GBgood_hasEGON, use merchantValue as cap
    if (  hitObject.single_EGON or hitObject.cross_GBGood_hasEGON  ) \
        and MerchValue_UpdDate:
        threshold_rankNum = MerchValue_rankNum
        # if singleGBrule/SingleGBfeature , use latest of UserValue or PrioritiseValue
    elif hitObject.singleModule and not hitObject.single_EGON  \
         and (UserValue_UpdDate or priorValue_UpdDate):
        candidates = []
        if UserValue_UpdDate:
            candidates.append((UserValue_UpdDate, UserValue_rankNum))
        if priorValue_UpdDate:
            candidates.append((priorValue_UpdDate, PriorValue_rankNum))
        _, threshold_rankNum = max(candidates, key=lambda x: x[0])
        # if crossGBonly/GBbad_EgonBad , use latest of UserValue or PrioritiseValue or MerchantValue
    elif hitObject.cross_onlyGBs_noEGON or hitObject.cross_GBBad_EGONBad or hitObject.cross_GBBad_EGONGood \
        and (UserValue_UpdDate or PriorValue_rankNum or MerchValue_UpdDate):
        candidates = []
        if UserValue_UpdDate:
            candidates.append((UserValue_UpdDate, UserValue_rankNum))
        if priorValue_UpdDate:
            candidates.append((priorValue_UpdDate, PriorValue_rankNum))
        if MerchValue_UpdDate:
            candidates.append((MerchValue_UpdDate, MerchValue_rankNum))
        _, threshold_rankNum = max(candidates, key=lambda x: x[0])
        # if required Uservalue/Prioritise/Merchant is not available, use value upon creation
    else:
        threshold_rankNum = initial_rankNum
'''


# # get threshold value(latest of userManualUpd or prioritisedValue. if both N/A, use value uponCreation)
# if UserValue_UpdDate and priorValue_UpdDate:  # has both userManual & prioritiseFlag
#     threshold_rankNum = UserValue_rankNum if UserValue_UpdDate > priorValue_UpdDate else PriorValue_rankNum
# elif UserValue_UpdDate:  # has userManual
#     threshold_rankNum = UserValue_rankNum
# elif priorValue_UpdDate:  # has prioritiseFlag
#     threshold_rankNum = PriorValue_rankNum
# else:  # has no userManualUpd & prioritisedFlag, then use value uponCreation
#     threshold_rankNum = initial_rankNum


from dataclasses import dataclass

@dataclass
class ModuleType:
    GbRule: bool = False
    GbRule_GbRule: bool = False
    GbRule_Egon: bool = False
    GbFeature: bool = False
    unknown: bool = False

def get_moduletype(module,pass_in_format) -> ModuleType:
    # check if this hitName is one of gbule(including egon) , if not then must be gbfeature
    if pass_in_format == 'module_code':

        if GbRuleMapper.get_id_byCode(module):
            gbrule_hit_type_id = GbRuleMapper.get_id_byCode(module)
            # If gbrule_hit_type_id exists, gbrule/egon is always True
            # then we cleanly separate the sub-types using a ternary operator
            return ModuleType(
                    GbRule=True,
                    GbRule_Egon=(gbrule_hit_type_id == 11),
                    GbRule_GbRule=(gbrule_hit_type_id != 11)
            )
        elif GbFeatureMapper.get_id_byCode(module):
            return ModuleType(GbFeature=True)  # instantiates the class (change gbfeature to true)
        else:
            return ModuleType(unknown=True)  # not system module

    if pass_in_format == 'updatedby_module':
        if GbRuleMapper.get_id_by_updByName(module):
            gbrule_hit_type_id = GbRuleMapper.get_id_by_updByName(module)
            # If gbrule_hit_type_id exists, gbrule/egon is always True
            # then we cleanly separate the sub-types using a ternary operator
            return ModuleType(
                    GbRule=True,
                    GbRule_Egon=(gbrule_hit_type_id == 11),
                    GbRule_GbRule=(gbrule_hit_type_id != 11)
            )
        elif GbFeatureMapper.get_id_by_updByName(module):
            return ModuleType(GbFeature=True)  # instantiates the class (change gbfeature to true)
        else:
            return ModuleType(unknown=True)  # # not system module

    return ModuleType(unknown=True)

def is_system(updatedby):
    #if  updatedby and updatedby.startswith('GB_') and not updatedby.startswith('GB_MemberList'):
    if  (GbRuleMapper.get_id_by_updByName(updatedby) is not None   or   GbFeatureMapper.get_id_byCode(updatedby) is not None ):
        return True
    return False


def get_module_validFromDate_utc(updatedBy_module,module_format):
    # pass in moduleName, and it returns a class object
    # periodValidity is hardcoded based on generalsetting, any changes change hardcoding in 'getMemHitHistory_Mysql.sql' too
    ThisModuleTypeIs = get_moduletype(updatedBy_module,module_format)  # pass in the lastupdby Name(can be system can be user)
    if ThisModuleTypeIs.GbRule_GbRule:
        validFrom_utc = helper.get_past_date_UTC(24,'hours')   #must tally with PP_RuleValidityPeriod
    elif ThisModuleTypeIs.GbRule_Egon:
        validFrom_utc = helper.get_past_date_UTC(24, 'hours')   #must tally with PP_EgonValidityPeriod
    elif ThisModuleTypeIs.GbFeature:
        validFrom_utc = helper.get_past_date_UTC(3, 'months')   #must tally with PP_FeatureValidityPeriod
    else:
        raise ValueError("unable to check validity period for this {module_format} --> '{updatedBy_module}' ")
    return validFrom_utc

def check_if_within_validity_period(validFrom_utc, updatedDate_utc):
    if updatedDate_utc >= validFrom_utc: # both are in <class 'datetime.datetime'> format  (eg. 2026-07-04 13:44:53 UTC)
        return True # within validity period
    else:
        return False