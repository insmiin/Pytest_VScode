#this is to verify that the AGBrpt returns the relevant records according to the selected filters
# to run this, jz execute this command in pycharm terminal:   pytest verify_AGBrptfilter.py -v --tb=short
import csv
import requests
import pytest
import sys
from datetime import datetime

def getMemCatList():

    url = "https://api.qat.fraudsterkill.com/api/common/getMemberCategoryList"

# Send a POST request with data
    response = callAPI('get',url,None)
    if response.status_code != 200:
        print("~~~ERROR~~~ response from function(getMemCatList) is not 200")
        sys.exit()
    return response

def getCompanyList():

    url = "https://api.qat.fraudsterkill.com/api/common/getCompanyList"

# Send a POST request with data
    response = callAPI('get',url,None)
    if response.status_code != 200:
        print("~~~ERROR~~~ response from function(getCompanyList) is not 200")
        sys.exit()
    return response

def getAGBreport(csvFilter):
    url = "https://api.qat.fraudsterkill.com/api/wagerlevelreport/getAGBList"

    data = {"startDate":csvFilter['c_startDate'],"endDate":csvFilter['c_endDate'],"companyIDs":csvFilter['c_intListCoyID'],"memberCode":csvFilter['c_memberCode'] ,"isMemberCodeNull":False,"platformIDs":[],\
            "gbMemberCategoryIDs":csvFilter['c_ListgbMemCatID'],"sfMemberCategoryIDs":csvFilter['c_ListsfMemCatID'],"eventID":-1,"isEventIDNull":False,"betStatusIDs":[],"competitions":[],\
            "minExposureAmount":0,"agbPercentage":-1,"agbInterval":0,"wagerActionReasonIDs":[],"memberActionReasonIDs":[],\
            "ManualCancelReasonTypeIDs":[],"SystemCancelReasonTypeIDs":[],"agbId":-1,"actionReasonId":-1,"sportIDs":[1],"page":1,\
            "pageSize":10,"timezone":-4}
    #print("data:",data)

# Send a POST request with data
    response = callAPI('post',url,data)
    return response

def callAPI(method,url,json):
    headers = {
        "Authorization": "Bearer eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9.eyJ1c2VyIjp7ImlkIjoxLCJuYW1lIjoiYWRtaW4ifSwicGVybWlzc2lvbnMiOlszLDExLDEyLDE1LDE2LDE3LDE5LDIwLDIxLDIyLDIzLDI0LDI1LDI4LDI5LDMwLDMxLDMyLDMzLDM0LDM1LDM2LDM3LDM5LDQwLDQxLDQyLDQzLDQ0LDQ1LDQ2LDQ3LDQ4LDQ5LDUwLDUxLDUyLDUzLDYwLDYxLDYyLDYzLDY0LDY1LDY2LDY3LDY4LDY5LDczLDc0LDc1LDc2LDc3LDc4LDc5LDgwLDgxLDgyLDgzLDg0LDg1LDg2LDg3LDg4LDg5LDkzLDk0LDk1LDk2LDk3LDk4LDk5LDEwMCwxMDEsMTAyLDEwMywxMDQsMTA1LDEwNiwxMDcsMTA4LDEwOSwxMTAsMTExLDExMiwxMTMsMTE0LDExNSwxMTYsMTE3LDExOCwxMjAsMTIxLDEyMiwxMjMsMTI0LDEyNSwxMjYsMTI3LDEyOCwxMjksMTMwLDEzMSwxMzIsMTMzLDEzNCwxMzUsMTM2LDEzNywxMzksMTQwLDE0MSwxNDIsMTQzLDE0NCwxNDUsMTQ2LDE0NywxNDgsMTQ5LDE1MCwxNTEsMTUyLDE1MywxNTQsMTU1LDE1NiwxNTcsMTU4LDE1OSwxNjAsMTY3LDE2OCwxNjksMTcwLDE3MSwxNzIsMTczLDE3NCwxNzUsMTc2LDE3OCwxNzksMTgwLDE4MSwxODIsMTgzLDE4NCwxODUsMTg2LDE4NywxODgsMTg5LDE5MCwxOTEsMTkyLDE5MywxOTQsMTk1LDE5NiwxOTcsMTk4LDE5OSwyMDAsMjAxLDIwMiwyMDMsMjA0LDIwNSwyMDYsMjA3LDIwOCwyMDksMjEwLDIxMSwyMTIsMjEzLDIxNCwyMTUsMjE5LDIyMCwyMjEsMjIyLDIyMywyMjQsMjI1LDIyNiwyMjcsMjI4LDIyOSwyMzAsMjMxLDIzMiwyMzMsMjM0LDIzNSwyMzYsMjM3LDIzOCwyMzksMjQwLDI0MSwyNDIsMjQzLDEsMiw5LDEwLDI2LDI3LDkwLDE3N10sImlhdCI6MTc0MzA0NDUyNiwiZXhwIjoxNzQzNjQ5MzI2fQ.klfh9mVxIl0KQHpt5rmItRLGmxL23HXaNtw8UQTcWcc",  # Example: Authorization token
        "Content-Type": "application/json",  # Specify that the body is in JSON format
        "Connection": "keep-alive"  # Example of a custom header
    }
    proxies = {
        'http': 'http://127.0.0.1:8888',  # Fiddler's default HTTP proxy
        'https': 'http://127.0.0.1:8888'  # Fiddler's default HTTPS proxy
    }
    if method == 'get':
        response = requests.get(url, headers=headers,json=json) #,proxies=proxies, verify=False) #if fiddler is open, include these 2 parameters too
    elif method == 'post':
        response = requests.post(url, headers=headers,json=json)  #,proxies=proxies, verify=False) #if fiddler is open, include these 2 parameters too
    return response

