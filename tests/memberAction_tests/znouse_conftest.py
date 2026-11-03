import csv
from typing import List, Dict
import time
from datetime import datetime, timezone, timedelta
import pytest
from mysql.connector import Error
import mysql.connector
import requests
import tests.myConstants as const
import sys
import os
from tests.memberAction_tests.helpers.myHelperFunc import call_api, get_new_date_UTC, parse_updatedby
#to add root directory into the sys.path, so that the script able to import module in root directory
root_dir = os.path.abspath(os.path.join(os.path.dirname(__file__), '..'))
sys.path.insert(0, root_dir)
from mappingModule import GbRuleMapper,GbFeatureMapper,SportGroupMapper
import memberAction_Constants as action_const
from tests.myUtils import is_not_match, is_match, is_GT, is_LT, is_LTE, is_GTE
import warnings

def load_test_data() -> List[Dict]:
    # Example data loading logic
    file_path = action_const.CSV_FILE_PATH
    try:
        with open(file_path, mode='r', newline='') as csvfile:
            reader = csv.DictReader(csvfile)
            return [row for row in reader if row['testcase']]  # ignore testcase that is space or empty
    except FileNotFoundError:
        print(f"File not found: {file_path}")
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
            "gbRuleScore": int(row["gbRuleScore"]) if row["gbRuleScore"] else None,
            "toActionFlag": row["toActionFlag"],
            # "prerequisiteFlag":row["prerequisiteFlag"],
            "prerequisite1": row["prerequisite1"],
            "prerequisite2": row["prerequisite2"],
            "prerequisite3": row["prerequisite3"],
            # "EditUpdByDateFlag":row["EditUpdByDateFlag"],
            "EditUpdByDate": row["EditUpdByDate"],
            "pre_actionOnOffFlag": row["pre_actionOnOffFlag"],  # featureOn/Off
            "post_actionOnOffFlag": row["post_actionOnOffFlag"]
        }
        formatted_filters.append(formatted_filter)
    return formatted_filters





@pytest.fixture(scope="session")
def mysql_connection():
    print('mysql_connection fixtureee')
    conn = None
    try:
        conn = mysql.connector.connect(
            host='35.229.171.142',
            user='sfqat_superadmin_qa',  #'qat_readonly',
            password='dL72QF1Ia4',   #'NTZ6Wt3tzqCp4k7v',
            port=3306,
            database='GB_Qat'  # !!this is DATABASEname(GB_Qat) in mysql , not the connectionName on mysql workbench....
        )
        yield conn
    except Error as err:
        pytest.fail(f"MySQL connection error: {err}")
    finally:
        print('mysql at finally')
        if conn and conn.is_connected():
            print('going to close the mysql connection')
            conn.close()


@pytest.fixture(scope="function")
def mysql_connection2():
    print('mysql_connection2222 fixtureee')
    conn = None
    try:
        conn = mysql.connector.connect(
            host='35.229.171.142',
            user='sfqat_superadmin_qa',  #'qat_readonly',
            password='dL72QF1Ia4',   #'NTZ6Wt3tzqCp4k7v',
            port=3306,
            database='GB_Qat'  # !!this is DATABASEname(GB_Qat) in mysql , not the connectionName on mysql workbench....
        )
        yield conn
    except Error as err:
        pytest.fail(f"MySQL connection22 error: {err}")
    finally:
        print('mysql2 at finally')
        if conn and conn.is_connected():
            print('going to close the mysql2 connection')
            conn.close()

@pytest.fixture(scope="session")
def api_session():
    print('api_session GB fixtureeeeee')
    session = requests.Session()
    session.headers.update(
        {"Authorization": const.AUTH_TOKEN, "Content-Type": "application/json", "Connection": "keep-alive"})
    yield session
    session.close()

