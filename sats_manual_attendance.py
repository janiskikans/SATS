from configparser import ConfigParser
import mysql.connector
import getpass

# Config file import
parser = ConfigParser()
#parser.read('./config/dev_settings_local.ini') # local
parser.read('./config/dev_settings.ini') # remote LAN

# Globals


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
        print("[INFO] Script entered.")
    else:
        print("[INFO] Returning to start.")