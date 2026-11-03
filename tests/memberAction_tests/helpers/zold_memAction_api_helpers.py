
import pytest
import time
import os
from datetime import datetime, timezone, timedelta
import tests.myConstants as const  ##not found in sys.path, so just directly add the folder name
from tests.memberAction_tests.helpers.myHelperFunc import call_api
import tests.memberAction_tests.helpers.memAction_sql_helpers as qhlp
from tests.utils.comparison_utils import is_match, is_LT
from tests.memberAction_tests.mappingModule import SpreadGroupMappers, MemberProfileSettingMappers, GbRuleMapper, GbFeatureMapper
import warnings
import tests.memberAction_tests.memberAction_Constants as action_const

def get_MemCat_Hierarchy(companyName, api_MemHierarchyGroupList, api_session):
    '''
    memberCategory Hierarchy is not fixed. so cannot hardcoded like limit & spread
    diff company has diff hierarchy for their member. it is defined in memberCategorySetting UI
    '''
    memCat_Hierarchy_GrpID = api_MemHierarchyGroupList.get(
        companyName)  # get the groupName/ID where this company defined
    url = f"{const.API_BASE_URL}/MemberSetting/GetMemberCategoryGroupByID"
    data = {"memberCategoryGroupID": memCat_Hierarchy_GrpID}  # return list of hierarchy for this company
    response = call_api(api_session, 'get_MemCat_Hierarchy', 'post', url, data)
    assert response.status_code == 200, f"calling to get_MemCat_Hierarchy return {response.status_code} "
    return response.json()['data']


def get_memCat_hierarchyID(memCat_hierarchy, sfMemberCategoryID):
    int_sfMemberCategoryID = int(sfMemberCategoryID)
    memCat_hierarchy_ID = next((item['hierarchy'] for item in memCat_hierarchy \
                                if item['memberCategoryID'] == int_sfMemberCategoryID), None)
    return memCat_hierarchy_ID


