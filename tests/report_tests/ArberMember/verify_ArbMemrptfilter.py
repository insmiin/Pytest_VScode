#update your testing filters csv file
#go terminal and enter this command "pytest verify_ArbMemrptfilter.py -v --tb=short"
import csv
import requests
import pytest
import sys
from datetime import datetime
from typing import List, Dict, Any, Optional
from unittest.mock import patch

# Constants
API_BASE_URL = "https://api.qat.fraudsterkill.com/api"
AUTH_TOKEN = "Bearer eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9.eyJ1c2VyIjp7ImlkIjoxLCJuYW1lIjoiYWRtaW4ifSwicGVybWlzc2lvbnMiOlszLDExLDEyLDE1LDE2LDE3LDE5LDIwLDIxLDIyLDIzLDI0LDI1LDI4LDI5LDMwLDMxLDMyLDMzLDM0LDM1LDM2LDM3LDM5LDQwLDQxLDQyLDQzLDQ0LDQ1LDQ2LDQ3LDQ4LDQ5LDUwLDUxLDUyLDUzLDYwLDYxLDYyLDYzLDY0LDY1LDY2LDY3LDY4LDY5LDczLDc0LDc1LDc2LDc3LDc4LDc5LDgwLDgxLDgyLDgzLDg0LDg1LDg2LDg3LDg4LDg5LDkzLDk0LDk1LDk2LDk3LDk4LDk5LDEwMCwxMDEsMTAyLDEwMywxMDQsMTA1LDEwNiwxMDcsMTA4LDEwOSwxMTAsMTExLDExMiwxMTMsMTE0LDExNSwxMTYsMTE3LDExOCwxMjAsMTIxLDEyMiwxMjMsMTI0LDEyNSwxMjYsMTI3LDEyOCwxMjksMTMwLDEzMSwxMzIsMTMzLDEzNCwxMzUsMTM2LDEzNywxMzksMTQwLDE0MSwxNDIsMTQzLDE0NCwxNDUsMTQ2LDE0NywxNDgsMTQ5LDE1MCwxNTEsMTUyLDE1MywxNTQsMTU1LDE1NiwxNTcsMTU4LDE1OSwxNjAsMTY3LDE2OCwxNjksMTcwLDE3MSwxNzIsMTczLDE3NCwxNzUsMTc2LDE3OCwxNzksMTgwLDE4MSwxODIsMTgzLDE4NCwxODUsMTg2LDE4NywxODgsMTg5LDE5MCwxOTEsMTkyLDE5MywxOTQsMTk1LDE5NiwxOTcsMTk4LDE5OSwyMDAsMjAxLDIwMiwyMDMsMjA0LDIwNSwyMDYsMjA3LDIwOCwyMDksMjEwLDIxMSwyMTIsMjEzLDIxNCwyMTUsMjE5LDIyMCwyMjEsMjIyLDIyMywyMjQsMjI1LDIyNiwyMjcsMjI4LDIyOSwyMzAsMjMxLDIzMiwyMzMsMjM0LDIzNSwyMzYsMjM3LDIzOCwyMzksMjQwLDI0MSwyNDIsMjQzLDEsMiw5LDEwLDI2LDI3LDkwLDE3N10sImlhdCI6MTc0MzA0NDUyNiwiZXhwIjoxNzQzNjQ5MzI2fQ.klfh9mVxIl0KQHpt5rmItRLGmxL23HXaNtw8UQTcWcc"
HEADERS = {
    "Authorization": AUTH_TOKEN,
    "Content-Type": "application/json",
    "Connection": "keep-alive"
}
PROXIES = {
    'http': 'http://127.0.0.1:8888', # Fiddler's default HTTP proxy
    'https': 'http://127.0.0.1:8888' # Fiddler's default HTTP proxy
}

