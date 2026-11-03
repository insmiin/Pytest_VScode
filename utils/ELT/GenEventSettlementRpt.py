import mysql.connector
import csv
from datetime import datetime,timedelta

def output_SF_Event(var_inp_file,var_out_file,var_Eventid,var_ELTDate):  #to gen the SF_Wager_yyyymmdd.csv file
    with open(var_inp_file,'r') as csv_file:
        with open(var_out_file,mode='w', newline='') as output_file:
            csv_reader = csv.DictReader(csv_file)
            csv_writer = csv.DictWriter(output_file, csv_reader.fieldnames, delimiter='|') #if wan split file, change delimiter to comma ','
            csv_writer.writeheader()
            line_count = 0
            xday = 4  # file has recs with EventDate from ELT-4days till ELT-1day
            ELT_convToDate = datetime.strptime(var_ELTDate, '%Y%m%d') #convert str from this format to date
            eventid_str = var_Eventid
            prev_AllDate = ""
            EventDate_Temp = " "
            MatchStart1HDate_Temp = " "
            # MatchEnd1HDate_Temp = " "
            MatchStartFTDate_Temp = " "
            # MatchEndFTDate_Temp = " "
            KeepFTUpdatedDate_Temp = " "
            Keep1HUpdatedDate_Temp = " "
            ScoutFeedMatchEnd1HDate_Temp = " "
            ScoutFeedMatchEndFTDate_Temp = " "
            for row in csv_reader:
                if row["EventID"] == '':
                    print(f'\t{line_count} from SF_Event has been read ')
                    break

                line_count += 1
                row["EventID"] = eventid_str
                if line_count == 1:  #this para is to auto increase CreateDate when there is change of CreateDate
                    prev_AllDate = row["EventDate"][0:10]
                elif row["EventDate"][0:10] != prev_AllDate:
                    prev_AllDate = row["EventDate"][0:10]
                    xday -= 1
                EventDate_Temp = MatchStart1HDate_Temp  = MatchStartFTDate_Temp = ELT_convToDate - timedelta(days=xday)
                KeepFTUpdatedDate_Temp = Keep1HUpdatedDate_Temp = ELT_convToDate - timedelta(days=xday)
                ScoutFeedMatchEnd1HDate_Temp = ScoutFeedMatchEndFTDate_Temp  = ELT_convToDate - timedelta(days=xday)
                #     MatchEndFTDate_Temp = KeepFTUpdatedDate_Temp = Keep1HUpdatedDate_Temp = ELT_convToDate - timedelta(days=4)
                # if line_count >= 1 and line_count <= 3:
                #     EventDate_Temp = MatchStart1HDate_Temp = MatchEnd1HDate_Temp = MatchStartFTDate_Temp  = ELT_convToDate - timedelta(days=4)
                #     MatchEndFTDate_Temp = KeepFTUpdatedDate_Temp = Keep1HUpdatedDate_Temp = ELT_convToDate - timedelta(days=4)
                # elif line_count >= 4 and line_count <= 6:
                #     EventDate_Temp = MatchStart1HDate_Temp = MatchEnd1HDate_Temp = MatchStartFTDate_Temp  = ELT_convToDate - timedelta(days=3)
                #     MatchEndFTDate_Temp = KeepFTUpdatedDate_Temp = Keep1HUpdatedDate_Temp = ELT_convToDate - timedelta(days=3)
                # elif line_count >= 7 and line_count <= 9:
                #     EventDate_Temp = MatchStart1HDate_Temp = MatchEnd1HDate_Temp = MatchStartFTDate_Temp  = ELT_convToDate - timedelta(days=2)
                #     MatchEndFTDate_Temp = KeepFTUpdatedDate_Temp = Keep1HUpdatedDate_Temp = ELT_convToDate - timedelta(days=2)
                # else:
                #     EventDate_Temp = MatchStart1HDate_Temp = MatchEnd1HDate_Temp = MatchStartFTDate_Temp  = ELT_convToDate - timedelta(days=1)
                #     MatchEndFTDate_Temp = KeepFTUpdatedDate_Temp = Keep1HUpdatedDate_Temp = ELT_convToDate - timedelta(days=1)
                row["EventDate"] = str(EventDate_Temp)[0:10] + " " + row["EventDate"][11:35]
                if row["MatchStart1HDate"].upper() != 'NULL':
                    row["MatchStart1HDate"] = str(MatchStart1HDate_Temp)[0:10] + " " + row["MatchStart1HDate"][11:35]
                #if row["MatchEnd1HDate"].upper() != 'NULL':
                #    row["MatchEnd1HDate"] = str(MatchEnd1HDate_Temp)[0:10] + " " + row["MatchEnd1HDate"][11:35]
                if row["MatchStartFTDate"].upper() != 'NULL':
                    row["MatchStartFTDate"] = str(MatchStartFTDate_Temp)[0:10] + " " + row["MatchStartFTDate"][11:35]
                #if row["MatchEndFTDate"].upper() != 'NULL':
                #    row["MatchEndFTDate"] = str(MatchEndFTDate_Temp)[0:10] + " " + row["MatchEndFTDate"][11:35]
                if row["KeepFTUpdatedDate"].upper() != 'NULL':
                    row["KeepFTUpdatedDate"] = str(KeepFTUpdatedDate_Temp)[0:10] + " " + row["KeepFTUpdatedDate"][11:35]
                if row["Keep1HUpdatedDate"].upper() != 'NULL':
                    row["Keep1HUpdatedDate"] = str(Keep1HUpdatedDate_Temp)[0:10] + " " + row["Keep1HUpdatedDate"][11:35]
                if row["ScoutFeedMatchEnd1HDate"].upper() != 'NULL':
                    row["ScoutFeedMatchEnd1HDate"] = str(ScoutFeedMatchEnd1HDate_Temp)[0:10] + " " + row["ScoutFeedMatchEnd1HDate"][11:35]
                if row["ScoutFeedMatchEndFTDate"].upper() != 'NULL':
                    row["ScoutFeedMatchEndFTDate"] = str(ScoutFeedMatchEndFTDate_Temp)[0:10] + " " + row["ScoutFeedMatchEndFTDate"][11:35]

                csv_writer.writerow(row)
                eventid_str += 1

