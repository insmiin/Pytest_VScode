import mysql.connector
import csv
from datetime import datetime,timedelta
import copy
import math
import requests

def output_SF_Wager(var_inp_file_Soc,var_inp_file_Soc_OE,var_inp_file_BB,var_inp_file_BB_OE,var_inp_file_TT,var_out_file,var_mem_list,
                    var_ELTDate,var_wagerno,var_totRealWagers,var_ruleSoc,var_ruleBB,var_Chg_AdditionalCnt,var_HighLowerFlag):  #to gen the SF_Wager_yyyymmdd.csv file
    with open(var_inp_file_Soc,'r') as csv_file_Soc,open(var_inp_file_Soc_OE,'r') as csv_file_Soc_OE,open(var_inp_file_BB,'r') as csv_file_BB,open(var_inp_file_BB_OE,'r') as csv_file_BB_OE,open(var_inp_file_TT,'r') as csv_file_TT:
        with open(var_out_file,mode='w', newline='') as output_file:   #use 'a' if append to existing outputFile[beware,header will be write again]
            csv_reader_Soc = csv.DictReader(csv_file_Soc)
            csv_writer = csv.DictWriter(output_file, csv_reader_Soc.fieldnames, delimiter='|') #if wan split file, change delimiter to comma ','
            csv_writer.writeheader()
            csv_reader_BB= csv.DictReader(csv_file_BB)
            csv_reader_TT = csv.DictReader(csv_file_TT)
            csv_reader_Soc_OE = csv.DictReader(csv_file_Soc_OE)
            csv_reader_BB_OE = csv.DictReader(csv_file_BB_OE)

            ELT_ToYmd = datetime.strptime(var_ELTDate, '%Y%m%d').date() #conv from 20230121 to 2023-01-21
            ELT_YmdToStr = str(ELT_ToYmd) #convert  to string 2023-01-21
            wagerno_str = var_wagerno
            xSec = 1
            WrittenItem = 0
            rec_name = ''
            Wager_RealSocBB = {}
            Wager_OtherSport = {}
            Wager_RealSocBB_OE = {}
            stakeodds = []
            #stakeodds = get_oddsStake(var_rule)

            Wager_ArberRule_soc = next(csv_reader_Soc)  #type dic
            Wager_ArberRule_BB = next(csv_reader_BB)  #type dic
            Wager_ArberRule_TT = next(csv_reader_TT)  # type dic
            Wager_ArberRule_soc_OE = next(csv_reader_Soc_OE)  # type dic
            Wager_ArberRule_BB_OE = next(csv_reader_BB_OE)  # type dic
            global errorFlag

