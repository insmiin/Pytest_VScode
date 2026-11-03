import mysql.connector
import csv
from datetime import datetime,timedelta

def output_memTag(var_inp_file,var_out_file,var_wagerno,var_fpjs,var_eventid,var_inp_file_odds,var_out_file_odds,var_oddsLogid,var_batchid,var_ELTRunDate):  #to gen the SF_Wager_yyyymmdd.csv file
    with open(var_inp_file,'r') as csv_file,open(var_inp_file_odds,'r') as csv_file_odds:
        with open(var_out_file,mode='w', newline='') as output_file,open(var_out_file_odds,mode='w', newline='') as output_file_odds:
            csv_reader = csv.DictReader(csv_file)
            csv_writer = csv.DictWriter(output_file, csv_reader.fieldnames, delimiter='|') #if wan split file, change delimiter to comma ','
            csv_writer.writeheader()
            csv_reader_odds = csv.DictReader(csv_file_odds)
            csv_writer_odds = csv.DictWriter(output_file_odds, csv_reader_odds.fieldnames, delimiter='|') #if wan split file, change delimiter to comma ','
            csv_writer_odds.writeheader()
            crDate = ''
            line_count = 0
            ELT_minus1 = str((datetime.today() - timedelta(days=1)).strftime('%Y-%m-%d')) #+ " 17:09:25.8940000 -04:00"
            ELT_minus1 = str(datetime.strptime(var_ELTRunDate, '%Y-%m-%d').date() - timedelta(days=1))
            wagerno_str = var_wagerno
            OddsLogID_str = var_oddsLogid
            BatchID_str = var_batchid
            fpjs = var_fpjs
            eventid = var_eventid
            prev_evid = 0
            #- use by odds_log file -#
            wager_odds_idx = 0
            for row in csv_reader:
                line_count += 1
                if line_count == 1:
                    prev_evid = row["EventID"]
                    odds_log_next = next(csv_reader_odds)
                elif row["WagerNo"] == '':
                    line_count -= 1
                    break
                elif row["EventID"] != prev_evid:
                    eventid +=1
                    prev_evid = row["EventID"]
                get_time=row["CreatedDate"][11:]
                crDate = ELT_minus1 + ' ' + get_time
                row["CreatedDate"] = crDate
                row["EventDate"] = crDate
                if line_count == 12:
                    get_Goaltime = row["GoalTime"][11:]
                    get_Settledtime = row["SettledDate"][11:]
                    row["GoalTime"] = ELT_minus1 + ' ' + get_Goaltime
                    row["SettledDate"] = ELT_minus1 + ' ' + get_Settledtime
                row["EventID"] = eventid
                row["WagerNo"] = wagerno_str
                row["WagerID"] = wagerno_str
                csv_writer.writerow(row)
                wagerno_str +=1

                while odds_log_next["EventID"] == prev_evid:
                    odds_log_next["EventID"] = row["EventID"]
                    odds_log_next["DateCreated"] = ELT_minus1 + ' ' + row["CreatedDate"][11:]
                    odds_log_next["OddsLogID"] = OddsLogID_str
                    odds_log_next["BatchID"] = BatchID_str
                    csv_writer_odds.writerow(odds_log_next)
                    OddsLogID_str +=1
                    BatchID_str +=1
                    odds_log_next = next(csv_reader_odds)




            print(f'total of {line_count} was written')




def get_mem(list_mem):     #to query mysql to get memDetails
    query_p2 = ""
    for index,x in enumerate(list_mem):
        temp_qy = f'select \'{x[0]}\' as coy, \'{x[1]}\' as mem union all\n'
        if index == len(list_mem) - 1:
            temp_qy = f'select \'{x[0]}\' as coy, \'{x[1]}\' as mem\n'
        query_p2 = query_p2 + temp_qy

    query_p1 = "with get_member as (\n "
    query_p3 = ")\n \
    SELECT  companyID,companyName,memberid,membercode, enu.name,enu.displayname, enu.enumID\n \
    FROM GB_Qat.members m\n \
    inner join GB_Qat.displaynameenum  enu\n \
    on m.sfMemberCategoryID = enu.enumid\n \
    inner join get_member um\n \
    on um.mem = m.membercode and um.coy = m.companyname\n \
    where enu.enumName= 'MemberCategoryEnum'"

    query_stmt = query_p1 + query_p2 + query_p3
    #print(query_stmt)

    mydb = mysql.connector.connect(
        host="192.168.14.218",
        user="qat_readonly",
        password="NTZ6Wt3tzqCp4k7v",
        port="3308",
        database="GB_Qat"
    )
    mycursor = mydb.cursor()

    mycursor.execute(query_stmt)

    myresult = mycursor.fetchall()

    output_list = []
    for x in myresult:
        output_list.append(list(x))
    return output_list

var_inp_file = 'C:/Users/LimMiin/OneDrive - Morpheus Consulting Pte Ltd/Desktop/testing/base file ETL/SF_Wager_WagerReport_template.csv'
var_inp_file_odds = 'C:/Users/LimMiin/OneDrive - Morpheus Consulting Pte Ltd/Desktop/testing/base file ETL/SF_OddsLog_WagerReport_template.csv'
########################ONLY EDIT FIELDS BELOW:--######################
var_out_file = 'C:/Users/LimMiin/OneDrive - Morpheus Consulting Pte Ltd/Desktop/try ELT files/20240527run()/SF_Wager_20240527.csv'
var_out_file_odds = 'C:/Users/LimMiin/OneDrive - Morpheus Consulting Pte Ltd/Desktop/try ELT files/20240527run()/SF_OddsLog_20240527.csv'
var_wagerno = 1236621  #provide wagerNo to start from
var_ELTRunDate = "2024-05-27"   #which ELTdate u will run the ETL (flexible, no need wait on ELT date to gen data)
var_fpjs="f12b"   #provide fpjs(should be not used)
var_eventid = 13  #from last eventid
var_oddsLogid = 173  #from last oddslogid
var_batchid = 1 #should be doesnt matter wat value

######################################################################

#var_mem_list = get_mem(mem_list)  #-to return list of memDtl in list91253,SfMiniIGPCW1,233065,gbmember0601,REG,Regular,5)
output_memTag(var_inp_file,var_out_file,var_wagerno,var_fpjs,var_eventid,var_inp_file_odds,var_out_file_odds,var_oddsLogid,var_batchid,var_ELTRunDate)
