from google.cloud import bigquery
from google.oauth2 import service_account

# Path to your service account key file
key_path = "C:/Users/lim.miin/OneDrive - Morpheus Consulting Pte Ltd/Desktop/testing/py-gcpBQ/carbon-sensor-259109-d37561cb1a02.json"

# Create a credentials object
credentials = service_account.Credentials.from_service_account_file(key_path)

# Instantiate the BigQuery client with the credentials
client = bigquery.Client(credentials=credentials, project=credentials.project_id)
member_value = 'abc123'
#copy sql from bq script and paste in text file #select * from ghostbuster-dev.RAW.SF_Member where memberCode = {P_member}
with open("C:/Users/lim.miin/OneDrive - Morpheus Consulting Pte Ltd/Desktop/querytxt.txt", "r") as file:
    query_template = file.read()

    # Inject the dynamic value
query = query_template.replace("{P_member}", f"'{member_value}'")


query_job = client.query(query)

# Fetch and print the results
results = query_job.result()
print('jobid=',query_job)
print('location=',query_job.result())
for row in results:
    print(row)