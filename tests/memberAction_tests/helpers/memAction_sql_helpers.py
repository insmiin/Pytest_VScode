
import pytest
from mysql.connector import Error
from datetime import datetime, timezone,timedelta
import tests.memberAction_tests.helpers.myHelperFunc as helper
from tests.memberAction_tests.mappingModule import SpreadGroupMappers, MemberProfileSettingMappers, GbRuleMapper, GbFeatureMapper
import tests.memberAction_tests.memberAction_Constants as action_const
import tests.memberAction_tests.helpers.memAction_helpers as hlp
import logging

logger = logging.getLogger(__name__)

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
            #test_dir = action_const.SQL_FILE_PATH
            #sql_path = os.path.join(test_dir, sql_file)
            sql_path = action_const.SQL_FILE_PATH / sql_file

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
        if sql_file == "getMemDetails_Mysql.sql":
            assert len(data) == 1, f"no member or more than 1 same member row was returned from mysql"
            return data[0]  # only expect 1 member detail to be return
        else:
            return data
    except Error as err:
        pytest.xfail(f"MySQL <{sql_file}> query error: {err}")
    finally:
        if mycursor:
            mycursor.close()


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
            #test_dir = action_const.SQL_FILE_PATH
            #sql_path = os.path.join(test_dir, "getMemHitHistory_Mysql.sql")
            sql_path = action_const.SQL_FILE_PATH / "getMemHitHistory_Mysql.sql"
            with open(sql_path, 'r') as f:
                mysql_query = f.read()
        except FileNotFoundError:
            pytest.xfail("SQL query file getMemHitHistory_Mysql.sql not found: path/to/your/mysql_query.sql")

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

def reset_member_hits(mysql_connection, csv_filter):
    # reset date to very old date to make sure it is outside validity period and will be ignored
    p_params = {
        'memberCode': csv_filter['memberCode'],
        'companyID': csv_filter['companyID'],
        'date_to_change_UTC': '2025-02-02 04:00:00'
    }
    call_mySQL_query(mysql_connection, csv_filter, 'reset_mem_GbFeatureHits_Mysql.sql', p_params)
    call_mySQL_query(mysql_connection, csv_filter, 'reset_mem_GbRuleHits_Mysql_msp.sql', p_params)
    call_mySQL_query(mysql_connection, csv_filter, 'reset_mem_GbRuleHits_Mysql_mspa.sql', p_params)
    call_mySQL_query(mysql_connection, csv_filter, 'reset_mem_BetDelay_Mysql.sql', p_params)


def modify_HitDate_or_mem_attribute_date(mysql_connection, csv_filter):
    pairs = {}

    # convert prerequisite into json
    for line in csv_filter['EditUpdatedDate'].splitlines():
        key, value = line.split(":")  # split by : into string on both side
        pairs[key] = value

    past_date_UTC = hlp.get_module_validFromDate_utc(pairs['module_to_Upd'],'module_code')
    if (pairs['outsideValidPeriod']).lower() == 'yes':
        new_date_utc = past_date_UTC - timedelta(minutes=10)  # make it expired by setting it to 10 mins past expired
    else:
        new_date_utc = past_date_UTC + timedelta(minutes=10)  # make it Almost expired by setting it 10 mins to expired


    new_date_utc_string = new_date_utc.strftime("%Y-%m-%d %H:%M:%S") #convert to string
    ThisModuleTypeIs = hlp.get_moduletype(pairs['module_to_Upd'],'module_code')

    if ThisModuleTypeIs.GbRule:
       HitType_ID = GbRuleMapper.get_id_byCode(pairs['module_to_Upd'])
       HitType_updbyName = GbRuleMapper.get_updByName_byCode(pairs['module_to_Upd'])
    else:
       HitType_ID = GbFeatureMapper.get_id_byCode(pairs['module_to_Upd'])
       HitType_updbyName = GbFeatureMapper.get_updByName_byCode(pairs['module_to_Upd'])

    p_params = {
        'memberCode': csv_filter['memberCode'],
        'companyID': csv_filter['companyID'],
        'date_to_change_UTC': new_date_utc_string,
        'use_ruleID_to_update': HitType_ID,
        'use_ruleUpdByName_to_update_BD': HitType_updbyName + '%'
        # BD use updateName, so make sure cater for prefix _1 &_2
    }

    # update the ScoreDate,ActionDate of inputted module
    if pairs['upd_module_DT'].lower() == 'yes':
        if ThisModuleTypeIs.GbRule:  # gbrule & egon
            call_mySQL_query(mysql_connection, csv_filter, 'edit_UpdByDate_GbRuleHits_Mysql_msp.sql', p_params)
            call_mySQL_query(mysql_connection, csv_filter, 'edit_UpdByDate_GbRuleHits_Mysql_mspa.sql', p_params)
        else:  # gbfeature
            call_mySQL_query(mysql_connection, csv_filter, 'edit_UpdByDate_GbFeatureHits_Mysql.sql', p_params)

    # update the lastupdateby of member's setting(bl,sg,bd,memCat)
    if pairs['upd_memsetting_DT'].lower() == 'yes':
        call_mySQL_query(mysql_connection, csv_filter, 'edit_UpdByDate_BD_Mysql.sql', p_params)
        call_mySQL_query(mysql_connection, csv_filter, 'edit_UpdByDate_BLSGMemCat_Mysql.sql', p_params)