#var_EachRealSport_defaultCnt

            for mem in var_mem_list:
                if mem[7] == "Soc" and mem[10] == "":
                    var_RealHitMaxAvgCnt_Soc = var_RealHitMaxAvgCnt
                    TotRealWager_BB = 0
                elif mem[7] == "" and mem[10] == "BB":
                    TotRealWager_Soc = 0
                    var_RealHitMaxAvgCnt_BB = var_RealHitMaxAvgCnt
                elif mem[8] == 100 and mem[9] == 46 and mem[11] == 100 and mem[12]==53 and var_HighLowerFlag == '': #Soc:Rule%=46%,Exp=50% #BB:Rule%=53%,Exp=50%
                    var_RealHitMaxAvgCnt_Soc = 26  #hardcoded
                    var_RealHitMaxAvgCnt_BB = 30
                elif mem[8] == 100 and mem[9] == 53 and mem[11] == 100 and mem[12] == 46 and var_HighLowerFlag == '':  # BB:Rule%=46%,Exp=50% #Soc:Rule%=53%,Exp=50%
                    var_RealHitMaxAvgCnt_Soc = 30
                    var_RealHitMaxAvgCnt_BB = 26
                else:
                    errorFlag = 1
                    print('ERROR ==> for ArberMember testing: Mem with both Real Soc & BB, only 2 combo Rule%/Exp% can be processed, \
 (Pls scroll up to see the combo). or only support NewScore computation \n \
    ==> for ArberRule testing: Mem with both Real Soc & BB, use seperate Mem record, 1 only has Soc data & another 1 only has BB data' )
                    break

                TotWagerWritten = 0
                TotRealWagerWritten = 0
                TotRealWagerSoc = 0
                TotRealWagerBB = 0
                OthrSportCnt = 0
                Max20MsgSoc = "---------------------"
                Max20MsgBB =  "---------------------"
                printMsg_RealExp_Soc = "-------------"
                printMsg_RealExp_BB =  "-------------"


                for Rule in (mem[7],mem[10]):
                    RealMaxAvgHitTotCnt =0
                    RealMaxAvgNoHitTotCnt = 0
                    HitCnt = 0
                    NoHitCnt = 0

                    if Rule == "":
                        continue
                    Wager_OtherSport = copy.deepcopy(Wager_ArberRule_TT)
                    if Rule == 'Soc':
                        stakeodds = get_oddsStake(var_ruleSoc)
                        Wager_RealSocBB= copy.deepcopy(Wager_ArberRule_soc)  #can't jz assign directly. for dict, u will refer them to same memory
                        Wager_RealSocBB_OE = copy.deepcopy(Wager_ArberRule_soc_OE)
                        if var_HighLowerFlag == 'L':
                            RealMaxAvgHitTotCnt = 0
                            RealMaxAvgNoHitTotCnt = var_Chg_AdditionalCnt
                        else:
                            RealMaxAvgHitTotCnt = var_RealHitMaxAvgCnt_Soc
                            if var_HighLowerFlag == 'H':
                                RealMaxAvgHitTotCnt = var_Chg_AdditionalCnt
                            RealMaxAvgNoHitTotCnt= math.floor(100/mem[9] * RealMaxAvgHitTotCnt) - RealMaxAvgHitTotCnt # roundDown to lower integer to prevent computed % lower than requested
                        TotRealWager_Soc = RealMaxAvgHitTotCnt + RealMaxAvgNoHitTotCnt
                        TotOthrSportTT = math.floor((100 / mem[8] * TotRealWager_Soc) - TotRealWager_Soc)
                    elif Rule == 'BB':
                        stakeodds = get_oddsStake(var_ruleBB)
                        Wager_RealSocBB = copy.deepcopy(Wager_ArberRule_BB)  #so use copy to really create a new variable
                        Wager_RealSocBB_OE = copy.deepcopy(Wager_ArberRule_BB_OE)
                        if var_HighLowerFlag == 'L':
                            RealMaxAvgHitTotCnt = 0
                            RealMaxAvgNoHitTotCnt = var_Chg_AdditionalCnt
                        else:
                            RealMaxAvgHitTotCnt = var_RealHitMaxAvgCnt_BB
                            if var_HighLowerFlag == 'H':
                                RealMaxAvgHitTotCnt = var_Chg_AdditionalCnt
                            RealMaxAvgNoHitTotCnt= math.floor(100/mem[12] * RealMaxAvgHitTotCnt) - RealMaxAvgHitTotCnt # roundDown to lower integer to prevent computed % lower than requested
                        TotRealWager_BB = RealMaxAvgHitTotCnt + RealMaxAvgNoHitTotCnt
                        TotOthrSportTT = math.floor((100 / mem[11] * TotRealWager_BB) - TotRealWager_BB)
                    else:
                        print(f'ERROR ==> Invalid ArberRuleSport:  {Rule}, please check!')



                    #static wager variable
                    Wager_RealSocBB["CompanyID"] = mem[0]
                    Wager_RealSocBB["CompanyName"] = mem[1]
                    Wager_RealSocBB['MemberID'] = mem[2]
                    Wager_RealSocBB["MemberCode"] = mem[3]
                    Wager_RealSocBB["MemberCategoryCode"] = mem[4]
                    Wager_RealSocBB["MemberCategoryName"] = mem[5]
                    Wager_RealSocBB["MemberCategoryID"] = mem[6]
                    Wager_RealSocBB_OE["CompanyID"] = mem[0]
                    Wager_RealSocBB_OE["CompanyName"] = mem[1]
                    Wager_RealSocBB_OE['MemberID'] = mem[2]
                    Wager_RealSocBB_OE["MemberCode"] = mem[3]
                    Wager_RealSocBB_OE["MemberCategoryCode"] = mem[4]
                    Wager_RealSocBB_OE["MemberCategoryName"] = mem[5]
                    Wager_RealSocBB_OE["MemberCategoryID"] = mem[6]
                    Wager_OtherSport["CompanyID"] = mem[0]
                    Wager_OtherSport["CompanyName"] = mem[1]
                    Wager_OtherSport['MemberID'] = mem[2]
                    Wager_OtherSport["MemberCode"] = mem[3]
                    Wager_OtherSport["MemberCategoryCode"] = mem[4]
                    Wager_OtherSport["MemberCategoryName"] = mem[5]
                    Wager_OtherSport["MemberCategoryID"] = mem[6]
                    WagerCrDate = Wager_ArberRule_soc["CreatedDate"]
                    WagerCrToELTDate_Str = ELT_YmdToStr + WagerCrDate[10:19] #use ELTDate + crDate original time
                    WagerCrToELTDate_YmdHMS= datetime.strptime(WagerCrToELTDate_Str, "%Y-%m-%d %H:%M:%S") #conv to ymdhms format
                    NewCrDate =WagerCrToELTDate_YmdHMS-timedelta(days=1)  #use 1 day before ELTdate

                    #dynamic wager variable - loop to gen RealMaxAvgHitTotCnt Cnt of wager that hit max/Avg%Rule
                    #sample record get from ( SF_Wager_ArberRuleSoc/BB_sprd20.csv)
                    while HitCnt < RealMaxAvgHitTotCnt:
                        Wager_RealSocBB["WagerNo"] = wagerno_str
                        Wager_RealSocBB["WagerID"] = wagerno_str
                        NewDateNewSec = str(NewCrDate + timedelta(seconds=xSec)) + ".0000000 -04:00" #add 1 sec to each new rec
                        Wager_RealSocBB["CreatedDate"] = NewDateNewSec
                        Wager_RealSocBB["EventDate"] = NewDateNewSec
                        Wager_RealSocBB['StakeOdds'] = stakeodds[0]
                        xSec += 1
                        HitCnt += 1
                        wagerno_str += 1
                        csv_writer.writerow(Wager_RealSocBB)
                        #HitCntWritten +=1
                        TotWagerWritten += 1

                    #dynamic wager variable -loop to gen RealMaxAvgNoHitTotCnt Cnt of wager that did NOT hit maxAvg%Rule
                    #use either option A OR B. both are working,depends on ur need


                    #  denominator option A (No HitMaxAvgRule cox  stakeodds not > #% of spread of Max/Avg)
                    # sample record get from ( SF_Wager_ArberRuleSoc/BB_sprd20.csv)
                    while NoHitCnt < RealMaxAvgNoHitTotCnt:
                        Wager_RealSocBB["WagerNo"] = wagerno_str
                        Wager_RealSocBB["WagerID"] = wagerno_str
                        NewDateNewSec = str(NewCrDate + timedelta(seconds=xSec)) + ".0000000 -04:00"
                        Wager_RealSocBB["CreatedDate"] = NewDateNewSec
                        Wager_RealSocBB["EventDate"] = NewDateNewSec
                        Wager_RealSocBB['StakeOdds'] = stakeodds[1]
                        xSec += 1
                        NoHitCnt += 1
                        wagerno_str += 1
                        csv_writer.writerow(Wager_RealSocBB)
                        TotWagerWritten += 1
                    '''
                    # denominator option B (No HitMaxAvgRule cox BetType is OddEven.now only AHOU use in MAxAvgRule) (GBCRQ-397)
                    # sample record get from ( SF_Wager_ArberRuleSoc/BB_sprd20_OE.csv)
                    while NoHitCnt < RealMaxAvgNoHitTotCnt:
                        Wager_RealSocBB_OE["WagerNo"] = wagerno_str
                        Wager_RealSocBB_OE["WagerID"] = wagerno_str
                        NewDateNewSec = str(NewCrDate + timedelta(seconds=xSec)) + ".0000000 -04:00"
                        Wager_RealSocBB_OE["CreatedDate"] = NewDateNewSec
                        Wager_RealSocBB_OE["EventDate"] = NewDateNewSec
                        Wager_RealSocBB_OE['StakeOdds'] = stakeodds[0]
                        xSec += 1
                        NoHitCnt += 1
                        wagerno_str += 1
                        csv_writer.writerow(Wager_RealSocBB_OE)
                        TotWagerWritten += 1   '''

                    OverallMax20Rule = round(HitCnt / (HitCnt + NoHitCnt) * 100, 2)
                    if Rule == 'Soc':
                        TotRealWagerSoc = HitCnt + NoHitCnt
                        Max20MsgSoc = f'Max20Exp%({HitCnt}/{NoHitCnt}=>{OverallMax20Rule})'
                    elif Rule == 'BB':
                        TotRealWagerBB = HitCnt + NoHitCnt
                        Max20MsgBB = f'Max20Exp%({HitCnt}/{NoHitCnt}=>{OverallMax20Rule})'


                # dynamic wager variable -loop to gen OtherSport Cnt of wager to use in RealSoc/BB Exp% computation
                while OthrSportCnt < TotOthrSportTT:
                    Wager_OtherSport["WagerNo"] = wagerno_str
                    Wager_OtherSport["WagerID"] = wagerno_str
                    NewDateNewSec = str(NewCrDate + timedelta(seconds=xSec)) + ".0000000 -04:00"
                    Wager_OtherSport["CreatedDate"] = NewDateNewSec
                    Wager_OtherSport["EventDate"] = NewDateNewSec
                    xSec += 1
                    OthrSportCnt += 1
                    wagerno_str += 1
                    csv_writer.writerow(Wager_OtherSport)
                    #OthrSportCntWritten +=1
                    TotWagerWritten += 1

                if mem[7] == "Soc":
                    RealSportExp_Soc = round(TotRealWagerSoc/ TotWagerWritten * 100, 2)
                    printMsg_RealExp_Soc = f'Exp%({RealSportExp_Soc})'
                if mem[10] == "BB":
                    RealSportExp_BB = round(TotRealWagerBB / TotWagerWritten * 100, 2)
                    printMsg_RealExp_BB = f'Exp%({RealSportExp_BB})'


                #OverallMax20Rule = round(  HitCntWritten/(HitCntWritten + NoHitCntWritten) *100  ,  2)
                print(f'{mem[3]}({TotWagerWritten})  - RealSport({TotRealWagerSoc + TotRealWagerBB }),TT({OthrSportCnt}) => \
RealSoc : {printMsg_RealExp_Soc} {Max20MsgSoc} ,RealBB : {printMsg_RealExp_BB} {Max20MsgBB}')

                WrittenItem +=1
        print(f'last wagerno printed is {wagerno_str-1}')
    return WrittenItem