@pytest.fixture(scope="session")
def api_session_SF():
    print('api_session SF fixtureeeeee')
    session = requests.Session()
    session.headers.update(
        {"Authorization": const.AUTH_TOKEN, "Content-Type": "application/json", "Connection": "keep-alive"})
    yield session
    session.close()

# Fixture to fetch companies once per session
@pytest.fixture(scope="session")
def companies_list(api_session):
    print('companies_list fixtureeeeee')
    url = f"{const.API_BASE_URL}/common/getCompanyList"
    response = call_api(api_session,'get_companies_list', 'get', url)
    assert response.status_code == 200, f"calling to 'companies_list' return {response.status_code} "
    #convert to dictionary where key is companyid and value is companyName
    return {item['companyID']: item['companyName'] for item in response.json()['data'] }


@pytest.fixture(scope="session")
def api_MemHierarchyGroupList(api_session):
    print('api_MemHierarchyGroupList fixtureeeeee')
    url = f"{const.API_BASE_URL}/MemberSetting/GetMemberCategoryGroupList"
    data = {"memberCategoryGroupName":"","companyIDs":[],"status":1,"page":1,"pageSize":10}
    response = call_api(api_session,'api_MemHierarchyGroupList', 'post', url, data)
    assert response.status_code == 200, f"calling to api_MemHierarchyGroupList return {response.status_code} "

    #extract only groupId & companies and convert into dictionary
    #eg. dict_lookup = {'IMDemo': 8, 'MINICOMMONWALLET2': 8, 'MINITRANSFERWALLET2': 8, 'MINITRANSFERWALLET3': 8}
    dict_lookup = {}
    for memCatHierGroup in response.json()['data']:
        if memCatHierGroup['status'] == 1:
            companies = [comp.strip() for comp in memCatHierGroup['companyName'].split(',')]
            for company in companies:
                dict_lookup[company] = memCatHierGroup['memberCategoryGroupID']
    return dict_lookup

# get list of finalCreditScore and its criterias
    # Mapping table for raw string operators to native Python operators
OPERATORS = {
        ">=": lambda given_value, defined_value: given_value >= defined_value,
        "<=": lambda given_value, defined_value: given_value <= defined_value,
        ">": lambda given_value, defined_value: given_value > defined_value,
        "<": lambda given_value, defined_value: given_value < defined_value,
        "==": lambda given_value, defined_value: given_value == defined_value,
    }
def get_criteria_checking_function(criteria):
    """Compiles a rule into a native, fast-executing python closure."""
    if not criteria:
        return lambda inp_value: True  #if this metric doesnt exists, means not applicable ,means no check, regardless wat value jz let it passed

    criteria_minValue, minOp = criteria.get("value"), criteria.get("valueOperator")
    criteria_maxValue, maxOp = criteria.get("value2"), criteria.get("value2Operator")

    func1 = OPERATORS[minOp] if (minOp and criteria_minValue is not None) else None #eg.func1 = lambda given_value, defined_value: given_value >= defined_value
    func2 = OPERATORS[maxOp] if (maxOp and criteria_maxValue is not None) else None
    criteria_minValue_f = float(criteria_minValue) if criteria_minValue is not None else None
    criteria_maxValue_f = float(criteria_maxValue) if criteria_maxValue is not None else None

    if func1 and func2:
        return lambda input_value: func1(input_value, criteria_minValue_f) and func2(input_value, criteria_maxValue_f)
    elif func1:
        return lambda input_value: func1(input_value, criteria_minValue_f)
    elif func2:
        return lambda input_value: func2(input_value, criteria_maxValue_f)
    return lambda input_value: True   #if any value or operator is null , means not applicable ,means no check, regardless wat value jz let it passed

