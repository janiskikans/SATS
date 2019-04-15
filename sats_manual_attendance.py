from configparser import ConfigParser
import mysql.connector
import getpass
from tabulate import tabulate

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

def delete_attendance_record(attendance_id, config_file_loc):
    parser = ConfigParser()
    parser.read(config_file_loc)

    mydb = mysql.connector.connect(
            host = parser.get('db', 'db_host'),
            user = parser.get('db', 'db_user'),
            passwd = parser.get('db', 'db_passwd'),
            database = parser.get('db', 'db_database')
        )

    mycursor = mydb.cursor()
    sql_query = """SELECT su.id_studentu_uzskaite, su.apliecibas_numurs, s.uzvards, s.vards, su.registracijas_laiks, su.nodarbibas_id, n.kursa_nosaukums, su.telpas_numurs
                    FROM studentu_uzskaite AS su
                    INNER JOIN studenti AS s ON su.apliecibas_numurs = s.apliecibas_numurs
                    INNER JOIN nodarbibas AS n ON su.nodarbibas_id = n.nodarbibas_id
                    WHERE su.id_studentu_uzskaite = %s"""

    mycursor.execute(sql_query, (attendance_id, ))
    attendance_records = mycursor.fetchall()

    if mycursor.rowcount > 0:
        for records in attendance_records:
            print("\n[INFO] Izvēlētā apmeklējuma detaļas: ")
            table_data = attendance_records
            print(tabulate(table_data, headers = ["ID", "Apliecības numurs", "Uzvārds", "Vārds", "Reģistrācijas laiks", "Nodarbības ID", "Kursa nosauk.", "Telpas numurs"], tablefmt = "psql", stralign = "center"))

        user_choice = None
        while user_choice not in ("y", "n", "yes", "no"):
            user_choice = input("\n[IEVADE] Vai tiešām vēlaties dzēst izvēlēto apmeklējuma ierakstu? (y/n): ")
            if user_choice == "y" or user_choice == "yes":
                sql_query = """DELETE FROM studentu_uzskaite WHERE id_studentu_uzskaite = %s"""
                mycursor.execute(sql_query, (attendance_id,))
                mydb.commit()
                print("\n[INFO] Veiksmīgi izdzēsts {0} ieraksts ar ID: {1}.".format(mycursor.rowcount, attendance_id))
            elif user_choice == "n" or user_choice == "no":
                # Returns to main menu
                break
            else:
                print("[KĻŪDA] Ievads kļūda! Ievadiet y vai n.")
    else:
        print("\n[INFO] Netika atrasts apmeklējums ar doto ID! Mēģiniet vēlreiz.")

    mydb.close()