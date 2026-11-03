import pymysql

conn = pymysql.connect(
    host="10.127.10.4",
    port=3306,
    user="sfqat_superadmin_qa",
    password="YOUR_MYSQL_PASSWORD",
    database="GB_Qat",
    connect_timeout=10
)

cursor = conn.cursor()
cursor.execute("SELECT NOW()")

print(cursor.fetchone())

conn.close()