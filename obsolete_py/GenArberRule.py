import mysql.connector
import csv
from datetime import datetime, timedelta
import math


def get_count(inp_score, inp_exp, p_minWagerhitMrkt_cnt):
    nohit_mrkt_cnt = (p_minWagerhitMrkt_cnt / (inp_score / 100)) - p_minWagerhitMrkt_cnt
    # sometimes it yields count with decimal number. so system must convert it to count in whole number, either by rounding up or rounding down
    # system recalculate score using count after rounding up & rounding down , & pick among the two that actually fullfil the Score wanted
    if p_minWagerhitMrkt_cnt / (p_minWagerhitMrkt_cnt + math.floor(nohit_mrkt_cnt)) * 100 >= inp_score:
        nohit_mrkt_cnt = math.floor(nohit_mrkt_cnt)
    else:
        nohit_mrkt_cnt = math.ceil(nohit_mrkt_cnt)

    otr_cnt = ((p_minWagerhitMrkt_cnt + nohit_mrkt_cnt) / (inp_exp / 100)) - p_minWagerhitMrkt_cnt - nohit_mrkt_cnt
    if ((p_minWagerhitMrkt_cnt + nohit_mrkt_cnt) / (
            p_minWagerhitMrkt_cnt + nohit_mrkt_cnt + math.floor(otr_cnt))) * 100 >= inp_score:
        otr_cnt = math.floor(otr_cnt)
    else:
        otr_cnt = math.ceil(otr_cnt)

    return nohit_mrkt_cnt, otr_cnt


def get_new_Score_Exp(p_socRealcnt_Hit, p_socRealcnt_NoHit, p_othcnt_Sport):
    new_score = (p_socRealcnt_Hit / (p_socRealcnt_Hit + p_socRealcnt_NoHit)) * 100
    new_exposure = ((p_socRealcnt_Hit + p_socRealcnt_NoHit) / (p_socRealcnt_Hit + p_socRealcnt_NoHit + p_othcnt_Sport)) * 100
    return round(new_score,2), round(new_exposure,2)


def gen_AdditonalRealCnt(p_socScore, p_old_score, p_old_realHitcnt, p_old_realcnt):
    if p_socScore <= p_old_score:  # reduce score
        NewTotRealCnt = 100 / p_socScore * p_old_realHitcnt  # round down
        AdditionalRealNoHitCnt = NewTotRealCnt - p_old_realcnt
        # sometimes it yields count with decimal number. so system must convert it to count in whole number, either by rounding up or rounding down
        # system recalculate score using count after rounding up & rounding down , & pick among the two that actually fullfil the Score wanted
        if (p_old_realHitcnt) / (p_old_realcnt + math.floor(AdditionalRealNoHitCnt)) * 100 >= p_socScore:
            AdditionalRealNoHitCnt = math.floor(AdditionalRealNoHitCnt)
        else:
            AdditionalRealNoHitCnt = math.ceil(AdditionalRealNoHitCnt)
        return AdditionalRealNoHitCnt
    else:  # increase score
        percToFraction = p_socScore / 100
        AdditionalRealHITMaxCnt = ((percToFraction * p_old_realcnt) - p_old_realHitcnt) / (1 - percToFraction)
        if ((p_old_realHitcnt + math.floor(AdditionalRealHITMaxCnt)) / (
                p_old_realcnt + math.floor(AdditionalRealHITMaxCnt))) * 100 >= p_socScore:
            AdditionalRealHITMaxCnt = math.floor(AdditionalRealHITMaxCnt)
        else:
            AdditionalRealHITMaxCnt = math.ceil(AdditionalRealHITMaxCnt)
        return AdditionalRealHITMaxCnt