# Helper Functions
def call_api(method: str, url: str, json_data: Optional[Dict] = None) -> requests.Response:
    """Make an API request."""
    try:
        if method == 'get':
            response = requests.get(url, headers=HEADERS, json=json_data)  #, proxies=PROXIES, verify=False)   #if fiddler is open, include these 2 parameters too
        elif method == 'post':
            response = requests.post(url, headers=HEADERS, json=json_data) #, proxies=PROXIES, verify=False)
        else:
            raise ValueError(f"Invalid method: {method}")
        response.raise_for_status()
        return response
    except requests.exceptions.RequestException as e:
        print(f"API request failed: {e}")
        #sys.exit(1)

def get_mem_cat_list() -> List[Dict]:
    """Call member category API and returns a list of dict,each dict contains diff memCat details."""
    url = f"{API_BASE_URL}/common/getMemberCategoryList"
    response = call_api('get', url)
    memCat_list = response.json()['data']
    # Create a dictionary to map company names to their coyid and age
    memCat_dict = {c['label']:  c['value']  for c in memCat_list}
    return memCat_dict

def get_company_list() -> List[Dict]:
    """Call member category API and returns a list of dict,each dict contains diff company details."""
    url = f"{API_BASE_URL}/common/getCompanyList"
    response = call_api('get', url)
    coy_list = response.json()['data']
    # Create a dictionary to map company names to their coyid and age
    company_dict = {c['companyName']:  c['companyID']  for c in coy_list}
    return company_dict

def latest_job_schedule(job_type_id: Dict) -> Dict:
    """Get the latest job schedule from API."""
    url = f"{API_BASE_URL}/common/getDBJobInfoDetailByJobTypeId"
    response = call_api('post', url, job_type_id)
    return response.json()['data']['value']

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
    mem_cat_dict = get_mem_cat_list() #list of dict with memCat details
    company_dict  = get_company_list()
    job_date = latest_job_schedule({"jobTypeID": 59})
    date_object = datetime.strptime(job_date, '%Y-%m-%d %H:%M:%S')
    fmt_job_date = date_object.strftime('%Y-%m-%dT%H:%M:%S')
    formatted_filters = []
    for row in csv_rows:
        csv_coy_list = row['companyName'].split(';')
        csv_gbMemberCategoryName = row['gbMemberCategoryName'].split(';')
        csv_sfMemberCategoryName = row['sfMemberCategoryName'].split(';')
        csv_hitSFMemberCategoryName = row['hitSFMemberCategoryName'].split(';')
        formatted_filter = {
            "testcase": row['testcase'],
            "taggedDate_from": f"{row['taggedDate_from']}T04:00:00" if row['taggedDate_from'] else None,
            "taggedDate_to": f"{row['taggedDate_to']}T04:00:00" if row['taggedDate_to'] else None,
            "API_fmt_job_date": fmt_job_date,
            "API_companyName": [company_dict[coy] for coy in csv_coy_list if coy in company_dict],
            "companyName": csv_coy_list if row['companyName'] else row['companyName'],
            "memberCode": row['memberCode'],
            "API_gbMemberCategoryName": [mem_cat_dict[mem_cat] for mem_cat in csv_gbMemberCategoryName if mem_cat in mem_cat_dict],
            "gbMemberCategoryName": csv_gbMemberCategoryName if row['gbMemberCategoryName'] else row['gbMemberCategoryName'],
            "API_sfMemberCategoryName": [mem_cat_dict[mem_cat] for mem_cat in csv_sfMemberCategoryName if mem_cat in mem_cat_dict],
            "sfMemberCategoryName": csv_sfMemberCategoryName if row['sfMemberCategoryName'] else row['sfMemberCategoryName'],
            "API_hitSFMemberCategoryName": [mem_cat_dict[mem_cat] for mem_cat in csv_hitSFMemberCategoryName if mem_cat in mem_cat_dict],
            "hitSFMemberCategoryName": csv_hitSFMemberCategoryName if row['hitSFMemberCategoryName'] else row['hitSFMemberCategoryName'],
            "soccerPMRejectedBetCount": int(row['soccerPMRejectedBetCount']) if row['soccerPMRejectedBetCount'] else None,
            "soccerRBRejectedBetCount": int(row['soccerRBRejectedBetCount']) if row['soccerRBRejectedBetCount'] else None,
            "basketballPMRejectedBetCount": int(row['basketballPMRejectedBetCount']) if row['basketballPMRejectedBetCount'] else None,
            "basketballRBRejectedBetCount": int(row['basketballRBRejectedBetCount']) if row['basketballRBRejectedBetCount'] else None,
            "dayRangeTypeID": [int(id) for id in row['dayRangeTypeID'].split(';')] if row['dayRangeTypeID'] else [],
            "API_soccerScore" : row['soccerScore'] if row['soccerScore'] else None,
            "soccerScore": int(row['soccerScore']) if row['soccerScore'] else None,
            "API_bbScore": row['bbScore'] if row['bbScore'] else None,
            "bbScore": int(row['bbScore']) if row['bbScore'] else None,
            "API_totalWagerCount":  row['totalWagerCount'] if row['totalWagerCount'] else None,
            "totalWagerCount": int(row['totalWagerCount']) if row['totalWagerCount'] else None,
            "API_totalExposureAmountBase": row['totalExposureAmountBase'] if row['totalExposureAmountBase'] else None,
            "totalExposureAmountBase": float(row['totalExposureAmountBase']) if row['totalExposureAmountBase'] else None,
            "API_realSoccerExposurePercent":  row['realSoccerExposurePercent'] if row['realSoccerExposurePercent'] else None,
            "realSoccerExposurePercent": float(row['realSoccerExposurePercent']) if row['realSoccerExposurePercent'] else None,
            "API_realBBExposurePercent": row['realBBExposurePercent'] if row['realBBExposurePercent'] else None,
            "realBBExposurePercent": float(row['realBBExposurePercent']) if row['realBBExposurePercent'] else None,
            "API_totalWinLoseAmountBase": row['totalWinLoseAmountBase'] if row['totalWinLoseAmountBase'] else None,
            "totalWinLoseAmountBase": float(row['totalWinLoseAmountBase']) if row['totalWinLoseAmountBase'] else None
        }
        formatted_filters.append(formatted_filter)
    return formatted_filters


