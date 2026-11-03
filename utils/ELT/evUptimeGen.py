import mysql.connector
import csv
from datetime import datetime,timedelta

def read_write_new_ev(csv_reader_Ev,columns_to_exclude_ev,csv_writer_ev,var_ELTDate,csv_file_EvResultLog,csv_reader_EvResultLog,csv_writer_EvResultLog):
    event_rec  = []
    try:
        event_rec = next(csv_reader_Ev)
    except StopIteration:
        return event_rec #stop processing subsequent logs
    dt = datetime.strptime(var_ELTDate, '%Y%m%d')
    output_date = dt.strftime('%Y-%m-%d %H:%M:%S.%f') + '0' + ' -04:00'
    event_rec['UpdatedDate'] = output_date
    event_rec['CreatedDate'] = output_date
    # get difference in secs btw EventStatusUpdatedDateSamp & EventDateSamp
    temp_KeepFTUpdatedDate = event_rec['KeepFTUpdatedDate']
    temp_EventDate = event_rec['temp_EventDate']
    datetime1 = datetime.strptime(temp_KeepFTUpdatedDate[0:19], '%Y-%m-%d %H:%M:%S')
    datetime2 = datetime.strptime(temp_EventDate[0:19], '%Y-%m-%d %H:%M:%S')
    time_difference = datetime1 - datetime2
    difference_in_seconds = time_difference.total_seconds()

    # add difference in secs to new EventDate to get new KeepFTUpdatedDate
    dt = datetime.strptime(event_rec["EventDate"][0:19], '%Y-%m-%d %H:%M:%S')
    dt_updated = dt + timedelta(seconds=difference_in_seconds)
    updated_timestamp = dt_updated.strftime('%Y-%m-%d %H:%M:%S')
    event_rec['KeepFTUpdatedDate'] = updated_timestamp + temp_KeepFTUpdatedDate[19:34]
    filtered_row = {key: value for key, value in event_rec.items() if key not in columns_to_exclude_ev}
    csv_writer_ev.writerow(filtered_row)

    for resultLog_rec in csv_reader_EvResultLog:
        resultLog_rec['EventDate'] = event_rec['EventDate']
        resultLog_rec['EventDateClosed'] = updated_timestamp + temp_KeepFTUpdatedDate[19:34]   #random date not important
        resultLog_rec['EventID'] = event_rec['EventID']
        resultLog_rec['EventName'] = event_rec['temp_EventName']
        resultLog_rec['CompetitionName'] = event_rec['CompetitionName']
        resultLog_rec['CompetitionNameCH'] = event_rec['CompetitionName']
        resultLog_rec['CompetitionID'] = event_rec['CompetitionID']
        resultLog_rec['SportID'] = event_rec['SportID']
        resultLog_rec['SportName'] = event_rec['SportName']
        resultLog_rec['EventTypeName'] = event_rec['EventTypeName']
        if resultLog_rec['ResultSelectionName'] == 'Home':
            resultLog_rec['TeamID'] = event_rec['HomeTeamID']
            resultLog_rec['TeamName'] = event_rec['HomeTeamName']
            resultLog_rec['TeamNameCH'] = event_rec['HomeTeamName']
        else:
            resultLog_rec['TeamID'] = event_rec['AwayTeamID']
            resultLog_rec['TeamName'] = event_rec['AwayTeamName']
            resultLog_rec['TeamNameCH'] = event_rec['AwayTeamName']

        csv_writer_EvResultLog.writerow(resultLog_rec)

    csv_file_EvResultLog.seek(0)
    next(csv_file_EvResultLog)
    return event_rec

