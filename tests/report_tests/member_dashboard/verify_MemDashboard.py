#update your testing filters csv file
#go terminal and enter this command : pytest test_scenarios/test_reports/verify_MemDashboard.py -v --tb=short
#jsut execute from root directly.standard practice
import csv
import requests
import pytest
import sys
import os
import datetime
from typing import List, Dict, Any, Optional
from google.cloud import bigquery
from google.oauth2 import service_account
from unittest.mock import patch
from collections import defaultdict

# Constants
API_BASE_URL = "https://api.qat.fraudsterkill.com/api"
#when copying auth_token from f12 developer tool, copy as raw source to avoid ...(abreviation)
AUTH_TOKEN = "Bearer eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9.eyJleHAiOjE3OTI2NDE3MDEsInVzZXIiOnsiaWQiOjQyLCJuYW1lIjoiYWRtaW4ucWFteXRlc3QiLCJyb2xlR3JvdXAiOiJDb21wbGlhbmNlIiwidHJhY2VJRCI6IjBITlA5TlJDTU5EQUI6MDAwMDAwMTYifSwicGVybWlzc2lvbnMiOlszLDExLDEyLDE1LDE2LDE3LDE5LDIwLDIxLDIyLDIzLDI0LDI1LDI4LDI5LDMwLDMxLDMyLDMzLDM0LDM1LDM2LDM3LDM5LDQwLDQxLDQyLDQzLDQ0LDQ1LDQ2LDQ3LDQ4LDQ5LDUwLDUxLDUyLDUzLDYwLDYxLDYyLDYzLDY0LDY1LDY2LDY3LDY4LDY5LDczLDc0LDc1LDc2LDc3LDc4LDc5LDgwLDgxLDgyLDgzLDg0LDg1LDg2LDg3LDg4LDg5LDkzLDk0LDk1LDk3LDk4LDk5LDEwMCwxMDEsMTAyLDEwMywxMDQsMTA1LDEwNiwxMDcsMTA4LDEwOSwxMTAsMTExLDExMiwxMTMsMTE0LDExNSwxMTYsMTE3LDExOCwxMjAsMTIxLDEyMiwxMjMsMTI0LDEyNSwxMjYsMTI3LDEyOCwxMjksMTMwLDEzMSwxMzIsMTMzLDEzNCwxMzUsMTM2LDEzNywxMzksMTQwLDE0MSwxNDIsMTQzLDE0NCwxNDUsMTQ2LDE0NywxNDgsMTQ5LDE1MCwxNTEsMTUyLDE1MywxNTQsMTU1LDE1NiwxNTgsMTU5LDE2MCwxNjcsMTY4LDE2OSwxNzAsMTcxLDE3MiwxNzMsMTc0LDE3NSwxNzYsMTc4LDE3OSwxODAsMTgxLDE4MiwxODMsMTg0LDE4NSwxODYsMTk5LDIwMCwyMDEsMjAyLDIwMywyMDQsMjA1LDIwNiwyMDcsMjA4LDIwOSwyMTAsMjExLDIxMiwyMTksMjIwLDIyMSwyMjIsMjIzLDIyNCwyMjUsMjI2LDIyNywyMjgsMjI5LDIzMCwyMzEsMjMyLDIzMywyMzQsMjM1LDIzNiwyMzcsMjM4LDIzOSwyNDAsMjQxLDI0MiwyNDMsMjQ0LDI0NSwyNDYsMjQ3LDI0OCwyNDksMjUwLDI1MiwyNTMsMjU0LDI1NSwyNTYsMjU3LDI2MCwyNjEsMjYyLDI2MywxLDIsOSwyNiwyNyw5MCwxNTcsMTc3LDI1MV19.-iXT7gO6e3DLNYdEZX_axf8k17zO5IIadoNWsxolpYQ"
# Helper Functions
def call_api(api_session, who: str,method: str, url: str, json_data: Optional[Dict] = None) -> requests.Response:
    """Make an API request."""
    #print('urllll,',url)
    response = api_session.request(
            method=method,
            url=url,
            json=json_data)
        # proxies=PROXIES)
        # verify=not bool(PROXIES))  # Disable verify if using proxy
    assert response.status_code == 200,f"calling to {who} return {response.status_code} "
    return response
        # sys.exit(1)