def get_action(api_session, hitObject, companyName, ruleScore):
    if hitObject.hitGbRule:
        url = f"{const.API_BASE_URL}/MemberSetting/GetScoreProfileList"
        data = {"profileName": "", "status": 1, "gbRuleIDs": [hitObject.HitID], "page": 1, "pageSize": 100}
        response = call_api(api_session, 'get_action', 'post', url, data)
        assert response.status_code == 200, f"calling to GetScoreProfileList return {response.status_code} "
        scoreProfileID = next((item['scoreProfileID'] for item in response.json()['data'] if
                               companyName in [name.strip() for name in item['companyName'].split(',')]), None)
        # check if it is in Group with company 'excludeOnly' or 'All',as backend wont return long list company to UI
        # 'excludeOnly' & 'All', only 1 type can exist. if not in those group, then this company is really not defined yet
        if scoreProfileID == None:
            scoreProfileID = next((item['scoreProfileID'] for item in response.json()['data'] if
                                   item['companyType'] in [0, 2]), None)
        url = f"{const.API_BASE_URL}/MemberSetting/GetScoreProfileByID"
        data = {"scoreProfileID": scoreProfileID}
        response = call_api(api_session, 'GetScoreProfileByID', 'post', url, data)
        assert response.status_code == 200, f"calling to GetScoreProfileByID return {response.status_code} for data {data} "
        actionList = response.json()['data']['actionList']
        bandAction = next(band for band in actionList if band['gbRuleBandName'] == str(
            ruleScore))  # ScoreProfile has diff set ofAction for diff scoreBand
        # will return None if defined as NoAction or return -998 if leave it blank.
        # use this approach to get 1st trusty value in bracket. (None, 3) -> will return 3
        #      in case bandAction.get('memberSettingProfileSelected') is None, use {}. as None do not have get attribute, will throw error
        new_MemberSettingProfileID = None if (bandAction.get('memberSettingProfileSelected') or {}).get('value') in (
        None, -998) else bandAction['memberSettingProfileSelected']['value']
        new_SpreadGroupID = None if (bandAction.get('memberSpreadGroupSelected') or {}).get('value') in (
        None, -998) else bandAction['memberSpreadGroupSelected']['value']
        new_ScoretypeID = bandAction['scoreTypeSelected']['value']
        new_BetDelayID = bandAction['memberBetDelay']
        new_MemberCategoryID = None if (bandAction.get('memberCategorySelected') or {}).get('value') in (
        None, -998) else bandAction['memberCategorySelected']['value']
        new_IsAdvisedID = None if (bandAction.get('isAdvisedSelected') or {}).get('value') in (None, -998) else \
        bandAction['isAdvisedSelected']['value']
        new_IsNotifyMerchantID = None if (bandAction.get('isNotifyMerchantSelected') or {}).get('value') in (
        None, -998) else \
            bandAction['isNotifyMerchantSelected']['value']
        betdelayGroupList = response.json()['data']['sportGroupList']  # ==[{1001,soccer},{1002,bb}]
        new_BDSportGroupIDs = [BDsportgroup["sportGroupID"] for BDsportgroup in betdelayGroupList]  # [1000,1001,-1]
        new_BDSportGroupIDs = [
            -1] if -1 in new_BDSportGroupIDs else new_BDSportGroupIDs  # if has -1 then [-1] else remain [1001,1002]
        print(f"SP/PG ui sportGgroup is ,", new_BDSportGroupIDs)
    elif hitObject.hitGbFeature:
        url = f"{const.API_BASE_URL}/MemberSetting/GetMemberProfileGroupList"
        data = {"memberProfileGroupName": "", "status": 1, "gbFeatureModules": [hitObject.HitID], "page": 1,
                "pageSize": 100}
        response = call_api(api_session, 'GetMemberProfileGroupList', 'post', url, data)
        assert response.status_code == 200, f"calling to GetMemberProfileGroupList return {response.status_code} "
        memberProfileGroupID = next((item['id'] for item in response.json()['data'] if
                                     companyName in [name.strip() for name in item['companyName'].split(',')]), None)
        if memberProfileGroupID == None:
            memberProfileGroupID = next((item['memberProfileGroupID'] for item in response.json()['data'] if
                                         item['companyType'] in [0, 2]), None)
        url = f"{const.API_BASE_URL}/MemberSetting/GetMemberProfileGroupByID"
        data = {"memberProfileGroupID": memberProfileGroupID}
        response = call_api(api_session, 'GetMemberProfileGroupByID', 'post', url, data)
        assert response.status_code == 200, f"calling to GetMemberProfileGroupByID return {response.status_code} "
        actionList = response.json()['data']  # ProfileGroup has no bandScore.only 1 set of Action
        new_MemberSettingProfileID = None if actionList['memberSettingProfileSelected'] == None else \
        actionList['memberSettingProfileSelected']['value']
        new_SpreadGroupID = None if actionList['memberSpreadGroupSelected'] == None else \
        actionList['memberSpreadGroupSelected']['value']
        new_ScoretypeID = None
        new_BetDelayID = actionList['betDelay']
        new_MemberCategoryID = None if actionList['memberCategorySelected'] == None else \
        actionList['memberCategorySelected']['value']
        new_IsAdvisedID = None if actionList['isAdvisedSelected'] == None else actionList['isAdvisedSelected']['value']
        new_IsNotifyMerchantID = None if actionList['isNotifyMerchantSelected'] == None else \
        actionList['isNotifyMerchantSelected']['value']
        betdelayGroupList = response.json()['data']['sportGroupSelected']  # ==[{1001,soccer},{1002,bb},{-1,all}]
        new_BDSportGroupIDs = [BDsportgroup["value"] for BDsportgroup in betdelayGroupList]  # [1000,1001,-1]
        new_BDSportGroupIDs = [-1] if -1 in new_BDSportGroupIDs else new_BDSportGroupIDs
    else:
        pytest.xfail("Explicit failure.HitType not clear")
    return {"UI_ScoretypeID":new_ScoretypeID, "UI_BetDelayID":new_BetDelayID, "UI_MemberSettingProfileID":new_MemberSettingProfileID, \
            "UI_SpreadGroupID":new_SpreadGroupID, "UI_MemberCategoryID":new_MemberCategoryID,\
            "UI_IsAdvisedID":new_IsAdvisedID, "UI_IsNotifyMerchantID":new_IsNotifyMerchantID, "UI_BDSportGroupIDs":new_BDSportGroupIDs}