@pytest.fixture(scope="session")
def api_CalcBL_CSfinalBL_mapping(api_session):
    print('api_CalcBL_CSfinalBL_mapping fixtureeeeee')
    url = f"{const.API_BASE_URL}/systemsetting/GetCreditScoreSettingListByKey"   #@@change all related....
    data = {"key": "Final_Bet_Limit_Mapping"}
    response = call_api(api_session,'api_CalcBL_CSfinalBL_mapping', 'post', url, data)
    assert response.status_code == 200, f"calling to api_CalcBL_CSfinalBL_mapping return {response.status_code} "

    CSfinalBL_calculatedBL_mapping = []
    for item in response.json()["data"]:
        # for each CS_finalBL row, put all metrics/criteria into a list
        # {  'minwager':{..,'key':'minwager','value': '0.10', 'valueOperator': '>='},'minExp':{..,'key':'minExp','value': '0.30', 'valueOperator': '>='}  }
        #criteria_dict = {s["key"]: s for s in item["settingList"]}

        # then for each metric , convert the value/operator & value2/operator2 into a lambda function
        # lastly, append {finalBL_creditScore & its criteria lambda function} into mapping dictionary
        CSfinalBL_calculatedBL_mapping.append(
            {
                "CS_finalBL_ID": item["resultValue"],  #resultValue is the betlimit valudID eg. valueID5 = 10%group
                #"func_within_defined_CalcBL_range": get_criteria_checking_function(criteria_dict.get("MinExpRatio")
                "func_within_defined_CalcBL_range": get_criteria_checking_function(item)
            }
        )
    #print(f'COMPILED_BANDSx:{CSfinalBL_calculatedBL_mapping}')
    # CSfinalBL_calculatedBL_mapping =
    # [{'CS_finalBL_ID': 1, 'func_within_defined_CalcBL_range': return lambda input >= minValue, 'check_max_avg_condition': return lambdainput >= minValue},
    #  {'CS_finalBL_ID': 2, 'func_within_defined_CalcBL_range': return lambda input >= minValue and input <=maxValue, 'check_max_avg_condition': return lambda input >= minValue},
    #  {'CS_finalBL_ID': 3, 'func_within_defined_CalcBL_range': return lambda input >= minValue, 'check_max_avg_condition': return lambda input >= minValue},
    #  ...]
    # just loop thru CSfinalBL_calculatedBL_mapping and
    # return 1st CSfinalBL_calculatedBL_mapping['CS_finalBL] if CSfinalBL_calculatedBL_mapping[CalcBL_range_condition](calculated_BL)
    # print(CSfinalBL_calculatedBL_mapping)
    # import inspect
    # func = CSfinalBL_calculatedBL_mapping[1]['func_within_defined_CalcBL_range']
    # print(inspect.getsource(func))
    return CSfinalBL_calculatedBL_mapping


# @pytest.fixture(scope="session")
# def mspID_by_rankNum():
#     ranking_lookup_mps = {v['ranking']: k for k,v in MemberProfileSettingMappers.member_profileSetting_dict.items()}
#     return ranking_lookup_mps   #{mspranking1:mspid1,mspranking2:mspid2,mspranking3:mspid3}

# @pytest.fixture(scope="session")
# def spreadID_by_rankNum():
#     ranking_lookup_spread = {v['ranking']: k for k,v in SpreadGroupMappers.member_spread_group_dict.items()}
#     return ranking_lookup_spread

# @pytest.fixture(scope="session")
# def sports_by_GbRuleID():
#     id_lookup_sport = {v['id']:v['sport']  for k,v in GbRuleMapper._mapping.items()}
#     return id_lookup_sport
#
# @pytest.fixture(scope="session")
# def sports_by_GbFeatureID():
#     id_lookup_sport = {v['id']:v['sport']  for k,v in GbFeatureMapper._mapping.items()}
#     return id_lookup_sport

@pytest.fixture(scope="session")
def prev_memberCode():
    return {"value": None}

