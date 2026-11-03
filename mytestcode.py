#cannot run. not authorised.missing permission cloudsql.instances.connect on resource instances/gb-qat-db-02

import os

from google.cloud.sql.connector import Connector, IPTypes
import pymysql

import sqlalchemy


def connect_with_connector() -> sqlalchemy.engine.base.Engine:
    """
    Initializes a connection pool for a Cloud SQL instance of MySQL.

    Uses the Cloud SQL Python Connector package.
    """
    # Note: Saving credentials in environment variables is convenient, but not
    # secure - consider a more secure solution such as
    # Cloud Secret Manager (https://cloud.google.com/secret-manager) to help
    # keep secrets safe.

    instance_connection_name = "ghostbuster-dev:asia-east1:gb-qat-db-02" # e.g. 'project:region:instance'
    db_user = "sfqat_superadmin_qa"  # e.g. 'my-db-user'
    db_pass =  "DB_PASS"   # e.g. 'my-db-password'
    db_name = "GB_Qat"  # e.g. 'my-database'

    ip_type = IPTypes.PRIVATE if os.environ.get("PRIVATE_IP") else IPTypes.PUBLIC

    # initialize Cloud SQL Python Connector object
    connector = Connector(ip_type=ip_type, refresh_strategy="LAZY")

    def getconn() -> pymysql.connections.Connection:
        conn: pymysql.connections.Connection = connector.connect(
            instance_connection_name,
            "pymysql",
            user=db_user,
            password=db_pass,
            db=db_name,
        )
        return conn

    pool = sqlalchemy.create_engine(
        "mysql+pymysql://",
        creator=getconn,
        # ...
    )

    with pool.connect() as db_conn:

        # query database
        result = db_conn.execute(sqlalchemy.text("SELECT * from my_table")).fetchall()

        # commit transaction (SQLAlchemy v2.X.X is commit as you go)
        db_conn.commit()

        # Do something with the results
        for row in result:
            print(row)
    connector.close()
    #return pool


connect_with_connector()