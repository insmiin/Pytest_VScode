# pytest test_scenarios\test_memActions\verify_ScoreAction.py -v --tb=short
import sys
import pytest
from mysql.connector import Error
from typing import List, Dict
import time
import os
import csv
from datetime import datetime, timezone, timedelta
from tests.memberAction_tests.helpers.myHelperFunc import  parse_updatedby
import tests.memberAction_tests.helpers.memAction_sql_helpers as qhlp
import tests.memberAction_tests.helpers.memAction_api_helpers as ahlp
import tests.memberAction_tests.helpers.memAction_assert_helpers as ashlp
import tests.memberAction_tests.helpers.memAction_helpers as hlp
from tests.utils.comparison_utils import is_match, is_LT
import memberAction_Constants as action_const
from mappingModule import SpreadGroupMappers, MemberProfileSettingMappers, GbRuleMapper, GbFeatureMapper
import ast


def read_csv(csv_filename: str) -> List[Dict]:
    """Read all lines from CSV and return a list of dictionaries with each dic as a line from csv"""
    """[{"date":'2024-04-2","memcat":'VIP","soccount":3},{"date":'2024-04-2","memcat":'VIP","soccount":3},...]"""
    try:
        csv_file = action_const.CSV_FILE_PATH / csv_filename
        with open(csv_file, mode='r', newline='') as csvfile:
            reader = csv.DictReader(csvfile)
            return [row for row in reader if row['testcase']]  # ignore testcase that is space or empty
    except FileNotFoundError:
        print(f"File not found: {csv_file}")
        sys.exit(1)


def format_filters(csv_rows: List[Dict]) -> List[Dict]:
    """convert each of the value provided in csv(data read from csv is always str) to the value used in API request"""
    """notes: when using statement 'if <some_var>', sys always returns False when <some_var> is None,empty string,empty list,NUMBER 0,etc"""
    """   since csv only read as string format, so we can use 'if <some_var> to determine the existence of csv value"""
    """   but after converting all csv value into api format, the original csv value can be in different format now(eg. int,str,list,tuple,None,etc...)"""
    """ so in validating/assertion part, careful when checking the existense of int field, as Number 0 will be treated as false"""
    """ so on int field, use 'if abc or abc ==0' to ensure assertion to carry out even for 0 value"""
    formatted_filters = []
    for row in csv_rows:
        formatted_filter = {
            "testcase": row['testcase'],
            "memberCode": row['memberCode'],
            "companyID": int(row['companyID']),
            "hitType": row["hitType"],
            "gbRuleScore": int(row["gbRuleScore"]) if row["gbRuleScore"] else '',
            "toActionFlag": row["toActionFlag"],
            # "prerequisiteFlag":row["prerequisiteFlag"],
            "prerequisite1": row["prerequisite1"],
            "prerequisite2": row["prerequisite2"],
            "prerequisite3": row["prerequisite3"],
            # "EditUpdatedDateFlag":row["EditUpdatedDateFlag"],
            "EditUpdatedDate": row["EditUpdatedDate"],
            "pre_actionOnOffFlag": row["pre_actionOnOffFlag"],  # featureOn/Off
            "post_actionOnOffFlag": row["post_actionOnOffFlag"]
        }
        formatted_filters.append(formatted_filter)
    return formatted_filters




def assert_ActionUpdate(hitObject, smallest_rankNum, threshold_rankNum, memSetting_before_hit, memSetting_after_hit,
                        assert_type, api_CalcBL_CSfinalBL_mapping, errMsg):
    if assert_type == 'msp':
        value_before_hit = memSetting_before_hit['sfMemberSettingProfileID']
        value_after_hit = memSetting_after_hit['sfMemberSettingProfileID']
        rankingTo_valueId_method = MemberProfileSettingMappers.get_ID_by_ranking
    else:
        value_before_hit = memSetting_before_hit['sfSpreadGroupID']
        value_after_hit = memSetting_after_hit['sfSpreadGroupID']
        rankingTo_valueId_method = SpreadGroupMappers.get_ID_by_ranking

    if smallest_rankNum:  # if there is Action
        if is_LT(threshold_rankNum,
                 smallest_rankNum):  # use Threshold as Action if threshold is more severe, else use Action
            smallest_rankNum = threshold_rankNum


        expected_valueID = rankingTo_valueId_method(smallest_rankNum)
        assert is_match(value_after_hit,
                        expected_valueID), f"{assert_type} expected Action is incorrect,behaviour:{hitObject.HitSingleOrCross} ,crossType={hitObject.cross_type}"
    else:  # there is no Action allowed from current hit
        if errMsg:
            errMsg = f"{errMsg}"
        else:
            errMsg = f"{assert_type} has been updated with new Action"
        assert is_match(value_after_hit, value_before_hit), errMsg


#C:/Users/lim.miin/OneDrive - Morpheus Consulting Pte Ltd/Desktop/testing/Output check/scoreAction.csv
@pytest.mark.parametrize("csv_filter"
    , format_filters(read_csv(
        "scoreAction.csv"))
    , ids=lambda csv_filter: f"testcase_{csv_filter['testcase']}"
                         )