@pytest.fixture(scope="session")
def sportGroup_sportIDs_UImap_dict(mysql_connection):
    try:
        mycursor = mysql_connection.cursor(dictionary=True)
        mysql_query = "SELECT sportID FROM GB_Qat.sports where sportID !=0"
        mycursor.execute(mysql_query)
        data = mycursor.fetchall()   #[{'sportID': 1}, {'sportID': 2}, {'sportID': 3}]
        mysql_connection.commit()  # Ends the transaction
        all_sportIDs_dict = [sport['sportID'] for sport in data]  #[1, 2, 3, 4,....,67]
    except Error as err:
        pytest.fail(f"MySQL getMemHitHistory_Mysql query error: {err}")
    finally:
        if mycursor:
            mycursor.close()

    SportGroup_SportID_mapping = SportGroupMapper.get_all()
    # Step 1: Collect all IDs that already appear in mapping (excluding key 1000)
    used_sportids = set()
    for key, value_list in SportGroup_SportID_mapping.items():
        if key != 1000:  # Skip the placeholder key 1000
            used_sportids.update(value_list)

    # Step 2: Find missing IDs (those in 'id' but not in existing_ids)
    other_sportids = [num for num in all_sportIDs_dict if num not in used_sportids]

    # Step 3: Update mapping for key 1000
    SportGroup_SportID_mapping[1000] = other_sportids
    return SportGroup_SportID_mapping  #{1001: [1], 1002: [2], 1003: [54, 55], 1000: [3, 4, 5, 6, 7, 8,etc..]}


def call_mySQL_query(mysql_connection, csv_filter, sql_file,
                     p_params):  # to query mysql to get memDetails, \'is to escape '
    mycursor = None
    if p_params:
        params = p_params
    else:
        params = {
            'memberCode': csv_filter['memberCode'],
            'companyID': csv_filter['companyID']
        }
    try:
        try:
            #test_dir = os.path.dirname(__file__)  # in the same directory of running test script
            test_dir = action_const.SQL_FILE_PATH
            sql_path = os.path.join(test_dir, sql_file)
            with open(sql_path, 'r') as f:
                mysql_query = f.read()
        except FileNotFoundError:
            pytest.xfail(f"SQL query file '{sql_file}' not found")

        mycursor = mysql_connection.cursor(dictionary=True)
        mycursor.execute(mysql_query, params)
        # --- FIX: Only fetch if the query returns a result set, else might throw sql error ---
        if mycursor.with_rows:
            data = mycursor.fetchall()
        else:
            data = []  # Return an empty list for UPDATE/INSERT queries
        #data = mycursor.fetchall()  # return 1 dict

        # fixture(scope=session) is use to setup mysql connection(i.e create once &share across all tests.
        # to ensure row is not read-lock, issue commit after every query
        mysql_connection.commit()  # Ends the transaction so that AfterHit_data will not reuse BeforeHit_data
        if sql_file == "getMemDetails_Mysql.txt":
            assert len(data) == 1, f"no member or more than 1 same member row was returned from mysql"
            return data[0]  # only expect 1 member detail to be return
        else:
            return data
    except Error as err:
        pytest.xfail(f"MySQL <{sql_file}> query error: {err}")
    finally:
        if mycursor:
            mycursor.close()



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


def reset_member_hits(mysql_connection, csv_filter):
    # reset date to very old date to make sure it is outside validity period and will be ignored
    p_params = {
        'memberCode': csv_filter['memberCode'],
        'companyID': csv_filter['companyID'],
        'date_to_change_UTC': '2025-02-02 04:00:00'
    }
    call_mySQL_query(mysql_connection, csv_filter, 'reset_mem_GbFeatureHits_Mysql.txt', p_params)
    call_mySQL_query(mysql_connection, csv_filter, 'reset_mem_GbRuleHits_Mysql_msp.txt', p_params)
    call_mySQL_query(mysql_connection, csv_filter, 'reset_mem_GbRuleHits_Mysql_mspa.txt', p_params)
    call_mySQL_query(mysql_connection, csv_filter, 'reset_mem_BetDelay_Mysql.txt', p_params)

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
                    sql_path = os.path.join(test_dir, "reset_mem_MerchantInfo_Mysql.txt")

                    with open(sql_path, "w") as f:
                        f.write(query_statement)
                except FileNotFoundError:
                    pytest.xfail(f"SQL query file '{sql_path}' not found")
                print(f'what is the statement,', query_statement)
                print(f'what is the params,', p_params)

                # call sql to run reset_mem_MerchantInfo_Mysql.txt
                call_mySQL_query(mysql_connection, None, 'reset_mem_MerchantInfo_Mysql.txt', p_params)
                time.sleep(2)

        else:
            pytest.xfail("prerequisite update: byUser value is not valid,please check")
        # though prequisite are all manual trigger.and no checking on prev trigger, eg.lastUpdatedby etc..
        # still better wait for a while. if too fast, GB will only push out the lastest manual trigger
    return


