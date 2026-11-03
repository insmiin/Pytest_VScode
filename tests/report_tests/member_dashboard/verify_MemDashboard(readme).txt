#prepare csv file. populate column headers with each of fields in API request
#prepare your BQscript so that format of each return row matches the row in API response

#use Fixture to setup API session & get bqClient to be shared among all testcase(scope=session)
#read all rows from csv into list of dictionary. Then scan thru each dictionary to convert the value into API accepted format

#test_function:
  -execute only fixture once
  -read and process each of the dictionary/csvRow until end of the list
	1)pass in the formatted_csv filtering and call API to get API response in Json
        -split the APIresponse row into differenct category of dictionary based on the 'performancetype'
         eg.{
'betType':[{'eventDate': None, 'eventMonth': None, 'sportName': None},{'eventDate': None, 'eventMonth': None, 'sportName': None},{'eventDate': None, 'eventMonth': None, 'sportName': None}],
'sports':[{'eventDate': None, 'eventMonth': None, 'sportName': None},{'eventDate': None, 'eventMonth': None, 'sportName': None},{'eventDate': None, 'eventMonth': None, 'sportName': None}],
'eventDate':[{'eventDate': None, 'eventMonth': None, 'sportName': None},{'eventDate': None, 'eventMonth': None, 'sportName': None},{'eventDate': None, 'eventMonth': None, 'sportName': None}]
}
	2)pass in the formatted_csv filtering and call myBQscript to get sql output in Json

	3)for each bqRow in SQL_Output,
            identify the dictionaryCategory to scan (eg.bettype --> "betType":[{},{},{}]) based on the performanceType
            scan thru each of the dictionary in betType and see if all fields in bqRow match with any of the dictionary {}
            if found ok, not found, give error