# Purpose: auto update & assert update for member setting of all members in 'update_cases'
# to run this test, 
# #1)make sure to first run the command 'python -m utils.save-gbqat-login' to run the script to save the login state.
# #2)then run command, pytest tests\ui_tests\test_memberlisting_update.py -v --log-file=memberAction_test.log --log-file-level=INFO
import pytest
from playwright.sync_api import Page, expect, sync_playwright


# ============================================================
# Test Data
# ============================================================

update_cases = [
    {
        "memberCode": "gbmock_t3442n040",
        "memberProfile": "800% Group",
        "spread": "A",
        "memberCategory": "Regular",
        "realsoc_bd": "0",
        "realbb_bd": "0",
        "cyber_bd": "0",
        "others_bd": "0",
        "isAdvised": "No",
        "applied_cs": "0.50",
        "isManualRevisedList": "No",
    }

    # Add nine more test cases here.
]


# ============================================================
# Helper Functions
# ============================================================

def select_dropdown(page: Page, selector: str, value: str,
                    arrow_down: bool = True):
    """
    Fill and select a dropdown option.
    """
    dropdown = page.locator(selector)
    dropdown.fill(value)

    if arrow_down:
        dropdown.press("ArrowDown")

    dropdown.press("Enter")


def update_form_field(page: Page, label: str, value: str):
    """
    Find a form-group by label and update its input.
    """
    form_group = page.locator("div.form-group").filter(
        has=page.locator("label", has_text=label)
    )

    form_group.locator("input").fill(value)


# ============================================================
# Test Cases
# ============================================================
@pytest.fixture(scope="session")
def page():
    with sync_playwright() as p:
        browser = p.chromium.launch(headless=False)
        context = browser.new_context(
            storage_state='playwright/.auth/gbqat_login_state.json',
            permissions=['clipboard-read', 'clipboard-write']
        )
        page = context.new_page()
        yield page

        context.close()
        browser.close()

@pytest.mark.parametrize("update_case", update_cases)
def test_manual_update(page: Page, update_case):

    member_code = update_case["memberCode"]

    # --------------------------------------------------------
    # Step 1: Navigate to Member Listing
    # --------------------------------------------------------

    page.goto(
        "https://qat.fraudsterkill.com/membersetting/memberlisting"
    )

    expect(
        page.get_by_text("Last EGON Score Updated At")
    ).to_be_visible()

    expect(
        page.get_by_role("heading", name="Member Listing")
    ).to_be_visible()

    page.get_by_role(
        "textbox", name="Member Code"
    ).fill(member_code)

    page.get_by_role(
        "button", name="Search", exact=True
    ).click()

    expect(
        page.get_by_role("button", name=member_code)
    ).to_be_visible()

    # --------------------------------------------------------
    # Step 2: Get current GB Member Setting
    # --------------------------------------------------------

    row = page.locator("#row-0")

    element_msp_gb = (
        row.locator('[role="gridcell"]')
        .nth(7)
        .locator(".table_row")
        .first
        .locator(".table_col")
        .nth(2)
    )

    element_spread_gb = (
        row.locator('[role="gridcell"]')
        .nth(7)
        .locator(".table_row")
        .first
        .locator(".table_col")
        .nth(3)
    )

    element_bd_gb = (
        row.locator('[role="gridcell"]')
        .nth(7)
        .locator(".table_row")
        .first
        .locator(".table_col")
        .nth(4)
    )

    expected_membersetting = {
        "mspText": (
            update_case["memberProfile"]
            if update_case["memberProfile"] is not None
            else element_msp_gb.inner_text().strip()
        ),
        "spreadText": (
            update_case["spread"]
            if update_case["spread"] is not None
            else element_spread_gb.inner_text().strip()
        ),
    }

    print("Current GB BD:", element_bd_gb.inner_text())

    # --------------------------------------------------------
    # Step 3: Open Member Setting
    # --------------------------------------------------------

    page.locator('i[title="Member Settings"]').click()

    expect(
        page.get_by_role("heading", name="Member Setting")
    ).to_be_visible()

    expect(
        page.get_by_text("Real Soccer", exact=True)
    ).to_be_visible()

    # --------------------------------------------------------
    # Step 4: Update BD values
    # --------------------------------------------------------

    bd_fields = [
        ("realsoc_bd", "Real Soccer"),
        ("realbb_bd", "Real Basketball"),
        ("cyber_bd", "Cyber Soccer and Cyber Basketball"),
        ("others_bd", "All Other Sports"),
    ]

    for field, label in bd_fields:
        value = update_case[field]

        if value is not None:
            update_form_field(page, label, value)

    # --------------------------------------------------------
    # Step 5: Update Member Setting dropdowns
    # --------------------------------------------------------

    if update_case["memberProfile"] is not None:
        select_dropdown(
            page,
            "#memberSettingProfileList input[role='combobox']",
            update_case["memberProfile"],
            arrow_down=False
        )

    if update_case["spread"] is not None:
        select_dropdown(
            page,
            "#memberSpreadGroupList input[role='combobox']",
            update_case["spread"]
        )

    if update_case["memberCategory"] is not None:
        select_dropdown(
            page,
            "#memberCategoryList input[role='combobox']",
            update_case["memberCategory"]
        )

    if update_case["isAdvised"] is not None:
        select_dropdown(
            page,
            "#IsAdvisedList input[role='combobox']",
            update_case["isAdvised"]
        )

    if update_case["applied_cs"] is not None:
        select_dropdown(
            page,
            "#appliedCreditScore input[role='combobox']",
            update_case["applied_cs"]
        )

    if update_case["isManualRevisedList"] is not None:
        select_dropdown(
            page,
            "#isManualRevisedList input[role='combobox']",
            update_case["isManualRevisedList"]
        )

    # --------------------------------------------------------
    # Step 6: Save Member Setting
    # --------------------------------------------------------

    page.get_by_role(
        "button", name="Save", exact=True
    ).click()

    expect(
        page.get_by_text(
            "Updates has triggerred to SF. Please refer to Member Action Status for more details"
        )
    ).to_be_visible()

    page.get_by_role(
        "button", name="OK", exact=True
    ).click()

    # --------------------------------------------------------
    # Step 7: Verify GB row data
    # --------------------------------------------------------

    expect(element_msp_gb).to_contain_text(
        expected_membersetting["mspText"]
    )

    expect(element_spread_gb).to_contain_text(
        expected_membersetting["spreadText"]
    )

    # --------------------------------------------------------
    # Step 8: Get SF row locators
    # --------------------------------------------------------

    element_msp_sf = (
        row.locator('[role="gridcell"]')
        .nth(7)
        .locator(".table_row")
        .nth(1)
        .locator(".table_col")
        .nth(2)
    )

    element_spread_sf = (
        row.locator('[role="gridcell"]')
        .nth(7)
        .locator(".table_row")
        .nth(1)
        .locator(".table_col")
        .nth(3)
    )

    # --------------------------------------------------------
    # Step 9: Wait for SF synchronization
    # --------------------------------------------------------

    page.wait_for_timeout(45_000)

    page.get_by_role(
        "button", name="Search", exact=True
    ).click()

    expect(
        page.get_by_role("button", name=member_code)
    ).to_be_visible()

    # --------------------------------------------------------
    # Step 10: Verify SF row data
    # --------------------------------------------------------

    expect(element_msp_sf).to_contain_text(
        expected_membersetting["mspText"],
        timeout=120_000
    )

    expect(element_spread_sf).to_contain_text(
        expected_membersetting["spreadText"],
        timeout=120_000
    )