def get_oddsStake(wagerrule):
    global errorFlag
    #ie. Max20%= 0.90 will hit max20%, 0.88% will not hit max20%
    #    Max50%= 0.96 will hit max50%(including 20,30,40), 0.94% will not hit max50%(but will still hit 20,30,40)
    #refer ur tc scenario for details explanation
    marketmaxDict = {
        "20%": [0.90, 0.88],
        "30%": [0.92, 0.90],
        "40%": [0.94, 0.92],
        "50%": [0.96, 0.94],
        "Max": [0.88, 0.82],
        "BelowMax":[0.84,0.84]    #this belowMAx havent tested yet
    }
    marketaveDict = {
        "20%": [0.88, 0.87],
        "30%": [0.90, 0.89],
        "40%": [0.92, 0.91],
        "50%": [0.94, 0.93],
        "Ave": [0.85, 0.83],
        "BelowAve": [0.83, 0.83] #this belowAve havent tested yet
    }
    if wagerrule[0] == 'Max' and (wagerrule[1] == '20%' or  wagerrule[1] == '30%' or wagerrule[1] == '40%' or wagerrule[1] == '50%' or wagerrule[1] == 'Max' or wagerrule[1] == 'BelowMax'):
        return marketmaxDict[wagerrule[1]]
    elif wagerrule[0] == 'Ave' and (wagerrule[1] == '20%' or  wagerrule[1] == '30%' or wagerrule[1] == '40%' or wagerrule[1] == '50%' or wagerrule[1] == 'Ave' or wagerrule[1] == 'BelowAve'):
        return marketaveDict[wagerrule[1]]
    else:
        errorFlag = 1
        print(f'ERROR ==> Invalid rule:  {wagerrule}, please check!')
        return [0.0,0.0]