def turn_OnOff_action_featureflag(api_session, csv_featureOnOff_actionFlag):
    pairs = {}
    # convert prerequisite into json
    for line in csv_featureOnOff_actionFlag.splitlines():
        key, value = line.split(":")  # split by : into string on both side
        pairs[key] = value

    # get ID of ActionFeatureOnOff flag of hitType
    if GbRuleMapper.get_id_byCode(pairs['hittype_to_Upd']):
        action_onoffFlag_ID = GbRuleMapper.get_action_featureOnOffFlag_id_byCode(pairs['hittype_to_Upd'])
    else:
        action_onoffFlag_ID = GbFeatureMapper.get_action_featureOnOffFlag_id_byCode(pairs['hittype_to_Upd'])

    url_get = f"{const.API_BASE_URL}/systemsetting/GetSystemSettingByID"
    data = {"id": action_onoffFlag_ID}
    response = call_api(api_session, 'get_module_actionONOFF_details', 'post', url_get, data)
    assert response.json()['data'][
               'id'] == action_onoffFlag_ID, f" FeatureONOFF_action flag for this hitType is not found. please check"
    flag_data = response.json()['data']

    # update featureOnOff_action flag
    onoff_flag = None
    if pairs['flag'].lower() == 'on':
        onoff_flag = 'true'
    elif pairs['flag'].lower() == 'off':
        onoff_flag = 'false'
    else:
        pytest.xfail("invalid featureOnOff_action flag, please check")
    url_upd = f"{const.API_BASE_URL}/systemsetting/updateSystemSetting"
    data = {"key": flag_data["key"], "value": onoff_flag, "description": flag_data["description"],
            "updatedBy": "admin.qa2"}
    response = call_api(api_session, 'call_to_update_FeatureOnOff_actionFlag', 'post', url_upd, data)
    assert response.status_code == 200, f"calling to FeatureOnOff_action flag update returns {response.status_code} "


