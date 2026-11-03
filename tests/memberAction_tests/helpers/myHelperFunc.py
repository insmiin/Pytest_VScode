from typing import List, Dict, Any, Optional
import requests
import sys
import os
#to add root directory into the sys.path, so that the script able to import module in root directory
root_dir = os.path.abspath(os.path.join(os.path.dirname(__file__), '..'))
sys.path.insert(0, root_dir)
from tests.utils.comparison_utils import is_match,is_match,is_GT,is_LT,is_LTE,is_GTE
from datetime import datetime, timezone, timedelta
from dateutil.relativedelta import relativedelta
import logging

logger = logging.getLogger(__name__)

# def call_api(api_session, who: str,method: str, url: str, json_data: Optional[Dict] = None) -> requests.Response:
#     """Make an API request."""
#     response = api_session.request(
#             method=method,
#             url=url,
#             json=json_data)
#         # proxies=PROXIES)
#         # verify=not bool(PROXIES))  # Disable verify if using proxy
#     #assert response.status_code == 200,f"calling to {who} return {response.status_code} "
#     return response


def get_past_date_UTC(value,unit):
    # get current_datetime in GMT-4 ,then compute old date using parameter.lastly, return the olddate in UTC to b saved in mysql
    now = datetime.now()  # SGT/UTC+8
    now_GMTminus4 = now - timedelta(hours=12) #GMT-4

    if unit == 'months':
        # get First day of the x months ago(excluding current month)
        months_ago_GMTminus4 = (now_GMTminus4.replace(day=1, hour=0, minute=0, second=0, microsecond=0) - relativedelta(months=3))
        # return 1st day of x months ago in UTC format  (type:datetime.datetime. value sample:2026-04-01 04:00:00)
        new_date_UTC = months_ago_GMTminus4 + timedelta(hours=4)
    elif unit == 'hours':
        # get hours ago
        hours_ago_GMTminus4 = (now_GMTminus4 - timedelta(hours=value)).replace(microsecond=0) #remove millisecs
        # return x hours ago,in UTC format  (type:datetime.datetime. value sample:2026-04-01 04:00:00)
        new_date_UTC = hours_ago_GMTminus4 + timedelta(hours=4)
    elif unit == 'days':
        pass
    return new_date_UTC



def parse_updatedby(updatedby):
    '''
    if lastUpdatedby is system,
       *GBfeature (since noscoreType,so lastupdatedBy=lastupdatedBy and LastScoreType is defaulted to Bad)
       *GBrule will split it into 2 parts( lastupdatedBy part and LastScoreType part)
    # GB_EGON_1 -> GB_EGON & goodScore
    # GB_TWM_SC_1 -> GB_TWM_SC & goodScore
    # GB_MemberListing-admin_1 -> GB_MemberListing-admin_1  & None
    # soc_user -> soc_user & None
    # GB_LateBet -> GB_LateBet & None
    '''
    lastUpdatedBy = updatedby

    # if last update is by non-system(user/null)
    lastScoreType = None

    # if last update is by system(GBrule/GBfeature)
    if updatedby and updatedby.startswith('GB_') and not updatedby.startswith('GB_MemberList'):
        lastScoreType = 'Bad' #default to Bad 1st to cater for GBfeature(no scoreType).  scoreType of GBrule will be further determined below
        # Split from the right only once , delimited by _
        # if there is a numeric suffix(1=goodScore,2=BadScore),this is GBrule, replace both parts
        sys_lastUpd_list = updatedby.rsplit("_", 1)
        if len(sys_lastUpd_list) == 2 and sys_lastUpd_list[1] in ('1', '2'):
            lastUpdatedBy = sys_lastUpd_list[0]
            if is_match(sys_lastUpd_list[1], 1):
                lastScoreType = 'Good'
            else:
                lastScoreType = 'Bad'

    return lastUpdatedBy, lastScoreType