def gen_AdditonalRealCnt(var_HighLower,var_newMaxPerc,var_existingRealHitMAxCnt,var_existingTotalRealCnt):
    global errorFlag
    if var_HighLower == 'L':
        NewTotRealCnt = math.floor(100 / var_newMaxPerc * var_existingRealHitMAxCnt)  #round down
        AdditionalRealNoHitMaxCnt = NewTotRealCnt - var_existingTotalRealCnt
        return AdditionalRealNoHitMaxCnt
    elif var_HighLower == 'H':
        percToFraction = var_newMaxPerc / 100
        AdditionalRealHITMaxCnt = math.floor(  ((percToFraction * var_existingTotalRealCnt) - var_existingRealHitMAxCnt) / (1-percToFraction)  )
        return AdditionalRealHITMaxCnt
    else:
        errorFlag = 1
        print (f'ERROR==> {var_HighLower} not valid!!!!!!!!')

def modify_memList(var_HighLower,mem_list):
    if var_HighLower == 'L':
        for i in mem_list:
            if i[2] == 'Soc':
                i[3] = 100
                i[4] = 0
            if i[5] == 'BB':
                i[6] = 100
                i[7] = 0
    elif var_HighLower == 'H':
        for i in mem_list:
            if i[2] == 'Soc':
                i[3] = 100
                i[4] = 100
            if i[5] == 'BB':
                i[6] = 100
                i[7] = 100

