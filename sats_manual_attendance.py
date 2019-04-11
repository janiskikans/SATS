from configparser import ConfigParser
import mysql.connector
import getpass

# Config file import
parser = ConfigParser()
parser.read('./config/dev_settings_local.ini') # local
#parser.read('./config/dev_settings.ini') # remote LAN

def pass_input():
    password = getpass.getpass("[INPUT] Enter admin password: ")
    correct = False
    
    if password == "satsadmin":
        print("[INFO] Password accepted.")
        correct = True
    else:
        print("[INFO] Password incorrect!")
        correct = False

    return correct

def manual_attendance():
    check_pass = pass_input()
    if check_pass == True:
        print("\n", "-" * 27, "Manual attendance input", "-" * 27)

        student_id = input("Enter student ID:")
        registration_time = input("Enter registration time (YYYY-MM-DD HH:MM:SS):")
        auditorium_nr = input("Enter auditorium number:")
        class_id = input("Enter class ID:")

        print("Details:", student_id, registration_time, auditorium_nr, class_id)

        mydb = mysql.connector.connect(
            host = parser.get('db', 'db_host'),
            user = parser.get('db', 'db_user'),
            passwd = parser.get('db', 'db_passwd'),
            database = parser.get('db', 'db_database')
        )

        mycursor = mydb.cursor()
        sql_query = """INSERT INTO studentu_uzskaite (apliecibas_numurs, registracijas_laiks, telpas_numurs, nodarbibas_id)
        VALUES (%s, %s, %s, %s)"""
        values = (student_id, registration_time, auditorium_nr, class_id)

        mycursor.execute(sql_query, values)
        mydb.commit()
        mydb.close()

        print("\n[REGISTRATION]", mycursor.rowcount, "records inserted!")
    else:
        print("[INFO] Returning to start.")