def GetDashboardWagerPerformanceList(csv_filter: Dict,api_session) -> requests.Response:
    """
    """
    url = f"{API_BASE_URL}/membersetting/GetDashboardWagerPerformanceList"
    data = {"dateFrom":csv_filter['dateFrom_API'],
            "dateTo":csv_filter['dateTo_API'],
            "memberCode":csv_filter['memberCode'],
            "companyID":csv_filter['companyID'],
            "sportIDs":csv_filter['sportNames'],
            "competitionName":csv_filter['competitionName'],
            "wagerSourceIDs":csv_filter['wagerSourceNames'],
            "comboGroupIDs":csv_filter['comboGroupNames'],"comboSelectionIDs":csv_filter['comboSelectionNames'],"periodIDs":csv_filter['periodNames'],
            "marketIDs":csv_filter['marketNames'],"betTypeIDs":csv_filter['betTypeNames'],"minStakeAmount":csv_filter['minStakeAmount'],
            "maxStakeAmount":csv_filter['maxStakeAmount'],
            "minWinloseAmountBase":csv_filter['minWinloseAmountBase'],"manualCancelledReasonIDs":csv_filter['manualCancelledReasonNames'],
            "systemCancelledReasonIDs":csv_filter['systemCancelledReasonNames'],"soccerTypes":csv_filter['soccerTypes'],"basketballTypes":csv_filter['basketballTypes']
    }
    #print("Request bodyyyy:", data)
    response = call_api(api_session,'GetDashboardWagerPerformanceList', 'post', url, data)
    return response


def format_time1(ddmmyyyy_slash):
    # Original date string
    date_str = ddmmyyyy_slash
    # Parse the date string into a datetime object
    dt = datetime.datetime.strptime(date_str, '%d/%m/%Y')
    # Add 4 hours to set time to 04:00:00
    dtFROM = dt + datetime.timedelta(hours=4)
    dtTO = dt + datetime.timedelta(hours=28)  # end of day
    # Convert to YYYY-mm-ddTHH:MM:SS format
    dateFR_YmdTHMS = dtFROM.strftime('%Y-%m-%dT%H:%M:%S')
    dateFR_YmdSHMS = dtFROM.strftime('%Y-%m-%d %H:%M:%S')
    dateTO_YmdTHMS = dtTO.strftime('%Y-%m-%dT%H:%M:%S')
    dateTO_YmdSHMS = dtTO.strftime('%Y-%m-%d %H:%M:%S')
    return {"dateFR_YmdTHMS": dateFR_YmdTHMS, "dateFR_YmdSHMS": dateFR_YmdSHMS,"dateTO_YmdTHMS": dateTO_YmdTHMS, "dateTO_YmdSHMS": dateTO_YmdSHMS}

def read_csv(file_path: str) -> List[Dict]:
    """Read all lines from CSV and return a list of dictionaries with each dic as a line from csv"""
    """[{"date":'2024-04-2","memcat":'VIP","soccount":3},{"date":'2024-04-2","memcat":'VIP","soccount":3},...]"""
    try:
        with open(file_path, mode='r', newline='') as csvfile:
            reader = csv.DictReader(csvfile)
            return [row for row in reader]
    except FileNotFoundError:
        print(f"File not found: {file_path}")
        sys.exit(1)

