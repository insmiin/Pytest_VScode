#cannot , got error
import os
import google.auth
from google.auth.transport.requests import AuthorizedSession

creds, _ = google.auth.default(scopes=["https://www.googleapis.com/auth/cloud-platform"])
session = AuthorizedSession(creds)

# url = ("https://sqladmin.googleapis.com/v1/projects/ghostbuster-dev"
#        "/instances/gb-qat-db-02/executeSql")
url = (
    "https://sqladmin.googleapis.com/sql/v1beta4/"
    "projects/ghostbuster-dev/instances/gb-qat-db-02/executeSql"
)
body = {
    "database": "GB_Qat",
    "user": "sfqat_superadmin_qa",
    "passwordSecretVersion": "projects/ghostbuster-dev/locations/asia-east1/secrets/db-password/versions/latest",
    "sqlStatement": "SELECT * FROM memberextrainfos LIMIT 5",
}

resp = session.post(url, json=body)
print(resp.status_code)
print(resp.json())