def output_SF_EventResult(var_inp_file,var_out_file,var_Eventid,var_ELTDate):  #to gen the SF_Wager_yyyymmdd.csv file
    with open(var_inp_file,'r') as csv_file:
        with open(var_out_file,mode='w', newline='') as output_file:
            csv_reader = csv.DictReader(csv_file)
            csv_writer = csv.DictWriter(output_file, csv_reader.fieldnames, delimiter='|') #if wan split file, change delimiter to comma ','
            csv_writer.writeheader()
            line_count = 0
            xday = 4
            ELT_convToDate = datetime.strptime(var_ELTDate, '%Y%m%d') #convert str from this format to date
            eventid_str = var_Eventid
            EventDate_Temp = ""

            for row in csv_reader:
                if row["EventID"] == "":
                    print(f'\t{line_count} from SF_EventResult has been read ')
                    break

                line_count += 1
                row["EventID"] = eventid_str
                if line_count == 1:  #this para is to auto increase CreateDate when there is change of CreateDate
                    prev_AllDate = row["EventDate"][0:10]
                elif row["EventDate"][0:10] != prev_AllDate:
                    prev_AllDate = row["EventDate"][0:10]
                    xday -= 1

                EventDate_Temp = ELT_convToDate - timedelta(days=xday)

                row["EventDate"] = str(EventDate_Temp)[0:10] + " " + row["EventDate"][11:35]
                row["EventDateClosed"] = str(ELT_convToDate)[0:10] + " " + row["EventDateClosed"][11:35]

                csv_writer.writerow(row)

                if line_count % 6 == 0: #each eventid has 6 rec. at 6th, +1 to eventid for next eventid
                    eventid_str += 1