def output_SF_EventLog(var_inp_file_Ev,var_inp_file_EvLog,var_inp_file_EvResultLog,var_out_file_ev,var_out_file_EvLog,var_out_file_EvResultLog,var_EventLogID,var_ELTDate):  #to gen the SF_Wager_yyyymmdd.csv file
    with open(var_inp_file_Ev,'r') as csv_file_Ev, open(var_inp_file_EvLog,'r') as csv_file_EvLog, open(var_inp_file_EvResultLog,'r') as csv_file_EvResultLog:
        with open(var_out_file_EvLog,mode='w', newline='') as output_file_EvLog,open(var_out_file_ev,mode='w', newline='') as output_file_ev, open(var_out_file_EvResultLog,mode='w',newline='') as output_file_EvResultLog:
            csv_reader_Ev = csv.DictReader(csv_file_Ev)
            csv_reader_EvLog = csv.DictReader(csv_file_EvLog)
            csv_reader_EvResultLog = csv.DictReader(csv_file_EvResultLog)

            columns_to_exclude_ev = ['ev_mapid','temp_EventDate','temp_EventName']
            selected_columns_ev = [col for col in csv_reader_Ev.fieldnames if col not in columns_to_exclude_ev]
            csv_writer_ev = csv.DictWriter(output_file_ev, selected_columns_ev, delimiter='|') #if wan split file, change delimiter to comma ','
            csv_writer_ev.writeheader()

            columns_to_exclude = ['ev_evlog_mapid']
            selected_columns = [col for col in csv_reader_EvLog.fieldnames if col not  in columns_to_exclude]
            csv_writerEvLog = csv.DictWriter(output_file_EvLog, selected_columns, delimiter='|') #if wan split file, change delimiter to comma ','
            csv_writerEvLog.writeheader()

            csv_writer_EvResultLog = csv.DictWriter(output_file_EvResultLog, csv_reader_EvResultLog.fieldnames,delimiter='|') #if wan split file, change delimiter to comma ','
            csv_writer_EvResultLog.writeheader()

            gen_EventLogID = var_EventLogID
            evLog_written = 0
            ev_written = 0
            ev_writtenCnt = 0
            temp_ev_mapid = None
            event_EOF = None

            #read event for 1st rec.
            #Then reach evlog sequentially:
                #if event < evlog, keep read event
                #if event > evlog, skip loop(read evlog again)
                #other than that(i.e event = ev log), start processing

            event_rec = read_write_new_ev(csv_reader_Ev,columns_to_exclude_ev,csv_writer_ev,var_ELTDate,csv_file_EvResultLog,csv_reader_EvResultLog,csv_writer_EvResultLog)
            for evlog_rec in csv_reader_EvLog:
                #print('evlog_rec["ev_evlog_mapid"]:',evlog_rec["ev_evlog_mapid"])
                #print('event_rec["ev_mapid"]:', event_rec["ev_mapid"])
                while int(evlog_rec["ev_evlog_mapid"]) > int(event_rec["ev_mapid"]):
                    event_rec = read_write_new_ev(csv_reader_Ev,columns_to_exclude_ev,csv_writer_ev,var_ELTDate,csv_file_EvResultLog,csv_reader_EvResultLog,csv_writer_EvResultLog)
                    #print('event_rec["ev_mapid"] after:', event_rec["ev_mapid"])
                    if event_rec == []:
                        event_EOF = True
                        break # breakout of while loop if no more event rec to process.
                if event_EOF: # breakout of for loop, stop processing subsequent logs
                    break
                if int(evlog_rec["ev_evlog_mapid"]) < int(event_rec["ev_mapid"]):
                    continue
                #print('process')
                evlog_rec["EventLogID"] = gen_EventLogID
                evlog_rec['EventID'] = event_rec["EventID"]
                #get difference in secs btw EventStatusUpdatedDateSamp & EventDateSamp
                temp_EventStatusUpdatedDate = evlog_rec['EventStatusUpdatedDate']
                temp_EventDate = evlog_rec['EventDate']
                datetime1 = datetime.strptime(temp_EventStatusUpdatedDate[0:19], '%Y-%m-%d %H:%M:%S')
                datetime2 = datetime.strptime(temp_EventDate[0:19], '%Y-%m-%d %H:%M:%S')
                time_difference = datetime1 - datetime2
                difference_in_seconds = time_difference.total_seconds()

                # add difference in secs to new EventDate to get new EventStatusUpdatedDateSamp
                dt = datetime.strptime(event_rec["EventDate"][0:19], '%Y-%m-%d %H:%M:%S')
                dt_updated = dt + timedelta(seconds=difference_in_seconds)
                updated_timestamp = dt_updated.strftime('%Y-%m-%d %H:%M:%S')
                evlog_rec['EventDate'] = event_rec["EventDate"]
                evlog_rec['EventStatusUpdatedDate'] = updated_timestamp + temp_EventStatusUpdatedDate[19:34]
                evlog_rec['CreatedDate'] = updated_timestamp + temp_EventStatusUpdatedDate[19:34]
                filtered_row = {key: value for key, value in evlog_rec.items() if key not in columns_to_exclude}
                csv_writerEvLog.writerow(filtered_row)
                evLog_written = evLog_written + 1
                if temp_ev_mapid != int(event_rec["ev_mapid"]):
                    ev_writtenCnt = ev_writtenCnt + 1
                    temp_ev_mapid = int(event_rec["ev_mapid"])
                gen_EventLogID = gen_EventLogID + 1
            print('ending..')
            print(f'{ev_writtenCnt} events with total of {evLog_written} recs have been written into event_log output file ')



var_inp_file_Ev = 'D:/Miin/CRQ(miin draft)/RMGB-157/GBCRQ-409 [Main] Traders KPI report in GB/ELT to use/template_SF_Event_EventUptime_toedit.csv'
var_inp_file_EvLog = 'D:/Miin/CRQ(miin draft)/RMGB-157/GBCRQ-409 [Main] Traders KPI report in GB/ELT to use/template_SF_EventLog_EventUptime.csv'
var_inp_file_EvResultLog = 'D:/Miin/CRQ(miin draft)/RMGB-157/GBCRQ-409 [Main] Traders KPI report in GB/ELT to use/template_SF_EventResult_EventUptime.csv'

######################## --ONLY EDIT FIELDS BELOW:--######################
var_ELTDate = '20250218' #which ELTdate u will run the ETL (flexible, no need wait on ELT date to gen data)
var_out_file_EvLog = f'C:/Users/lim.miin/OneDrive - Morpheus Consulting Pte Ltd/Desktop/try ELT files/20260602run(nouse)/SF_EventLog_{var_ELTDate}xx.csv'
var_out_file_EvResultLog = f'C:/Users/lim.miin/OneDrive - Morpheus Consulting Pte Ltd/Desktop/try ELT files/20260602run(nouse)/SF_EventResult_{var_ELTDate}xx.csv'
var_out_file_ev = f'C:/Users/lim.miin/OneDrive - Morpheus Consulting Pte Ltd/Desktop/try ELT files/20260602run(nouse)/SF_Event_{var_ELTDate}xx.csv'
var_EventLogID = 907  #provide next eventresultlogid to start from
######################################################################


output_SF_EventLog(var_inp_file_Ev,var_inp_file_EvLog,var_inp_file_EvResultLog, var_out_file_ev,var_out_file_EvLog,var_out_file_EvResultLog,var_EventLogID,var_ELTDate)
