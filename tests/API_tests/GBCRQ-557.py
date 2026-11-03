import pytest
from tests.utils.api_utils import call_api
import tests.myConstants as const
import logging
import json
from pathlib import Path

logger = logging.getLogger(__name__)
def load_json_data(filename: str):
    file_path = const.TEST_DATA_FILE_PATH / "json" / "API_TESTS" / filename
    with open(file_path, "r", encoding="utf-8") as file:
        return json.load(file)

def build_payload(test_data):
    return [
        {
            "MemberID": item["MemberID"],
            "CompanyID": item["CompanyID"]
        }
        for item in test_data
    ]
@pytest.mark.parametrize("member_score_data",load_json_data("member_score_data.json"),ids=lambda test_case: test_case["testcase"])
def test_get_memberscore_by_member(provider_api_session, member_score_data):
    url = f"{const.GB_PROVIDER_API_BASE_URL}/member/getmemberscorebymember"
    json_input_data = build_payload(member_score_data['test_data']) if member_score_data['test_data'] is not None else member_score_data['test_data']
    response = call_api(provider_api_session, who='test_get_memberscore_by_member', method='post', url=url, json_data=json_input_data)

    response_json = response.json()
    expected = member_score_data["expected"]
    assert response.status_code == expected['status_code'], f"calling to memberScoreAPI return {response.status_code}: {response.text}"

    assert "responseCode" in response_json, "API response is missing 'responseCode'"
    assert response_json['responseCode'] == expected['response_code'] , (
    f"Expected responseCode={expected['response_code']}, "
    f"got {response_json['responseCode']}"
)
    assert "responseCode" in response_json, "API response is missing 'responseMessage'"
    assert response_json['responseMessage']== expected['response_message'],(
    f"Expected responseCode={expected['response_message']}, "
    f"got {response_json['responseMessage']}"
)
    if 'data' in response_json:
        response_data_json = json.loads(response_json['data'])
        response_data_str = response_json['data']
        logger.debug(f'response_data_json====>{response_data_json}')
        logger.debug(f'response_data_str====>{response_data_str}')
        # Verify that all expected members are returned
        assert len(response_data_json) == len(member_score_data['test_data'])

        # Index response records by MemberID
        response_by_member = {
            item["MemberID"]: item for item in response_data_json
        }
        # Verify each expected member
        for expected in member_score_data['test_data']:
            member_id = expected["MemberID"]

            assert member_id in response_by_member, (
                f"MemberID {member_id} not found in response"
            )

            memberid_details = response_by_member[member_id]

            assert memberid_details["CompanyID"] == expected["CompanyID"], (
                f"CompanyID mismatch for MemberID {member_id}"
            )
            assert memberid_details["GBRiskScore"] == expected["expected_GBRiskScore"], (
                f"expected_GBRiskScore mismatch for MemberID {member_id}"
            )
