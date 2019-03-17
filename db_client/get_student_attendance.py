import mysql.connector
from configparser import ConfigParser
import datetime

# Config parser
parser = ConfigParser()
parser.read('../config/dev_settings_local.ini')

# MySQL connection
mydb = mysql.connector.connect(
    host = parser.get('db', 'db_host'),
    user = parser.get('db', 'db_user'),
    passwd = parser.get('db', 'db_passwd'),
    database = parser.get('db', 'db_database')
)

# Gets all info from studentu_uzskaite table
def get_all_attendance_data():
    query = "SELECT u.id_studentu_uzskaite, s.vards, s.uzvards, u.apliecibas_numurs, u.registracijas_laiks, u.telpas_numurs FROM studentu_uzskaite as u INNER JOIN studenti as s ON u.apliecibas_numurs = s.apliecibas_numurs;"

    my_cursor = mydb.cursor()
    my_cursor.execute(query)

    # Result print
    print("-" * 76)
    print("%3s %6s %12s %12s %13s   %19s" % ("ID", "Vards", "Uzvards", "Apl. nr.", "Reg. laiks", "Telpas nr."))
    print("-" * 76)

    for (id_studentu_uzskaite, vards, uzvards, apliecibas_numurs, registracijas_laiks, telpas_numurs) in my_cursor:
        print("%3d  %-10s %-11s %8s %21s   %-15s" % (id_studentu_uzskaite, vards, uzvards, apliecibas_numurs, registracijas_laiks, telpas_numurs))

get_all_attendance_data()

mydb.close()