def initialise_member(api_session, api_session_SF, mysql_connection, csv_filter):
    for i in range(1, 4):
        prerequisite = f"prerequisite{i}"
        if not csv_filter[prerequisite]:
            # return early if the rest of the pre-req is empty
            return

        pairs = {}
        # CONVERT CSV PREREQUISITE INTO JSON FORMAT
        for line in csv_filter[prerequisite].splitlines():
            key, value = line.split(":")  # split by : into string on both side
            # handling when parameter is empty
            if value == '':
                # preset empty to None
                pairs[key] = None
                # for GBapi only, convert empty instead to 999(no change) ,except for ProfileGroup which should remain empty/none
                if pairs['byUser'].lower() == 'yes' and key != 'memberProfileGroupID':
                    pairs[key] = 999
            elif key == 'byUser':
                pairs['byUser'] = value
            else:
                pairs[key] = int(value)

        # RETRIEVE MEMBER'S DATA(especially UpdatedAt_key & memberid) using GB_API(memberlisting UI).
        url_get = f"{const.API_BASE_URL}/MemberSetting/GetMemberList"
        data = {"dateType": 4, "dateFrom": "2025-12-11T04:00:00", "dateTo": "2025-12-12T04:00:00",
                "companyIDs": [csv_filter['companyID']], "memberCodes": [csv_filter['memberCode']],
                "memberFirstSourceIDs": [], "currencyCodes": [],
                "sortBy": "TotalHitCriteria", "memberActions": [], "memberActionStatusIDs": [], "byGBFilter": True,
                "memberStatusIDs": [], "isHousePlayerIDs": [],
                "memberSettingProfileIDs": [], "spreadGroupIDs": [], "memberCategoryIDs": [], "isAdvisedIDs": [],
                "profileGroupIDs": [], "isProfileGroupNull": False, "isManualRevised": None,
                "isNotOverrideBySystem": [], "updatedBy": "", "updatedDateFrom": None, "updatedDateTo": None,
                "byGBFeature": False, "dayRange": "7D", "bySetting": None,
                "byOperand": None, "timezone": -4, "minMemberScore": None, "minEGONScore": None, "gbRuleIDs": [],
                "page": 1, "pageSize": 100, "minBetDelay": None, "sportGroupIDs": [], "minAppliedCreditScore":None,"minSuggestedCreditScore":None}

        response = call_api(api_session, 'call_to_get_memberListing', 'post', url_get, data)
        assert response.status_code == 200, f"calling to memberListing list returns {response.status_code} "
        assert len(response.json()[
                       'data']) == 1, f"there is no member or more than 1 similar member return in memberListing. please check"
        mem_details = response.json()['data'][0]

        # TESTCASE SELF-VALIDATION:
        # for Manual update(compliance/merchant), you will receive warning if you try to manual update same value as existing bl/sg value.
        # script will still trigger the api, but update will be ignored by gb and might lead to unexpected test result
        if pairs['isManualRevised'] != 1:  # for 0 & 999(nochange)
            if is_match(mem_details['sfSpreadGroupID'], pairs['spreadGroupID']):
                warnings.warn(UserWarning(
                    f"Warning: ManualUpd (pairs['byUser']:{pairs['byUser']}) spread value={mem_details['sfSpreadGroupID']} is similar with existing value , but continuing anyway.pls review your testcase if needed"))
            elif is_match(mem_details['sfMemberSettingProfileID'], pairs['memberSettingProfileID']):
                warnings.warn(UserWarning(
                    f"Warning: ManualUpd (pairs['byUser']:{pairs['byUser']}) limit value={mem_details['sfMemberSettingProfileID']} is similar with existing value , but continuing anyway. pls review your testcase if needed"))

        # PROCESS UPDATE by COMPLIANCE (this trigger from GB member listing)
        if pairs['byUser'].lower() == 'yes':

            if pairs['isManualRevised'] == 1 and (
                    pairs['memberSettingProfileID'] == 999 or pairs['spreadGroupID'] == 999):
                pytest.xfail("when isManualFlag is ON, both BL or SG mz have value")

            # UPDATE MEMBER DETAILS
            # !!memberProfileGroupUpdatedAt i default d value to d one belong to PG 'Reset_Initialise A' as it is more commonly used.(to review)
            # !!if wanna use other PG, pls update accordingly. the system will check
            url_upd = f"{const.API_BASE_URL}/MemberSetting/UpdateMemberByID"
            data = {"memberID": mem_details['memberID'], "memberStatusID": 999, "isHousePlayer": 999,
                    "memberSettingProfileID": pairs['memberSettingProfileID'],
                    "spreadGroupID": pairs['spreadGroupID'], "memberCategoryID": pairs['memberCategoryID'],
                    "isAdvised": pairs['isAdvised'], "isNotifyMerchant": 0,
                    "memberProfileGroupID": pairs['memberProfileGroupID'], "isNotOverrideBySystem": 999,
                    "updatedBy": "admin.qa2", "memberProfileGroupUpdatedAt": "2024-12-30T01:32:45",
                    "isManualRevised": pairs['isManualRevised'], "updatedAt": mem_details['maxUpdatedAt'],"appliedCreditScore":None,"isCreditScoreManualRevised":0}
            response = call_api(api_session, 'call_to_update_memberListing', 'post', url_upd, data)
            assert response.status_code == 200, f"calling to memberListing update returns {response.status_code} "
            assert response.json()['result'] == True, f'error: {response.json()['message']}'
            time.sleep(40)


        # PROCESS UPDATE by MERCHANT, 2 methods to do it:
        # (1) as merchant, trigger from SFBO (by triggering SF_API) [byuser=no] OR
        # (2) in case merchant is no longer allow to do upgrade, then we hv to we fabricate value in mysql to get whatever value we want [byuser=no_sql]
        #     for this , We have to trigger from SFBO as compliance 1st, to 1st populate data that we actually want to send in by merchant
        #                cox merchant update is quite similar to user update. let this populate all data needed, then we only edited those specialised to merchant
        #                After that we use query to fabricate above data in MYSQL to make it look like above record is sent by merchant
        #                Take notes: of cox in BQ audit log(TEMP.SF_LiveMember),would still show it is by compliance
        #     Reason why we do above, is to make sure GB & SF values are always tallied, as GB is always getting final BL/SG/MemCat/isAdv from SF side to take action
        #     It is pointless if we edit data in GB MYsql as it is not wat GB use to take action.
        #     but data like updatedby,IsUpdatedByInternalCompany,blah2 is using the value in GB mysql, so these are the data we can fabricate
        # ============
        # in my excel prerequisite, right now i'm always using method(1)[byuser='no'] to update as merchant. cox i realise i can use updatedby = 'GB_xxx'
        # to bypass all checking in SF.
        # in case i can no longer use 'GB_xxx' to by pass, then just use method (2)[byuser='no_sqledit']
        # ============
        elif pairs['byUser'].lower() in ('no', 'no_sqledit'):
            # # get memberid
            # url_get = f"{const.API_BASE_URL_SF}/Api/Member/GetMemberIdbyMemberCode"
            # data = {"CompanyId": csv_filter['companyID'],"MemberCode": csv_filter['memberCode']}
            # response = call_api(api_session_SF, 'call_SFAPI_to_get_memberid', 'post', url_get, data)
            # assert response.status_code == 200, f"calling to SFAPI_to_get_memberid returns {response.status_code} "
            # assert response.json()['Code'] == 100 and response.json()['Result']['Key'] !=0, f" SFAPI_to_get_memberid has no memberid returned. please check"
            # memberid = response.json()['Result']['Key']

            url_get = f"{const.API_BASE_URL_SF}/Api/Member/UpdateMemberSettingByBatch"
            if pairs['byUser'].lower() == 'no':
                p_isGB = False
                p_updatedby = 'GB_testBYmerchant'
            else:  # 'no_sqledit'
                p_isGB = True
                p_updatedby = 'GB_BYmerchant_SQLedit'
            data = {
                "MemberSettingList": [{"CompanyId": csv_filter['companyID'], "MemberId": mem_details['memberID'],
                                       "MemberCode": csv_filter['memberCode'],
                                       "UpdatedBy": p_updatedby,
                                       # use 'GB_*' to bypass SF logic of merchant upgrade restriction
                                       "MemberStatusId": None,
                                       "MemberSettingProfileId": pairs['memberSettingProfileID'],
                                       "MemberCategoryId": pairs['memberCategoryID'],
                                       "SpreadGroupId": pairs['spreadGroupID'],
                                       "IsAdvised": pairs['isManualRevised'], "IsOverrideBySystem": None}],
                "IsGB": p_isGB  # false=merchant, True=non-merchant
            }
            response = call_api(api_session_SF, 'call_SFAPI_to_upd_members', 'post', url_get, data)
            assert response.status_code == 200, f"calling to SFAPI_to_upd_members returns {response.status_code} "
            errorcode = response.json()['Result'][0]['ApiResponse']['Code']
            errormsg = response.json()['Result'][0]['ApiResponse']['Message']
            assert response.json()[
                       'Code'] == 100 and errorcode == 100, f" SFAPI_to_upd_members has errormsg:{errormsg}. please check"
            time.sleep(40)

            # after updateing necessary field using compliance, we run query to fabricate data in mysql to make it look like it is by merchant
            if pairs['byUser'].lower() == 'no_sqledit':
                # initialise the default value
                query_msp_spread = ""
                p_mspUpdatedDt = None
                p_spreadUpdatedDt = None
                p_mspID = None
                p_spreadID = None
                p_IsSpreadByMerchant = None
                p_IsMSPByMerchant = None
                # minus 30 seconds, to make it tally with above update by compliance
                currDateTime_utc_str = (datetime.now(timezone.utc) - timedelta(seconds=30)).strftime(
                    '%Y-%m-%d %H:%M:%S')

                query_opening = "update  memberextrainfos mex\n \
                                 set\n"
                query_msp = "mex.sfMemberProfileSettingIDUpdatedByMerchant = %(mspID)s,\n \
                mex.sfMemberProfileSettingUpdatedDateByMerchant=%(mspUpdatedDt)s,mex.sfMemberProfileSettingIDUpdatedByMerchant = %(mspID)s,\n \
                mex.IsSfMemberProfileSettingUpdatedByMerchant = %(IsMSPByMerchant)s,\n "
                query_spread = "mex.sfSpreadGroupIDUpdatedByMerchant=%(spreadID)s,\n \
                mex.sfSpreadGroupUpdatedDateByMerchant= %(spreadUpdatedDt)s, mex.sfSpreadGroupIDUpdatedByMerchant = %(spreadID)s,\n \
                mex.IsSfSpreadGroupUpdatedByMerchant = %(IsSpreadByMerchant)s,\n"
                query_closing = " mex.IsUpdatedByInternalCompany = %(IsUpdatedByInternalCompany)s where memberid = %(memberID)s"

                # if excel prerequisite has spread value, manual edit spread value in mysql
                # if excel prerequisite has limit value, manual edit limit value in mysql
                if pairs['memberSettingProfileID'] == None and pairs['spreadGroupID'] == None:
                    pytest.xfail(
                        f"when manual update merchantInfo in sql, either msp or spread must have value, please check")
                if pairs['memberSettingProfileID']:
                    p_mspUpdatedDt = currDateTime_utc_str
                    p_mspID = pairs['memberSettingProfileID']
                    p_IsMSPByMerchant = 1
                    query_msp_spread += query_msp
                if pairs['spreadGroupID']:
                    p_spreadUpdatedDt = currDateTime_utc_str
                    p_spreadID = pairs['spreadGroupID']
                    p_IsSpreadByMerchant = 1
                    query_msp_spread += query_spread
                p_params = {
                    'memberID': mem_details['memberID'],
                    'mspUpdatedDt': p_mspUpdatedDt,
                    # in case only spread value is provided, this field wont be used at all. as msp and spread query are separated
                    'spreadUpdatedDt': p_spreadUpdatedDt,
                    'mspID': p_mspID,
                    'spreadID': p_spreadID,
                    'IsUpdatedByInternalCompany': 0,
                    'IsSpreadByMerchant': p_IsSpreadByMerchant,
                    'IsMSPByMerchant': p_IsMSPByMerchant

                }
                # populate the dynamice query. depends on whether spread or/and settingprofile are provided
                query_statement = query_opening + query_msp_spread + query_closing

                # write dynamic query into reset_mem_MerchantInfo_Mysql.txt
                try:
                    #test_dir = os.path.dirname(__file__)  # in the same directory of running test script
                    test_dir = action_const.SQL_FILE_PATH
                    sql_path = os.path.join(test_dir, "reset_mem_MerchantInfo_Mysql.sql")

                    with open(sql_path, "w") as f:
                        f.write(query_statement)
                except FileNotFoundError:
                    pytest.xfail(f"SQL query file '{sql_path}' not found")
                print(f'what is the statement,', query_statement)
                print(f'what is the params,', p_params)

                # call sql to run reset_mem_MerchantInfo_Mysql.txt
                qhlp.call_mySQL_query(mysql_connection, None, 'reset_mem_MerchantInfo_Mysql.sql', p_params)
                time.sleep(2)

        else:
            pytest.xfail("prerequisite update: byUser value is not valid,please check")
        # though prequisite are all manual trigger.and no checking on prev trigger, eg.lastUpdatedby etc..
        # still better wait for a while. if too fast, GB will only push out the lastest manual trigger
    return

def trigger_module(api_session, hitObject, csv_filter):
    url = f"{const.API_BASE_URL}/Support/MockHitModule"
    if hitObject.hitGbRule:
        p_actionType = 1
        p_RuleID = hitObject.HitID
        p_ModuleID = None
        p_isActionConditionFulfilled = False
        if csv_filter['toActionFlag'].lower() == 'yes':
            p_isActionConditionFulfilled = True
        p_score = csv_filter['gbRuleScore']
    else:
        p_actionType = 2
        p_RuleID = None
        p_ModuleID = hitObject.HitID
        p_isActionConditionFulfilled = None
        p_score = None
    data = {"memberCode": csv_filter['memberCode'], "companyID": csv_filter['companyID'], "actionType": p_actionType,
            "ruleID": p_RuleID,
            "moduleID": p_ModuleID, "score": p_score, "isActionConditionFulfilled": p_isActionConditionFulfilled,
            "createdBy": "admin.qa2"}
    response = call_api(api_session, 'ActionSimulator', 'post', url, data)
    assert response.status_code == 200, f"calling to ActionSimulator return {response.status_code} "