def memCat_NametoID(MemCatName):
    matching_memCat_int = next((dictElement['value'] for dictElement in memCatMapList if dictElement['label'] == MemCatName), None)
    return matching_memCat_int

def Coy_NametoID(CoyName):
    matching_Coy_int = next((dictElement['companyID'] for dictElement in coyMapList if dictElement['companyName'] == CoyName), None)
    return matching_Coy_int

def read_csv():
    """Read data from CSV and return a list of dictionaries."""
    with open('C:/Users/lim.miin/OneDrive - Morpheus Consulting Pte Ltd/Desktop/testing/Output check/AGBreport.csv', mode='r',newline='') as csvfile:
        reader = csv.DictReader(csvfile)
        tempAllCSVrows  = [row for row in reader]
    #print('tempAllCSVrows',tempAllCSVrows)
    csvFilters = format_Filters(tempAllCSVrows)

    return csvFilters

def format_Filters(tempAllCSVrows):
    global memCatMapList
    global coyMapList
    memCatMapListsResp = getMemCatList()
    memCatMapList = memCatMapListsResp.json()['data']
    coyMapListsResp = getCompanyList()
    coyMapList = coyMapListsResp.json()['data']
    csvFilter = []
    for eachCSVrowDict in tempAllCSVrows:  #tempAllCSVrows is a list , eachCSVrow is a dictionary with columns&value
        if eachCSVrowDict['c_startDate'] == '':  #process each key&value (CSVcolumn&value)
           print("Error! startDate in csv file cannot be empty!")
           sys.exit()
        else:
            strDate = eachCSVrowDict['c_startDate']

        if eachCSVrowDict['c_endDate'] == '':
           print("Error! endDate in csv file cannot be empty!")
           sys.exit()
        else:
            endDate = eachCSVrowDict['c_endDate']



        strMemCode = eachCSVrowDict['c_memberCode']  #already string and single value only

        if eachCSVrowDict['c_companyNames'] == '':
           ListCoyID = list()
           ListCoy= eachCSVrowDict['c_companyNames']
        else:
            ListCoy = eachCSVrowDict['c_companyNames'].split(';')  # convert string into list
            ListCoyID = list(map(Coy_NametoID, ListCoy))  # convert each element in string using int function

        if eachCSVrowDict['c_gbMemberCategoryNames'] == '':
           ListgbMemCatID = list()
           ListgbMemCat = eachCSVrowDict['c_gbMemberCategoryNames']
        else:
            ListgbMemCat = eachCSVrowDict['c_gbMemberCategoryNames'].split(';')  # convert string into list
            ListgbMemCatID = list(map(memCat_NametoID, ListgbMemCat))  # convert each element in string using int function

        if eachCSVrowDict['c_sfMemberCategoryNames'] == '':
           ListsfMemCatID = list()
           ListsfMemCat = eachCSVrowDict['c_sfMemberCategoryNames']
        else:
            ListsfMemCat = eachCSVrowDict['c_sfMemberCategoryNames'].split(';')  # convert string into list
            ListsfMemCatID = list(map(memCat_NametoID, ListsfMemCat))  # convert each element in string using int function
        csvFilterdic = {
            "c_startDate": strDate,
            "c_endDate": endDate,
            "c_intListCoyID" : ListCoyID,
            "c_companyNames" : ListCoy,
            "c_memberCode" : strMemCode,
            "c_ListgbMemCatID": ListgbMemCatID,
            "c_gbMemberCategoryNames": ListgbMemCat,
            "c_ListsfMemCatID": ListsfMemCatID,
            "c_sfMemberCategoryNames":ListsfMemCat
        }
        csvFilter.append(csvFilterdic)
        print('csvFilter:',csvFilter)
    return csvFilter


