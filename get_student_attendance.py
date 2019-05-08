import mysql.connector
from configparser import ConfigParser
import datetime
from tabulate import tabulate
import HTML
import os

# Gets all attendance information from studentu_uzskaite table.
def get_all_attendance_data(config_file_loc, html_save_loc, html_report_save_toggle):
    # Config file import.
    parser = ConfigParser()
    parser.read(config_file_loc)

    # MySQL connection.
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
                INNER JOIN nodarbibas AS n ON u.nodarbibas_id = n.nodarbibas_id
                ORDER BY u.registracijas_laiks"""

    my_cursor = mydb.cursor()
    my_cursor.execute(query)
    attendance_info = my_cursor.fetchall()

    # Result print
    print_attendance_all(attendance_info, my_cursor)

    if html_report_save_toggle == "True":
        print_html_all_attendance(attendance_info, html_save_loc)

    mydb.close()

# Retrieve all attendance data corresponding to the selected lesson ID.
def get_attendance_by_lesson_id(lesson_id, config_file_loc, html_save_loc, html_report_save_toggle):
    # Config file import.
    parser = ConfigParser()
    parser.read(config_file_loc)

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
                WHERE u.nodarbibas_id = %s
                ORDER BY u.registracijas_laiks"""

    my_cursor = mydb.cursor()
    my_cursor.execute(query, (lesson_id,))
    attendance_info = my_cursor.fetchall()

    # Print all attendance records with the selected lesson ID.
    print_attendance_by_lesson(attendance_info, my_cursor, lesson_id)

    # Save attendance information to HTML file if option selected.
    if html_report_save_toggle == "True":
        print_html_attendance_by_lesson_id(attendance_info, html_save_loc, lesson_id)

    mydb.close()

# Retrieve all attendance records corresponding to the selected student ID.
def get_all_attendance_of_student(student_id, config_file_loc, html_save_loc, html_report_save_toggle):
    # Config file import.
    parser = ConfigParser()
    parser.read(config_file_loc)

    # MySQL connection.
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

    # Get input student's information from database.
    query_student_name = """SELECT s.uzvards, s.vards FROM studenti AS s
                            WHERE s.apliecibas_numurs = %s"""
    my_cursor_student_name = mydb.cursor()
    my_cursor_student_name.execute(query_student_name, (student_id,))
    student_name_info = my_cursor_student_name.fetchall()

    # Print out all retrieved attendance records corresponding to the input student ID.
    print_attendance_by_student(attendance_info, student_name_info, my_cursor, student_id)

    # Save attendance information to HTML file if option selected.
    if html_report_save_toggle == "True":
        print_html_attendance_by_student(attendance_info, html_save_loc, student_id)

    mydb.close()

# Print out all attendance records corresponding to the input lesson ID.
def print_attendance_by_lesson(attendance_info, mycursor, lesson_id):
    print("\n[INFO] Tika atrasti %s apmeklējuma ieraksti izvēlētajai nodarbībai (%s):" %(mycursor.rowcount, lesson_id))

    table = attendance_info
    print(tabulate(table, headers = ["ID", "Vārds", "Uzvārds", "Apliecības nr.", "Reg. laiks", "Telpas nr.", "Kursa nosauk.", "Pasn. vārds", "Pasn. uzvārds"], tablefmt = "psql", stralign = "center"))

# Print out all attendance records in the database table.
def print_attendance_all(attendance_info, mycursor):
    print("\n[INFO] Tika atrasti %s apmeklējuma ieraksti:" %(mycursor.rowcount))

    table = attendance_info
    print(tabulate(table, headers = ["ID", "Vārds", "Uzvārds", "Apliecības nr.", "Reg. laiks", "Telpas nr.", "Kursa nosauk.", "Nodarbības ID", "Pasn. vārds", "Pasn. uzvārds"], tablefmt = "psql", stralign = "center"))

