
from importlib.resources import path
import pytest
from mysql.connector import Error
from datetime import datetime, timezone,timedelta
import tests.memberAction_tests.helpers.myHelperFunc as helper
from tests.memberAction_tests.mappingModule import SpreadGroupMappers, MemberProfileSettingMappers, GbRuleMapper, GbFeatureMapper
import tests.memberAction_tests.memberAction_Constants as action_const
import tests.memberAction_tests.helpers.memAction_helpers as hlp
import tests.memberAction_tests.helpers.memAction_bq_helpers as bqhlp
import logging

logger = logging.getLogger(__name__)


import os
import pytest

from dotenv import load_dotenv
from playwright.sync_api import sync_playwright

load_dotenv()
# ---------- helpers (no Playwright needed) ----------

def sql_value(value):
    if value is None:
        return "NULL"
    if isinstance(value, bool):
        return "1" if value else "0"
    if isinstance(value, (int, float)):
        return str(value)
    escaped = str(value).replace("\\", "\\\\").replace("'", "''")
    return f"'{escaped}'"


def build_query(csv_filter, sql_file, p_params):
    params = p_params if p_params else {
        'memberCode': csv_filter['memberCode'],
        'companyID': csv_filter['companyID'],
    }
    sql_path = action_const.SQL_FILE_PATH / sql_file
    with open(sql_path, 'r', encoding='utf-8') as f:
        mysql_query = f.read()
    for key, value in params.items():
        mysql_query = mysql_query.replace(f"%({key})s", sql_value(value))
    return mysql_query

def call_mySQL_upd_query_cloudsql_ui(page, csv_filter, sql_file, p_params=None):
    try:
        mysql_query = build_query(csv_filter, sql_file, p_params)
    except Exception as err:
        logger.exception(f"Failed to prepare SQL <{sql_file}>")
        pytest.xfail(f"Failed to prepare SQL <{sql_file}>: {err}")

    try:
        page.get_by_role('button', name='New tab').click()

        page.locator('.monaco-editor .view-lines').first.click()
        page.evaluate("text => navigator.clipboard.writeText(text)", mysql_query)
        page.keyboard.press('ControlOrMeta+A')
        page.keyboard.press('ControlOrMeta+V')
        page.get_by_role('button', name='Run').click()

        page.get_by_role('status').filter(
            has_text='Statement executed successfully'
        ).wait_for(state='visible', timeout=10000)

        logger.info(f"Cloud SQL <{sql_file}> executed successfully via UI.")
        return []

    except Exception as err:
        try:
            page.screenshot(path=f'cloudsql-error-{sql_file}.png', full_page=True)
        except Exception:
            logger.warning("Could not capture screenshot")
        logger.exception(f"Cloud SQL <{sql_file}> query error")
        pytest.xfail(f"Cloud SQL <{sql_file}> query error: {err}")

def call_mySQL_upd_query_cloudsql_ui2222(csv_filter, sql_file, p_params):

    params = p_params if p_params else {
        'memberCode': csv_filter['memberCode'],
        'companyID': csv_filter['companyID']
    }

    # Prepare the query first (no Playwright needed)
    try:
        sql_path = action_const.SQL_FILE_PATH / sql_file
        with open(sql_path, 'r', encoding='utf-8') as f:
            mysql_query = f.read()

        def sql_value(value):
            if value is None:
                return "NULL"
            if isinstance(value, bool):
                return "1" if value else "0"
            if isinstance(value, (int, float)):
                return str(value)
            escaped = str(value).replace("\\", "\\\\").replace("'", "''")
            return f"'{escaped}'"

        for key, value in params.items():
            mysql_query = mysql_query.replace(f"%({key})s", sql_value(value))

        
    except Exception as err:
        logger.exception(f"Failed to prepare SQL <{sql_file}>")
        pytest.xfail(f"Failed to prepare SQL <{sql_file}>: {err}")

    # Playwright part
    with sync_playwright() as p:
        browser = p.chromium.launch(headless=True)
        context = browser.new_context(
            storage_state='playwright/.auth/googlecloudsql.json',
            permissions=['clipboard-read', 'clipboard-write'],
        )
        page = context.new_page()
        page.set_default_timeout(20000)

        try:
            page.goto(
                'https://console.cloud.google.com/sql/instances/'
                'gb-qat-db-02/studio?project=ghostbuster-dev'
            )

            page.get_by_role('combobox', name='Database').click()
            page.get_by_role('option', name=os.getenv('DB_NAME')).click()
            page.get_by_role('combobox', name='User').click()
            page.get_by_role('option', name=os.getenv('DB_USER')).click()
            page.get_by_role('textbox', name='Password').fill(os.getenv('DB_PASS'))
            page.get_by_role('button', name='Authenticate').click()
            page.get_by_role('dialog').wait_for(state='hidden', timeout=60000)

            page.get_by_label('Close tab').click()
            page.get_by_role('button', name='New tab').click()
            #logger.info(f"SQL query:\n{mysql_query}")

            # Click the visible editor text layer (the hidden textarea is covered by it)
            page.locator('.monaco-editor .view-lines').first.click()
            page.evaluate("text => navigator.clipboard.writeText(text)", mysql_query)
            page.keyboard.press('ControlOrMeta+A');
            page.keyboard.press('ControlOrMeta+V');
            page.get_by_role('button', name='Run').click()

            page.get_by_role('status').filter(
                has_text='Statement executed successfully'
            ).wait_for(state='visible', timeout=10000)

            logger.info(f"Cloud SQL <{sql_file}> executed successfully via UI.")
            return []

        except Exception as err:
            # Page is still alive here
            try:
                page.screenshot(path='cloudsql-error.png', full_page=True)
            except Exception:
                logger.warning("Could not capture screenshot")

            logger.exception(f"Cloud SQL <{sql_file}> query error")
            pytest.xfail(f"Cloud SQL <{sql_file}> query error: {err}")

        finally:
            context.close()
            browser.close()