def get_arber_mem_report(csv_filter: Dict) -> requests.Response:
    """
    Call the Arber Member Report API with the provided filter.

    Args:
        csv_filter (Dict): A dictionary containing filter parameters.

    Returns:
        requests.Response: The API response.
    """
    url = f"{API_BASE_URL}/memberlevelreport/GetArberMemberSummaryList"
    data = {
        "startDate": csv_filter['taggedDate_from'],
        "endDate": csv_filter['taggedDate_to'],
        "lastUpdatedDate": csv_filter['API_fmt_job_date'],
        "companyIDs": csv_filter['API_companyName'],
        "SFMemberCategoryIDs": csv_filter['API_sfMemberCategoryName'],
        "GBMemberCategoryIDs": csv_filter['API_gbMemberCategoryName'],
        "HitRuleMemberCategoryIDs": csv_filter['API_hitSFMemberCategoryName'],
        "memberCode": csv_filter['memberCode'],
        "minArberSoccerPMRejectedBetCount": csv_filter['soccerPMRejectedBetCount'],
        "minArberSoccerRBRejectedBetCount": csv_filter['soccerRBRejectedBetCount'],
        "minArberBasketballPMRejectedBetCount": csv_filter['basketballPMRejectedBetCount'],
        "minArberBasketballRBRejectedBetCount": csv_filter['basketballRBRejectedBetCount'],
        "dayRangeTypeIDs": csv_filter['dayRangeTypeID'],
        "minSoccerScore": csv_filter['API_soccerScore'],
        "minBasketballScore": csv_filter['API_bbScore'],
        "minWagerCount": csv_filter['API_totalWagerCount'],
        "minExposureAmount": csv_filter['API_totalExposureAmountBase'],
        "minSoccerExposurePCT": csv_filter['API_realSoccerExposurePercent'],
        "minBasketballExposurePCT": csv_filter['API_realBBExposurePercent'],
        "minWinLoseAmount": csv_filter['API_totalWinLoseAmountBase'],
        "page": 1,
        "pageSize": 10
    }
    print("Request bodyyyy:", data)
    response = call_api('post', url, data)
    return response

