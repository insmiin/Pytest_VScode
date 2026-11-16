# this is just a NOTEs of how you can save credentials for Google Cloud Platform.
#  which is required when triggering 'bigquery.Client()' which prepares the communication interface to GCP.

# just run command 'gcloud auth application-default login'
# after run, it is going to save the credentials in a json file in your local machine(save .json to 'C:\Users\lim.miin\AppData\Roaming\gcloud')
# so that when you run this code 'client = bigquery.Client(project="xxxx")'
#    Python looks for Application Default Credentials (ADC).
#    ADC provides your Google Cloud identity.
#    BigQuery checks whether your identity has the required permissions.
#    If authorized, BigQuery executes your SQL query.



#bigquery.Client() = Preparing your communication interface.
#client.query() = Actually sending a request to GCP.
#query_job.result() = Waiting for the response.