def format_filters(csv_rows: List[Dict]) -> List[Dict]:
    """convert each of the value provided in csv(data read from csv is always str) to the value used in API request"""
    """eg. memCat is VIP;Arber in csv file, reformat it into [16,3], which is required by API req"""
    """eg. socPMcount is 3 (str format),  reformat it into 3 (int format)"""
    """eg. memCat is empty in csv file, reformat it into [], which is required by API req"""
    """notes: when using statement 'if <some_var>', sys always returns False when <some_var> is None,empty string,empty list,NUMBER 0,etc"""
    """   since csv only read as string format, so we can use 'if <some_var> to determine the existence of csv value"""
    """   but after converting all csv value into api format, the original csv value can be in different format now(eg. int,str,list,tuple,None,etc...)"""
    """ so in validating/assertion part, careful when checking the existense of int field, as Number 0 will be treated as false"""
    """ so on int field, use 'if abc or abc ==0' to ensure assertion to carry out even for 0 value"""
    formatted_filters = []
    for row in csv_rows:
        formatted_filter = {
            "testcase": row['testcase'],
            "dateFrom_API": format_time1(row['dateFrom'])['dateFR_YmdTHMS'],
            "dateFrom_BQ": format_time1(row['dateFrom'])['dateFR_YmdSHMS'],
            "dateTo_API": format_time1(row['dateTo'])['dateTO_YmdTHMS'],
            "dateTo_BQ": format_time1(row['dateTo'])['dateTO_YmdSHMS'],
            "memberCode":row['memberCode'],
            "companyID":int(row['companyID']),
            "sportNames":[int(id) for id in row['sportNames'].split(';')] if row['sportNames'] else [],
            "competitionName":row['competitionName'],
            "wagerSourceNames":	[int(id) for id in row['wagerSourceNames'].split(';')] if row['wagerSourceNames'] else [],
            "wagerTypeNames": int(row['wagerTypeNames']) if row['wagerTypeNames'] else [],
            "comboGroupNames":int(row['comboGroupNames']) if row['comboGroupNames'] else [],
            "comboSelectionNames": int(row['comboSelectionNames']) if row['comboSelectionNames'] else [],
            "periodNames": int(row['periodNames']) if row['periodNames'] else [],
            "marketNames": int(row['marketNames']) if row['marketNames'] else [],
            "betTypeNames": int(row['betTypeNames']) if row['betTypeNames'] else [],
            "minStakeAmount": float(row['minStakeAmount']) if row['minStakeAmount'] else None,
            "maxStakeAmount": float(row['maxStakeAmount']) if row['maxStakeAmount'] else None,
            "minWinloseAmountBase": float(row['minWinloseAmountBase']) if row['minWinloseAmountBase'] else None,
            "manualCancelledReasonNames": int(row['manualCancelledReasonNames']) if row['manualCancelledReasonNames'] else [],
            "systemCancelledReasonNames": int(row['systemCancelledReasonNames']) if row['systemCancelledReasonNames'] else [],
            "basketballTypes": int(row['basketballTypes']) if row['basketballTypes'] else [],
            "soccerTypes": int(row['soccerTypes']) if row['soccerTypes'] else []

        }
        formatted_filters.append(formatted_filter)
    return formatted_filters



def bigquery_query_returns_rows(bigquery_client, csv_filter):
    try:
        test_dir = os.path.dirname(__file__)   #in the same directory of running test script
        sql_path = os.path.join(test_dir, "MemberDashboard_bq.txt")
        with open(sql_path, "r") as file:
            query_temp = file.read()

            # Inject the dynamic value
        query = query_temp.format(P_fromdt=csv_filter['dateFrom_BQ'], P_todt=csv_filter['dateTo_BQ'], P_members=csv_filter['memberCode'],P_coyid=csv_filter['companyID'])

        query_job = bigquery_client.query(query)
        results = list(query_job.result())
        #for row in results:
        #   print('wrow:',dict(row))
        # Basic assertion: Ensure at least one row is returned
        assert len(list(results)) > 0, "Expected at least one row from BigQuery"
        return [dict(row) for row in results]


    except FileNotFoundError as e:
        pytest.fail(f"Test failed due to missing credentials file: {e}")

    #except GoogleAPIError as e:
     #   pytest.fail(f"Google API error: {e}")

    except Exception as e:
        pytest.fail(f"Unexpected error: {e}")

