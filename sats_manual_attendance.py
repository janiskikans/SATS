from configparser import ConfigParser
import mysql.connector
import getpass

def pass_input():
    password = getpass.getpass("[IEVADE] Ievadiet administratora paroli: ")
    correct = False
    
    if password == "satsadmin":
        print("[INFO] Parole pieņemta.")
        correct = True
    else:
        print("[INFO] Parole nepareiza!")
        correct = False

    return correct

def manual_attendance(config_file_loc):
    # Config file import
    parser = ConfigParser()
    parser.read(config_file_loc)

    check_pass = pass_input()
    if check_pass == True:
        print("\n", "-" * 27, "Manuālā apmeklējuma ievade", "-" * 27)

        student_id = input("Ievadiet studenta apliecības numuru:")
        registration_time = input("Ievadiet reģistrācijas laiku (YYYY-MM-DD HH:MM:SS):")
        auditorium_nr = input("Ievadiet telpas numuru:")
        class_id = input("Ievadiet nodarbības ID:")

        print("Detaļas:", student_id, registration_time, auditorium_nr, class_id)

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

        print("\n[REĢISTRĀCIJA]", mycursor.rowcount, "apmeklējuma ieraksti saglabāti!")
    else:
        print("[INFO] Atgriežas uz sākumu.")