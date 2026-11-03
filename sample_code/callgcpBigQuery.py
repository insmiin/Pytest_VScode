from google.cloud import bigquery
from google.oauth2 import service_account

# Path to your service account key file
key_path = "C:/Users/LimMiin/OneDrive - Morpheus Consulting Pte Ltd/Desktop/testing/py-gcpBQ/carbon-sensor-259109-d37561cb1a02.json"

# Create a credentials object
credentials = service_account.Credentials.from_service_account_file(key_path)

# Instantiate the BigQuery client with the credentials
client = bigquery.Client(credentials=credentials, project=credentials.project_id)

# Query example
query = '''
DECLARE p_datefrom TIMESTAMP DEFAULT "2024-11-01 04:00:00";
DECLARE p_dateto   TIMESTAMP DEFAULT "2025-02-21 04:00:00";
DECLARE SocPct STRING DEFAULT "AboveMarket";
DECLARE socRule STRING DEFAULT "Avg";
DECLARE BBPct STRING DEFAULT "20PCT";
DECLARE BBRule STRING DEFAULT "AvgRule";
DECLARE p_SocRule STRING;
DECLARE p_BBRule STRING;
set p_SocRule = concat("Soccer_",SocPct,"_",socRule);
set p_BBRule = concat("BB_",BBPct,"_",BBRule);
--remember to escape any % within the executeimmediate formate string. escape with % even for commentOut statement
EXECUTE IMMEDIATE format("""
with RealWagerCovered as
(
SELECT w.memberid,w.membercode,w.companyid,potentialexposureamount,exchangerate,period,%s as SocRule,%s as BBrule ,sportid,BetTypeName --@@
FROM `ghostbuster-dev.RAW.SF_Wager_Derived` wd
inner join ghostbuster-dev.RAW.SF_Wager w
on wd.memberid = w.memberid and wd.wagerno = w.wagerno
inner join ghostbuster-dev.RAW.SF_Member m
on m.memberid = w.memberid and m.companyid = w.companyid
WHERE 1=1
and wagertypeid = 1
and sportid in(1,2)
--and BetTypeName in ("Handicap","Over / Under")
and lower(competitionname) not like "vs -%%" and lower(competitionname) not like "es -%%"
and w.eventdate >= @datefrom and w.eventdate < @dateto
),
RealWagerCovered_Exp as  --Amt use in RealBB/SocExp%% numerator/UPPER, RealSportSocAHOUcnt use as minCount to hit Arber criteria
(select membercode,memberid,companyid,sportid,sum(potentialexposureamount*exchangerate) as RealSportTotExp,
countif(BetTypeName in ("Handicap","Over / Under"))  as RealSportAHOUcnt
from RealWagerCovered
group by membercode,memberid,companyid,sportid
),
AllWagerTbl as  --For RealBB/SocExp%% denominator/bottom
(SELECT w.memberid,w.membercode,w.companyid , sum(potentialexposureamount*exchangerate) as AllWagersTotExp
FROM `ghostbuster-dev.RAW.SF_Wager_Derived` wd
inner join ghostbuster-dev.RAW.SF_Wager w
on wd.memberid = w.memberid and wd.wagerno = w.wagerno
inner join ghostbuster-dev.RAW.SF_Member m
on m.memberid = w.memberid and m.companyid = w.companyid
where w.eventdate >= @datefrom and w.eventdate < @dateto
group by w.memberid,w.membercode,w.companyid
),
MaxAvg_TotExpTbl as
(select membercode,memberid,companyid,sportid,sum(potentialexposureamount*exchangerate) as HitMaxAvg_TotExp,count(*) as HitMaxAvg_TotCnt
from RealWagerCovered
where 1=1
and BetTypeName in ("Handicap","Over / Under")
and (
     (sportid = 1 and period in ("1H","FT") and SocRule is true)  --@@
     or(sportid = 2 and period in ("1H","FT","1Q","3Q") and BBRule is true)
     )  --@@
group by membercode,memberid,companyid,sportid
)
select a.membercode,a.memberid,a.companyid,a.sportid,am.HitMaxAvg_TotExp,am.HitMaxAvg_TotCnt,a.RealSportTotExp, AllWagersTotExp, ieee_divide(RealSportTotExp,AllWagersTotExp)*100 as RealSportExp_perc,
ieee_divide(HitMaxAvg_TotExp,RealSportTotExp)*100 as MaxAvgRule_Scoreband
from RealWagerCovered_Exp a
inner join MaxAvg_TotExpTbl am
on a.memberid = am.memberid and a.companyid = am.companyid and a.sportid = am.sportid and a.membercode = am.membercode
inner join AllWagerTbl wall
on a.memberid = wall.memberid and a.companyid = wall.companyid and a.membercode = wall.membercode
and RealSportAHOUcnt >=20
order by am.membercode
""",p_socRule,p_BBRule)
USING p_datefrom as datefrom,p_dateto as dateto;
'''
query_job = client.query(query)

# Fetch and print the results
results = query_job.result()
print('query_job=',query_job.job_id)
print('job=',query_job.result())
for row in results:
    print(row)