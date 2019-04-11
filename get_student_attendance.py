import mysql.connector
from configparser import ConfigParser
import datetime
from tabulate import tabulate

# Config parser
parser = ConfigParser()
#parser.read('config/dev_settings_local.ini') # local
parser.read('./config/dev_settings.ini') # remote LAN

# Gets all info from studentu_uzskaite table
def get_all_attendance_data():
    # MySQL connection
    mydb = mysql.connector.connect(
        host = parser.get('db', 'db_host'),
        user = parser.get('db', 'db_user'),
        passwd = parser.get('db', 'db_passwd'),
        database = parser.get('db', 'db_database')
    )

    query = """SELECT u.id_studentu_uzskaite, s.vards, s.uzvards, u.apliecibas_numurs, u.registracijas_laiks, u.telpas_numurs, n.kursa_nosaukums, u.nodarbibas_id, p.pasniedzeja_vards, p.pasniedzeja_uzvards
                FROM studentu_uzskaite AS u 
                INNER JOIN studenti AS s ON u.apliecibas_numurs = s.apliecibas_numurs
                INNER JOIN macisanas_saraksts AS m ON u.nodarbibas_id = m.nodarbibas_id
                INNER JOIN pasniedzeji AS p ON m.pasniedzeja_id = p.pasniedzeja_id
                INNER JOIN nodarbibas AS n ON u.nodarbibas_id = n.nodarbibas_id"""

    my_cursor = mydb.cursor()
    my_cursor.execute(query)
    attendance_info = my_cursor.fetchall()

    # Result print
    print_attendance_all(attendance_info, my_cursor)
    
    mydb.close()

def get_attendance_by_lesson_id(lesson_id):
    # MySQL connection
    mydb = mysql.connector.connect(
        host = parser.get('db', 'db_host'),
        user = parser.get('db', 'db_user'),
        passwd = parser.get('db', 'db_passwd'),
        database = parser.get('db', 'db_database')
    )

    query = """SELECT u.id_studentu_uzskaite, s.vards, s.uzvards, u.apliecibas_numurs, u.registracijas_laiks, u.telpas_numurs, n.kursa_nosaukums, p.pasniedzeja_vards, p.pasniedzeja_uzvards
                FROM studentu_uzskaite AS u 
                INNER JOIN studenti AS s ON u.apliecibas_numurs = s.apliecibas_numurs
                INNER JOIN macisanas_saraksts AS m ON u.nodarbibas_id = m.nodarbibas_id
                INNER JOIN pasniedzeji AS p ON m.pasniedzeja_id = p.pasniedzeja_id
                INNER JOIN nodarbibas AS n ON u.nodarbibas_id = n.nodarbibas_id
                WHERE u.nodarbibas_id = %s"""

    my_cursor = mydb.cursor()
    my_cursor.execute(query, (lesson_id,))
    attendance_info = my_cursor.fetchall()

    # Result print
    print_attendance_by_lesson(attendance_info, my_cursor, lesson_id)
    
    mydb.close()

def get_all_attendance_of_student(student_id):
    # MySQL connection
    mydb = mysql.connector.connect(
        host = parser.get('db', 'db_host'),
        user = parser.get('db', 'db_user'),
        passwd = parser.get('db', 'db_passwd'),
        database = parser.get('db', 'db_database')
    )

    query = """SELECT su.id_studentu_uzskaite, su.registracijas_laiks, su.telpas_numurs, n.kursa_nosaukums, su.nodarbibas_id, p.pasniedzeja_vards, pasniedzeja_uzvards
                FROM studentu_uzskaite AS su
                INNER JOIN nodarbibas AS n ON n.nodarbibas_id = su.nodarbibas_id
                INNER JOIN macisanas_saraksts AS ms ON su.nodarbibas_id = ms.nodarbibas_id
                INNER JOIN pasniedzeji AS p ON ms.pasniedzeja_id = p.pasniedzeja_id
                WHERE su.apliecibas_numurs = %s
                ORDER BY su.id_studentu_uzskaite"""

    my_cursor = mydb.cursor()
    my_cursor.execute(query, (student_id,))
    attendance_info = my_cursor.fetchall()

    # Get student name and surname
    query_student_name = """SELECT s.uzvards, s.vards FROM studenti AS s
                            WHERE s.apliecibas_numurs = %s"""
    my_cursor_student_name = mydb.cursor()
    my_cursor_student_name.execute(query_student_name, (student_id,))
    student_name_info = my_cursor_student_name.fetchall()

    # Result print
    print_attendance_by_student(attendance_info, student_name_info, my_cursor, student_id)

    mydb.close()

def print_attendance_by_lesson(attendance_info, mycursor, lesson_id):
    print("\n[INFO] Tika atrasti %s apmeklējuma ieraksti izvēlētajai nodarbībai (%s):" %(mycursor.rowcount, lesson_id))
    table = attendance_info
    print(tabulate(table, headers = ["ID", "Vārds", "Uzvārds", "Apliecības nr.", "Reg. laiks", "Telpas nr.", "Kursa nosauk.", "Pasn. vārds", "Pasn. uzvārds"], tablefmt = "psql", stralign = "center"))

def print_attendance_all(attendance_info, mycursor):
    print("\n[INFO] Tika atrasti %s apmeklējuma ieraksti:" %(mycursor.rowcount))
    table = attendance_info
    print(tabulate(table, headers = ["ID", "Vārds", "Uzvārds", "Apliecības nr.", "Reg. laiks", "Telpas nr.", "Kursa nosauk.", "Nodarbības ID", "Pasn. vārds", "Pasn. uzvārds"], tablefmt = "psql", stralign = "center"))

def print_attendance_by_student(attendance_info, student_name_info, mycursor, student_id):
    for row in student_name_info:
        print("\n[INFO] Tika atrasti {0} apmeklējuma ieraksti izvēlētajam studentam(ID: {1}, Vārds: {2}, {3})".format(mycursor.rowcount, student_id, row[0], row[1]))
    
    if mycursor.rowcount == 0:
        print("\n[INFO] Netika atrasti apmeklējuma ieraksti!")
    else:
        table = attendance_info
        print(tabulate(table, headers = ["ID", "Reg. laiks", "Telpas nr.", "Kursa nosauk.", "Nodarbības ID", "Pasn. vārds", "Pasn. uzvārds"], tablefmt = "psql", stralign = "center"))