## call this backup function in case get_mem(mem_list) not working due to db issue
## the only thing to change b4 calling this is, pass in companyid instead of coyname in mem_list
def get_mem_api(mem_list):
    url = "https://api.qat.fraudsterkill.com/api/MemberSetting/GetMemberList"
    headers = {
        "Authorization": "Bearer eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9.eyJ1c2VyIjp7Im5hbWUiOiJhZG1pbi5xYTMifSwicGVybWlzc2lvbnMiOlszLDExLDEyLDE1LDE2LDE3LDE5LDIwLDIxLDIyLDIzLDI0LDI1LDI4LDI5LDMwLDMxLDMyLDMzLDM0LDM1LDM2LDM3LDM5LDQwLDQxLDQyLDQzLDQ0LDQ1LDQ2LDQ3LDQ4LDQ5LDUwLDUxLDUyLDUzLDYwLDYxLDYyLDYzLDY0LDY1LDY2LDY3LDY4LDY5LDczLDc0LDc1LDc2LDc3LDc4LDc5LDgwLDgxLDgyLDgzLDg0LDg1LDg2LDg3LDg4LDg5LDkzLDk0LDk1LDk3LDk4LDk5LDEwMCwxMDEsMTAyLDEwMywxMDQsMTA1LDEwNiwxMDcsMTA4LDEwOSwxMTAsMTExLDExMiwxMTMsMTE0LDExNSwxMTYsMTE3LDExOCwxMjAsMTIxLDEyMiwxMjMsMTI0LDEyNSwxMjYsMTI3LDEyOCwxMjksMTMwLDEzMSwxMzIsMTMzLDEzNCwxMzUsMTM2LDEzNywxMzksMTQwLDE0MSwxNDIsMTQzLDE0NCwxNDUsMTQ2LDE0NywxNDgsMTQ5LDE1MCwxNTEsMTUyLDE1MywxNTQsMTU1LDE1NiwxNTgsMTU5LDE2MCwxNjcsMTY4LDE2OSwxNzAsMTcxLDE3MiwxNzMsMTc0LDE3NSwxNzYsMTc4LDE3OSwxODAsMTgxLDE4MiwxODMsMTg0LDE4NSwxODYsMTg3LDE4OCwxODksMTkwLDE5MSwxOTIsMTkzLDE5NCwxOTUsMTk2LDE5NywxOTgsMTk5LDIwMCwyMDEsMjAyLDIwMywyMDQsMjA1LDIwNiwyMDcsMjA4LDIwOSwyMTAsMjExLDIxMiwyMTMsMjE0LDIxNSwyMTksMjIwLDIyMSwyMjIsMjIzLDIyNCwyMjUsMjI2LDIyNywxLDIsOSwxMCwyNiwyNyw5MCwxNTcsMTc3XSwiaWF0IjoxNzM2ODE5MjM0LCJleHAiOjE3Mzc0MjQwMzR9.6C38ZAY-cEOuyYZ_YSm_9rFUYq3pmi15KBDF9WfD8ao",
        # Example: Authorization token
        "Content-Type": "application/json",  # Specify that the body is in JSON format
        "Connection": "keep-alive"  # Example of a custom header
    }
    output_list = []
    for mem in mem_list:
        data = {"dateType":4,"dateFrom":"2025-01-14","dateTo":"2025-01-15","companyIDs":[mem[0]],"memberCodes":[mem[1]],"memberFirstSourceIDs":[], \
             "currencyCodes":[],"sortBy":"TotalHitCriteria","memberActions":[],"memberActionStatusIDs":[],"byGBFilter":True,"memberStatusIDs":[],\
             "isHousePlayerIDs":[],"memberSettingProfileIDs":[],"spreadGroupIDs":[],"memberCategoryIDs":[],"isAdvisedIDs":[],"profileGroupIDs":[],\
             "isProfileGroupNull":False,"isManualRevised":None,"isNotOverrideBySystem":[],"updatedBy":"","updatedDateFrom":"0001-01-01",\
             "updatedDateTo":"0001-01-01","byGBFeature":False,"dayRange":"7D","bySetting":None,"byOperand":None,"timezone":-4,"minMemberScore":None,\
             "gbRuleIDs":[],"page":1,"pageSize":100}


    # Send a POST request with data
        response = requests.post(url,headers=headers, json=data)
        apiresp = response.json()
        apiresp_data = apiresp['data'][0]
        #print(apiresp_data['companyID'])
        x = [apiresp_data['companyID'],apiresp_data['companyName'],apiresp_data['memberID'],apiresp_data['memberCode'],apiresp_data['sfMemberCategoryName'],apiresp_data['sfMemberCategoryName'],apiresp_data['sfMemberCategoryID'],mem[2],mem[3],mem[4],mem[5],mem[6],mem[7]]
        output_list.append(list(x))

    return output_list