def get_hit_nohit_othr_count(row, score_field, exp_field, old_score_field, old_realHitcnt_field, old_realcnt_field
                      ,out_Realcnt):
    if row['socScore'] and row['bbScore']: #hardcode all the value if row has both bb & soc
        if row['socScore'] == '46' and row['bbScore'] == '53':
           row['bbRealcnt_Hit'] = 30
           row['bbRealcnt_NoHit'], row['othcnt_Sport'] = get_count(int(row['bbScore']), 100, int(row['bbRealcnt_Hit']))
           row['socRealcnt_Hit'] = 26
           row['socRealcnt_NoHit'], row['othcnt_Sport'] = get_count(int(row['socScore']), 100, int(row['socRealcnt_Hit']))
        elif row['socScore'] == '53' and row['bbScore'] == '46':
            row['bbRealcnt_Hit'] = 26
            row['bbRealcnt_NoHit'], row['othcnt_Sport'] = get_count(int(row['bbScore']), 100, int(row['bbRealcnt_Hit']))
            row['socRealcnt_Hit'] = 30
            row['socRealcnt_NoHit'], row['othcnt_Sport'] = get_count(int(row['socScore']), 100, int(row['socRealcnt_Hit']))
        elif row['socScore'] == '44' and row['bbScore'] == '55':  #gen less wagers
            row['bbRealcnt_Hit'] = 14
            row['bbRealcnt_NoHit'], row['othcnt_Sport'] = get_count(int(row['bbScore']), 100, int(row['bbRealcnt_Hit']))
            row['socRealcnt_Hit'] = 11
            row['socRealcnt_NoHit'], row['othcnt_Sport'] = get_count(int(row['socScore']), 100, int(row['socRealcnt_Hit']))
        elif row['socScore'] == '55' and row['bbScore'] == '44':
            row['bbRealcnt_Hit'] = 11
            row['bbRealcnt_NoHit'], row['othcnt_Sport'] = get_count(int(row['bbScore']), 100, int(row['bbRealcnt_Hit']))
            row['socRealcnt_Hit'] = 14
            row['socRealcnt_NoHit'], row['othcnt_Sport'] = get_count(int(row['socScore']), 100, int(row['socRealcnt_Hit']))
        return row

    # Extract the relevant fields
    score = int(row[score_field])
    exp = int(row[exp_field]) if row[exp_field] else 0
    old_score = int(row[old_score_field]) if row.get(old_score_field) else None
    old_realHitcnt = int(row[old_realHitcnt_field]) if row.get(old_realHitcnt_field) else 0
    old_realcnt = int(row[old_realcnt_field]) if row.get(old_realcnt_field) else 0

    # Handle lower or higher score based on old score
    if old_score and score <= old_score:  # reduce score
        row[f'{out_Realcnt}_NoHit'] = gen_AdditonalRealCnt(score, old_score, old_realHitcnt, old_realcnt)
    elif old_score and score > old_score:  # increase score
        row[f'{out_Realcnt}_Hit'] = gen_AdditonalRealCnt(score, old_score, old_realHitcnt, old_realcnt)
    else:  # 1st time gen score (no previous score)
        minWagerhitMrkt_cnt = int(row['minWagerhitMrkt_cnt'])
        row[f'{out_Realcnt}_Hit'] = minWagerhitMrkt_cnt
        row[f'{out_Realcnt}_NoHit'], row['othcnt_Sport'] = get_count(score, exp, minWagerhitMrkt_cnt)

    return row