def call_big_query(bq_client, csv_filter, sql_file,
                     p_params):  # to query mysql to get memDetails, \'is to escape '

    if p_params:
        params = p_params
    else:   
        params = {
            'memberCode': csv_filter['memberCode'],
            'companyID': csv_filter['companyID']
        }

    data = bqhlp.run_bq_query(bq_client,sql_file, params)
    return data

def call_big_query_getHitHistory(bq_client, csv_filter, p_input_filter, p_NoAction_statusID,
                             whichHit, sql_file):  # to query mysql to get memDetails, \'is to escape ':
 
    params = {
        'memberCode': csv_filter['memberCode'],
        'companyID': csv_filter['companyID']
    }

    data = bqhlp.run_bq_query_with_input(bq_client, sql_file, params, p_input_filter, p_NoAction_statusID, whichHit)
    return data

def reset_member_hits(cloudsql_page, csv_filter):
    # reset date to very old date to make sure it is outside validity period and will be ignored
    p_params = {
        'memberCode': csv_filter['memberCode'],
        'companyID': csv_filter['companyID'],
        'date_to_change_UTC': '2025-02-02 04:00:00'
    }
    call_mySQL_upd_query_cloudsql_ui(cloudsql_page,csv_filter, 'reset_mem_GbRuleHits_Mysql_msp.sql', p_params)
    call_mySQL_upd_query_cloudsql_ui(cloudsql_page,csv_filter, 'reset_mem_GbRuleHits_Mysql_mspa.sql', p_params)
    call_mySQL_upd_query_cloudsql_ui(cloudsql_page,csv_filter, 'reset_mem_GbFeatureHits_Mysql.sql', p_params)
    call_mySQL_upd_query_cloudsql_ui(cloudsql_page,csv_filter, 'reset_mem_BetDelay_Mysql.sql', p_params)

def modify_HitDate_or_mem_attribute_date(cloudsql_page, csv_filter):
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
            call_mySQL_upd_query_cloudsql_ui(cloudsql_page,csv_filter, 'edit_UpdByDate_GbRuleHits_Mysql_msp.sql', p_params)
            call_mySQL_upd_query_cloudsql_ui(cloudsql_page,csv_filter, 'edit_UpdByDate_GbRuleHits_Mysql_mspa.sql', p_params)
        else:  # gbfeature
            call_mySQL_upd_query_cloudsql_ui(cloudsql_page,csv_filter, 'edit_UpdByDate_GbFeatureHits_Mysql.sql', p_params)

    # update the lastupdateby of member's setting(bl,sg,bd,memCat)
    if pairs['upd_memsetting_DT'].lower() == 'yes':
        call_mySQL_upd_query_cloudsql_ui(cloudsql_page,csv_filter, 'edit_UpdByDate_BD_Mysql.sql', p_params)
        call_mySQL_upd_query_cloudsql_ui(cloudsql_page,csv_filter, 'edit_UpdByDate_BLSGMemCat_Mysql.sql', p_params)
