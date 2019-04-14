import mysql.connector
import os
import datetime

mydb = mysql.connector.connect(
        host = 'localhost',
        user = 'bakalaurs',
        passwd = 'bakalaurs',
        database = 'bakalaurs'
    )

lesson_check_cursor = mydb.cursor()
sql_query = "SELECT nodarbibas_id, kursa_numurs, telpa, datums, sakuma_laiks, beigu_laiks FROM bakalaurs.nodarbibas WHERE datums = %s AND %s BETWEEN SUBTIME(sakuma_laiks, '0:10:0.000000') AND beigu_laiks AND telpa = %s"
current_date = datetime.datetime.now().strftime("%Y-%m-%d")
current_time = datetime.datetime.now().strftime("%H:%M:%S")
print("[TEST] Current time and date, auditorium:", str(current_date), str(current_time), "303")
values = (current_date, current_time, "303")

lesson_check_cursor.execute(sql_query, values)
print("[TEST] Last query:", lesson_check_cursor.statement)
myresult = lesson_check_cursor.fetchall()
print('[MYSQL] Lessons found:', lesson_check_cursor.rowcount)

for x in myresult:
    print(x)

""" if lesson_check_cursor.rowcount > 0:
    print("[MYSQL] Current lesson: %s, %s, %s, %s, %s, %s" % (nodarbibas_id, kursa_numurs, telpa, datums, sakuma_laiks, beigu_laiks))
else:
    print("[MYSQL] No lesson found!") """

mydb.close()