def output_jmx_inpfile(var_inp_members, var_out_jmx):  # to gen the SF_Wager_yyyymmdd.csv file
    line_count = 0


    try:
        with (open(var_inp_members, 'r') as mem_file):
            with open(var_out_jmx, mode='w', newline='') as jmx_mem_file:
                csv_reader_mem_file = csv.DictReader(mem_file)
                csv_writer_jmx_mem_file = csv.DictWriter(jmx_mem_file, csv_reader_mem_file.fieldnames, delimiter=',')
                csv_writer_jmx_mem_file.writeheader()

                for row in csv_reader_mem_file:
                    if row["member"] == "":
                        print(f'since empty line met, processing end here')
                        break

                    # Default values for 'Hit', 'NoHit' and 'othcnt_Sport'
                    row['socRealcnt_Hit'], row['socRealcnt_NoHit'], row['bbRealcnt_Hit'], row['bbRealcnt_NoHit'], row[
                        'othcnt_Sport'] = 0, 0, 0, 0, 0


                    # Handle row with both `socScore` and `bbScore`
                    if (row['socScore'] and row['bbScore']):
                        if (row['socScore'] == '53' and row['bbScore'] == '46') or (row['socScore'] == '46' and row['bbScore'] == '53') or\
                            (row['socScore'] == '55' and row['bbScore'] == '44') or (row['socScore'] == '44' and row['bbScore'] == '55'):
                            score = 'both   '
                            exposure = ''
                            cnt = 'socRealcnt' #able to display only 1 sport, so i just pick soc.it wont affect wagercnt as value are all hardcoded
                        else:
                            print('===ERROR=====!!! only 2 combo of soc/bb score is supported if row has both bb & soc score.please check the combo value')
                            break
                    # Handle row with either `socScore` or `bbScore`
                    elif (row['socScore'] and row['socExp']) or\
                        (row['socScore'] and row['old_score'] and row['old_realHitcnt']and row['old_realcnt'] and row['old_othcnt']) :
                        score = 'socScore'
                        exposure = 'socExp'
                        cnt = 'socRealcnt'
                    elif (row['bbScore'] and row['bbExp']) or \
                            (row['bbScore'] and row['old_score'] and row['old_realHitcnt']and row['old_realcnt'] and row['old_othcnt']) :
                        score = 'bbScore'
                        exposure = 'bbExp'
                        cnt = 'bbRealcnt'
                    else:
                        print('ERROR!!! value in csv is missing or not valid.')
                        break

                    row = get_hit_nohit_othr_count(row, score, exposure, 'old_score', 'old_realHitcnt', 'old_realcnt'
                                                ,cnt)

                    # Calculate the new score and exposure based on updated values
                    othcnt_Sport = (int(row['othcnt_Sport'])) + (int(row['old_othcnt']) if row['old_othcnt'] else 0)
                    Realcnt_Hit = (int(row[f'{cnt}_Hit'])) + (int(row['old_realHitcnt']) if row['old_realHitcnt'] else 0)
                    Realcnt_NoHit = (int(row[f'{cnt}_NoHit'])) + (
                                (int(row['old_realcnt']) if row['old_realcnt'] else 0) -
                                (int(row['old_realHitcnt']) if row['old_realHitcnt'] else 0) )
                    row['new_Score'], row['new_Exp'] = get_new_Score_Exp(Realcnt_Hit, Realcnt_NoHit, othcnt_Sport)
                    # Write the row to the output file
                    csv_writer_jmx_mem_file.writerow(row)
                    newORchg = 'chg' if row['old_score'] else 'NEW'
                    print(
                        f'{row['member']}[{newORchg} {score}]\t oth_spor==>{row['othcnt_Sport']}\t, ||RealSoc=> sochitCnt: {row["socRealcnt_Hit"]}, socNohitCnt: {row["socRealcnt_NoHit"]},\
||Realbb=> bbhitCnt: {row["bbRealcnt_Hit"]}, bbNohitCnt: {row["bbRealcnt_NoHit"]},  ||New=> newScore: {row["new_Score"]}, newExposure: {row["new_Exp"]}')
                    line_count += 1

                print(f'Total of {line_count} records have been updated in the file.')

    except FileNotFoundError as e:
        print(f"File not found: {e}")
    #except Exception as e:
    #    print(f"An error occurred: {e}")


# Input and output paths
var_inp_members = "C:/Users/lim.miin/OneDrive - Morpheus Consulting Pte Ltd/Desktop/jm/Arber/Arber member -python input.csv"
var_out_jmx = "C:/Users/lim.miin/OneDrive - Morpheus Consulting Pte Ltd/Desktop/jm/Arber//Arber member -jmeter.csv"
#min_hitMrkt_cnt = 19  ##this value is fixed, >= generalsetting, to satisfy minWagercnt metrics of ArberRule
output_jmx_inpfile(var_inp_members, var_out_jmx)


