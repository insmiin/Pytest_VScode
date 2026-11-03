#update your testing filters csv file
#go terminal and enter this command "pytest (old 7july)verify_ArbMemrptfilter.py -v --tb=short"
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
    return response.json()['data']

def get_company_list() -> List[Dict]:
    """Call member category API and returns a list of dict,each dict contains diff company details."""
    url = f"{API_BASE_URL}/common/getCompanyList"
    response = call_api('get', url)
    return response.json()['data']

def latest_job_schedule(job_type_id: Dict) -> Dict:
    """Get the latest job schedule from API."""
    url = f"{API_BASE_URL}/common/getLatestSuccessJobScheduleByJobType"
    response = call_api('post', url, job_type_id)
    return response.json()['data']['jobInfo']

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
    mem_cat_map = get_mem_cat_list() #list of dict with memCat details
    coy_map = get_company_list()
    job_date = latest_job_schedule({"jobTypeID": 91})
    date_object = datetime.strptime(job_date, '%Y%m%d')
    fmt_job_date = date_object.strftime('%Y-%m-%dT04:00:00')

    formatted_filters = []
    for row in csv_rows:
        formatted_filter = {
            "c_startDate": f"{row['c_startDate']}T04:00:00" if row['c_startDate'] else None,
            "c_endDate": f"{row['c_endDate']}T04:00:00" if row['c_endDate'] else None,
            "fmt_job_date": fmt_job_date,
            "c_companyNames_API": [coy['companyID'] for coy in coy_map if coy['companyName'] in row['c_companyNames'].split(';')],
            "c_companyNames": row['c_companyNames'].split(';') if row['c_companyNames'] else row['c_companyNames'],
            "c_memberCode": row['c_memberCode'],
            "c_gbMemberCategoryNames_API": [mem_cat['value'] for mem_cat in mem_cat_map if mem_cat['label'] in row['c_gbMemberCategoryNames'].split(';')],
            "c_gbMemberCategoryNames": row['c_gbMemberCategoryNames'].split(';') if row['c_gbMemberCategoryNames'] else row['c_gbMemberCategoryNames'],
            "c_sfMemberCategoryNames_API": [mem_cat['value'] for mem_cat in mem_cat_map if mem_cat['label'] in row['c_sfMemberCategoryNames'].split(';')],
            "c_sfMemberCategoryNames": row['c_sfMemberCategoryNames'].split(';') if row['c_sfMemberCategoryNames'] else row['c_sfMemberCategoryNames'],
            "c_hitSFMemberCategoryNames_API": [mem_cat['value'] for mem_cat in mem_cat_map if mem_cat['label'] in row['c_hitSFMemberCategoryNames'].split(';')],
            "c_hitSFMemberCategoryNames": row['c_hitSFMemberCategoryNames'].split(';') if row['c_hitSFMemberCategoryNames'] else row['c_hitSFMemberCategoryNames'],
            "c_soccerPMRejectedBetCount_API": int(row['c_soccerPMRejectedBetCount']) if row['c_soccerPMRejectedBetCount'] else None,
            "c_soccerRBRejectedBetCount_API": int(row['c_soccerRBRejectedBetCount']) if row['c_soccerRBRejectedBetCount'] else None,
            "c_basketballPMRejectedBetCount_API": int(row['c_basketballPMRejectedBetCount']) if row['c_basketballPMRejectedBetCount'] else None,
            "c_basketballRBRejectedBetCount_API": int(row['c_basketballRBRejectedBetCount']) if row['c_basketballRBRejectedBetCount'] else None,
            "c_dayRangeTypeIDs": [int(id) for id in row['c_dayRangeTypeIDs'].split(';')] if row['c_dayRangeTypeIDs'] else [],
            "c_minSoccerScore": int(row['c_minSoccerScore']) if row['c_minSoccerScore'] else None,
            "c_minBasketballScore": int(row['c_minBasketballScore']) if row['c_minBasketballScore'] else None,
            "c_minWagerCount": int(row['c_minWagerCount']) if row['c_minWagerCount'] else None,
            "c_minExposureAmount": float(row['c_minExposureAmount']) if row['c_minExposureAmount'] else None,
            "c_minSoccerExposurePCT": float(row['c_minSoccerExposurePCT']) if row['c_minSoccerExposurePCT'] else None,
            "c_minBasketballExposurePCT": float(row['c_minBasketballExposurePCT']) if row['c_minBasketballExposurePCT'] else None,
            "c_minWinLoseAmount": float(row['c_minWinLoseAmount']) if row['c_minWinLoseAmount'] else None
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
        "startDate": csv_filter['c_startDate'],
        "endDate": csv_filter['c_endDate'],
        "lastUpdatedDate": csv_filter['fmt_job_date'],
        "companyIDs": csv_filter['c_companyNames_API'],
        "SFMemberCategoryIDs": csv_filter['c_sfMemberCategoryNames_API'],
        "GBMemberCategoryIDs": csv_filter['c_gbMemberCategoryNames_API'],
        "HitRuleMemberCategoryIDs": csv_filter['c_hitSFMemberCategoryNames_API'],
        "memberCode": csv_filter['c_memberCode'],
        "minArberSoccerPMRejectedBetCount": csv_filter['c_soccerPMRejectedBetCount_API'],
        "minArberSoccerRBRejectedBetCount": csv_filter['c_soccerRBRejectedBetCount_API'],
        "minArberBasketballPMRejectedBetCount": csv_filter['c_basketballPMRejectedBetCount_API'],
        "minArberBasketballRBRejectedBetCount": csv_filter['c_basketballRBRejectedBetCount_API'],
        "dayRangeTypeIDs": csv_filter['c_dayRangeTypeIDs'],
        "minSoccerScore": csv_filter['c_minSoccerScore'],
        "minBasketballScore": csv_filter['c_minBasketballScore'],
        "minWagerCount": csv_filter['c_minWagerCount'],
        "minExposureAmount": csv_filter['c_minExposureAmount'],
        "minSoccerExposurePCT": csv_filter['c_minSoccerExposurePCT'],
        "minBasketballExposurePCT": csv_filter['c_minBasketballExposurePCT'],
        "minWinLoseAmount": csv_filter['c_minWinLoseAmount'],
        "page": 1,
        "pageSize": 10
    }
    print("Request body:", data)
    response = call_api('post', url, data)
    return response