def get_mem(list_mem):     #to query mysql to get memDetails, \'is to escape '
    query_p2 = ""
    for index,x in enumerate(list_mem):  #index is 1st dimension
        temp_qy = f'select \'{x[0]}\' as coy, \'{x[1]}\' as mem, \'{x[2]}\' as RuleSoc, \
{x[3]} as ExpPerctgSoc , {x[4]} as Max20PerctgSoc, \'{x[5]}\' as RuleBB, {x[6]} as ExpPerctgBB , {x[7]} as Max20PerctgBB'

        if index != len(list_mem) - 1 :  #need add union all to all except the last line
            temp_qy = temp_qy + f' union all\n'
        query_p2 = query_p2 + temp_qy

    query_p1 = "with get_member as (\n "
    query_p3 = ")\n \
    SELECT  companyID,companyName,memberid,membercode, enu.name,enu.displayname, enu.enumID, um.RuleSoc,um.ExpPerctgSoc,um.Max20PerctgSoc,\n \
    um.RuleBB,um.ExpPerctgBB,um.Max20PerctgBB \n \
    FROM GB_Qat.members m\n \
    inner join GB_Qat.displaynameenum  enu\n \
    on m.sfMemberCategoryID = enu.enumid\n \
    inner join get_member um\n \
    on um.mem = m.membercode and um.coy = m.companyname\n \
    where enu.enumName= 'MemberCategoryEnum'"

    query_stmt = query_p1 + query_p2 + query_p3
    #print(query_stmt)

    mydb = mysql.connector.connect(
        host='35.229.171.142',
        user='qat_readonly',
        password='NTZ6Wt3tzqCp4k7v',
        port=3306,
        database='GB_Qat' #!!this is DATABASEname(GB_Qat) in mysql , not the connectionName on mysql workbench....
    )

    mycursor = mydb.cursor()

    mycursor.execute(query_stmt)

    myresult = mycursor.fetchall()

    output_list = []
    for x in myresult:
        output_list.append(list(x))
    return output_list



