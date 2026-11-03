###not going to use this version. bcox i think for end to end flow, it is better to group all the checking under the same test function.
###i.e when one assertion failed. failed the whole thing. because a lot of things are dependent of each other

import pytest
from tests.myUtils import is_not_match, is_match, is_GT, is_LT, is_LTE, is_GTE
import tests.myConstants as const
from tests.memberAction_tests.helpers.myHelperFunc import call_api
import memberAction_Constants as action_const
from mysql.connector import Error
import os, ast

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
    return (new_ScoretypeID, new_BetDelayID, new_MemberSettingProfileID, new_SpreadGroupID, new_MemberCategoryID,
            new_IsAdvisedID, new_IsNotifyMerchantID, new_BDSportGroupIDs)


def call_mySQL_getHitHistory(mysql_connection, csv_filter, p_input_filter, p_NoAction_statusID,
                             whichHit):  # to query mysql to get memDetails, \'is to escape '
    mycursor = None
    params = {
        'memberCode': csv_filter['memberCode'],
        'companyID': csv_filter['companyID']
    }

    if p_input_filter:
        input_filter = p_input_filter
    else:
        input_filter = '1=1'

    if whichHit == 'AllHits':
        actionID_to_filter = p_NoAction_statusID
    else:
        actionID_to_filter = "''"

    try:
        try:
            #test_dir = os.path.dirname(__file__)  # in the same directory of running test script
            test_dir = action_const.SQL_FILE_PATH
            sql_path = os.path.join(test_dir, "getMemHitHistory_Mysql.txt")

            with open(sql_path, 'r') as f:
                mysql_query = f.read()
        except FileNotFoundError:
            pytest.xfail("SQL query file getMemHitHistory_Mysql.txt not found: path/to/your/mysql_query.sql")

        mycursor = mysql_connection.cursor(dictionary=True)
        mysql_query = mysql_query.format(filter_statement=input_filter, action_disallowed=p_NoAction_statusID,
                                         actionID_to_filter=actionID_to_filter)
        mycursor.execute(mysql_query, params)
        data = mycursor.fetchall()
        mysql_connection.commit()  # Ends the transaction

        return data  # only expect 1 member detail to be return
    except Error as err:
        pytest.xfail(f"MySQL getMemHitHistory_Mysql query error: {err}")
    finally:
        if mycursor:
            mycursor.close()


def test_hit(member_data,api_session,mysql_connection,api_session_SF):
    csv_filter,hitObject,memSetting_before_hit,memBetDelay_before_hit,memBetDelay_before_hit_dict,memBetDelay_before_hit_fmt,\
        moduleHistory_after_hit,memSetting_after_hit,memBetDelay_after_hit,memBetDelay_after_hit_dict,companyName,action_to_exclude,member_new_hit = member_data
    print('action_to_exclude====',action_to_exclude)
    action_to_exclude_set = set(map(int, [x.strip() for x in action_to_exclude.split(',')]))
    # 7  >>>>>  GET DEFINED ACTIONS ASSOCIATED WITH NEW HIT FROM SP/PG UI  <<<<<
    # retrieve all defined Actions(in SP/PG UI) associated with newhit
    UI_ScoretypeID, UI_BetDelayID, UI_MemberSettingProfileID, UI_SpreadGroupID, UI_MemberCategoryID, UI_IsAdvisedID, UI_IsNotifyMerchantID, UI_BDSportGroupIDs = \
        get_action(api_session, hitObject, companyName, csv_filter['gbRuleScore'])

    assert len(member_new_hit) == 1, f'NewHit issue: either new hit is not successful & not saved in DB ORR there is >1 similar ModulehitType'
    new_Hit_Action = member_new_hit[0]
    print('===new_Hit_Action:===>', new_Hit_Action)
    assert is_match(new_Hit_Action['latest_ScoreType'],
                    UI_ScoretypeID), f'Hit latest_ScoreType is different from UI setting'
    assert is_match(new_Hit_Action['latest_BetDelay'],
                    UI_BetDelayID), f'Hit latest_BetDelay is different from UI setting'
    assert is_match(new_Hit_Action['latest_MemberProfile'],
                    UI_MemberSettingProfileID), f'Hit latest_MemberProfile is different from UI setting'
    assert is_match(new_Hit_Action['latest_SpreadGroup'],
                    UI_SpreadGroupID), f'Hit latest_SpreadGroup is different from UI setting'
    assert is_match(new_Hit_Action['latest_MemberCategory'],
                    UI_MemberCategoryID), f'Hit latest_MemberCategory is different from UI setting'
    assert is_match(new_Hit_Action['latest_IsAdvised'],
                    UI_IsAdvisedID), f'Hit latest_IsAdvised is different from UI setting'
    assert is_match(new_Hit_Action['latest_NotifyMerchant'],
                    UI_IsNotifyMerchantID), f'Hit latest_NotifyMerchant is different from UI setting'
    assert is_match(ast.literal_eval(new_Hit_Action['latest_BDSportGroups']),
                    UI_BDSportGroupIDs), f'Hit latest_BDSportGroups is different from UI setting'
    # Hits that is not (SP/PG not found, whitelist, featureoff, ActionCondNotMet) need save in la
    if new_Hit_Action['actionStatusID'] not in action_to_exclude_set and hitObject.hitGbRule:
        assert is_match(new_Hit_Action['latest_ScoreType'],
                        new_Hit_Action['lastWfActn_ScoreType']), f'latest_ScoreType is not being saved as la'
        assert is_match(new_Hit_Action['latest_BetDelay'],
                        new_Hit_Action['lastWfActn_BetDelay']), f'latest_BetDelay is not being saved as la'
        assert is_match(new_Hit_Action['latest_MemberProfile'],
                        new_Hit_Action['lastWfActn_MemberProfile']), f'latest_MemberProfile is not being saved as la'
        assert is_match(new_Hit_Action['latest_SpreadGroup'],
                        new_Hit_Action['lastWfActn_SpreadGroup']), f'latest_SpreadGroup is not being saved as la'
        assert is_match(new_Hit_Action['latest_MemberCategory'],
                        new_Hit_Action['lastWfActn_MemberCategory']), f'latest_MemberCategory is not being saved as la'
        assert is_match(new_Hit_Action['latest_IsAdvised'],
                        new_Hit_Action['lastWfActn_IsAdvised']), f'latest_IsAdvised is not being saved as la'
        assert is_match(new_Hit_Action['latest_NotifyMerchant'],
                        new_Hit_Action['lastWfActn_NotifyMerchant']), f'latest_NotifyMerchant is not being saved as la'
        assert is_match(new_Hit_Action['latest_BDSportGroups'],
                        new_Hit_Action['lastWfActn_BDSportGroups']), f'latest_BDSportGroups is not being saved as la'
    else:
        assert new_Hit_Action['lastWfActn_updatedAt'] != new_Hit_Action[
            'updatedAt'], f'hit without action has been saved as la(lasthitwithAction)'


def test_msp(member_data,api_session,mysql_connection,api_session_SF):
    csv_filter,hitObject,memSetting_before_hit,memBetDelay_before_hit,memBetDelay_before_hit_dict,memBetDelay_before_hit_fmt,\
        moduleHistory_after_hit,memSetting_after_hit,memBetDelay_after_hit,memBetDelay_after_hit_dict,companyName,action_to_exclude = member_data
    msp_smallest_rankNum = None  # expected action to take . None means no action allowed
    msp_threshold_rankNum = None
    to_apply_creditScore = False
    MerrMsg = ''