def validate_date_range(csv_filter,UI_rec) -> None:
    """Validate that the TaggedDate of all d records on report, fall within the inputted date range."""
    if csv_filter['taggedDate_from'] and csv_filter['taggedDate_to']:
        csv_start_date = datetime.strptime(csv_filter['taggedDate_from'], "%Y-%m-%dT%H:%M:%S") #convert str to datetime
        csv_end_date = datetime.strptime(csv_filter['taggedDate_to'], "%Y-%m-%dT%H:%M:%S")

        tagged_date = datetime.strptime(UI_rec['taggedDate'], "%Y-%m-%dT%H:%M:%SZ")
        assert csv_start_date <= tagged_date <= csv_end_date, \
                f"TaggedDate {tagged_date} of {UI_rec['memberCode']} doesn't meet filtering dateRange."


def validate_others(csv_filter,UI_rec,csv_field) -> None:
    assert isinstance(csv_filter[csv_field], (int, float,list,str)), f"invalid data type for {csv_field}"


    if isinstance(csv_filter[csv_field], list):
        expected_values = set(map(str.upper, csv_filter[csv_field]))
        assert UI_rec[csv_field].upper() in expected_values, \
            f"{csv_field} '{UI_rec[csv_field]}' of {UI_rec['memberCode']} does not meet filtering input list."
    elif isinstance(csv_filter[csv_field], (int, float)):
        assert UI_rec[csv_field] >= csv_filter[csv_field], \
            f"{csv_field} '{UI_rec[csv_field]}' of {UI_rec['memberCode']} is less than filtering input value."
    else:
        assert UI_rec[csv_field].upper() == csv_filter[csv_field].upper(), \
            f"{csv_field} '{UI_rec[csv_field]}' of {UI_rec['memberCode']} is different from filtering input value."


    ## filtering of 'dayRange to search'
    ## if all dayRange & (minSocscore = 60 & minbbScore = 60) -> return only if any of the dayRange has combi of (minSocscore>=60 & minBBscore>=60)
    ## if all dayRange & (minSocscore = 60) -> return only if any of the dayRange has minSocscore>=60
    ## if dayRange 1 only & (minSocscore = 60 & minbbScore = 60)  -> return only if dayRange 1 has combi of (minSocscore = 60 & minbbScore = 60)
def verify_with_dayRange(csv_filter,UI_rec,csv_field) -> None:
    """Verify that the records meet the criteria for the specified dayRange."""
    csv_day_range_type_ids = csv_filter['dayRangeTypeID']

    fulfilled = False
    for dayRange in UI_rec['dayRanges']:
        #eg: if rpt rec's 1st_dayRange min_socScore >= 50(filter value) and
        #    (dayRange filter empty  OR  1stDayRange is selected in dayRange filter), then met filtering option
        if (dayRange[csv_field] or 0) >= csv_filter[csv_field] and \
                (not csv_day_range_type_ids or dayRange['dayRangeTypeID'] in csv_day_range_type_ids):
            fulfilled = True
            break

    assert fulfilled, \
        f"{UI_rec['memberCode']}'s {csv_field} in dayRange {dayRange['dayRangeTypeID']} is less than filtering option {csv_filter[csv_field]}."

# Test Function
@pytest.mark.parametrize("csv_filter"
                         ,format_filters(read_csv("C:/Users/lim.miin/OneDrive - Morpheus Consulting Pte Ltd/Desktop/testing/Output check/ArberMemberRpt.csv"))
                         ,ids=lambda csv_filter: f"testcase_{csv_filter['testcase']}"
                         )