var_inp_file_Soc = 'C:/Users/lim.miin/OneDrive - Morpheus Consulting Pte Ltd/Desktop/testing/base file ETL/SF_Wager_ArberRuleSoc_sprd20.csv'
var_inp_file_Soc_OE = 'C:/Users/lim.miin/OneDrive - Morpheus Consulting Pte Ltd/Desktop/testing/base file ETL/SF_Wager_ArberRuleSoc_sprd20_OE.csv'
var_inp_file_BB = 'C:/Users/lim.miin/OneDrive - Morpheus Consulting Pte Ltd/Desktop/testing/base file ETL/SF_Wager_ArberRuleBB_sprd20.csv'
var_inp_file_BB_OE = 'C:/Users/lim.miin/OneDrive - Morpheus Consulting Pte Ltd/Desktop/testing/base file ETL/SF_Wager_ArberRuleBB_sprd20_OE.csv'
var_inp_file_TT = 'C:/Users/lim.miin/OneDrive - Morpheus Consulting Pte Ltd/Desktop/testing/base file ETL/SF_Wager_ArberRuleTT.csv'

#########################~ONLY EDIT FIELDS BELOW:--~###########################
var_out_file = 'C:/Users/lim.miin/OneDrive - Morpheus Consulting Pte Ltd/Desktop/try ELT files/20250414run(twm)/SF_Wager_20250414xxdelete.csv'
var_ruleSoc = ['Max','20%'] #MUST FOLLOW general setting, else will get wrong outcome   [Max/Ave , 20%/30%/40%/50%/Max/Ave/BelowMax/BelowAve]
var_ruleBB =  ['Ave','20%'] #MUST FOLLOW general setting, else will get wrong outcome   [Max/Ave , 20%/30%/40%/50%/Max/Ave/BelowMax/BelowAve]
var_wagerno = 1261982      #provide wagerNo to start from
var_RealHitMaxAvgCnt = 25  #fixed, this is RealCnt that hit Max/AvgHitCnt(single,AHOU). it is also used as min WagerCnt.min mz tally with GeneralSetting
var_ELTDate = '20250413' #which ELTdate u will run the ETL (flexible, no need wait on ELT date to gen data)
var_computeNewORChangeScore = 'New'  # 'New' for new member, 'Chg' for existing member to test score change

### Edit BELOW only if var_computeNewORChangeScore = 'Chg' ,else ignore      ####
#for chg , dun use odd/even for nohit, got bug...[affectedlist wont pick up if not AH bets..]
var_HighLower = 'L'  # 'H'=to gen higher score/MAxpercentage,  'L'=  to gen lower score
var_newMaxPerc = 40 # New percentage/score u wanna gen(try with lowest range # 30,40,50, count urself aft get result, then slowly increase 31,32,..)
var_existingRealHitMAxCnt = 22   #mem's existing count of Real that HIT20/30/40/50Max/Ave
var_existingTotalRealCnt = 36   #mem's existing count of RealCnt(hit + no hit ,in respect to MaxAvg% formula)(get from ur bq sql)

