#cannot , got error
import google.auth
from google.auth.transport.requests import AuthorizedSession

creds, _ = google.auth.default(
    scopes=["https://www.googleapis.com/auth/cloud-platform"]
)
session = AuthorizedSession(creds)

project = "ghostbuster-dev"
instance = "gb-qat-db-02"

# 1. Patch instance settings to enable Data API access
patch_url = f"https://sqladmin.googleapis.com/v1/projects/{project}/instances/{instance}"
patch_body = {
    "settings": {
        "dataApiAccess": "ALLOW_DATA_API"
    }
}

patch_response = session.patch(patch_url, json=patch_body)
print("Patch status:", patch_response.status_code, patch_response.json())

# Note: The patch operation may take 10-30 seconds to complete on the instance.