@pytest.mark.parametrize("csvFilters", read_csv())
def test_api_response(csvFilters):
    # for each set of csvFilters (from each csv row /dictionary), do below

    # Call the API for AGB report y providing the selected filter options
    APIresponse = getAGBreport(csvFilters)

    # Check if the response is valid (status code 200)
    assert APIresponse.status_code == 200, f"API returned {APIresponse.status_code} after calling AGBapi get list"

    # Get the JSON data(playload) from the API response to display on report UI
    apiResp = APIresponse.json()
    rptRec = apiResp['data']

    print('  total agb rec return is :', apiResp['totalCount'])
    #assert apiResp['totalCount'] > 0  ,f"no matching record found" can happen if no recs fullfilled the filters


    if csvFilters['c_startDate'] != '' and csvFilters['c_endDate'] != '':
        csvStrDate = datetime.strptime(csvFilters['c_startDate'], "%Y-%m-%d")
        csvStrDateUTC = csvStrDate.replace(hour=4, minute=0, second=0)   #convert to UTC as record  return are all in UTC timezone
        csvEndDate = datetime.strptime(csvFilters['c_endDate'], "%Y-%m-%d")
        csvEndDateUTC = csvEndDate.replace(hour=4, minute=0, second=0)   #convert to UTC as record  return are all in UTC timezone
        for UIrec in rptRec:
            AGBcreatedAtUTC = datetime.strptime(UIrec['createdAt'], "%Y-%m-%dT%H:%M:%S")
            assert AGBcreatedAtUTC >= csvStrDateUTC and AGBcreatedAtUTC <= csvEndDateUTC,f"record has createdDate thats is not within filter date"

    if csvFilters['c_companyNames'] != '':
        for UIrec in rptRec:
            assert UIrec['companyName'] in csvFilters['c_companyNames'], f" companyName '{UIrec['companyName']}' is not in filter selections"

    if csvFilters['c_memberCode'] != '':
        for UIrec in rptRec:
            assert UIrec['memberCode'] == csvFilters['c_memberCode'], f" memberCode '{UIrec['memberCode']}' is not in filter selections"

    if csvFilters['c_sfMemberCategoryNames'] != '':
        for UIrec in rptRec:
            assert UIrec['sfMemberCategoryName'] in csvFilters[
                'c_sfMemberCategoryNames'], f"sfMemberCategory '{UIrec['sfMemberCategoryName']}' is not in filter selections"

    if csvFilters['c_gbMemberCategoryNames'] != '':
        for UIrec in rptRec:
            assert UIrec['gbMemberCategoryName'] in csvFilters[
                'c_gbMemberCategoryNames'], f"sfMemberCategory '{UIrec['gbMemberCategoryName']}' is not in filter selections"