def validate_date_range(csv_filter: Dict, rpt_recs: List[Dict]) -> None:
    """Validate that the TaggedDate of all d records on report, fall within the inputted date range."""
    if csv_filter['c_startDate'] and csv_filter['c_endDate']:
        csv_start_date = datetime.strptime(csv_filter['c_startDate'], "%Y-%m-%dT%H:%M:%S") #convert str to datetime
        csv_end_date = datetime.strptime(csv_filter['c_endDate'], "%Y-%m-%dT%H:%M:%S")

        for record in rpt_recs:
            tagged_date = datetime.strptime(record['taggedDate'], "%Y-%m-%dT%H:%M:%SZ")
            assert csv_start_date <= tagged_date <= csv_end_date, \
                f"TaggedDate {tagged_date} of {record['memberCode']} doesn't meet filtering dateRange."


def validate_company_names(csv_filter: Dict, rpt_recs: List[Dict]) -> None:
    """Validate that the company names in the records match the filter."""
    print('companiesss:', csv_filter['c_companyNames_API'] )
    if csv_filter['c_companyNames']:
        expected_companies = set(map(str.upper, csv_filter['c_companyNames']))

        for record in rpt_recs:
            assert record['companyName'].upper() in expected_companies, \
                f"CompanyName '{record['companyName']}' of {record['memberCode']} doesn't meet filtering companies."


def validate_member_code(csv_filter: Dict, rpt_recs: List[Dict]) -> None:
    """Validate that the member codes in the records match the filter."""
    if csv_filter['c_memberCode']:
        for record in rpt_recs:
            assert record['memberCode'] == csv_filter['c_memberCode'], \
                f"MemberCode '{record['memberCode']}' of {record['memberCode']} is not in filter selections."


def validate_member_categories(csv_filter: Dict, rpt_recs: List[Dict], category_type: str) -> None:
    """Validate that the member categories in the records match the filter."""
    filter_key = f'c_{category_type}MemberCategoryNames'
    record_key = f'{category_type}MemberCategoryName'

    if csv_filter[filter_key]:
        expected_categories = set(csv_filter[filter_key])

        for record in rpt_recs:
            assert record[record_key] in expected_categories, \
                f"{category_type}MemberCategory '{record[record_key]}' of {record['memberCode']} is not in filter selections."