# companies_list,api_session,mysql_connection only need to call 1 time per run
def test_memAction(mysql_connection, companies_list, api_session, api_session_SF, api_MemHierarchyGroupList, \
                   api_CalcBL_CSfinalBL_mapping,
                   sportGroup_sportIDs_UImap_dict, prev_memberCode, csv_filter):

    # flag to manually control certain processing
    to_triggerActionFlag = True  # flag for me to control triggering
    to_reset_member = True  # sometime if wan to continue subsequent action of SAME member, set this manually to false
    apply_creditScore_FLAG = True  # @@changeCS? see if there is a need to retrieve the flag once to determine if using CS or not


    # create a class to store all the necessary information related to NewHit
    class NewHit:
        def __init__(self):
            self.hitGbRule = False   # new hit is GBrule or Egon
            self.hitGbRule_Egon = False  #new hit is Gbrule(non-egon)
            self.hitGbRule_GbRule = False #new hit is Gbrule(Egon)
            self.hitGbFeature = False
            self._HitID = None
            self.BD_Sportid = None
            self.mysql_filter_statement = None
            self.singleModule = False
            self.crossModule = False
            self.HitSingleOrCross = None
            self.UpdBy_Module = None  # current Hit moduleName to be stored in updatedBy field
            self.single_EGON = False
            self.cross_GB_Good = False
            self.cross_GB_Bad = False
            self.cross_has_EGON = False
            self.cross_EGON_Good = False
            self.cross_EGON_Bad = False
            self.cross_onlyGBs_noEGON = False  # type1
            self.cross_GBGood_hasEGON = False  # type2
            self.cross_GBBad_EGONBad = False  # type3
            self.cross_GBBad_EGONGood = False  # type4
            self.cross_onlyGBs_noEGON_GBBad = False
            self.cross_onlyGBs_noEGON_GBGood = False
            self.cross_type = None

        @property
        def HitID(self):  # getter of HitID. when request for HitID value, return _HitID(final hitID after going thru internal logic in setter)
            return self._HitID

        # setter function of HITID. when u assign value to HitID. function to jz set/modify the value and assigned after processing value to another var(eg. _HitID)
        @HitID.setter
        def HitID(self, hitName):
            if hitName is None:
                return  # Just exit without doing anything. it has no where to return to anywhere.
            if GbRuleMapper.get_id_byCode(hitName):
                self._HitID = GbRuleMapper.get_id_byCode(hitName)
                self.hitGbRule = True
                self.hitGbRule_GbRule = True
                if self._HitID == 11:
                    self.hitGbRule_Egon = True
                    self.hitGbRule_GbRule = False
                self.mysql_filter_statement = f'scr_gbRuleID = {self.HitID}'
                self.BD_Sportid = GbRuleMapper.get_sports_byCode(hitName)
                self.UpdBy_Module = GbRuleMapper.get_updByName_byCode(hitName)
            elif GbFeatureMapper.get_id_byCode(hitName):
                self._HitID = GbFeatureMapper.get_id_byCode(hitName)
                self.hitGbFeature = True
                self.mysql_filter_statement = f'prof_moduleID = {self.HitID}'
                self.BD_Sportid = GbFeatureMapper.get_sports_byCode(hitName)
                self.UpdBy_Module = GbFeatureMapper.get_updByName_byCode(hitName)

        #  >>> after Hit, comparing all the existing modules to determine cross or single module
        def hit_Single_Or_CrossModule(self, moduleHistory_after_hit):
            if len(moduleHistory_after_hit) == 1:
                self.singleModule = True
                self.HitSingleOrCross = 'SingleModule'
                if self.hitGbRule and self._HitID == 11:
                    self.single_EGON = True
            elif len(moduleHistory_after_hit) > 1:
                self.crossModule = True
                self.HitSingleOrCross = 'CrossModule'

        def determine_GB_EGON_crossstatus(self, moduleHistory_after_hit):
            self.cross_GB_Good = True  # default good until it has at least 1 bad

            for hitmodule in moduleHistory_after_hit:
                # process EGON (only has 1 EGON type in lifecycle)
                if is_match(hitmodule['scr_gbRuleID'], 11):
                    self.cross_has_EGON = True
                    if is_match(hitmodule['ScoreType'], 1):
                        self.cross_EGON_Good = True
                    else:
                        self.cross_EGON_Bad = True

                # process GBrule/feature(can have more diff rule/feature type than 1 in lifecycle).
                # default is Good(1), as long as there is 1 badscore(scoretype2)/gbfeature=yes(scoretype empty) ,it is consider bad(2)
                elif not is_match(hitmodule['ScoreType'], 1):
                    self.cross_GB_Good = False
                    self.cross_GB_Bad = True

            if not self.cross_has_EGON:
                self.cross_onlyGBs_noEGON = True  # type1
                self.cross_onlyGBs_noEGON_GBGood = True
                self.cross_type = 'cross_onlyGBs_noEGON_GBGood'
                if self.cross_GB_Bad:
                    self.cross_onlyGBs_noEGON_GBGood = False
                    self.cross_onlyGBs_noEGON_GBBad = True
                    self.cross_type = 'cross_onlyGBs_noEGON_GBBad'
            elif self.cross_GB_Good and self.cross_has_EGON:
                self.cross_GBGood_hasEGON = True  # type2
                self.cross_type = 'cross_GBGood_hasEGON'
            elif self.cross_GB_Bad and self.cross_EGON_Bad:
                self.cross_GBBad_EGONBad = True  # type3
                self.cross_type = 'cross_GBBad_EGONBad'
            elif self.cross_GB_Bad and self.cross_EGON_Good:
                self.cross_GBBad_EGONGood = True  # type4
                self.cross_type = 'cross_GBBad_EGONGood'

    # 1 >>>>> STORE AND PROCESS DATA FROM CSV   <<<<<
    hitObject = NewHit()
    hitObject.HitID = csv_filter['hitType']
    assert hitObject.HitID is not None, f"no valid HitID found, please check your input"
    if hitObject.hitGbRule:
        assert csv_filter[
                   'gbRuleScore'] != None, f"HitType is GBrule but no score is provided in your csv file"  # 0 is false
        assert csv_filter['toActionFlag'] != None, f"HitType is GBrule but no toActionFlag is provided in your csv file"


    # 2  >>>>> SETUP & DATA PREPARATION BEFORE ACTION TRIGGERING STARTS   <<<<<
    if to_triggerActionFlag == True:
        # (Automatically not via CSV), for each member,
        # For this member, reset updDate(score,mainAction,childAction of all the hits(by setting them outside validity,so that i can reuse existing testing members & not creating new one each time)
        # reset all member's existing BD to NULL & data to outside validity(to confirm if updatedBy need to be reset too..)
        # i dint reset BL/SG/memCat yet,as initial cross/single module checking wont involved this attribute(to add if needed)
        if to_reset_member == True:
            if csv_filter['memberCode'] != prev_memberCode["value"]:
                qhlp.reset_member_hits(mysql_connection, csv_filter)
                prev_memberCode["value"] = csv_filter['memberCode']

        # (initiated by csv)Before any system hit, initialise member setting by doing manual update. (both userValue & merchant update)
        # The ManualUpdate approach performs direct updates.
        if csv_filter['prerequisite1']:
            ahlp.initialise_member(api_session, api_session_SF, mysql_connection, csv_filter)

        # for outside validity period testing:
        # to fabricate updatedDate of modulehit(mainActionTable,childActionTable) and/or updatedDate of membersetting(i.e BL/SG/BD/MemCat)
        # for crossModule, csv i set to update hitDate only( no update on membersetting field like bl,sg,bd,memCat cox cross module only check hitdate to determine validityperiod)
        # for singleModule, csv i set to update both hitDate and membersetting fields. (cox single use those field to determine validityperiod when lastupdby=diffModule)
        if csv_filter['EditUpdatedDate']:
            qhlp.modify_HitDate_or_mem_attribute_date(mysql_connection, csv_filter)
        if csv_filter['pre_actionOnOffFlag']:
            ahlp.turn_OnOff_action_featureflag(api_session, csv_filter['pre_actionOnOffFlag'])
            time.sleep(4)  # time buffer to make sure flag is updated


    # 3 >>>>>  SAVE MEMBER'S SETTING (BL,SG,MemCat,isAdv,BetDelay) BEFORE HIT  <<<<<
    memSetting_before_hit = qhlp.call_mySQL_query(mysql_connection, csv_filter, "getMemDetails_Mysql.sql", None)  # 1 dict
    print('===memSetting_before_hit:===>', memSetting_before_hit)
    memBetDelay_before_hit = qhlp.call_mySQL_query(mysql_connection, csv_filter, 'getMemBetDelay_Mysql.sql', None)  # 1 dict
    memBetDelay_before_hit_dict = {item['sportid']: item['gbMemberBetDelay'] for item in
                                   memBetDelay_before_hit}  # dict
    memBetDelay_before_hit_fmt = {}
    for row in memBetDelay_before_hit:
        # key = (row["sportid"], row["sportTypeID"])
        key = row["sportid"]
        updated_by, prev_score_type = parse_updatedby(row["updatedBy"])
        memBetDelay_before_hit_fmt[key] = {
            "gbMemberBetDelay": row["gbMemberBetDelay"],
            "updatedBy": updated_by,
            "prev_scoreType": prev_score_type,
            "Bdelay_updatedAt": row['updatedAt']
        }
    print('===memBetDelay_before_hit_dict:===>', memBetDelay_before_hit_dict)

    # 4 >>>>>   TRIGGER ACTION VIA MOCK SIMULATOR  <<<<<
    # [b4 processing action logic,GB will call SF to get latest member setting 1st. i guess SF takes long to return and might cause GB to start processing late,like > 60sec0
    if to_triggerActionFlag == True:
        ahlp.trigger_module(api_session, hitObject, csv_filter)
        print(f'===triggered done for (test case#{csv_filter['testcase']}) ===>:, {datetime.now()}')
        if csv_filter['toActionFlag'].lower() == 'no':
            time.sleep(45)  #
        else:
            time.sleep(45)  # to allow time for SF to send in and update to be reflected in GB db
        print(
            f'===start verifying for (test case#{csv_filter['testcase']}) ===>:, {datetime.now()} (this time mz be after bq GBCreatedDT to work properly')

    # tear down
    if to_triggerActionFlag == True:
        if csv_filter['post_actionOnOffFlag']:
            ahlp.turn_OnOff_action_featureflag(api_session, csv_filter['post_actionOnOffFlag'])

    # 5 >>>>>  ACTION TRIGGERING done, GET ALL OF THE MODULES(RULE/FEATURES) THAT MEMBER HAS HIT BEFORE   <<<<<
    action_to_exclude = '95,96,98,99,100'  # excludes all Hit types where action is not supposed to be allowed
    # eg: featureOff,whitelist & SP/PG x found (for ActionCondNotMet, exclude only if neverMet since day 1. will cater in sql script)
    action_to_exclude_set = set(map(int, [x.strip() for x in action_to_exclude.split(',')]))
    moduleHistory_after_hit = qhlp.call_mySQL_getHitHistory(mysql_connection, csv_filter, None, action_to_exclude,
                                                       'AllHits')  # list of dict
    hitObject.hit_Single_Or_CrossModule(moduleHistory_after_hit)
    if hitObject.crossModule:
        hitObject.determine_GB_EGON_crossstatus(moduleHistory_after_hit)

    # 6  >>>>>  GET MEMBER'S SETTING (BL,SG,MemCat,isAdv,BetDelay) AFTER HIT  <<<<<
    memSetting_after_hit = qhlp.call_mySQL_query(mysql_connection, csv_filter, "getMemDetails_Mysql.sql", None)
    print('===memSetting_after_hit:===>', memSetting_after_hit)
    memBetDelay_after_hit = qhlp.call_mySQL_query(mysql_connection, csv_filter, 'getMemBetDelay_Mysql.sql', None)  # 1 dict
    memBetDelay_after_hit_dict = {item['sportid']: item['gbMemberBetDelay'] for item in memBetDelay_after_hit}
    print('===memBetDelay_after_hit_dict:===>', memBetDelay_after_hit_dict)

    companyName = companies_list.get(csv_filter['companyID'])
    assert companyName is not None, f'not able to proceed as there is not matching companyID for companyName from csv_row'

    # 7&8 >>>>CHECK THAT TRIGGERRING IS SUCCESSFUL (BY ENSURING THAT ACTION HAS BEEN SAVED IN MYSQL & TALLY WITH DEFINED ACTION FROM SP/PG UI)    <<<<<
    member_new_hit = ashlp.assert_new_hit_action(api_session, hitObject, companyName, mysql_connection,csv_filter,action_to_exclude)
    new_Hit_Action = member_new_hit[0]

    # initialise the variables
    msp_smallest_rankNum = None  # expected action to take . None means no action allowed
    spread_smallest_rankNum = None
    msp_threshold_rankNum = None
    spread_threshold_rankNum = None
    to_apply_creditScore = False
    betDelay_Severest_dict = {}
    MerrMsg = ''
    SerrMsg = ''
    expected_betDelay_dict = memBetDelay_before_hit_dict
    beforeHit_memCat = memSetting_before_hit['sfMemberCategoryID']
    afterHit_memCat = memSetting_after_hit['sfMemberCategoryID']
    afterHit_isAdv = memSetting_after_hit['sfisAdvised']
    expected_memCat = memSetting_before_hit['sfMemberCategoryID']
    expected_isAdv = memSetting_before_hit['sfisAdvised']
    MemCat_errMsg = 'noAction not allowed for this hit, but there is update on MemCat'
    isAdv_errMsg = 'noAction not allowed for this hit, but there is update on isAdv'

    # 9 >>>>> PERFORM ACTION LOGIC HERE (SINGLE/CROSS LOGIC)    <<<<<
    # perform verification only if CurrentHit is expected to have Action(eg.succ,etc..), else before and After memberSetting should remain the same
    if new_Hit_Action['has_action_to_verify'] == 'true':

        # >> >> validation on BL & SG (convert to ranking for comparison. smallest ranking = most severe)
        # ------------------------------BL/SG/BD------------------------------------------
        # 1)for crossModule, Action =  the most severe value(BL/SG is lowest rankNum, BetDelay is highest number) from HitHistory(past + new)
        # 2)for SingleModule and currentHit BL/SG has action defined(in SP or PG setting UI), Action = currentHit
        # 3)if has Action from above:
        #       ~get threshold(default userValue), to compare with Action in assertion part later on
        #       ~for below cases(singleModule), apply additional checking to the Action. else remain Action in (3)
        #           ~For Gbrule,SingleModule & user/null
        #            (goodScore) or (badScore & action less severe than defaultValue), hardcoded Action to None(action not allowed)
        #           ~For singleModule & lastUpdby=DiffModule.
        #             goodScore,hardcoded Action to None(action not allowed)
        #             badScore and withinvalidityperiod, use most severe as Action
        # 5)assertion:: with Action -> make sure not over threshold. without Action -> make sure no update
        # --------------------------------------------------------------------------------
        if hitObject.crossModule:
            print('===mem_moduleHistory_after_hit:===>', moduleHistory_after_hit)
            # get most severe value of BL,SG & BD
            msp_smallest_rankNum, spread_smallest_rankNum, betDelay_Severest_dict, memCategory_of_directEGON, isAdvised_of_directEGON, BetDelay_of_directEGON = \
                hlp.get_most_severe_value_from_all_moduleHits(hitObject, moduleHistory_after_hit, msp_smallest_rankNum,
                                                          spread_smallest_rankNum, sportGroup_sportIDs_UImap_dict,
                                                          betDelay_Severest_dict)

        # if single Modules and currentHit(MSP) has value, directly assing current Hit value
        if hitObject.singleModule and new_Hit_Action['UpdateMemberProfile']:
            msp_smallest_rankNum = hlp.get_ranking_byID(new_Hit_Action['UpdateMemberProfile'], 'msp')
        # if there is msp Action(either from Cross or Single Module)
        if msp_smallest_rankNum is not None:
            # @@changeCS:option 2 (i.e apply CS to new value first then only comparing with existing value)(for single/cross that need comopare with existing value ones)
            if apply_creditScore_FLAG == True:
                msp_smallest_rankNum,to_apply_creditScore = hlp.creditScore_application(msp_smallest_rankNum, api_CalcBL_CSfinalBL_mapping,memSetting_before_hit['appliedCreditScore'])

            msp_threshold_rankNum = hlp.get_threshold(hitObject, memSetting_before_hit, to_apply_creditScore,'msp')
            if hitObject.singleModule:
                msp_smallest_rankNum, MerrMsg = hlp.BL_SG_Single_Module_check(memSetting_before_hit, hitObject,new_Hit_Action, msp_smallest_rankNum,msp_threshold_rankNum, 'msp')
            # CRQ-513(no more special handling)
            # if hitObject.crossModule:
            #     msp_smallest_rankNum, MerrMsg = BL_SG_Cross_Module_check(memSetting_before_hit, hitObject,msp_smallest_rankNum, 'msp')
            # @@changeCS: option 1 (i.e above compare existingValud vs newValue without CS first, then here only apply CS)
            # @@right now i use option2. if option 1 is used instead, move that line (creditScore_application) here and remove option2

        # if single Modules and currentHit(SPREAD) has value, directly assing current Hit value
        if hitObject.singleModule and new_Hit_Action['UpdateMemberSpreadGroup']:
            spread_smallest_rankNum = hlp.get_ranking_byID(new_Hit_Action['UpdateMemberSpreadGroup'], 'spread')
        # if there is spread Action(either from Cross or Single Module)
        if spread_smallest_rankNum is not None:
            spread_threshold_rankNum = hlp.get_threshold(hitObject, memSetting_before_hit, to_apply_creditScore,'spread')
            if hitObject.singleModule:
                spread_smallest_rankNum, SerrMsg = hlp.BL_SG_Single_Module_check(memSetting_before_hit, hitObject,
                                                                             new_Hit_Action, spread_smallest_rankNum,
                                                                             spread_threshold_rankNum, 'spread')
            # CRQ-513(no more special handling)
            # if hitObject.crossModule:
            #     spread_smallest_rankNum, SerrMsg = BL_SG_Cross_Module_check(memSetting_before_hit, hitObject,
            #                                                                 spread_smallest_rankNum, 'spread')

        # >> ------------------------------Bet Delay------------------------------------------
        # 1)for crossModule, get most severe value of each sport from all hits(past + new)
        #                    if currentHit BD is null, system will still compare the rest of the BD to get most severe value(already handle in function)
        #   use member's original BetDelay record(memBetDelay_before_hit_dict) as base(expected_betDelay_dict).
        #   for each NewHit sport, directly replace or add into base expected_betDelay_dict
        # 2)for SingleModule,
        #    lastupdatedby=DiffModule & within validity period, use most severe BD btw existing and NewHit
        #    iif Gbrule,Good,lstUpd=user  or Gbrule,Good,DiffModule ,noAction . else direct update
        # ------------------------------Bet Delay------------------------------------------

        # for crossModule, most severe of each sports from past HitModules are stored in betDelay_Severest_dict
        # if currentHit has action, compare d sports from currentHit wif d same sports in betDelay_Severest_dict. then replace with d most severe one, or add in if currentHit sport is not inside
        # get the original sports' BD before Hit. Replace/add the currentHit triggered sports using value from betDelay_Severest_dict

        NewHit_BetDelay = int(new_Hit_Action['UpdateMemberBetDelay'])
        BDsportIDs = []  # to store sportid of new Hit
        newHit_sportGroup_list = ast.literal_eval(new_Hit_Action['UpdateBDSportGroups'])
        if hitObject.cross_GBGood_hasEGON:
            newHit_sportGroup_list = BetDelay_of_directEGON
            BDerrMsg = f'system did not use all BD is from EGON, should direct egon for this crossModule type. Behaviour Hit: {hitObject.cross_type}'
        if newHit_sportGroup_list == [-1]:
            for sportGroup in sportGroup_sportIDs_UImap_dict:  # get all from {1001: [1], 1002: [2], 1003: [54, 55], 1000: [3, 4, 5, 6, 7, 8,etc..]}
                BDsportIDs.extend(sportGroup_sportIDs_UImap_dict.get(sportGroup, []))
        else:
            for sportGroup in newHit_sportGroup_list:
                BDsportIDs.extend(sportGroup_sportIDs_UImap_dict.get(sportGroup, []))

        # print(f"new_Hit_Action['UpdateBDSportGroups'] is ,",newHit_sportGroup_list)
        # print(f"BDsportIDs 2 isss,", BDsportIDs)
        # print(f"betDelay_Severest_dict is ,", betDelay_Severest_dict)
        # expected_betDelay_dict contains member's original form of BetDelay before hit.
        # When new hit triggered, each sports' BD from new ModuleHit that is allowed to take action will direct add in(if not yet exist)/replace(if already exist) the original one in expected_betDelay_dict
        # the rest of the sports(not in newHit) should remain in expected_betDelay_dict(original form)
        if hitObject.crossModule:
            # add in/replace betDelay from new Hit into the most-severe list
            for sportid in BDsportIDs:  # for each NewHit sporttype,directly replace/add with most severe one
                # each newHit sportType is expectd to be found in betDelay_Severest_dict,as it has collected all most severe sportType from all hit including the new hit.
                if sportid in betDelay_Severest_dict:
                    #bd_lastUpdBy = memBetDelay_before_hit_fmt.get(sportid, {}).get('updatedBy')
                    #bd_existingValue = memBetDelay_before_hit_fmt.get(sportid, {}).get('gbMemberBetDelay')
                    # # remove by CRQ-531: special handling for cross_GB_Bad_EGONgood, when upgrading, bd_lastupd mz be EGON
                    # if ((hitObject.cross_GBBad_EGONGood)
                    #         and is_LT(betDelay_Severest_dict[sportid], bd_existingValue) and bd_lastUpdBy != 'GB_EGON'):
                    #     BDerrMsg = f'sport: {sportid}.BD only allowed to be upgraded if lastUpdby=EGON; behaviour: {hitObject.cross_type}'
                    # else:
                    expected_betDelay_dict[sportid] = betDelay_Severest_dict[sportid]
                    BDerrMsg = f'sport: {sportid}. BD did not use most severe; behaviour: {hitObject.cross_type}'
                else:
                    BDerrMsg = f'sport: {sportid} is not found in betDelaySeverest_dict.why?. behaviour: {hitObject.cross_type}'

        # for Single
        if hitObject.singleModule and NewHit_BetDelay is not None: #NewHit_BetDelay can be 0 too
            # Process each sportType of NewHit
            for sportid in BDsportIDs:
                bd_withinValidityPeriod = False
                bd_lastUpdBy = memBetDelay_before_hit_fmt.get(sportid, {}).get('updatedBy')
                bd_prevScoreType = memBetDelay_before_hit_fmt.get(sportid, {}).get('prev_scoreType')
                bd_existingValue = memBetDelay_before_hit_fmt.get(sportid, {}).get('gbMemberBetDelay')
                LastUpdatedby_system_BD = hlp.is_system(bd_lastUpdBy)
                if LastUpdatedby_system_BD:
                    module_validFrom_utc = hlp.get_module_validFromDate_utc(bd_lastUpdBy,'updatedby_module')
                    bd_withinValidityPeriod = hlp.check_if_within_validity_period(module_validFrom_utc,memBetDelay_before_hit_fmt.get(sportid, {}).get('Bdelay_updatedAt'))



                # process single EGON
                if hitObject.single_EGON:
                    # if lastUpdby=DiffModule & withinValidityPeriod & prevScoreType is not Good, use severity btw existing & new hit value.
                    # else direct update
                    if LastUpdatedby_system_BD and not is_match(bd_lastUpdBy,
                                                                hitObject.UpdBy_Module) and bd_withinValidityPeriod == True and bd_prevScoreType != 'Good':
                        if NewHit_BetDelay > bd_existingValue:
                            expected_betDelay_dict[sportid] = NewHit_BetDelay
                            BDerrMsg = f'bet delay failed to use most severe value btw new & existing value. behaviour Hit: singleEGON & LastUpdby=diffModule & withinValidity & LastScoreType !=good'
                        else:
                            BDerrMsg = f'BetDelay of one or more sport has been updated with newValue. Behaviour: Single EGON'
                    else:
                        BDerrMsg = f'BetDelay of one or more sport did not get updated with newValue.Behaviour: Single EGON'
                        expected_betDelay_dict[sportid] = NewHit_BetDelay

                # process single GBrule/GBfeature
                else:
                    # if Gbrule,Good,(lstUpd=user or DiffModule) ,noAction
                    if hitObject.hitGbRule and is_match(new_Hit_Action['ScoreType'], 1) and \
                            (not is_match(bd_lastUpdBy, hitObject.UpdBy_Module) or not LastUpdatedby_system_BD):
                        BDerrMsg = f'sport:{sportid}- no BD update is allowed. Behaviour Hit: GoodScore and Gbrule and (Lstupdby=User or DiffModule)'
                    # lastupdatedby=DiffModule & within validity period, use most severe BD btw existing and NewHit
                    # lastupdated by user,get most severe BD btwn existing and NewHit
                    # this elif logic will never catch lastupdated=null, since only sportid with value will exist in sportmembersetting mysql table
                    #                                  sportid with no BD before(aka lastupdated=null), will go else logic to direct update
                    #elif LastUpdatedby_system_BD and not is_match(bd_lastUpdBy,hitObject.UpdBy_Module) and bd_withinValidityPeriod == True:
                    elif (LastUpdatedby_system_BD and not is_match(bd_lastUpdBy,
                                                                       hitObject.UpdBy_Module) and bd_withinValidityPeriod == True) or not LastUpdatedby_system_BD:
                        if NewHit_BetDelay > bd_existingValue:
                            expected_betDelay_dict[sportid] = NewHit_BetDelay
                            BDerrMsg = f'BetDelay of one or more sport failed to use most severe value btw new & existing value. behaviour Hit: SingleModuleHit,LstUpdBy=DiffModule,withinvalidityPeriod'
                        else:
                            BDerrMsg = f'BetDelay of one or more sport has been updated with newValue with lower severity. behaviour Hit: SingleModuleHit,LstUpdBy=DiffModule,withinvalidityPeriod'
                    else:
                        expected_betDelay_dict[sportid] = NewHit_BetDelay
                        BDerrMsg = f'BetDelay of one or more sport did not get updated with newValue'

        # --------------------------------------------------------------------------------------
        # >> validation on member Category
        #    update only if newHit hierarchy is greater than existing hierarchy
        # --------------------------------------------------------------------------------------
        # memCategory

        new_Hit_Action_MemCat = new_Hit_Action['UpdateMemberCategory']
        new_Hit_Action_isAdv = new_Hit_Action['UpdateMemberIsAdvised']

        # overwrite newHit with new value for below cross module scenarios:
        #                   if GBgood & hasEGON, use EGON memberCategory to take action
        #                   if GBbad & EGONgood, ignore EGON (i.e if new hit is EGON, dun take any action on memberCategory)
        if hitObject.crossModule:
            # if hitObject.cross_GB_Good and hitObject.cross_has_EGON:
            if hitObject.cross_GBGood_hasEGON:
                new_Hit_Action_MemCat = memCategory_of_directEGON
                new_Hit_Action_isAdv = isAdvised_of_directEGON
            elif hitObject.cross_GB_Bad and hitObject.cross_EGON_Good and hitObject.hitGbRule and hitObject.HitID == 11:
                new_Hit_Action_MemCat = None
                new_Hit_Action_isAdv = None

        # if newHit_MemCat has Action(not None), do comparison. if None = NoAction,Before&After value are the same
        if new_Hit_Action_MemCat is not None:
            # retrieve hierarchy of memCategory for comparison
            memCat_hierarchy_of_this_company = ahlp.get_MemCat_Hierarchy(companyName, api_MemHierarchyGroupList, api_session)
            before_hit_memCat_hierarchy_ID = ahlp.get_memCat_hierarchyID(memCat_hierarchy_of_this_company['hierarchyList'],
                                                                    beforeHit_memCat)
            New_hit_memCat_hierarchy_ID = ahlp.get_memCat_hierarchyID(memCat_hierarchy_of_this_company['hierarchyList'],
                                                                 new_Hit_Action_MemCat)
            memCat_lastUpdatedBy, memCat_prevScoreType = parse_updatedby(memSetting_before_hit['sfMemberCategoryLastUpdatedBy'])
            memCat_LastUpdatedby_system = hlp.is_system(memCat_lastUpdatedBy)
            memCat_isWithinValidityPeriod = False
            if memCat_LastUpdatedby_system:
                module_validFrom_utc = hlp.get_module_validFromDate_utc(memCat_lastUpdatedBy,'updatedby_module')
                memCat_isWithinValidityPeriod = hlp.check_if_within_validity_period(module_validFrom_utc,memSetting_before_hit['sfMemberCategoryUpdatedDate'])


            # direct update with EGON:
            # For crossModule(of GBgood & hasEGON)
            # For Single EGON , direct update with EGON except for (lastUpdby=DiffModule & withinValidityPeriod & prevScore=Bad/hasGBfeature)
            if (hitObject.cross_GBGood_hasEGON) or \
                    (
                            hitObject.single_EGON and not (not is_match(memCat_lastUpdatedBy,
                                                                        hitObject.UpdBy_Module) and memCat_isWithinValidityPeriod == True and memCat_prevScoreType == 'Bad')
                    ):
                expected_memCat = new_Hit_Action_MemCat
                MemCat_errMsg = f"memCategory is not being replaced with new EGON action.behaviour:{hitObject.HitSingleOrCross} ,crossType={hitObject.cross_type}"
                if new_Hit_Action_isAdv:
                    expected_isAdv = new_Hit_Action_isAdv
                    isAdv_errMsg = f"isAdvised is not being replaced to new EGON Action.behaviour:{hitObject.HitSingleOrCross} ,crossType={hitObject.cross_type}"
                else:
                    isAdv_errMsg = f"isAdvised has been updated with new EGON Action,while memCat has no change.behaviour:{hitObject.HitSingleOrCross} ,crossType={hitObject.cross_type}"
            # update using hierarchy check
            else:
                if New_hit_memCat_hierarchy_ID > before_hit_memCat_hierarchy_ID:
                    expected_memCat = new_Hit_Action_MemCat
                    MemCat_errMsg = f"memCategory is not being updated to new memCategory with higher hierarchy.behaviour:{hitObject.HitSingleOrCross} ,crossType={hitObject.cross_type}"
                    # if newHit_isAdvise has Action(not None), do comparison. if None = NoAction,Before&After value are the same
                    if new_Hit_Action_isAdv:
                        expected_isAdv = new_Hit_Action_isAdv
                        isAdv_errMsg = f"isAdvised is not being updated to new Action.behaviour:{hitObject.HitSingleOrCross} ,crossType={hitObject.cross_type}"
                    else:
                        isAdv_errMsg = f"isAdvised has been updated.behaviour:{hitObject.HitSingleOrCross} ,crossType={hitObject.cross_type}"
                else:
                    MemCat_errMsg = f"memCategory has been wrongly updated.behaviour:{hitObject.HitSingleOrCross} ,crossType={hitObject.cross_type}"
                    isAdv_errMsg = f"isAdvised has been wrongly updated.behaviour:{hitObject.HitSingleOrCross} ,crossType={hitObject.cross_type}"

        else:
            MemCat_errMsg = f"memCat Action is null, but there is update on memCategory.behaviour:{hitObject.HitSingleOrCross} ,crossType={hitObject.cross_type}"
            isAdv_errMsg = f"isAdv Action is null, but there is update on isAdv.behaviour:{hitObject.HitSingleOrCross} ,crossType={hitObject.cross_type}"

    print('===expected_betDelay_dict:===>', expected_betDelay_dict)

    # assertion must do last , to include checking that has no action(eg.feature off,whitelist,etc..)
    assert_ActionUpdate(hitObject, msp_smallest_rankNum, msp_threshold_rankNum, memSetting_before_hit,
                        memSetting_after_hit, 'msp', api_CalcBL_CSfinalBL_mapping, MerrMsg)
    assert_ActionUpdate(hitObject, spread_smallest_rankNum, spread_threshold_rankNum, memSetting_before_hit,
                        memSetting_after_hit, 'spread', None, SerrMsg)
    assert expected_betDelay_dict == memBetDelay_after_hit_dict, f' {BDerrMsg}'
    assert is_match(expected_memCat, afterHit_memCat), f"{MemCat_errMsg}"
    assert is_match(expected_isAdv, afterHit_isAdv), f"{isAdv_errMsg}"