def output_SF_EventResultLog(var_inp_file,var_out_file,var_Eventid,var_ELTDate,var_EventResultLogID):  #to gen the SF_Wager_yyyymmdd.csv file
    with open(var_inp_file,'r') as csv_file:
        with open(var_out_file,mode='w', newline='') as output_file:
            csv_reader = csv.DictReader(csv_file)
            csv_writer = csv.DictWriter(output_file, csv_reader.fieldnames, delimiter='|') #if wan split file, change delimiter to comma ','
            csv_writer.writeheader()
            line_count = 0
            prev_eventid = 0
            ELT_convToDate = datetime.strptime(var_ELTDate, '%Y%m%d') #convert str from this format to date
            eventid_str = var_Eventid
            EventDate_Temp = " "
            CrDate_Temp = " "
            xday = 4
            for row in csv_reader:
                if row["EventID"] is None or row["EventID"] == "": #purposely use None, u may refer to csv in text format. the last few line has no ,,,
                    print(f'\t{line_count} from SF_EventResultLog has been read ')
                    break

                line_count += 1
                if line_count == 1:  #this para is to auto increase eventid when there is change of eventid
                    prev_eventid = row["EventID"]
                elif row["EventID"] != prev_eventid:
                    prev_eventid = row["EventID"]
                    eventid_str += 1

                if line_count == 1:  #this para is to auto increase CreateDate when there is change of CreateDate
                    prev_CrDate = row["CreatedDate"][0:10]
                elif row["CreatedDate"][0:10] != prev_CrDate:
                    prev_CrDate = row["CreatedDate"][0:10]
                    xday -= 1

                row["EventID"] = eventid_str
                row["EventResultLogID"] = var_EventResultLogID
                CrDate_Temp = ELT_convToDate - timedelta(days=xday)
                row["CreatedDate"] = str(CrDate_Temp)[0:10] + " " + row["CreatedDate"][11:35]

                csv_writer.writerow(row)
                var_EventResultLogID +=1

def output_SF_ReferenceEventResult(var_inp_file,var_out_file,var_Eventid,var_ELTDate,var_RefResultID):  #to gen the SF_Wager_yyyymmdd.csv file
    with open(var_inp_file,'r') as csv_file:
        with open(var_out_file,mode='w', newline='') as output_file:
            csv_reader = csv.DictReader(csv_file)
            csv_writer = csv.DictWriter(output_file, csv_reader.fieldnames, delimiter='|') #if wan split file, change delimiter to comma ','
            csv_writer.writeheader()
            line_count = 0
            prev_eventid = 0
            ELT_convToDate = datetime.strptime(var_ELTDate, '%Y%m%d') #convert str from this format to date
            eventid_str = var_Eventid
            EventDate_Temp = " "
            CrDate_Temp = " "
            xday = 4
            for row in csv_reader:
                if row["EventID"] is None or row["EventID"] == "": #purposely use None, u may refer to csv in text format. the last few line has no ,,,
                    print(f'\t{line_count} from SF_ReferenceEventResult has been read ')
                    break

                line_count += 1
                if line_count == 1:  #this para is to auto increase eventid when there is change of eventid
                    prev_eventid = row["EventID"]
                elif row["EventID"] != prev_eventid:
                    prev_eventid = row["EventID"]
                    eventid_str += 1

                if line_count == 1:  #this para is to auto increase CreateDate when there is change of CreateDate
                    prev_CrDate = row["CreatedDate"][0:10]
                elif row["CreatedDate"][0:10] != prev_CrDate:
                    prev_CrDate = row["CreatedDate"][0:10]
                    xday -= 1

                row["EventID"] = eventid_str
                row["ReferenceEventResultID"] = var_RefResultID
                CrDate_Temp = ELT_convToDate - timedelta(days=xday)
                row["CreatedDate"] = str(CrDate_Temp)[0:10] + " " + row["CreatedDate"][11:35]
                row["UpdatedDate"] = str(CrDate_Temp)[0:10] + " " + row["UpdatedDate"][11:35]

                csv_writer.writerow(row)
                var_RefResultID +=1

