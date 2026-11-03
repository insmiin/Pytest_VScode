import mysql.connector
import csv
from datetime import datetime,timedelta

def output_memTag(var_inp_file,var_out_file,var_mem_list):  #to gen the SF_Wager_yyyymmdd.csv file
    with open(var_inp_file,'r') as csv_file:
        with open(var_out_file,mode='w', newline='') as output_file:
            csv_reader = csv.DictReader(csv_file)
            csv_writer = csv.DictWriter(output_file, csv_reader.fieldnames, delimiter='|') #if wan split file, change delimiter to comma ','
            csv_writer.writeheader()
            ttl_line_count = 0
            times = 0
            mem_list = var_mem_list
            member_cnt = len(mem_list)
            while times < member_cnt:
                    ttl_line_count += 1
                    my_names_dict = dict(zip(csv_reader.fieldnames, mem_list[times])) #give fieldname to list item
                    crDate = my_names_dict["CreatedDate"].strftime("%Y-%m-%d %H:%M:%S.%f -04:00") #reformat
                    updDate_2secs = (my_names_dict["UpdatedDate"] + timedelta(seconds=2)).strftime("%Y-%m-%d %H:%M:%S.%f -04:00") #add 2 secs to be greather than existing updDate
                    my_names_dict["CreatedDate"] = crDate
                    my_names_dict["UpdatedDate"] = updDate_2secs

                    csv_writer.writerow(my_names_dict)
                    # print(line_count, row)
                    times += 1

            print(f'\tTotal {ttl_line_count} lines has been written')

def get_mem(list_mem):     #to query mysql to get memDetails
    query_p2 = ""
    for index,x in enumerate(list_mem):
        temp_qy = f'select \'{x[0]}\' as coy, \'{x[1]}\' as mem union all\n'
        if index == len(list_mem) - 1:
            temp_qy = f'select \'{x[0]}\' as coy, \'{x[1]}\' as mem\n'
        query_p2 = query_p2 + temp_qy

    query_p1 = "with get_member as (\n "
    query_p3 = ")\n \
    SELECT  m.memberID, m.membercode, m.companyid ,m.companyname, m.currencycode, m.membercode as legacymemberCode,\n \
    mCat.CatID, 'White' as catColor, mCat.CatLName, m.sfIsAdvised, mSpreadGrp.SpreadGrpLName, \n \
    mSettingprf.SettingPrfLName,SUBTIME(sfUpdatedDate, '4:0:0.000000'), sfUpdatedBy, \n \
    SUBTIME(sfCreatedDate, '4:0:0.000000'),\n \
    m.sfIsHousePlayer,mSettingprf.SettingPrfID, mSpreadGrp.SpreadGrpID,m.sfMemberStatusID,\n \
    '1' as BusUnitID, m.sfIsOverrideBySystem, '1' as SetprfBU, '1' as SprdGrpBU , '0' isfollowAll, '0' isFreeze,\n \
    '1' as isNotifyMerch, m.SourceID, m.isFirstTimeLogin\n \
    FROM GB_Qat.members m\n \
    inner join (select enumID as CatID,name as CatSName,displayName as CatLName \n \
    from GB_Qat.displaynameenum where enumName= 'MemberCategoryEnum' ) mCat\n \
    on m.sfMemberCategoryID = mCat.CatID\n \
    inner join (select enumID as SpreadGrpID, name as SpreadGrpSName,displayName as SpreadGrpLName \n \
    from GB_Qat.displaynameenum where enumName= 'SpreadGroupEnum' ) mSpreadGrp \n \
    on m.sfSpreadGroupID = mSpreadGrp.SpreadGrpID \n \
    inner join (select enumID as SettingPrfID, name as SettingPrfSName,displayName as SettingPrfLName \n \
    from GB_Qat.displaynameenum where enumName= 'MemberSettingProfileEnum' ) mSettingprf \n \
    on m.sfMemberSettingProfileID = mSettingprf.SettingPrfID \n \
    inner join get_member um \n \
    on um.mem = m.membercode and um.coy = m.companyname"

    query_stmt = query_p1 + query_p2 + query_p3

    mydb = mysql.connector.connect(
        host='35.229.171.142',
        user='qat_readonly',
        password='NTZ6Wt3tzqCp4k7v',
        port=3306,
        database='GB_Qat'  # !!this is DATABASEname(GB_Qat) in mysql , not the connectionName on mysql workbench....
    )
    mycursor = mydb.cursor()

    mycursor.execute(query_stmt)

    myresult = mycursor.fetchall()

    output_list = []
    for x in myresult:
        output_list.append(list(x))
    return output_list


########################ONLY EDIT FIELDS BELOW:--######################
#after gen, check created/UpdatedDate, make sure within etldateprocess range
var_inp_file = 'C:/Users/lim.miin/OneDrive - Morpheus Consulting Pte Ltd/Desktop/testing/base file ETL/SF_Member_template.csv'
var_out_file = 'C:/Users/lim.miin/OneDrive - Morpheus Consulting Pte Ltd/Desktop/testing/to del/SF_Member_test.csv'
#var_out_file = 'C:/Users/LimMiin/OneDrive - Morpheus Consulting Pte Ltd/Desktop/try ELT files/20231207run(sf_wager_memtag)/SF_Member_20231207.csv'
#provide coyname & memCode    --if add new field,remember to add in function too
mem_list = [
            ["SfMiniIGPTW2", "gbtest01"],
             ["SfMiniIGPTW2", "gbtest02"],
             ["SfMiniIGPTW2",  "gbtest03"],
             ["SfMiniIGPTW2", "gbtest04"],
             ["SfMiniIGPTW2",  "gbtest04"],
             [ "SfMiniIGPTW2", "gbtest05"]
            ]

######################################################################

var_mem_list = get_mem(mem_list)  #-to return list of memDtl in list91253,SfMiniIGPCW1,233065,gbmember0601,REG,Regular,5)
output_memTag(var_inp_file,var_out_file,var_mem_list)