def validate_rejected_bet_counts(csv_filter: Dict, rpt_recs: List[Dict], bet_type: str) -> None:
    """Validate that the rejected bet counts in the records meet the filter criteria."""
    filter_key = f'c_{bet_type}RejectedBetCount_API'
    record_key = f'{bet_type}RejectedBetCount'

    #csv_filter[filter_key] is int datatype,where number 0 is valid and required assertion
    #using 'if csv_filter[filter_key]' will return false which will skip the assertion
    if csv_filter[filter_key] or csv_filter[filter_key] == 0:
        min_count = csv_filter[filter_key]

        for record in rpt_recs:
            assert record[record_key] >= min_count, \
                f"{bet_type}RejectedBetCount '{record[record_key]}' of {record['memberCode']} is less than filtering betcount."

    ## filtering of 'dayRange to search'
    ## if all dayRange & (minSocscore = 60 & minbbScore = 60) -> return only if any of the dayRange has combi of (minSocscore>=60 & minBBscore>=60)
    ## if all dayRange & (minSocscore = 60) -> return only if any of the dayRange has minSocscore>=60
    ## if dayRange 1 only & (minSocscore = 60 & minbbScore = 60)  -> return only if dayRange 1 has combi of (minSocscore = 60 & minbbScore = 60)
def verify_with_dayRange(rpt_recs: List[Dict], csv_filter: Dict,csv_min_value:str,API_return_value: str) -> None:
    """Verify that the records meet the criteria for the specified dayRange."""
    csv_day_range_type_ids = csv_filter['c_dayRangeTypeIDs']
    #csv_fmt_day_range_type_ids = csv_filter['c_fmtdayRangeTypeIDs']
    #csv_min_value_type = csv_filter[f'c_min{API_verify_field}']

    for record in rpt_recs:
        fulfilled = False
        for dayRange in record['dayRanges']:
            #eg: if rpt rec's 1st_dayRange min_socScore >= 50(filter value) and
            #    (dayRange filter empty  OR  1stDayRange is selected in dayRange filter), then met filtering option
            if (dayRange[API_return_value] or 0) >= csv_min_value and \
                    (not csv_day_range_type_ids or dayRange['dayRangeTypeID'] in csv_day_range_type_ids):
                fulfilled = True
                break

        assert fulfilled, \
            f"{record['memberCode']}'s {API_return_value} in dayRange {dayRange['dayRangeTypeID']} is less than filtering option {csv_min_value}."

# Test Function
@pytest.mark.parametrize(
    "csv_filter",
    format_filters(read_csv("C:/Users/lim.miin/OneDrive - Morpheus Consulting Pte Ltd/Desktop/testing/Output check/ArberMemberRpt - Copy.csv")),
    ids=lambda csv_filter: f"testcase_{csv_filter['testcase']}"
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
    rpt_recs = api_resp['data']  #contains all recs after entering filter values and click search
    print(f"Total records returned: {api_resp['totalCount']}")

    print('csv_filter yoyo:', csv_filter)
    # Validate date range
    validate_date_range(csv_filter, rpt_recs)

    # Validate company names
    validate_company_names(csv_filter, rpt_recs)

    # Validate member code
    validate_member_code(csv_filter, rpt_recs)

    # Validate member categories
    validate_member_categories(csv_filter, rpt_recs, 'sf')
    validate_member_categories(csv_filter, rpt_recs, 'gb')
    validate_member_categories(csv_filter, rpt_recs, 'hitSF')

    # Validate rejected bet counts
    validate_rejected_bet_counts(csv_filter, rpt_recs, 'soccerPM')
    validate_rejected_bet_counts(csv_filter, rpt_recs, 'soccerRB')
    validate_rejected_bet_counts(csv_filter, rpt_recs, 'basketballPM')
    validate_rejected_bet_counts(csv_filter, rpt_recs, 'basketballRB')

    # Verify dayRange-based criteria
    if csv_filter['c_minSoccerScore']:
        verify_with_dayRange(rpt_recs, csv_filter, csv_filter['c_minSoccerScore'],'soccerScore')
    if csv_filter['c_minBasketballScore']:
        verify_with_dayRange(rpt_recs, csv_filter, csv_filter['c_minBasketballScore'],'bbScore')
    if csv_filter['c_minWagerCount']:
        verify_with_dayRange(rpt_recs, csv_filter, csv_filter['c_minWagerCount'],'totalWagerCount')
    if csv_filter['c_minExposureAmount']:
        verify_with_dayRange(rpt_recs, csv_filter, csv_filter['c_minExposureAmount'],'totalExposureAmountBase')
    if csv_filter['c_minSoccerExposurePCT']:
        verify_with_dayRange(rpt_recs, csv_filter, csv_filter['c_minSoccerExposurePCT'],'realSoccerExposurePercent')
    if csv_filter['c_minBasketballExposurePCT']:
        verify_with_dayRange(rpt_recs, csv_filter, csv_filter['c_minBasketballExposurePCT'],'realBBExposurePercent')
    if csv_filter['c_minWinLoseAmount']:
        verify_with_dayRange(rpt_recs, csv_filter, csv_filter['c_minWinLoseAmount'],'totalWinLoseAmountBase')


# Main Execution
if __name__ == "__main__":
    pytest.main()

