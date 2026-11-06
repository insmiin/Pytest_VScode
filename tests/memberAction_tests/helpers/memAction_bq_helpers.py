from datetime import date, datetime
from pathlib import Path
import pytest
import tests.memberAction_tests.memberAction_Constants as action_const
import logging
import warnings
warnings.filterwarnings(
    "ignore",
    message="Your application has authenticated using end user credentials from Google Cloud SDK without a quota project.*",
    category=UserWarning
)
from google.cloud import bigquery
from google.api_core import exceptions as gexc

logger = logging.getLogger(__name__)

# PROJECT_ID = "carbon-sensor-259109"
# _client = bigquery.Client(project=PROJECT_ID)


def _to_python(value):
    """Convert numpy/pandas scalars to plain Python types."""
    return value.item() if hasattr(value, "item") else value


# def _build_param(name, value):
#     value = _to_python(value)

#     # Lists -> array parameter
#     if isinstance(value, (list, tuple)):
#         values = [_to_python(v) for v in value]
#         elem_type = _bq_type(values[0]) if values else "STRING"
#         return bigquery.ArrayQueryParameter(name, elem_type, values)

#     return bigquery.ScalarQueryParameter(name, _bq_type(value), value)


def _bq_type(value):
    # bool must be checked before int (bool is a subclass of int)
    if isinstance(value, bool):
        return "BOOL"
    if isinstance(value, int):
        return "INT64"
    if isinstance(value, float):
        return "FLOAT64"
    if isinstance(value, datetime):
        return "TIMESTAMP"
    if isinstance(value, date):
        return "DATE"
    return "STRING"

import re

def render_sql(template: str, params: dict) -> str:
    for key, value in params.items():
        if isinstance(value, bool):
            raise ValueError(f"Bool not supported for '{key}'")
        if isinstance(value, (int, float)):
            literal = str(value)
        else:
            value = str(value)
            if not re.fullmatch(r"[A-Za-z0-9_\-]+", value):
                raise ValueError(f"Unsafe value for '{key}': {value!r}")
            literal = f"'{value}'"
        # \b stops @age from matching inside @agenda
        template = re.sub(rf"@{re.escape(key)}\b", lambda m: literal, template)
    return template

def run_bq_query(bq_client: bigquery.Client, sql_file: str, params: dict | None = None) -> list[dict]:
    """
    Run a SQL file against BigQuery with named parameters.

    sql_file: file name (or full path) of the SQL text file
    params:   dict whose keys match the @placeholders in the SQL
    returns:  list of row dicts
    """
    try:
        sql_path = action_const.SQL_FILE_PATH / sql_file
    
        with open(sql_path, 'r') as f:
            mysql_query = f.read()
    except FileNotFoundError:
            pytest.xfail(f"SQL query file '{sql_file}' not found")

    try:
    #     job_config = bigquery.QueryJobConfig(
    #     query_parameters=[_build_param(k, v) for k, v in (params or {}).items()]
    # )
    #   job = _client.query(mysql_query, job_config=job_config) 

    #   call render_sql to replace placeholders with actual values to build the final query string
        mysql_query = render_sql(mysql_query, params)
        
        job = bq_client.query(mysql_query)
        data = [dict(row) for row in job.result()]
    except gexc.BadRequest as e:
        pytest.fail(f"SQL error in '{sql_file}': {e.message}")
    except gexc.GoogleAPICallError as e:
        pytest.fail(f"BigQuery error for '{sql_file}': {e.message}")

    if sql_file == "getMemDetails_Mysql.sql":
        assert len(data) == 1, "no member or more than 1 same member row was returned from mysql"
        return data[0]
    return data

def run_bq_query_with_input(bq_client: bigquery.Client, sql_file: str, params: dict | None = None, p_input_filter: str | None = None, p_NoAction_statusID: str | None = None, whichHit: str | None = None) -> list[dict]:
    if p_input_filter:
            input_filter = p_input_filter
    else:
            input_filter = '1=1'
    
    if whichHit == 'AllHits':
            actionID_to_filter = p_NoAction_statusID
    else:
            actionID_to_filter = "''"
    
    try:
        sql_path = action_const.SQL_FILE_PATH / sql_file
    
        with open(sql_path, 'r') as f:
            mysql_query = f.read()

        mysql_query = mysql_query.format(filter_statement=input_filter, action_disallowed=p_NoAction_statusID,
                                                 actionID_to_filter=actionID_to_filter)
        
    except FileNotFoundError:
            pytest.xfail(f"SQL query file '{sql_file}' not found")

    
    try:
    #     job_config = bigquery.QueryJobConfig(
    #     query_parameters=[_build_param(k, v) for k, v in (params or {}).items()]
    # )
    #   job = _client.query(mysql_query, job_config=job_config) 

    #   call render_sql to replace placeholders with actual values to build the final query string
        mysql_query = render_sql(mysql_query, params)
        
        job = bq_client.query(mysql_query)
        data = [dict(row) for row in job.result()]
    except gexc.BadRequest as e:
        pytest.fail(f"SQL error in '{sql_file}': {e.message}")
    except gexc.GoogleAPICallError as e:
        pytest.fail(f"BigQuery error for '{sql_file}': {e.message}")

    if sql_file == "getMemDetails_Mysql.sql":
        assert len(data) == 1, "no member or more than 1 same member row was returned from mysql"
        return data[0]
    return data

# params = {
#     'memberCode': "abc123",
#     'companyID': 2395
# }

# rows = run_bq_query(bq_client, "querytxt2.txt", params)

# for r in rows:
#     print(r)