# Print out all attendance records corresponding to the input student ID.
def print_attendance_by_student(attendance_info, student_name_info, mycursor, student_id):
    for row in student_name_info:
        print("\n[INFO] Tika atrasti {0} apmeklējuma ieraksti izvēlētajam studentam(ID: {1}, Vārds: {2}, {3})".format(mycursor.rowcount, student_id, row[0], row[1]))
    
    if mycursor.rowcount == 0:
        print("\n[INFO] Netika atrasti apmeklējuma ieraksti!")
    else:
        table = attendance_info
        print(tabulate(table, headers = ["ID", "Reg. laiks", "Telpas nr.", "Kursa nosauk.", "Nodarbības ID", "Pasn. vārds", "Pasn. uzvārds"], tablefmt = "psql", stralign = "center"))

# Save all attendance records to a HTML table. Save the file.
def print_html_all_attendance(attendance_info, html_save_loc):
    current_date_time = datetime.datetime.now()

    os.chdir(html_save_loc)

    html_file = ("all_attendance_report_" + current_date_time.strftime('%Y%m%d_%H%M%S') + ".html")
    f = open(html_file, 'w')

    htmlcode = HTML.table(attendance_info, header_row = ["ID", "Vārds", "Uzvārds", "Apliecības nr.", "Reg. laiks", "Telpas nr.", "Kursa nosauk.", "Nodarbības ID", "Pasn. vārds", "Pasn. uzvārds"])
    
    f.write("<h4>SATS</h4>")
    f.write("<h3>Informācija par visiem apmeklējumiem:</h3>")
    f.write(htmlcode)
    f.write("<br>")
    f.write("Iegūts: " + current_date_time.strftime('%Y-%m-%d %H:%M:%S'))
    f.write("<p>")

    f.close()

    os.chdir("..")

    print("/n[INFO] Apmeklējumu ieraksti saglabāti! (/" + html_file + ")")

# Save all attendance records corresponding to specific student ID to a HTML table. Save the file.
def print_html_attendance_by_student(attendance_info, html_save_loc, student_id):
    current_date_time = datetime.datetime.now()

    os.chdir(html_save_loc)

    html_file = ("attendance_by_student_report_" + student_id + "_" + current_date_time.strftime('%Y%m%d_%H%M%S') + ".html")
    f = open(html_file, 'w')

    htmlcode = HTML.table(attendance_info, header_row = ["ID", "Reg. laiks", "Telpas nr.", "Kursa nosauk.", "Nodarbības ID", "Pasn. vārds", "Pasn. uzvārds"])
    
    f.write("<h4>SATS</h4>")
    f.write("<h3>Informācija par studenta ({0}) apmeklējumu:</h3>".format(student_id))
    f.write(htmlcode)
    f.write("<br>")
    f.write("Iegūts: " + current_date_time.strftime('%Y-%m-%d %H:%M:%S'))
    f.write("<p>")

    f.close()

    os.chdir("..")

    print("\n[INFO] Apmeklējumu ieraksti saglabāti! (/" + html_file + ")")

# Save all attendance records corresponding to specific lesson ID to a HTML table. Save the file.
def print_html_attendance_by_lesson_id(attendance_info, html_save_loc, lesson_id):
    current_date_time = datetime.datetime.now()

    os.chdir(html_save_loc)

    html_file = ("attendance_by_lesson_report_" + lesson_id + "_" + current_date_time.strftime('%Y%m%d_%H%M%S') + ".html")
    f = open(html_file, 'w')

    htmlcode = HTML.table(attendance_info, header_row = ["ID", "Vārds", "Uzvārds", "Apliecības nr.", "Reg. laiks", "Telpas nr.", "Kursa nosauk.", "Pasn. vārds", "Pasn. uzvārds"])
    
    f.write("<h4>SATS</h4>")
    f.write("<h3>Informācija par nodarbības ({0}) apmeklējumu:</h3>".format(lesson_id))
    f.write(htmlcode)
    f.write("<br>")
    f.write("Iegūts: " + current_date_time.strftime('%Y-%m-%d %H:%M:%S'))
    f.write("<p>")

    f.close()

    os.chdir("..")

    print("\n[INFO] Apmeklējumu ieraksti saglabāti! (/" + html_file + ")")