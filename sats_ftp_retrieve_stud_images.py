from configparser import ConfigParser
import ftplib
import os
import mysql.connector
# Other scripts
from sats_encode_faces import encode_faces

# Globals
retr_images = 0

# Connetion to ftp server
def ftp_connect(img_ref_list, student_sel, ftp_address, ftp_account, ftp_password):
    while True:
        try:
            with ftplib.FTP(ftp_address) as ftp:
                ftp.login(ftp_account, ftp_password)
                #print(ftp.getwelcome())
                #print("[FTP] Current directory", ftp.pwd())
                #ftp.dir()
                ftp_get_images(ftp, img_ref_list, student_sel)
                break
        except ftplib.all_errors as e:
            print("[ERROR] Error connecting to FTP server!", e)

def ftp_get_images(ftp, img_ref_list, student_sel):
    global retr_images

    ftp.cwd("/bildes/studentu_bildes/%s" %str(student_sel))
    #print("[FTP] Current path:", ftp.pwd())

    os.chdir('dataset')

    if not os.path.exists(student_sel):
        os.mkdir(student_sel)
        print("[FTP] Directory ", student_sel, " created")
    else:
        print("[FTP] Directory ", student_sel, " already exists")

    os.chdir("%s" %str(student_sel)) # Changes to created student's image path

    for image in img_ref_list:
        ftp.retrbinary("RETR " + str(image[0]), open(str(image[0]), 'wb').write)
        print("[FTP] Downloaded " + str(image[0]) + " successfully! Image of student with id: " + student_sel)
        retr_images += 1

    os.chdir("../..") # Returns to main directory after downloading student images

def ftp_retrieve_stud_images_main(dev_settings_loc):
    global retr_images
    parser = ConfigParser()
    parser.read(dev_settings_loc)

    ftp_address = parser.get('ftp', 'ftp_address')
    ftp_account = parser.get('ftp', 'ftp_account')
    ftp_password = parser.get('ftp', 'ftp_password')

    print("[INFO] FTP savienojuma detaļas:", "Adrese: ", ftp_address, "| Konts:", ftp_account, "| Parole:", ftp_password)

    # MySQL connection details
    mydb = mysql.connector.connect(
        host = parser.get('db', 'db_host'),
        user = parser.get('db', 'db_user'),
        passwd = parser.get('db', 'db_passwd'),
        database = parser.get('db', 'db_database')
    )

    mycursor = mydb.cursor()

    # Get all student ids in database
    sql_query = """SELECT studenti.apliecibas_numurs FROM bakalaurs.studenti"""
    mycursor.execute(sql_query)
    myresult = mycursor.fetchall()

    print('[MYSQL] Ierakstu skaits:', mycursor.rowcount)
    print('[MYSQL] student_id_list vērtības:')
    print('[MYSQL] Izvada vērtības...')

    student_id_list = [list(i) for i in myresult]
    for records in student_id_list:
        print("[MYSQL]", str(records[0]))
    print('[MYSQL] Izvade pabeigta')

    print("-" * 30)
    print("[INFO] Iegūst studentu attēlus!")

    retr_students = 0 # Counts how many student id images downloaded
    # For every student id get image refs and download images
    for student_ids in student_id_list:
        # Get all image references connected to selected student ID
        print("\n[MYSQL] Studenta apliecības numurs:", str(student_ids[0]))
        sql_query = """SELECT pb.ref_link FROM studenti s JOIN bildes_savienojumi bs on s.apliecibas_numurs = bs.apliecibas_numurs JOIN profila_bildes pb on pb.bildes_id = bs.bildes_id WHERE s.apliecibas_numurs='%s'""" % (student_ids[0],)
        mycursor.execute(sql_query)
        myresult = mycursor.fetchall()
        
        img_ref_list = [list(i) for i in myresult]

        if mycursor.rowcount != 0:
            print('[MYSQL] Ierakstu skaits:', mycursor.rowcount)
            print('[MYSQL] Izvada vērtības...')
            print('[MYSQL] img_ref_list vērtības:')

            for records in img_ref_list:
                print("[MYSQL]", str(records[0]))

            print('[MYSQL] Izvade pabeigta')
        else:
            print('[MYSQL] Netika atrastas bildes izvēlētajam studentam!')

        print("[MYSQL] Pabeigts! Attēlu atsauces iegūtas.")

        # Retrieve each image from FTP server from specified student
        ftp_connect(img_ref_list, str(student_ids[0]), ftp_address, ftp_account, ftp_password)

        retr_students += 1

    print("\n[INFO] Attēlu ieguve pabeigta! Iegūtas {} studentu bildes (Kopā {} attēli)!.".format(retr_students, retr_images))

    # Check if also encode retrieved student images
    choice = None
    while choice not in ("y", "n", "yes", "no"):
        choice = input("[INPUT] Vai vēlaties kodēt iegūtos attēlus? (y/n): ")
        if choice == "y" or choice == "yes":
            # Run encode faces script with parameters
            encode_faces()
        elif choice == "n" or choice == "no":
            print("[INFO] Ieguves skripts pabeigts!")
            break
        else:
            print("[KĻŪDA] Ievads kļūda! Ievadiet y vai n.")

if __name__ == "__main__":
    ftp_get_images()
    ftp_connect()