@pytest.fixture(scope="session")
def api_session():
    session = requests.Session()
    session.headers.update(
        {"Authorization": AUTH_TOKEN, "Content-Type": "application/json; charset=utf-8", "Connection": "keep-alive"})
    yield session
    session.close()

KEY_PATH = "C:/Users/lim.miin/Desktop/testing/py-gcpBQ/carbon-sensor-259109-d37561cb1a02.json"
@pytest.fixture(scope="session")
def bigquery_client():
    if not os.path.exists(KEY_PATH):
        pytest.skip("Service account key file not found")
    credentials = service_account.Credentials.from_service_account_file(KEY_PATH)
    client = bigquery.Client(credentials=credentials, project=credentials.project_id)
    return client

def format_value(key,value):
    # Parse date to string to tally with date format in API response"
    # Format float to 2 decimal places
    if isinstance(value, (int, float)):
        return round(value, 2)
    if isinstance(value, str):
        return value.lower()
    if isinstance(value, datetime.date)  and key == 'eventDate':
        return value.strftime('%Y-%m-%dT00:00:00')
    if isinstance(value, datetime.date) and key == 'eventMonth':
        return value.strftime('%Y-%m')

    return value  # keep other types (int, None, str, etc.)


# Test Function
@pytest.mark.parametrize("csv_filter"
                         ,format_filters(read_csv("C:/Users/lim.miin/Desktop/testing/Output check/MemberDashboard.csv"))
                         ,ids=lambda csv_filter: f"testcase_{csv_filter['testcase']}"
                         )
#comment:: use this block of code if calling real Object(GetArberMemberSummaryList API)
#===========================[BEGIN of code]==================================
def test_MemberDashboard(csv_filter,bigquery_client,api_session):
#===========================[END of code]====================================