def modify_member_latestHit_attribute_date(mysql_connection, csv_filter):
    pairs = {}
    GbRule = False
    # convert prerequisite into json
    for line in csv_filter['EditUpdByDate'].splitlines():
        key, value = line.split(":")  # split by : into string on both side
        pairs[key] = value

    past_date_UTC = get_new_date_UTC(3, 'months')
    if (pairs['outsideValidPeriod']).lower() == 'yes':
        past_date_time_utc = str(past_date_UTC) + ' 03:00:00'
    else:
        past_date_time_utc = str(past_date_UTC) + ' 04:00:00'
    if GbRuleMapper.get_id_byCode(pairs['id_to_Upd']):
        HitType_ID = GbRuleMapper.get_id_byCode(pairs['id_to_Upd'])
        HitType_updbyName = GbRuleMapper.get_updByName_byCode(pairs['id_to_Upd'])
        GbRule = True
    else:
        HitType_ID = GbFeatureMapper.get_id_byCode(pairs['id_to_Upd'])
        HitType_updbyName = GbFeatureMapper.get_updByName_byCode(pairs['id_to_Upd'])
    p_params = {
        'memberCode': csv_filter['memberCode'],
        'companyID': csv_filter['companyID'],
        'date_to_change_UTC': past_date_time_utc,
        'use_ruleID_to_update': HitType_ID,
        'use_ruleUpdByName_to_update_BD': HitType_updbyName + '%'
        # BD use updateName, so make sure cater for prefix _1 &_2
    }
    print(f'p_params is ,{p_params}')
    if GbRule:
        call_mySQL_query(mysql_connection, csv_filter, 'edit_UpdByDate_GbRuleHits_Mysql_msp.txt', p_params)
        call_mySQL_query(mysql_connection, csv_filter, 'edit_UpdByDate_GbRuleHits_Mysql_mspa.txt', p_params)
    else:
        call_mySQL_query(mysql_connection, csv_filter, 'edit_UpdByDate_GbFeatureHits_Mysql.txt', p_params)

    call_mySQL_query(mysql_connection, csv_filter, 'edit_UpdByDate_BD_Mysql.txt', p_params)
    call_mySQL_query(mysql_connection, csv_filter, 'edit_UpdByDate_BLSGMemCat_Mysql.txt', p_params)

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


