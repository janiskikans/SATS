import mysql.connector
from configparser import ConfigParser
import datetime

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

    query = """SELECT u.id_studentu_uzskaite, s.vards, s.uzvards, u.apliecibas_numurs, u.registracijas_laiks, u.telpas_numurs, u.nodarbibas_id, p.pasniedzeja_vards, p.pasniedzeja_uzvards
                FROM studentu_uzskaite AS u 
                INNER JOIN studenti AS s ON u.apliecibas_numurs = s.apliecibas_numurs
                INNER JOIN macisanas_saraksts AS m ON u.nodarbibas_id = m.nodarbibas_id
                INNER JOIN pasniedzeji AS p ON m.pasniedzeja_id = p.pasniedzeja_id"""

    my_cursor = mydb.cursor()
    my_cursor.execute(query)

    # Result print
    print("-" * 103)
    print("%3s %6s %12s %12s %13s   %19s %8s %17s" % ("ID", "Vards", "Uzvards", "Apl. nr.", "Reg. laiks", "Telpas nr.", "Nod. ID", "Pasniedzejs"))
    print("-" * 103)

    for (id_studentu_uzskaite, vards, uzvards, apliecibas_numurs, registracijas_laiks, telpas_numurs, nodarbibas_id, pasniedzeja_vards, pasniedzeja_uzvards) in my_cursor:
        print("%3d  %-10s %-11s %8s %21s   %-10s %12s %8s %s" % (id_studentu_uzskaite, vards, uzvards, apliecibas_numurs, registracijas_laiks, telpas_numurs, nodarbibas_id, pasniedzeja_vards, pasniedzeja_uzvards))
    
    mydb.close()

def get_attendance_by_lesson_id(lesson_id):
    # MySQL connection
    mydb = mysql.connector.connect(
        host = parser.get('db', 'db_host'),
        user = parser.get('db', 'db_user'),
        passwd = parser.get('db', 'db_passwd'),
        database = parser.get('db', 'db_database')
    )

    query = """SELECT u.id_studentu_uzskaite, s.vards, s.uzvards, u.apliecibas_numurs, u.registracijas_laiks, u.telpas_numurs, u.nodarbibas_id, p.pasniedzeja_vards, p.pasniedzeja_uzvards
                FROM studentu_uzskaite AS u 
                INNER JOIN studenti AS s ON u.apliecibas_numurs = s.apliecibas_numurs
                INNER JOIN macisanas_saraksts AS m ON u.nodarbibas_id = m.nodarbibas_id
                INNER JOIN pasniedzeji AS p ON m.pasniedzeja_id = p.pasniedzeja_id
                WHERE u.nodarbibas_id = %s"""

    my_cursor = mydb.cursor()
    my_cursor.execute(query, (lesson_id,))

    # Result print
    print("-" * 103)
    print("%3s %6s %12s %12s %13s   %19s %8s %17s" % ("ID", "Vards", "Uzvards", "Apl. nr.", "Reg. laiks", "Telpas nr.", "Nod. ID", "Pasniedzejs"))
    print("-" * 103)

    for (id_studentu_uzskaite, vards, uzvards, apliecibas_numurs, registracijas_laiks, telpas_numurs, nodarbibas_id, pasniedzeja_vards, pasniedzeja_uzvards) in my_cursor:
        print("%3d  %-10s %-11s %8s %21s   %-10s %12s %8s %s" % (id_studentu_uzskaite, vards, uzvards, apliecibas_numurs, registracijas_laiks, telpas_numurs, nodarbibas_id, pasniedzeja_vards, pasniedzeja_uzvards))
    
    mydb.close()