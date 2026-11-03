import pytest
from mysql.connector import Error
import mysql.connector
import requests
import tests.myConstants as const

@pytest.fixture(scope="session")
def mysql_connection():
    print('mysql_connection fixtureee')
    conn = None
    try:
        conn = mysql.connector.connect(
            host='35.229.171.142',
            user='sfqat_superadmin_qa',  #'qat_readonly',
            password='@Td£0Vjw1J2$',   #'NTZ6Wt3tzqCp4k7v',
            port=3306,
            database='GB_Qat'  # !!this is DATABASEname(GB_Qat) in mysql , not the connectionName on mysql workbench....
        )
        yield conn
    except Error as err:
        pytest.fail(f"MySQL connection error: {err}")
    finally:
        print('mysql at finally')
        if conn and conn.is_connected():
            print('going to close the mysql connection')
            conn.close()

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