#comment:: use this block of code if calling real Object(GetArberMemberSummaryList API)
#===========================[BEGIN of code]==================================
def test_ArberMem_filters(csv_filter):
#===========================[END of code]====================================

#===========================[BEGIN of code]==================================

# @patch('verify_ArbMemrptfilter.get_arber_mem_report')
# def test_arber_mem_filters(MockArberAPI,csv_filter):
#     #i'm patching get_arber_mem_report() function & replace it with a mock object, named 'MockArberAPI'
#     #then i need to assign a returnValue for this mock object. under returnvalue, it consists of many attributes,eg.statuscode,
#     #json value,etc..
#     #eventually, when i call the realObject(get_arber_mem_report()), it will directly refer to mock object 'MockArberAPI' & return to me the
#     #value i requested.
#     MockArberAPI.return_value.status_code = 200
#     MockArberAPI.return_value.json.return_value = {'totalCount': 7, 'pageSize': 10, 'page': 1, 'data': [{'totalCount': 7, \
#     'taggedDate': '2024-12-24T04:00:00Z', 'memberID': 258254, 'memberCode': 'MERVINRMBTEST', 'companyID': 3118,\
#     'companyName': 'MINITRANSFERWALLET2', 'sfMemberCategoryName': 'N.A', 'gbMemberCategoryName': 'Monitoring',\
#     'hitSFMemberCategoryName': 'Monitoring', 'memberActionName': 'ArberMember PG 3118', 'memberActionStatusID': 1,\
#     'memberActionStatusName': 'Action - Success', 'dayRanges': [{'dayRangeTypeID': 1, 'dateFrom': '2024-06-01T04:00:00Z', \
#     'soccerScore': None, 'bbScore': 90, 'totalWagerCount': 92, 'totalExposureAmountBase': 920.0, 'totalWinLoseAmountBase': 0.0, \
#     'avgBetSize': 10.0, 'realSoccerExposurePercent': 0.0, 'realBBExposurePercent': 100.0, 'realSoccerWinloseAmountBase': 0.0, \
#     'realBBWinloseAmountBase': 0.0}], 'soccerPMRejectedBetCount': 10, 'soccerRBRejectedBetCount': 0, 'basketballPMRejectedBetCount': 0,\
#     'basketballRBRejectedBetCount': 0}, {'totalCount': 7, 'taggedDate': '2024-12-23T04:00:00Z', 'memberID': 262925, \
#     'memberCode': 'JHELT00117', 'companyID': 2395, 'companyName': 'SFMINIIGPTW2', 'sfMemberCategoryName': 'N.A', 'gbMemberCategoryName': 'Arber', 'hitSFMemberCategoryName': 'N.A', 'memberActionName': 'ArberMember PG 2395', 'memberActionStatusID': 1, 'memberActionStatusName': 'Action - Success',\
#     'dayRanges': [{'dayRangeTypeID': 1, 'dateFrom': '2024-06-01T04:00:00Z', 'soccerScore': None, 'bbScore': 70, 'totalWagerCount': 25, 'totalExposureAmountBase': 2500.0, 'totalWinLoseAmountBase': 2500.0, 'avgBetSize': 100.0, 'realSoccerExposurePercent': 0.0, \
#                    'realBBExposurePercent': 100.0, 'realSoccerWinloseAmountBase': 0.0, 'realBBWinloseAmountBase': 2500.0}], 'soccerPMRejectedBetCount': 0, 'soccerRBRejectedBetCount': 0, 'basketballPMRejectedBetCount': 0, 'basketballRBRejectedBetCount': 0}, {'totalCount': 7, 'taggedDate': '2024-12-20T04:00:00Z', 'memberID': 262922, 'memberCode': 'JHELT00114', 'companyID': 2395, 'companyName': 'SFMINIIGPTW2', 'sfMemberCategoryName': 'Arber', 'gbMemberCategoryName': None, 'hitSFMemberCategoryName': 'N.A', 'memberActionName': 'ArberMember PG 2395', 'memberActionStatusID': 1, 'memberActionStatusName': 'Action - Success', 'dayRanges': [{'dayRangeTypeID': 1, 'dateFrom': '2024-06-01T04:00:00Z', 'soccerScore': None, 'bbScore': 70, 'totalWagerCount': 25, 'totalExposureAmountBase': 2500.0, 'totalWinLoseAmountBase': 2500.0, 'avgBetSize': 100.0, 'realSoccerExposurePercent': 0.0, 'realBBExposurePercent': 100.0, 'realSoccerWinloseAmountBase': 0.0, 'realBBWinloseAmountBase': 2500.0}], 'soccerPMRejectedBetCount': 0, 'soccerRBRejectedBetCount': 0, 'basketballPMRejectedBetCount': 0, 'basketballRBRejectedBetCount': 0}, {'totalCount': 7, 'taggedDate': '2024-12-19T04:00:00Z', 'memberID': 258197, 'memberCode': 'JHELT00076', 'companyID': 2395, 'companyName': 'SFMINIIGPTW2', 'sfMemberCategoryName': 'Odds Mover', 'gbMemberCategoryName': None, 'hitSFMemberCategoryName': 'Odds Mover', 'memberActionName': 'test 2395 RealBb', 'memberActionStatusID': 1, 'memberActionStatusName': 'Action - Success', 'dayRanges': [{'dayRangeTypeID': 1, 'dateFrom': '2024-06-01T04:00:00Z', 'soccerScore': None, 'bbScore': 80, 'totalWagerCount': 25, 'totalExposureAmountBase': 2500.0, 'totalWinLoseAmountBase': 2500.0, 'avgBetSize': 100.0, 'realSoccerExposurePercent': 0.0, 'realBBExposurePercent': 100.0, 'realSoccerWinloseAmountBase': 0.0, 'realBBWinloseAmountBase': 2500.0}], 'soccerPMRejectedBetCount': 0, 'soccerRBRejectedBetCount': 0, 'basketballPMRejectedBetCount': 0, 'basketballRBRejectedBetCount': 0}, {'totalCount': 7, 'taggedDate': '2024-11-26T04:00:00Z', 'memberID': 285855, 'memberCode': 'ARBER0423', 'companyID': 2395, 'companyName': 'SFMINIIGPTW2', 'sfMemberCategoryName': 'Arber', 'gbMemberCategoryName': 'Arber', 'hitSFMemberCategoryName': 'Regular', 'memberActionName': 'ArberMember PG 2395', 'memberActionStatusID': 1, 'memberActionStatusName': 'Action - Success', 'dayRanges': [{'dayRangeTypeID': 1, 'dateFrom': '2024-05-01T04:00:00Z', 'soccerScore': None, 'bbScore': 70, 'totalWagerCount': 57, 'totalExposureAmountBase': 5700.0, 'totalWinLoseAmountBase': -3000.0, 'avgBetSize': 100.0, 'realSoccerExposurePercent': 0.0, 'realBBExposurePercent': 84.21052631578947, 'realSoccerWinloseAmountBase': 0.0, 'realBBWinloseAmountBase': -4800.0}], 'soccerPMRejectedBetCount': 0, 'soccerRBRejectedBetCount': 0, 'basketballPMRejectedBetCount': 0, 'basketballRBRejectedBetCount': 0}, {'totalCount': 7, 'taggedDate': '2024-11-24T04:00:00Z', 'memberID': 285853, 'memberCode': 'ARBER0421', 'companyID': 2395, 'companyName': 'SFMINIIGPTW2', 'sfMemberCategoryName': 'Arber', 'gbMemberCategoryName': 'Arber', 'hitSFMemberCategoryName': 'Regular', 'memberActionName': 'ArberMember PG 2395', 'memberActionStatusID': 1, 'memberActionStatusName': 'Action - Success', 'dayRanges': [{'dayRangeTypeID': 1, 'dateFrom': '2024-05-01T04:00:00Z', 'soccerScore': None, 'bbScore': 60, 'totalWagerCount': 45, 'totalExposureAmountBase': 4500.0, 'totalWinLoseAmountBase': -1800.0, 'avgBetSize': 100.0, 'realSoccerExposurePercent': 0.0, 'realBBExposurePercent': 80.0, 'realSoccerWinloseAmountBase': 0.0, 'realBBWinloseAmountBase': -3600.0}, {'dayRangeTypeID': 2, 'dateFrom': '2024-11-25T04:00:00Z', 'soccerScore': None, 'bbScore': 80, 'totalWagerCount': 37, 'totalExposureAmountBase': 3700.0, 'totalWinLoseAmountBase': -3700.0, 'avgBetSize': 100.0, 'realSoccerExposurePercent': 0.0, 'realBBExposurePercent': 100.0, 'realSoccerWinloseAmountBase': 0.0, 'realBBWinloseAmountBase': -3700.0}], 'soccerPMRejectedBetCount': 0, 'soccerRBRejectedBetCount': 0, 'basketballPMRejectedBetCount': 0, 'basketballRBRejectedBetCount': 0}, {'totalCount': 7, 'taggedDate': '2024-11-24T04:00:00Z', 'memberID': 293391, 'memberCode': 'LALAMOVE048', 'companyID': 2395, 'companyName': 'SFMINIIGPTW2', 'sfMemberCategoryName': 'Monitoring', 'gbMemberCategoryName': 'Arber', 'hitSFMemberCategoryName': 'Monitoring', 'memberActionName': 'ArberMember PG 2395', 'memberActionStatusID': 1, 'memberActionStatusName': 'Action - Success', \
#     'dayRanges': [{'dayRangeTypeID': 1, 'dateFrom': '2024-05-01T04:00:00Z', 'soccerScore': None, 'bbScore': 70, 'totalWagerCount': 40, 'totalExposureAmountBase': 4000.0, 'totalWinLoseAmountBase': -2200.0, 'avgBetSize': 100.0, 'realSoccerExposurePercent': 0.0, \
#                    'realBBExposurePercent': 85.0, 'realSoccerWinloseAmountBase': 0.0, 'realBBWinloseAmountBase': -3400.0}], 'soccerPMRejectedBetCount': 0, 'soccerRBRejectedBetCount': 0, 'basketballPMRejectedBetCount': 0, 'basketballRBRejectedBetCount': 0}], 'result': True, 'message': None}