#input mem[coyname,memcode,ArberRealSportType,RealSportExp%, OverallMax20%(scoreband)]
#Mem with BOTH Real "Soc" & "BB",
#      only 2 combo Exp% can be processed : (jz randomly hardcoded, jz in case need same member to hit both sport,u can use this]
#      ["Soc",100,46,"BB",100,53] where mem hit SocScore=40(46%),Exp=50% & BBScore=50(53%,)Exp=50%  & vice versa
#Mem with ONLY 1 Real sport, either "Soc"  OR  "BB", you are free to input any RealSportExp% and OverallMaxAve20% value
#to test scoreChange, input Soc or BB enuf, no need bother RealSportExp% & OverallMax/Ave20%
mem_list = [
["SfMiniIGPTW2","arber0455","Soc",100,46,"BB",100,53],
["SfMiniIGPTW2","arber0466","Soc",100,100,"",-1,-1],
["SfMiniIGPTW2","arber0467","Soc",100,100,"",-1,-1],
["SfMiniIGPTW2","arber0468","",-1,-1,"BB",100,100],
["SfMiniIGPTW2","arber0469","",-1,-1,"BB",100,100],
["SfMiniIGPTW2","arber0470","",-1,-1,"BB",100,100],
["SfMiniIGPTW2","arber0471","Soc",100,100,"",-1,-1],
["SfMiniIGPTW2","arber0472","Soc",100,100,"",-1,-1],
["SfMiniIGPTW2","arber0473","",-1,-1,"BB",100,100],
["SfMiniIGPTW2","arber0474","",-1,-1,"BB",100,100]
    ]

#check if using all bettype or ou/ou only
mem_listxxx = [
["SfMiniIGPTW2","arber0444","Soc",80,60,"",-1,-1],
["SfMiniIGPTW2","arber0445","",-1,-1,"BB",80,60],
["SfMiniIGPTW2","arber0446","Soc",80,60,"",-1,-1],
["SfMiniIGPTW2","arber0447","",-1,-1,"BB",80,60],
["SfMiniIGPTW2","arber0359","Soc",44,40,"BB",38,40]
]

#Remarks:
#for mem with both RealSoc & RealBB:
# 30/(30 +26 + 11) = 44%:
# 30=>harcoded cnt of RealSport1, 26=>cnt of another RealSport2, 11=>cnt of NonSocBbRealSport
# 26/(30 +26 + 11) = 38%:
# 26=>harcoded cnt of RealSport1, 26=>cnt of another RealSport2, 11=>cnt of NonSocBbRealSport
# 25/(25 +25 +5) = 45%
# 25=>harcoded cnt of RealSport, 25=>cnt of another RealSport, 5=>cnt of NonSocBbRealSport
#for mem with either RealSoc || RealBB:
# totRealWagers 25 are fixed/hardcoded , system will gen record based on the % u requested, and
#      some logic has been modified a bit to prevent smaller %. so when u provided 50%, system might give 52%
#########################~END of EDIT part~###########################

var_HighLowerFlag = ''
var_Chg_AdditionalCnt= 0
if var_computeNewORChangeScore == 'Chg':
    var_HighLowerFlag=var_HighLower
    AdditionalRealCnt = gen_AdditonalRealCnt(var_HighLower,var_newMaxPerc,var_existingRealHitMAxCnt,var_existingTotalRealCnt)
    var_Chg_AdditionalCnt = AdditionalRealCnt  #replace the existing RealCnt before calling main function for computation
    modify_memList(var_HighLower,mem_list)

#[[coyid,coynam,memid,memcode,memcatcode,memcatnam,memcatid,socrule,xp,max,bbruke.xp,max],[],[]]
var_mem_list = get_mem(mem_list)
errorFlag = 0   #define outside function, then inside function define this var as global
WrittenItem = output_SF_Wager(var_inp_file_Soc,var_inp_file_Soc_OE,var_inp_file_BB,var_inp_file_BB_OE,var_inp_file_TT,
                              var_out_file,var_mem_list,var_ELTDate,var_wagerno,var_RealHitMaxAvgCnt,var_ruleSoc,var_ruleBB,
                              var_Chg_AdditionalCnt,var_HighLowerFlag)

if errorFlag == 1:
    print("there is ERRORR, pls check all printed error")
else:
    print(
        f'Total items return from MYSQL == {len(var_mem_list)} ,requested items =={len(mem_list)} , processed Item== {WrittenItem}.make sure they are same. ')

