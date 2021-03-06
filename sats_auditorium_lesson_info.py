from configparser import ConfigParser
import mysql.connector
import datetime
from tabulate import tabulate

# Retrieve information about the lessons that are happening today in the specified auditorium.
def get_auditorium_lesson_list(auditorium_number, config_file_loc):
    # Config file import
    parser = ConfigParser()
    parser.read(config_file_loc)

    # MySQL connection details
    mydb = mysql.connector.connect(
        host = parser.get('db', 'db_host'),
        user = parser.get('db', 'db_user'),
        passwd = parser.get('db', 'db_passwd'),
        database = parser.get('db', 'db_database')
    )

    mycursor = mydb.cursor()
    current_date = datetime.datetime.now().strftime("%Y-%m-%d")

    sql_query = """SELECT n.sakuma_laiks, n.beigu_laiks, p.pasniedzeja_vards, p.pasniedzeja_uzvards, n.nodarbibas_id, n.kursa_nosaukums 
                    FROM nodarbibas AS n INNER JOIN macisanas_saraksts AS ms ON n.nodarbibas_id = ms.nodarbibas_id 
                    INNER JOIN pasniedzeji AS p ON ms.pasniedzeja_id = p.pasniedzeja_id 
                    WHERE n.datums = %s AND n.telpa = %s
                    ORDER BY n.sakuma_laiks"""
    values = (current_date, auditorium_number)

    mycursor.execute(sql_query, values)
    auditorium_lessons = mycursor.fetchall()

    if mycursor.rowcount == 0:
        print("\n[INFO] Netika atrastas nodarbības izvēlētajai telpai, kas notiktu šodien!")
    else:
        lesson_print(auditorium_lessons, auditorium_number, current_date, mycursor)

    mydb.close()

# Print out the table of lesson records.
def lesson_print(auditorium_lessons, auditorium_number, current_date, mycursor):
    print("\n[INFO] Nodarbības atrastas! Šodien (%s) notiek %s nodarbības izvēlētajā telpā (%s):" %(current_date, mycursor.rowcount, auditorium_number))  
    
    table = auditorium_lessons
    print(tabulate(table, headers = ["Sākuma laiks", "Beigu laiks", "Pasn. vārds", "Pasn. uzvārds", "Nodarbības ID", "Kursa nosaukums"], tablefmt = "psql", stralign = "center"))