from configparser import ConfigParser
import ftplib
import os
import mysql.connector

parser = ConfigParser()
parser.read('./config/dev_settings_local.ini')

# Global vars
ftp_address = parser.get('ftp', 'ftp_address')
ftp_account = parser.get('ftp', 'ftp_account')
ftp_password = parser.get('ftp', 'ftp_password')
retr_images = 0

print("[INFO] FTP connection details:", "Address: ", ftp_address, "| Account:", ftp_account, "| Password:", ftp_password)

# Connetion to ftp server
def ftp_connect(img_ref_list, student_sel):
    while True:
        try:
            with ftplib.FTP(ftp_address) as ftp:
                ftp.login(ftp_account, ftp_password)
                #print(ftp.getwelcome())
                #print("[FTP] Current directory", ftp.pwd())
                ftp.dir()
                ftp_get_images(ftp, img_ref_list, student_sel)
                break
        except ftplib.all_errors as e:
            print("[ERROR] Error connecting to FTP server!", e)

def ftp_get_images(ftp, img_ref_list, student_sel):
    global retr_images

    ftp.cwd("/bildes/studentu_bildes/%s" %str(student_sel))
    #print("[FTP] Current path:", ftp.pwd())

    os.chdir('retr_files')

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

print('[MYSQL] Record count:', mycursor.rowcount)
print('[MYSQL] student_id_list values:')
print('[MYSQL] Printing values...')

student_id_list = [list(i) for i in myresult]
for records in student_id_list:
    print("[MYSQL]", str(records[0]))
print('[MYSQL] Print finished')

print("-" * 30)
print("[INFO] Getting student images!")

retr_students = 0 # Counts how many student id images downloaded
# For every student id get image refs and download images
for student_ids in student_id_list:
    # Get all image references connected to selected student ID
    print("\n[MYSQL] Current student ID:", str(student_ids[0]))
    sql_query = """SELECT pb.ref_link FROM studenti s JOIN bildes_savienojumi bs on s.apliecibas_numurs = bs.apliecibas_numurs JOIN profila_bildes pb on pb.bildes_id = bs.bildes_id WHERE s.apliecibas_numurs='%s'""" % (student_ids[0],)
    mycursor.execute(sql_query)
    myresult = mycursor.fetchall()
    
    img_ref_list = [list(i) for i in myresult]

    if mycursor.rowcount != 0:
        print('[MYSQL] Record count:', mycursor.rowcount)
        print('[MYSQL] Printing values...')
        print('[MYSQL] img_ref_list values:')

        for records in img_ref_list:
            print("[MYSQL]", str(records[0]))

        print('[MYSQL] Print finished')
    else:
        print('[MYSQL] No images found for selected student id!')

    print("[MYSQL] Success! Image references retrieved")

    # Retrieve each image from FTP server from specified student
    ftp_connect(img_ref_list, str(student_ids[0]))

    retr_students += 1

print("\n[INFO] Image retrieval finished! Retrieved images of {} students ({} images total)!.".format(retr_students, retr_images))

# Check if also encode retrieved student images
choice = None
while choice not in ("y", "n", "yes", "no"):
    choice = input("[INPUT] Do you want to encode retrieved faces? (y/n): ")
    if choice == "y" or choice == "yes":
        # Run encode faces script with parameters
    elif choice == "n" or choice == "no":
        break
    else:
        print("[ERROR] Invalid input! Enter y or n.")