#===================================[END of code]==================================
    """key in the filter values(a line in csv_filter), call ArberMem API & verify each rec return on report matches the filters' inputted value"""
    response = get_arber_mem_report(csv_filter)
    assert response.status_code == 200, f"API returned {response.status_code} after calling ArberMemberRpt get list"

    api_resp = response.json()
    UI_recs = api_resp['data']  #contains all recs after entering filter values and click search
    print(f"Total records returned: {api_resp['totalCount']}")

    # scan thru all records return from a click/testcase and verify that data is consistent with the applied filters
    for UI_rec in UI_recs:
        # verify that data consistent with all the applied filters
        for csv_field in csv_filter:
            if not csv_filter[csv_field] and csv_filter[csv_field] !=0 :
                continue   #skip checking if the csv column value or particular filtering field is not applied
            if csv_field in ('testcase','dayRangeTypeID') or csv_field.startswith('API_') :
                continue   #skip checking on this csv columnValue as not involved in comparison
            if csv_field in ('soccerScore','bbScore','totalWagerCount','totalExposureAmountBase','realSoccerExposurePercent','realBBExposurePercent',
                'totalWinLoseAmountBase'):
                verify_with_dayRange(csv_filter,UI_rec,csv_field)
            elif csv_field in ('taggedDate_from','taggedDate_to'):
                validate_date_range(csv_filter,UI_rec)
            else:
                validate_others(csv_filter,UI_rec,csv_field)

# Main Execution
if __name__ == "__main__":
    pytest.main()



