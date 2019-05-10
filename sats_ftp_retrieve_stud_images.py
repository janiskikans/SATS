from configparser import ConfigParser
import ftplib
import os
import mysql.connector
from sats_encode_faces import encode_faces # Import face encoding script module encode_faces.

# Globals
retr_images = 0

# Attempt a FTP connection.
def ftp_connect(img_ref_list, student_sel, ftp_address, ftp_account, ftp_password):
    while True:
        try:
            with ftplib.FTP(ftp_address) as ftp:
                ftp.login(ftp_account, ftp_password)
                # Call script that retrieves selected students images to a local folder.
                ftp_get_images(ftp, img_ref_list, student_sel)
                break
        except ftplib.all_errors as e:
            print("[KĻŪDA] Kļūda izveidojot savienojumu ar FTP serveri!", e)

# Retrieve the images from the FTP server.
def ftp_get_images(ftp, img_ref_list, student_sel):
    global retr_images

    ftp.cwd("/bildes/studentu_bildes/%s" %str(student_sel))
    os.chdir('dataset')

    # Check if a directory with current student's ID exists. If not - create one.
    if not os.path.exists(student_sel):
        os.mkdir(student_sel)
        print("[FTP] Directory ", student_sel, " created")
    else:
        print("[FTP] Directory ", student_sel, " already exists")

    # Enter the current student's image path.
    os.chdir("%s" %str(student_sel))

    # Download all images listed in img_ref_list.
    for image in img_ref_list:
        ftp.retrbinary("RETR " + str(image[0]), open(str(image[0]), 'wb').write)
        print("[FTP] Downloaded " + str(image[0]) + " successfully! Image of student with id: " + student_sel)
        retr_images += 1

    os.chdir("../..") # Returns to main directory after downloading student images

# Main image retrieval script.
def ftp_retrieve_stud_images_main(dev_settings_loc):
    global retr_images

    parser = ConfigParser()
    parser.read(dev_settings_loc)

    ftp_address = parser.get('ftp', 'ftp_address')
    ftp_account = parser.get('ftp', 'ftp_account')
    ftp_password = parser.get('ftp', 'ftp_password')

    print("[INFO] FTP savienojuma detaļas:", "Adrese: ", ftp_address, "| Konts:", ftp_account, "| Parole:", ftp_password)

    # MySQL connection details.
    mydb = mysql.connector.connect(
        host = parser.get('db', 'db_host'),
        user = parser.get('db', 'db_user'),
        passwd = parser.get('db', 'db_passwd'),
        database = parser.get('db', 'db_database')
    )

    mycursor = mydb.cursor()

    # Get all student IDs in database.
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

    # Counts how many student ID images have been downloaded.
    retr_students = 0
    # For every student ID in student_id_list get image references and download the images.
    for student_ids in student_id_list:
        # Get all image references connected to selected student ID.
        print("\n[MYSQL] Studenta apliecības numurs:", str(student_ids[0]))
        sql_query = """SELECT pb.ref_link FROM studenti s JOIN bildes_savienojumi bs on s.apliecibas_numurs = bs.apliecibas_numurs JOIN profila_bildes pb on pb.bildes_id = bs.bildes_id WHERE s.apliecibas_numurs='%s'""" % (student_ids[0],)
        mycursor.execute(sql_query)
        myresult = mycursor.fetchall()
        
        # Save references to a list.
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

        # Retrieve each image from FTP server from the specified student.
        ftp_connect(img_ref_list, str(student_ids[0]), ftp_address, ftp_account, ftp_password)

        retr_students += 1

    print("\n[INFO] Attēlu ieguve pabeigta! Iegūtas {} studentu bildes (Kopā {} attēli).".format(retr_students, retr_images))

    # Check if user want's to encode the retrieved faces.
    choice = None
    while choice not in ("y", "n", "yes", "no"):
        choice = input("\n[INPUT] Vai vēlaties sagatavot iegūto attēlu mērījumus? (y/n): ")
        if choice == "y" or choice == "yes":
            encode_faces()
        elif choice == "n" or choice == "no":
            print("\n[INFO] Attēlu ieguves skripts pabeigts!")
            break
        else:
            print("[KĻŪDA] Ievads kļūda! Ievadiet y vai n.")

if __name__ == "__main__":
    ftp_get_images()
    ftp_connect()