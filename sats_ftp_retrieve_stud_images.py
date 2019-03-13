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

print("[INFO] FTP connection details:", "Address: ", ftp_address, "| Account:", ftp_account, "| Password:", ftp_password)

# Connetion to ftp server
def ftp_connect(img_ref_list):
    while True:
        try:
            with ftplib.FTP(ftp_address) as ftp:
                ftp.login(ftp_account, ftp_password)
                print(ftp.getwelcome())
                print("[FTP] Current directory", ftp.pwd())
                ftp.dir()
                ftp_get_images(ftp, img_ref_list)
                break
        except ftplib.all_errors as e:
            print("[ERROR] Error connecting to FTP server!", e)

def ftp_get_images(ftp, img_ref_list):
    ftp.cwd("/bildes/studentu_bildes/")
    print("[FTP] Current path:", ftp.pwd())

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

# For every student id get image refs and download images"
for student_ids in student_id_list:
    print("[MYSQL] Current student ID:", str(student_ids[0]))
    sql_query = """SELECT pb.ref_link FROM studenti s JOIN bildes_savienojumi bs on s.apliecibas_numurs = bs.apliecibas_numurs JOIN profila_bildes pb on pb.bildes_id = bs.bildes_id WHERE s.apliecibas_numurs='%s'""" % (student_ids[0],)
    mycursor.execute(sql_query)
    myresult = mycursor.fetchall()
    
    img_ref_list = [list(i) for i in myresult]

    if mycursor.rowcount != 0:
        print('[MYSQL] Record count:', mycursor.rowcount)
        print('[MYSQL] Printing values...')
        print('[MYSQL] student_id_list values:')

        for records in img_ref_list:
            print("[MYSQL]", str(records[0]))

        print('[MYSQL] Print finished')
    else:
        print('[MYSQL] No images found for selected student id!')

    print("[MYSQL] Success! Image refrences retrieved")