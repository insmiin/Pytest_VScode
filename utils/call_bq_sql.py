# work. use my own gcp credential to access
# 1) Install the Google Cloud CLI
# 2) run this on pycharm terminal  -->  gcloud auth application-default login
#    login using your credentials
#    it will save .json to 'C:\Users\lim.miin\AppData\Roaming\gcloud'
# run below script
from google.cloud import bigquery

# Use the project where your queries should run (and be billed)
client = bigquery.Client(project="carbon-sensor-259109")
member_value = 'abc123'
#copy sql from bq script and paste in text file #select * from ghostbuster-dev.RAW.SF_Member where memberCode = {P_member}
with open("C:/Users/lim.miin/Desktop/querytxt.txt", "r") as file:
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

# BELOW NO LONGER ABLE TO USE .JSON TO ACCESS
'''
from google.cloud import bigquery
from google.oauth2 import service_account

# Path to your service account key file
key_path = "C:/Users/lim.miin/Desktop/testing/py-gcpBQ/carbon-sensor-259109-d37561cb1a02.json"

# Create a credentials object
credentials = service_account.Credentials.from_service_account_file(key_path)

# Instantiate the BigQuery client with the credentials
client = bigquery.Client(credentials=credentials, project=credentials.project_id)
member_value = 'abc123'
#copy sql from bq script and paste in text file #select * from ghostbuster-dev.RAW.SF_Member where memberCode = {P_member}
with open("C:/Users/lim.miin/Desktop/querytxt.txt", "r") as file:
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
'''