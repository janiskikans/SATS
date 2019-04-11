import mysql.connector
from configparser import ConfigParser
import datetime
from tabulate import tabulate

# Config parser
parser = ConfigParser()
parser.read('config/dev_settings_local.ini') # local
#parser.read('./config/dev_settings.ini') # remote LAN

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

def print_attendance_by_lesson(attendance_info, mycursor, lesson_id):
    print("\n[INFO] Found %s attendance records for selected lesson(%s):" %(mycursor.rowcount, lesson_id))
    table = attendance_info
    print(tabulate(table, headers = ["ID", "Vārds", "Uzvārds", "Apliecības nr.", "Reg. laiks", "Telpas nr.", "Kursa nosauk.", "Pasn. vārds", "Pasn. uzvārds"], tablefmt = "psql", stralign = "center"))

def print_attendance_all(attendance_info, mycursor):
    print("\n[INFO] Found %s attendance records:" %(mycursor.rowcount))
    table = attendance_info
    print(tabulate(table, headers = ["ID", "Vārds", "Uzvārds", "Apliecības nr.", "Reg. laiks", "Telpas nr.", "Kursa nosauk.", "Nodarbības ID", "Pasn. vārds", "Pasn. uzvārds"], tablefmt = "psql", stralign = "center"))