# ===DONEEEE(TO REFINE after this)==
# 0.revisit the db connection.  can i use db.conn commit or...
# 1.start to add in triggering and test for different scenario to make sure all works fine
# 1.see any code need to be polish to make it maintainable and understandable
##right now, my sql extract modules periodity of past 5 months. take note and change back to 3 when necessary....

# not yet handle for curent hit =feature off
# I am running from root by providing path to d script(i.e  myRootDirectory> pytest test_scenarios/test_memActions/verify_ScoreAction.py)
# use os.path.dirname(__file__) to retrieve the path of ur script. to run external file within the same path
# my pytest script is using constant.py in root/test_scenario, so need to specify 'import test_scenario.constants'
# my pytest script is in root/test_scenario/test_memActions subfolder,in order for me to import & use module in root directory, i need to do 1 of below

''' standard practise to follow:
1) False means variable contains empty value, None(no value), or 0(zero)
In Python, these values are considered "falsy" :
0 (integer zero)
0.0 (float zero)
False (boolean)
None (null value)
"" (empty string)    <--this is empty. while " " is a string with a space(length 1) and will be True
[] (empty list)
{} (empty dictionary)
() (empty tuple)

eg1: use 'if abc is not None else xxx' . dun use 'if abc else xxxx'. cox latter will treat 0 and empty data as None too...
eg2: betDelay = {}
     if betDelay == None  -> return False        ---> dun confuse between none and False pls. none is a value...False means value is empty/0/none
     if betDelay  -> return True    
2)
whenever doing comparison, make sure the dataType are the same.., when equal, use string(is_match). when >/</>=/<=, use int (is_LT,is_LTE,etc..)

 pytest test_scenarios\test_memActions\verify_ScoreAction.py -v --tb=short
'''