#===========================[BEGIN of code]==================================
# @patch('verify_MemDashboard.GetDashboardWagerPerformanceList')
# @patch('verify_MemDashboard.bigquery_query_returns_rows')
# def test_MemberDashboard(MockMemDashBQ,MockMemDashAPI,csv_filter,bigquery_client,api_session):
#     MockMemDashAPI.return_value.status_code = 200
#     MockMemDashAPI.return_value.json.return_value = {
#     "totalCount": 0,
#     "pageSize": 0,
#     "page": 0,
#     "data":[{'performanceTypeName': 'BetType','eventDate': None, 'eventMonth': None, 'sportName': None, 'wagerComboSelection': None, 'competitionTierGroup': None, 'wagerSourceName': None, 'marketName': None, 'competitionName': None, 'betTypeName': 'Away clean sheet', 'betCount': None, 'turnoverAmountBase': 30, 'winLoseAmountBase': -10.45, 'potentialExposureAmountBase': 30, 'winLoseBTAmount': -10.45, 'winLossPercentage': -34.8333333333333, 'betSize': None, 'cancelledExposureVolume': None, 'avgWinLossDifferent': None, 'turnoverVolume': 1.86915887850467, 'brobtSourceVolume': None, 'winCount': None, 'loseCount': None, 'winStakeAmountBase': None, 'loseStakeAmountBase': None, 'avgWin':None, 'avgLose': None, 'stakeRange': None, 'ipAddress': None, 'countryName': None, 'wagerMemberCategoryID': None, 'wagerMemberCategoryName': '', 'goodBadPrice': None, 'maxCreatedDate': None, 'totalCount': 0} ],
#     "result": True,
#     "message": None
# }  #IPAddress
#     MockMemDashBQ.return_value = [
#         {'performanceTypeName': 'BetType', 'eventDate': None, 'eventMonth': None, 'sportName': None, 'wagerComboSelection': None, 'competitionTierGroup': None, 'wagerSourceName': None, 'marketName': None, 'competitionName': None, 'betTypeName': 'Away Clean Sheet', 'betCount': None, 'turnoverAmountBase': 30.0,
#          'potentialExposureAmountBase': None, 'winLoseBTAmount': -10.450000000000001, 'winLossPercentage': -34.833333333333336, 'betSize': None, 'cancelledExposureVolume': None, 'avgWinLossDifferent': None,
#  'turnoverVolume': 1.8691588785046727, 'brobtSourceVolume': None, 'winCount': None, 'loseCount': None, 'winStakeAmountBase': None, 'loseStakeAmountBase': None, 'avgWin': None,
#          'avgLose': None, 'stakeRange': None, 'ipAddress': None, 'countryName': None, 'wagerMemberCategoryID': None,
#          'wagerMemberCategoryName': None, 'goodBadPrice': None, 'maxCreatedDate': None, 'totalCount': None}
#     ]

    #===================================[END of code]==================================

    #print('csv_filter===',csv_filter)
    response = GetDashboardWagerPerformanceList(csv_filter, api_session)
    assert response.status_code == 200, f"API returned {response.status_code} after calling GetDashboardWagerPerformanceList"
    api_resp = response.json()

    # get bigquery result
    memDashboard_bq_rows = bigquery_query_returns_rows(bigquery_client,csv_filter)
    #print('memDashboard_bq_rows::',memDashboard_bq_rows)

    UI_recs = api_resp['data']  #contains all recs after entering filter values and click search
    #print('UI_recs==',UI_recs)

    grouped = defaultdict(list)            # to build empty dictionary. each key has value of list type
    # dictt = defaultdict(list)            # {a:[],b:[],c:[]}  supposed format when it contains value
    # dictt["a"].append("valuea")          # this will modify value(list type) of key "a"
    # dictt["a"].append({"x":"y","z":3})

    #put records into different group based on the performanceTypeName
    for row in UI_recs:
        row_copy = row.copy()  # Avoid modifying the original row
        group_key = row_copy.pop("performanceTypeName")  # Extract and remove 'type' from the row
        grouped[group_key].append(row_copy)  # Add the rest of the row to the appropriate group

    for bq_row in memDashboard_bq_rows: # get bq row
        #print('bq_row_current:',bq_row)
        #print('uir_row_all:',grouped[bq_row["performanceTypeName"]])
        #print(grouped,' ,type is:', type(grouped))
        for ui_row in grouped[bq_row["performanceTypeName"]]: #scan thru each Ui rec of that group, for each ui rec ,do below:
            for key,value in bq_row.items():
                if value == None  or key == 'performanceTypeName':
                    continue
                bq_value = format_value(key,value)
                ui_value = format_value(key,ui_row.get(key))
                if bq_value != ui_value:
                    match_uirec_found = False
                    break   #since item mismatched, break from this for loop(scan each item in ui dictionary)

                match_uirec_found = True
            #finish scanning current bq_row with curent ui_rec
            if match_uirec_found:
                break
        #finish scanning current bq_row thru all ui_rec
        assert match_uirec_found == True, f'No matching bq_row :{bq_row} can be found in ui_row of group {bq_row["performanceTypeName"]} :{grouped[bq_row["performanceTypeName"]]}'

            # item_found = all(                                  #compare current bq row against each ui row
            #     value is None or value == 'nan'  or key== 'performanceTypeName' or ui_row.get(key) == value
            #     for key, value in bq_row.items()
            # )
        #     print('found or not:',item_found)
        #     if item_found == True:
        #         break
        # assert item_found==True, f'bq_row :{bq_row} not tally with ui-rec'


# Main Execution
if __name__ == "__main__":
    pytest.main()

'''
#==NOTES:==
#refer to verify_MemDashboard(readme).txt for the high level flow
#what this script support/verify so far:   
  #for filtering only support eventDate & membercode, only 2 parameter are hardcoded in bq sql now
  #below table is not ready yet:
     #'Overall Performance' table as bq script is not ready yet
     #'good/bad price' table as data is stored in mysql(to explore later)
'''