# 1. Keep your fixture as is (default function scope re-runs setup/teardown per test)
@pytest.fixture(scope="module",params=format_filters(load_test_data()),ids=lambda params: f"testcase_{params['testcase']}")
#@pytest.fixture(scope="session",params=[1,2])
def member_data(mysql_connection, companies_list, api_session, api_session_SF, api_MemHierarchyGroupList, \
                   api_CalcBL_CSfinalBL_mapping,
                   sportGroup_sportIDs_UImap_dict,prev_memberCode,request):
    csv_filter = request.param

    # Manually control certain processing
    to_triggerActionFlag = True  # flag for me to control triggering
    to_reset_member = True  # sometime if wan to continue subsequent action of SAME member, set this manually to false
    apply_creditScore_FLAG = True  # @@changeCS? see if there is a need to retrieve the flag once to determine if using CS or not
    print('xxxxxxx')
    # 1  >>>>> SETUP & DATA PREPARATION BEFORE ACTION TRIGGERING STARTS   <<<<<
    if to_triggerActionFlag == True:
        # (Automatically not via CSV), for each member,
        # For this member, reset updDate(score,mainAction,childAction of all the hits(by setting them outside validity,so that i can reuse existing testing members & not creating new one each time)
        # reset all member's existing BD to 0 & data to outside validity(to confirm if updatedBy need to be reset too..)
        # i dint reset BL/SG/memCat yet,as initial cross/single module checking wont involved this attribute(to add if needed)
        if to_reset_member == True:
            if csv_filter['memberCode'] != prev_memberCode["value"]:
                reset_member_hits(mysql_connection, csv_filter)
                prev_memberCode["value"] = csv_filter['memberCode']

        # (initiated by csv)Before any system hit, initialise member setting by doing manual update. (both userValue & merchant update)
        # The ManualUpdate approach performs direct updates.
        if csv_filter['prerequisite1']:
            initialise_member(api_session, api_session_SF, mysql_connection, csv_filter)

        # to fabricate updateDate of attributes associated with latestHit(i.e  1 hit only) eg. BL/SG/MemCat/MainActiontable/ChildAction/table/BetDelay
        # only allow to change the latesthit. it doesnt make sense if you change bl/sg/memCat updateddate prior to latesthit a
        if csv_filter['EditUpdByDate']:
            modify_member_latestHit_attribute_date(mysql_connection, csv_filter)

        if csv_filter['pre_actionOnOffFlag']:
            turn_OnOff_action_featureflag(api_session, csv_filter['pre_actionOnOffFlag'])
            time.sleep(4)  # time buffer to make sure flag is updated

    # ===SYSTEM UPDATE(Auto Tag) processing starts here ====
    # score all the necessary hit information derived from csv input file
    class NewHit:
        def __init__(self):
            self.hitGbRule = False
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
        def HitID(self):  # getter. when u wan to get the value of HitID. jz to return real value
            return self._HitID

        @HitID.setter  # setter function. when u assign value to HitID. function to jz set/modifier the value, not to return value
        def HitID(self, hitName):
            if hitName is None:
                return  # Just exit without doing anything. it has no where to return to anywhere.
            if GbRuleMapper.get_id_byCode(hitName):
                self._HitID = GbRuleMapper.get_id_byCode(hitName)
                self.hitGbRule = True
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

    # 2 >>>>> STORE AND PROCESS DATA FROM CSV   <<<<<
    hitObject = NewHit()
    hitObject.HitID = csv_filter['hitType']
    assert hitObject.HitID is not None, f"no valid HitID found, please check your input"
    if hitObject.hitGbRule:
        assert csv_filter['gbRuleScore'] >=0, f"HitType is GBrule but no valid score is provided in your csv file"  # 0 is false
        assert csv_filter['toActionFlag'] in ('yes','no'), f"HitType is GBrule but no valid toActionFlag is provided in your csv file"


    # 3 >>>>>  SAVE MEMBER'S SETTING (BL,SG,MemCat,isAdv,BetDelay) BEFORE HIT  <<<<<
    memSetting_before_hit = call_mySQL_query(mysql_connection, csv_filter, "getMemDetails_Mysql.txt", None)  # 1 dict
    print('===memSetting_before_hit:===>', memSetting_before_hit)
    memBetDelay_before_hit = call_mySQL_query(mysql_connection, csv_filter, 'getMemBetDelay_Mysql.txt', None)  # 1 dict
    # memBetDelay_before_hit_dict = {(item['sportid'], item['sportTypeID']): item['gbMemberBetDelay'] for item in memBetDelay_before_hit}  # dict with tuple value
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
            "Bdelay_withinValidityPeriod": row["Bdelay_withinValidityPeriod"]
        }
    print('===memBetDelay_before_hit_dict:===>', memBetDelay_before_hit_dict)

    # 4 >>>>>   TRIGGER ACTION VIA MOCK SIMULATOR  <<<<<
    # [b4 processing action logic,GB will call SF to get latest member setting 1st. i guess SF takes long to return and might cause GB to start processing late,like > 60sec0
    if to_triggerActionFlag == True:
        trigger_module(api_session, hitObject, csv_filter)
        print(f'===triggered done for (test case#{csv_filter['testcase']}) ===>:, {datetime.now()}')
        if csv_filter['toActionFlag'].lower() == 'no':
            time.sleep(40)  #
        else:
            time.sleep(40)  # to allow time for SF to send in and update to be reflected in GB db
        print(
            f'===start verifying for (test case#{csv_filter['testcase']}) ===>:, {datetime.now()} (this time mz be after bq GBCreatedDT to work properly')

    # tear down
    if to_triggerActionFlag == True:
        if csv_filter['post_actionOnOffFlag']:
            turn_OnOff_action_featureflag(api_session, csv_filter['post_actionOnOffFlag'])

    # 5 >>>>>  ACTION TRIGGERING done, GET ALL OF THE MODULES(RULE/FEATURES) THAT MEMBER HAS HIT BEFORE   <<<<<
    action_to_exclude = '95,96,98,99,100'  # excludes all Hit types where action is not supposed to be allowed
    # eg: featureOff,whitelist & SP/PG x found (for ActionCondNotMet, exclude only if neverMet since day 1. will cater in sql script)

    moduleHistory_after_hit = call_mySQL_getHitHistory(mysql_connection, csv_filter, None, action_to_exclude,
                                                       'AllHits')  # list of dict
    hitObject.hit_Single_Or_CrossModule(moduleHistory_after_hit)
    if hitObject.crossModule:
        hitObject.determine_GB_EGON_crossstatus(moduleHistory_after_hit)

    # 6  >>>>>  GET MEMBER'S SETTING (BL,SG,MemCat,isAdv,BetDelay) AFTER HIT  <<<<<
    memSetting_after_hit = call_mySQL_query(mysql_connection, csv_filter, "getMemDetails_Mysql.txt", None)
    print('===memSetting_after_hit:===>', memSetting_after_hit)
    memBetDelay_after_hit = call_mySQL_query(mysql_connection, csv_filter, 'getMemBetDelay_Mysql.txt', None)  # 1 dict
    memBetDelay_after_hit_dict = {item['sportid']: item['gbMemberBetDelay'] for item in memBetDelay_after_hit}
    print('===memBetDelay_after_hit_dict:===>', memBetDelay_after_hit_dict)

    companyName = companies_list.get(csv_filter['companyID'])
    assert companyName is not None, f'not able to proceed as there is not matching companyID for companyName from csv_row'

    # 8 >>>>> CHECK THAT TRIGGERRING IS SUCCESSFUL (BY ENSURING THAT ACTION HAS BEEN SAVED IN MYSQL & TALLY WITH DEFINED ACTION FROM SP/PG UI)    <<<<<
    member_new_hit = call_mySQL_getHitHistory(mysql_connection, csv_filter, hitObject.mysql_filter_statement,
                                              action_to_exclude, 'NewHit')  # list of dict
    # function_do_initialise/setup()
    # function_do_store_hit_info()
    # function_do_save member'setting before triggering
    # function_do_trigger_action
    # function_do_save member'setting after triggering
    return (csv_filter,hitObject,memSetting_before_hit,memBetDelay_before_hit,memBetDelay_before_hit_dict,memBetDelay_before_hit_fmt,\
        moduleHistory_after_hit,memSetting_after_hit,memBetDelay_after_hit,memBetDelay_after_hit_dict,companyName,action_to_exclude,member_new_hit)