# var_inp_file_Ev = 'C:/Users/lim.miin/OneDrive - Morpheus Consulting Pte Ltd/Desktop/testing/base file ETL/SF_Event_EventSettRpt_template.csv'
# var_inp_file_EvRes = 'C:/Users/lim.miin/OneDrive - Morpheus Consulting Pte Ltd/Desktop/testing/base file ETL/SF_EventResult_EventSettRpt_template.csv'
# var_inp_file_EvResLog = 'C:/Users/lim.miin/OneDrive - Morpheus Consulting Pte Ltd/Desktop/testing/base file ETL/SF_EventResultLog_EventSettRpt_template.csv'
# var_inp_file_RefEvRes = 'C:/Users/lim.miin/OneDrive - Morpheus Consulting Pte Ltd/Desktop/testing/base file ETL/SF_ReferenceEventResult_EventSettRpt_template.csv'
var_inp_file_Ev = 'C:/Users/lim.miin/OneDrive - Morpheus Consulting Pte Ltd/Desktop/testing/base file ETL/SF_Event_EventSettRpt_template.csv'
var_inp_file_EvRes = 'C:/Users/lim.miin/OneDrive - Morpheus Consulting Pte Ltd/Desktop/testing/base file ETL/SF_EventResult_EventSettRpt_template.csv'
var_inp_file_EvResLog = 'C:/Users/lim.miin/OneDrive - Morpheus Consulting Pte Ltd/Desktop/testing/base file ETL/SF_EventResultLog_EventSettRpt_template.csv'
var_inp_file_RefEvRes = 'C:/Users/lim.miin/OneDrive - Morpheus Consulting Pte Ltd/Desktop/testing/base file ETL/SF_ReferenceEventResult_EventSettRpt_template.csv'


######################## --ONLY EDIT FIELDS BELOW:--######################
#var_out_file_Ev = 'C:/Users/lim.miin/OneDrive - Morpheus Consulting Pte Ltd/Desktop/testing/to del/SF_Event_test.csv'
var_out_file_Ev = 'C:/Users/lim.miin/OneDrive - Morpheus Consulting Pte Ltd/Desktop/try ELT files/20250222(evSettle)/New folder/SF_Event_20250222xx.csv'
var_out_file_EvRes = 'C:/Users/lim.miin/OneDrive - Morpheus Consulting Pte Ltd/Desktop/try ELT files/20250222(evSettle)/New folder/SF_EventResult_20250222xx.csv'
var_out_file_EvResLog = 'C:/Users/lim.miin/OneDrive - Morpheus Consulting Pte Ltd/Desktop/try ELT files/20250222(evSettle)/New folder/SF_EventResultLog_20250222xx.csv'
var_out_file_RefEvRes = 'C:/Users/lim.miin/OneDrive - Morpheus Consulting Pte Ltd/Desktop/try ELT files/20250222(evSettle)/New folder/SF_ReferenceEventResult_20250222xx.csv'
var_Eventid = 10000229   #provide next eventid to start from
var_EventResultLogID = 2024  #provide next eventresultlogid to start from
var_RefEventResultID = 203 # provide next referenceEventResultId
var_ELTDate = '20250222' #which ELTdate u will run the ETL (flexible, no need wait on ELT date to gen data)
######################################################################


output_SF_Event(var_inp_file_Ev,var_out_file_Ev,var_Eventid,var_ELTDate)
output_SF_EventResult(var_inp_file_EvRes,var_out_file_EvRes,var_Eventid,var_ELTDate)
output_SF_EventResultLog(var_inp_file_EvResLog,var_out_file_EvResLog,var_Eventid,var_ELTDate,var_EventResultLogID)
output_SF_ReferenceEventResult(var_inp_file_RefEvRes,var_out_file_RefEvRes,var_Eventid,var_ELTDate,var_RefEventResultID)
#21,126,166,59 RECS are expected