'''
------------------------------------------------------------------------------------------------------ Captured stdout call ------------------------------------------------------------------------------------------------------- 
===memSetting_before_hit:===> {'membercode': 'gbmock_t3449n024', 'memberid': 309235, 'companyid': 3449, 'sfMemberCategoryID': 3, 'sfisAdvised': 0, 'sfMemberCategoryLastUpdatedBy': 'GB_MemberList-admin.qa2', 'sfMemberCategoryUpda
tedDate': datetime.datetime(2026, 3, 17, 4, 15, 14), 'memCat_withinValidityPeriod': 1, '||': '||', 'defaultSfMemberSettingProfileID': 1, 'sfMemberSettingProfileID': 1, 'mexsfMemberProfileSettingLastUpdatedID': 1, 'sfMemberProfil
eSettingUpdatedDate': datetime.datetime(2026, 3, 17, 4, 15, 14), 'sfMemberProfileSettingLastUpdatedBy': 'GB_MemberList-admin.qa2', 'sfMemberProfileSettingIDUpdatedByUser': 1, 'sfMemberProfileSettingUpdatedDateByUser': datetime.d
atetime(2026, 3, 17, 4, 15, 14), 'sfMemberProfileSettingIDUpdatedByMerchant': None, 'sfMemberProfileSettingUpdatedDateByMerchant': None, 'revisedMemberProfileSettingID': None, 'msp_withinValidityPeriod': 1, 'defaultSfSpreadGroup
ID': 1, 'sfSpreadGroupID': 1, 'mexsfSpreadGroupLastUpdatedID': 1, 'sfSpreadGroupUpdatedDate': datetime.datetime(2026, 3, 17, 4, 15, 14), 'sfSpreadGroupLastUpdatedBy': 'GB_MemberList-admin.qa2', 'sfSpreadGroupIDUpdatedByUser': 1,
 'sfSpreadGroupUpdatedDateByUser': datetime.datetime(2026, 3, 17, 4, 15, 14), 'revisedSpreadGroupID': None, 'sfSpreadGroupIDUpdatedByMerchant': None, 'sfSpreadGroupUpdatedDateByMerchant': None, 'revisedValueUpdatedDate': None, 'spread_withinValidityPeriod': 1}
===memBetDelay_before_hit_dict:===> {(1, 1): 0, (1, 2): 0, (2, 1): 0, (2, 2): 0, (3, 1): 0, (3, 2): 0, (4, 1): 0, (4, 2): 0, (5, 1): 0, (5, 2): 0, (6, 1): 0, (6, 2): 0, (7, 1): 0, (7, 2): 0, (8, 1): 0, (8, 2): 0, (9, 1): 0, (9, 
2): 0, (10, 1): 0, (10, 2): 0, (11, 1): 0, (11, 2): 0, (12, 1): 0, (12, 2): 0, (13, 1): 0, (13, 2): 0, (14, 1): 0, (14, 2): 0, (15, 1): 0, (15, 2): 0, (16, 1): 0, (16, 2): 0, (17, 1): 0, (17, 2): 0, (18, 1): 0, (18, 2): 0, (19, 
1): 0, (19, 2): 0, (20, 1): 0, (20, 2): 0, (21, 1): 0, (21, 2): 0, (22, 1): 0, (22, 2): 0, (23, 1): 0, (23, 2): 0, (24, 1): 0, (24, 2): 0, (25, 1): 0, (25, 2): 0, (26, 1): 0, (26, 2): 0, (27, 1): 0, (27, 2): 0, (28, 1): 0, (28, 
2): 0, (29, 1): 0, (29, 2): 0, (30, 1): 0, (30, 2): 0, (31, 1): 0, (31, 2): 0, (32, 1): 0, (32, 2): 0, (33, 1): 0, (33, 2): 0, (34, 1): 0, (34, 2): 0, (35, 1): 0, (35, 2): 0, (36, 1): 0, (36, 2): 0, (37, 1): 0, (37, 2): 0, (38, 
1): 0, (38, 2): 0, (39, 1): 0, (39, 2): 0, (40, 1): 0, (40, 2): 0, (41, 1): 0, (41, 2): 0, (42, 1): 0, (42, 2): 0, (43, 1): 0, (43, 2): 0, (44, 1): 0, (44, 2): 0, (45, 1): 0, (45, 2): 0, (46, 1): 0, (46, 2): 0, (47, 1): 0, (47, 
2): 0, (48, 1): 0, (48, 2): 0, (49, 1): 0, (49, 2): 0, (50, 1): 0, (50, 2): 0, (51, 1): 0, (51, 2): 0, (52, 1): 0, (52, 2): 0, (53, 1): 0, (53, 2): 0, (54, 1): 0, (54, 2): 0, (55, 1): 0, (55, 2): 0, (56, 1): 0, (56, 2): 0, (57, 
1): 0, (57, 2): 0, (58, 1): 0, (58, 2): 0, (59, 1): 0, (59, 2): 0, (60, 1): 0, (60, 2): 0, (61, 1): 0, (61, 2): 0, (62, 1): 0, (62, 2): 0, (63, 1): 0, (63, 2): 0, (64, 1): 0, (64, 2): 0, (65, 1): 0, (65, 2): 0, (66, 1): 0, (66, 2): 0, (67, 1): 0, (67, 2): 0}
===triggered done for test case: 1 ===>: 2026-03-17 12:16:13.888910
===start verifying at              ===>: 2026-03-17 12:17:13.889992
===memSetting_after_hit:===> {'membercode': 'gbmock_t3449n024', 'memberid': 309235, 'companyid': 3449, 'sfMemberCategoryID': 1, 'sfisAdvised': 1, 'sfMemberCategoryLastUpdatedBy': 'GB_EGON_1', 'sfMemberCategoryUpdatedDate': datet
ime.datetime(2026, 3, 17, 4, 16, 20), 'memCat_withinValidityPeriod': 1, '||': '||', 'defaultSfMemberSettingProfileID': 1, 'sfMemberSettingProfileID': 18, 'mexsfMemberProfileSettingLastUpdatedID': 18, 'sfMemberProfileSettingUpdat
edDate': datetime.datetime(2026, 3, 17, 4, 16, 20), 'sfMemberProfileSettingLastUpdatedBy': 'GB_EGON_1', 'sfMemberProfileSettingIDUpdatedByUser': 1, 'sfMemberProfileSettingUpdatedDateByUser': datetime.datetime(2026, 3, 17, 4, 15,
 14), 'sfMemberProfileSettingIDUpdatedByMerchant': None, 'sfMemberProfileSettingUpdatedDateByMerchant': None, 'revisedMemberProfileSettingID': None, 'msp_withinValidityPeriod': 1, 'defaultSfSpreadGroupID': 1, 'sfSpreadGroupID': 
3, 'mexsfSpreadGroupLastUpdatedID': 3, 'sfSpreadGroupUpdatedDate': datetime.datetime(2026, 3, 17, 4, 16, 20), 'sfSpreadGroupLastUpdatedBy': 'GB_EGON_1', 'sfSpreadGroupIDUpdatedByUser': 1, 'sfSpreadGroupUpdatedDateByUser': datetime.datetime(2026, 3, 17, 4, 15, 14), 'revisedSpreadGroupID': None, 'sfSpreadGroupIDUpdatedByMerchant': None, 'sfSpreadGroupUpdatedDateByMerchant': None, 'revisedValueUpdatedDate': None, 'spread_withinValidityPeriod': 1}
===memBetDelay_after_hit_dict:===> {(1, 1): 3, (1, 2): 3, (2, 1): 3, (2, 2): 3, (3, 1): 3, (3, 2): 3, (4, 1): 3, (4, 2): 3, (5, 1): 3, (5, 2): 3, (6, 1): 3, (6, 2): 3, (7, 1): 3, (7, 2): 3, (8, 1): 3, (8, 2): 3, (9, 1): 3, (9, 2
): 3, (10, 1): 3, (10, 2): 3, (11, 1): 3, (11, 2): 3, (12, 1): 3, (12, 2): 3, (13, 1): 3, (13, 2): 3, (14, 1): 3, (14, 2): 3, (15, 1): 3, (15, 2): 3, (16, 1): 3, (16, 2): 3, (17, 1): 3, (17, 2): 3, (18, 1): 3, (18, 2): 3, (19, 1
): 3, (19, 2): 3, (20, 1): 3, (20, 2): 3, (21, 1): 3, (21, 2): 3, (22, 1): 3, (22, 2): 3, (23, 1): 3, (23, 2): 3, (24, 1): 3, (24, 2): 3, (25, 1): 3, (25, 2): 3, (26, 1): 3, (26, 2): 3, (27, 1): 3, (27, 2): 3, (28, 1): 3, (28, 2
): 3, (29, 1): 3, (29, 2): 3, (30, 1): 3, (30, 2): 3, (31, 1): 3, (31, 2): 3, (32, 1): 3, (32, 2): 3, (33, 1): 3, (33, 2): 3, (34, 1): 3, (34, 2): 3, (35, 1): 3, (35, 2): 3, (36, 1): 3, (36, 2): 3, (37, 1): 3, (37, 2): 3, (38, 1
): 3, (38, 2): 3, (39, 1): 3, (39, 2): 3, (40, 1): 3, (40, 2): 3, (41, 1): 3, (41, 2): 3, (42, 1): 3, (42, 2): 3, (43, 1): 3, (43, 2): 3, (44, 1): 3, (44, 2): 3, (45, 1): 3, (45, 2): 3, (46, 1): 3, (46, 2): 3, (47, 1): 3, (47, 2
): 3, (48, 1): 3, (48, 2): 3, (49, 1): 3, (49, 2): 3, (50, 1): 3, (50, 2): 3, (51, 1): 3, (51, 2): 3, (52, 1): 3, (52, 2): 3, (53, 1): 3, (53, 2): 3, (54, 1): 3, (54, 2): 3, (55, 1): 3, (55, 2): 3, (56, 1): 3, (56, 2): 3, (57, 1
): 3, (57, 2): 3, (58, 1): 3, (58, 2): 3, (59, 1): 3, (59, 2): 3, (60, 1): 3, (60, 2): 3, (61, 1): 3, (61, 2): 3, (62, 1): 3, (62, 2): 3, (63, 1): 3, (63, 2): 3, (64, 1): 3, (64, 2): 3, (65, 1): 3, (65, 2): 3, (66, 1): 3, (66, 2): 3, (67, 1): 3, (67, 2): 3}
===new_Hit_Action:===> {'membercode': 'gbmock_t3449n024', 'companyid': 3449, 'memberid': 309235, 'scr_batchID': '0', 'scr_gbRuleID': '11', 'src_gbruleName': 'EGON', 'prof_moduleID': ' ', 'prof_featureName': ' ', 'actionStatusID'
: 1, 'displayName': 'Action - Success', 'createdAt': datetime.datetime(2026, 3, 16, 8, 36, 5), 'createdBy': 'GB_EGON', 'updatedAt': datetime.datetime(2026, 3, 17, 4, 16, 14), 'updatedAt_GMTMinus4': datetime.datetime(2026, 3, 17,
 0, 16, 14), 'updatedby': 'GB_EGON', 'scr_gbRuleBandID': '144', 'scr_scoreProfileID': '80', 'prof_profileGroupID': ' ', 'latest_score': '30', 'lastWfActn_score': '30', 'lastWfActn_updatedAt': '2026-03-17 04:16:14', 'has_action_t
o_verify': 'true', 'gbmoduleid': ' ', 'gbruleid': '11', 'latest_ScoreType': '1', 'latest_BetDelay': '3', 'latest_MemberProfile': '18', 'latest_SpreadGroup': '3', 'latest_MemberCategory': '1', 'latest_IsAdvised': '1', 'latest_Not
ifyMerchant': '0', 'lastWfActn_ScoreType': '1', 'lastWfActn_BetDelay': '3', 'lastWfActn_MemberProfile': '18', 'lastWfActn_SpreadGroup': '3', 'lastWfActn_MemberCategory': '1', 'lastWfActn_IsAdvised': '1', 'lastWfActn_NotifyMerchant': '0', 'score': '30', 'ScoreType': '1', 'UpdateMemberBetDelay': '3', 'UpdateMemberProfile': '18', 'UpdateMemberSpreadGroup': '3', 'UpdateMemberCategory': '1', 'UpdateMemberIsAdvised': '1', 'UpdateNotifyMerchant': '0'}        
moduletocall=====,{2: [(2, 1)], 1: [(1, 1)], 4: [(1, 1), (1, 2), (2, 1), (2, 2), (54, 2), (55, 2)], 10: [(2, 1)], 6: [(2, 1)], 5: [(1, 1)], 7: [(1, 1), (1, 2), (2, 1), (2, 2), (3, 1), (3, 2), (4, 1), (4, 2), (5, 1), (5, 2), (6, 
1), (6, 2), (7, 1), (7, 2), (8, 1), (8, 2), (9, 1), (9, 2), (10, 1), (10, 2), (11, 1), (11, 2), (12, 1), (12, 2), (13, 1), (13, 2), (14, 1), (14, 2), (15, 1), (15, 2), (16, 1), (16, 2), (17, 1), (17, 2), (18, 1), (18, 2), (19, 1
), (19, 2), (20, 1), (20, 2), (21, 1), (21, 2), (22, 1), (22, 2), (23, 1), (23, 2), (24, 1), (24, 2), (25, 1), (25, 2), (26, 1), (26, 2), (27, 1), (27, 2), (28, 1), (28, 2), (29, 1), (29, 2), (30, 1), (30, 2), (31, 1), (31, 2), 
(32, 1), (32, 2), (33, 1), (33, 2), (34, 1), (34, 2), (35, 1), (35, 2), (36, 1), (36, 2), (37, 1), (37, 2), (38, 1), (38, 2), (39, 1), (39, 2), (40, 1), (40, 2), (41, 1), (41, 2), (42, 1), (42, 2), (43, 1), (43, 2), (44, 1), (44
, 2), (45, 1), (45, 2), (46, 1), (46, 2), (47, 1), (47, 2), (48, 1), (48, 2), (49, 1), (49, 2), (50, 1), (50, 2), (51, 1), (51, 2), (52, 1), (52, 2), (53, 1), (53, 2), (54, 1), (54, 2), (55, 1), (55, 2), (56, 1), (56, 2), (57, 1
), (57, 2), (58, 1), (58, 2), (59, 1), (59, 2), (60, 1), (60, 2), (61, 1), (61, 2), (62, 1), (62, 2), (63, 1), (63, 2), (64, 1), (64, 2), (65, 1), (65, 2), (66, 1), (66, 2), (67, 1), (67, 2)], 3: [(1, 1), (2, 1)], 9: [(2, 1)], 8
: [(1, 1)], 11: [(1, 1), (1, 2), (2, 1), (2, 2), (3, 1), (3, 2), (4, 1), (4, 2), (5, 1), (5, 2), (6, 1), (6, 2), (7, 1), (7, 2), (8, 1), (8, 2), (9, 1), (9, 2), (10, 1), (10, 2), (11, 1), (11, 2), (12, 1), (12, 2), (13, 1), (13,
 2), (14, 1), (14, 2), (15, 1), (15, 2), (16, 1), (16, 2), (17, 1), (17, 2), (18, 1), (18, 2), (19, 1), (19, 2), (20, 1), (20, 2), (21, 1), (21, 2), (22, 1), (22, 2), (23, 1), (23, 2), (24, 1), (24, 2), (25, 1), (25, 2), (26, 1)
, (26, 2), (27, 1), (27, 2), (28, 1), (28, 2), (29, 1), (29, 2), (30, 1), (30, 2), (31, 1), (31, 2), (32, 1), (32, 2), (33, 1), (33, 2), (34, 1), (34, 2), (35, 1), (35, 2), (36, 1), (36, 2), (37, 1), (37, 2), (38, 1), (38, 2), (
39, 1), (39, 2), (40, 1), (40, 2), (41, 1), (41, 2), (42, 1), (42, 2), (43, 1), (43, 2), (44, 1), (44, 2), (45, 1), (45, 2), (46, 1), (46, 2), (47, 1), (47, 2), (48, 1), (48, 2), (49, 1), (49, 2), (50, 1), (50, 2), (51, 1), (51,
 2), (52, 1), (52, 2), (53, 1), (53, 2), (54, 1), (54, 2), (55, 1), (55, 2), (56, 1), (56, 2), (57, 1), (57, 2), (58, 1), (58, 2), (59, 1), (59, 2), (60, 1), (60, 2), (61, 1), (61, 2), (62, 1), (62, 2), (63, 1), (63, 2), (64, 1), (64, 2), (65, 1), (65, 2), (66, 1), (66, 2), (67, 1), (67, 2)], 16: [(1, 1)], 17: [(1, 1)]}
==memBetDelay_before_hit_fmt====. {1: {'gbMemberBetDelay': None, 'updatedBy': 'GB_FAMemFeatures_InvKey', 'prev_scoreType': 'Bad', 'Bdelay_updatedAt': datetime.datetime(2025, 2, 2, 4, 0)}, 2: {'gbMemberBetDelay': None, 'updatedBy
': 'GB_FAMemFeatures_InvKey', 'prev_scoreType': 'Bad', 'Bdelay_updatedAt': datetime.datetime(2025, 2, 2, 4, 0)}, 3: {'gbMemberBetDelay': None, 'updatedBy': 'GB_EGON', 'prev_scoreType': 'Bad', 'Bdelay_updatedAt': datetime.datetim
e(2025, 2, 2, 4, 0)}, 4: {'gbMemberBetDelay': None, 'updatedBy': 'GB_EGON', 'prev_scoreType': 'Bad', 'Bdelay_updatedAt': datetime.datetime(2025, 2, 2, 4, 0)}, 5: {'gbMemberBetDelay': None, 'updatedBy': 'GB_EGON', 'prev_scoreType
': 'Bad', 'Bdelay_updatedAt': datetime.datetime(2025, 2, 2, 4, 0)}, 6: {'gbMemberBetDelay': None, 'updatedBy': 'GB_EGON', 'prev_scoreType': 'Bad', 'Bdelay_updatedAt': datetime.datetime(2025, 2, 2, 4, 0)}, 7: {'gbMemberBetDelay':
 None, 'updatedBy': 'GB_EGON', 'prev_scoreType': 'Bad', 'Bdelay_updatedAt': datetime.datetime(2025, 2, 2, 4, 0)}, 8: {'gbMemberBetDelay': None, 'updatedBy': 'GB_EGON', 'prev_scoreType': 'Bad', 'Bdelay_updatedAt': datetime.dateti
me(2025, 2, 2, 4, 0)}, 9: {'gbMemberBetDelay': None, 'updatedBy': 'GB_EGON', 'prev_scoreType': 'Bad', 'Bdelay_updatedAt': datetime.datetime(2025, 2, 2, 4, 0)}, 10: {'gbMemberBetDelay': None, 'updatedBy': 'GB_EGON', 'prev_scoreTy
pe': 'Bad', 'Bdelay_updatedAt': datetime.datetime(2025, 2, 2, 4, 0)}, 11: {'gbMemberBetDelay': None, 'updatedBy': 'GB_EGON', 'prev_scoreType': 'Bad', 'Bdelay_updatedAt': datetime.datetime(2025, 2, 2, 4, 0)}, 12: {'gbMemberBetDel
ay': None, 'updatedBy': 'GB_EGON', 'prev_scoreType': 'Bad', 'Bdelay_updatedAt': datetime.datetime(2025, 2, 2, 4, 0)}, 13: {'gbMemberBetDelay': None, 'updatedBy': 'GB_EGON', 'prev_scoreType': 'Bad', 'Bdelay_updatedAt': datetime.d
atetime(2025, 2, 2, 4, 0)}, 14: {'gbMemberBetDelay': None, 'updatedBy': 'GB_EGON', 'prev_scoreType': 'Bad', 'Bdelay_updatedAt': datetime.datetime(2025, 2, 2, 4, 0)}, 15: {'gbMemberBetDelay': None, 'updatedBy': 'GB_EGON', 'prev_s
coreType': 'Bad', 'Bdelay_updatedAt': datetime.datetime(2025, 2, 2, 4, 0)}, 16: {'gbMemberBetDelay': None, 'updatedBy': 'GB_EGON', 'prev_scoreType': 'Bad', 'Bdelay_updatedAt': datetime.datetime(2025, 2, 2, 4, 0)}, 17: {'gbMember
BetDelay': None, 'updatedBy': 'GB_EGON', 'prev_scoreType': 'Bad', 'Bdelay_updatedAt': datetime.datetime(2025, 2, 2, 4, 0)}, 18: {'gbMemberBetDelay': None, 'updatedBy': 'GB_EGON', 'prev_scoreType': 'Bad', 'Bdelay_updatedAt': date
time.datetime(2025, 2, 2, 4, 0)}, 19: {'gbMemberBetDelay': None, 'updatedBy': 'GB_EGON', 'prev_scoreType': 'Bad', 'Bdelay_updatedAt': datetime.datetime(2025, 2, 2, 4, 0)}, 20: {'gbMemberBetDelay': None, 'updatedBy': 'GB_EGON', '
prev_scoreType': 'Bad', 'Bdelay_updatedAt': datetime.datetime(2025, 2, 2, 4, 0)}, 21: {'gbMemberBetDelay': None, 'updatedBy': 'GB_EGON', 'prev_scoreType': 'Bad', 'Bdelay_updatedAt': datetime.datetime(2025, 2, 2, 4, 0)}, 22: {'gb
MemberBetDelay': None, 'updatedBy': 'GB_EGON', 'prev_scoreType': 'Bad', 'Bdelay_updatedAt': datetime.datetime(2025, 2, 2, 4, 0)}, 23: {'gbMemberBetDelay': None, 'updatedBy': 'GB_EGON', 'prev_scoreType': 'Bad', 'Bdelay_updatedAt'
: datetime.datetime(2025, 2, 2, 4, 0)}, 24: {'gbMemberBetDelay': None, 'updatedBy': 'GB_EGON', 'prev_scoreType': 'Bad', 'Bdelay_updatedAt': datetime.datetime(2025, 2, 2, 4, 0)}, 25: {'gbMemberBetDelay': None, 'updatedBy': 'GB_EG
ON', 'prev_scoreType': 'Bad', 'Bdelay_updatedAt': datetime.datetime(2025, 2, 2, 4, 0)}, 26: {'gbMemberBetDelay': None, 'updatedBy': 'GB_EGON', 'prev_scoreType': 'Bad', 'Bdelay_updatedAt': datetime.datetime(2025, 2, 2, 4, 0)}, 27
: {'gbMemberBetDelay': None, 'updatedBy': 'GB_EGON', 'prev_scoreType': 'Bad', 'Bdelay_updatedAt': datetime.datetime(2025, 2, 2, 4, 0)}, 28: {'gbMemberBetDelay': None, 'updatedBy': 'GB_EGON', 'prev_scoreType': 'Bad', 'Bdelay_upda
tedAt': datetime.datetime(2025, 2, 2, 4, 0)}, 29: {'gbMemberBetDelay': None, 'updatedBy': 'GB_EGON', 'prev_scoreType': 'Bad', 'Bdelay_updatedAt': datetime.datetime(2025, 2, 2, 4, 0)}, 30: {'gbMemberBetDelay': None, 'updatedBy': 
'GB_EGON', 'prev_scoreType': 'Bad', 'Bdelay_updatedAt': datetime.datetime(2025, 2, 2, 4, 0)}, 31: {'gbMemberBetDelay': None, 'updatedBy': 'GB_EGON', 'prev_scoreType': 'Bad', 'Bdelay_updatedAt': datetime.datetime(2025, 2, 2, 4, 0
)}, 32: {'gbMemberBetDelay': None, 'updatedBy': 'GB_EGON', 'prev_scoreType': 'Bad', 'Bdelay_updatedAt': datetime.datetime(2025, 2, 2, 4, 0)}, 33: {'gbMemberBetDelay': None, 'updatedBy': 'GB_EGON', 'prev_scoreType': 'Bad', 'Bdela
y_updatedAt': datetime.datetime(2025, 2, 2, 4, 0)}, 34: {'gbMemberBetDelay': None, 'updatedBy': 'GB_EGON', 'prev_scoreType': 'Bad', 'Bdelay_updatedAt': datetime.datetime(2025, 2, 2, 4, 0)}, 35: {'gbMemberBetDelay': None, 'update
dBy': 'GB_EGON', 'prev_scoreType': 'Bad', 'Bdelay_updatedAt': datetime.datetime(2025, 2, 2, 4, 0)}, 36: {'gbMemberBetDelay': None, 'updatedBy': 'GB_EGON', 'prev_scoreType': 'Bad', 'Bdelay_updatedAt': datetime.datetime(2025, 2, 2
, 4, 0)}, 37: {'gbMemberBetDelay': None, 'updatedBy': 'GB_EGON', 'prev_scoreType': 'Bad', 'Bdelay_updatedAt': datetime.datetime(2025, 2, 2, 4, 0)}, 38: {'gbMemberBetDelay': None, 'updatedBy': 'GB_EGON', 'prev_scoreType': 'Bad', 
'Bdelay_updatedAt': datetime.datetime(2025, 2, 2, 4, 0)}, 39: {'gbMemberBetDelay': None, 'updatedBy': 'GB_EGON', 'prev_scoreType': 'Bad', 'Bdelay_updatedAt': datetime.datetime(2025, 2, 2, 4, 0)}, 40: {'gbMemberBetDelay': None, '
updatedBy': 'GB_EGON', 'prev_scoreType': 'Bad', 'Bdelay_updatedAt': datetime.datetime(2025, 2, 2, 4, 0)}, 41: {'gbMemberBetDelay': None, 'updatedBy': 'GB_EGON', 'prev_scoreType': 'Bad', 'Bdelay_updatedAt': datetime.datetime(2025
, 2, 2, 4, 0)}, 42: {'gbMemberBetDelay': None, 'updatedBy': 'GB_EGON', 'prev_scoreType': 'Bad', 'Bdelay_updatedAt': datetime.datetime(2025, 2, 2, 4, 0)}, 43: {'gbMemberBetDelay': None, 'updatedBy': 'GB_EGON', 'prev_scoreType': '
Bad', 'Bdelay_updatedAt': datetime.datetime(2025, 2, 2, 4, 0)}, 44: {'gbMemberBetDelay': None, 'updatedBy': 'GB_EGON', 'prev_scoreType': 'Bad', 'Bdelay_updatedAt': datetime.datetime(2025, 2, 2, 4, 0)}, 45: {'gbMemberBetDelay': N
one, 'updatedBy': 'GB_EGON', 'prev_scoreType': 'Bad', 'Bdelay_updatedAt': datetime.datetime(2025, 2, 2, 4, 0)}, 46: {'gbMemberBetDelay': None, 'updatedBy': 'GB_EGON', 'prev_scoreType': 'Bad', 'Bdelay_updatedAt': datetime.datetim
e(2025, 2, 2, 4, 0)}, 47: {'gbMemberBetDelay': None, 'updatedBy': 'GB_EGON', 'prev_scoreType': 'Bad', 'Bdelay_updatedAt': datetime.datetime(2025, 2, 2, 4, 0)}, 48: {'gbMemberBetDelay': None, 'updatedBy': 'GB_EGON', 'prev_scoreTy
pe': 'Bad', 'Bdelay_updatedAt': datetime.datetime(2025, 2, 2, 4, 0)}, 49: {'gbMemberBetDelay': None, 'updatedBy': 'GB_EGON', 'prev_scoreType': 'Bad', 'Bdelay_updatedAt': datetime.datetime(2025, 2, 2, 4, 0)}, 50: {'gbMemberBetDel
ay': None, 'updatedBy': 'GB_EGON', 'prev_scoreType': 'Bad', 'Bdelay_updatedAt': datetime.datetime(2025, 2, 2, 4, 0)}, 51: {'gbMemberBetDelay': None, 'updatedBy': 'GB_EGON', 'prev_scoreType': 'Bad', 'Bdelay_updatedAt': datetime.d
atetime(2025, 2, 2, 4, 0)}, 52: {'gbMemberBetDelay': None, 'updatedBy': 'GB_EGON', 'prev_scoreType': 'Bad', 'Bdelay_updatedAt': datetime.datetime(2025, 2, 2, 4, 0)}, 53: {'gbMemberBetDelay': None, 'updatedBy': 'GB_EGON', 'prev_s
coreType': 'Bad', 'Bdelay_updatedAt': datetime.datetime(2025, 2, 2, 4, 0)}, 54: {'gbMemberBetDelay': None, 'updatedBy': 'GB_FAMemFeatures_InvKey', 'prev_scoreType': 'Bad', 'Bdelay_updatedAt': datetime.datetime(2025, 2, 2, 4, 0)}
, 55: {'gbMemberBetDelay': None, 'updatedBy': 'GB_FAMemFeatures_InvKey', 'prev_scoreType': 'Bad', 'Bdelay_updatedAt': datetime.datetime(2025, 2, 2, 4, 0)}, 56: {'gbMemberBetDelay': None, 'updatedBy': 'GB_EGON', 'prev_scoreType':
 'Bad', 'Bdelay_updatedAt': datetime.datetime(2025, 2, 2, 4, 0)}, 57: {'gbMemberBetDelay': None, 'updatedBy': 'GB_EGON', 'prev_scoreType': 'Bad', 'Bdelay_updatedAt': datetime.datetime(2025, 2, 2, 4, 0)}, 58: {'gbMemberBetDelay':
 None, 'updatedBy': 'GB_EGON', 'prev_scoreType': 'Bad', 'Bdelay_updatedAt': datetime.datetime(2025, 2, 2, 4, 0)}, 59: {'gbMemberBetDelay': None, 'updatedBy': 'GB_EGON', 'prev_scoreType': 'Bad', 'Bdelay_updatedAt': datetime.datet
ime(2025, 2, 2, 4, 0)}, 60: {'gbMemberBetDelay': None, 'updatedBy': 'GB_EGON', 'prev_scoreType': 'Bad', 'Bdelay_updatedAt': datetime.datetime(2025, 2, 2, 4, 0)}, 61: {'gbMemberBetDelay': None, 'updatedBy': 'GB_EGON', 'prev_score
Type': 'Bad', 'Bdelay_updatedAt': datetime.datetime(2025, 2, 2, 4, 0)}, 62: {'gbMemberBetDelay': None, 'updatedBy': 'GB_EGON', 'prev_scoreType': 'Bad', 'Bdelay_updatedAt': datetime.datetime(2025, 2, 2, 4, 0)}, 63: {'gbMemberBetD
elay': None, 'updatedBy': 'GB_EGON', 'prev_scoreType': 'Bad', 'Bdelay_updatedAt': datetime.datetime(2025, 2, 2, 4, 0)}, 64: {'gbMemberBetDelay': None, 'updatedBy': 'GB_EGON', 'prev_scoreType': 'Bad', 'Bdelay_updatedAt': datetime
.datetime(2025, 2, 2, 4, 0)}, 65: {'gbMemberBetDelay': None, 'updatedBy': 'GB_EGON', 'prev_scoreType': 'Bad', 'Bdelay_updatedAt': datetime.datetime(2025, 2, 2, 4, 0)}, 66: {'gbMemberBetDelay': None, 'updatedBy': 'GB_EGON', 'prev_scoreType': 'Bad', 'Bdelay_updatedAt': datetime.datetime(2025, 2, 2, 4, 0)}, 67: {'gbMemberBetDelay': None, 'updatedBy': 'GB_EGON', 'prev_scoreType': 'Bad', 'Bdelay_updatedAt': datetime.datetime(2025, 2, 2, 4, 0)}}

---------------------------------------------------------------------------------------------------- Captured stdout teardown -

'''











