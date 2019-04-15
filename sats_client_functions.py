from configparser import ConfigParser
from tabulate import tabulate

# Main client menu printout
def print_menu():
    #print("\n", 36 * "-", "MENU", 36 * "-")
    #print("1. RETRIEVE student images and ENCODE faces")
    #print("2. TAKE automatic ATTENDANCE")
    #print("3. Enter attendance MANUALLY (MySQL)")
    #print("4. Get ALL attendance data (MySQL)")
    #print("5. Get attendance data BY LESSON ID (MySQL)")
    #print("6. Get attendance data BY STUDENT ID (MySQL)")
    #print("7. Get information about today's lessons BY AUDITORIUM (MySQL)")
    #print("8. Exit SATS")
    print("\n", 36 * "-", "Izvēlne", 36 * "-")
    print("1. IEGŪT pieejamās studentu bildes un tās KODĒT")
    print("2. Sākt automātisko apmeklējuma reģistrāciju")
    print("3. Ievadīt apmeklējuma informāciju MANUĀLI (MySQL)")
    print("4. Iegūt informāciju par VISIEM apmeklējumiem (MySQL)")
    print("5. Iegūt apmeklējuma informāciju izvēlētajai NODARBĪBAI (MySQL)")
    print("6. Iegūt apmeklējuma informāciju izvēlētajam STUDENTAM (MySQL)")
    print("7. Iegūt informāciju par šodienas nodarbībām izvēlētajā TELPĀ (MySQL)")
    print("8. IZDZĒST apmeklējuma ierakstu (MySQL)")
    print("9. Skatīt programmas izmantotos uzstādījumus")
    print("10. Iziet no SATS")
    print(82 * "-")

def print_used_settings(config_file_loc):
    parser = ConfigParser()
    parser.read(config_file_loc)

    data = [["FTP adrese", parser.get('ftp', 'ftp_address')], ["FTP lietotājs", parser.get('ftp', 'ftp_account')], ["FTP parole", parser.get('ftp', 'ftp_password')],\
    ["MySQL adrese", parser.get('db', 'db_host')], ["MySQL lietotājs", parser.get('db', 'db_user')], ["MySQL parole", parser.get('db', 'db_passwd')],\
    ["MySQL datubāze", parser.get('db', 'db_database')], ["unknow_face_save", parser.get('sats_setting_vars', 'unknown_face_save')],\
    ["unknow_face_save_loc", parser.get('sats_setting_vars', 'unknown_face_save_loc')], ["html_save_loc", parser.get('sats_setting_vars', 'html_save_loc')],\
    ["html_report_save_toggle", parser.get('sats_setting_vars', 'html_report_save_toggle')]]

    print("\n[INFO] SATS izmantotie uzstādījumi ({0}):".format(config_file_loc))
    print(tabulate(data, headers = ["Uzstādījuma nosaukums", "Uzstādījuma vērtība"], tablefmt = "psql", colalign = ["left", "center"]))