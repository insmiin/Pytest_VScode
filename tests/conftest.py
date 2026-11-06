import pytest
import requests
import tests.myConstants as const
from dotenv import load_dotenv
from playwright.sync_api import sync_playwright
import os
# suppress this particular warning for google cloud sdk auth (asking for quota project to charge API etc..) 
import warnings
warnings.filterwarnings(
    "ignore",
    message="Your application has authenticated using end user credentials from Google Cloud SDK without a quota project.*",
    category=UserWarning
)

from google.cloud import bigquery

PROJECT_ID = "carbon-sensor-259109"


@pytest.fixture(scope="session")
def bq_client():
    client = bigquery.Client(project=PROJECT_ID)
    yield client
    client.close()  # cleanup after all tests finish


@pytest.fixture(scope="session")
def api_session():
    print('api_session GB fixtureeeeee')
    session = requests.Session()
    session.headers.update(
        {"Authorization": const.AUTH_TOKEN, "Content-Type": "application/json", "Connection": "keep-alive"})
    yield session
    session.close()

@pytest.fixture(scope="session")
def api_session_SF():
    print('api_session SF fixtureeeeee')
    session = requests.Session()
    session.headers.update(
        {"Authorization": const.AUTH_TOKEN, "Content-Type": "application/json", "Connection": "keep-alive"})
    yield session
    session.close()


@pytest.fixture(scope="session")
def provider_api_session():
    print('api_session GB fixtureeeeee')
    session = requests.Session()
    session.headers.update(
        {"x-api-key": const.X_API_KEY, "Content-Type": "application/json", "Connection": "keep-alive"})
    yield session
    session.close()


# login to cloudsql UI once using playwright, and return the page object for repeated use in tests. (so that we dont have to login for every test)
load_dotenv()
@pytest.fixture(scope="session")
def cloudmysql_page():
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
        except Exception as err:
            page.screenshot(path='cloudsql-login-error.png', full_page=True)
            context.close()
            browser.close()
            pytest.exit(f"Cloud SQL login failed: {err}")

        yield page

        context.close()
        browser.close()