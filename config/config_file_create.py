from configparser import ConfigParser

config = ConfigParser()

config['db'] = {
    'db_host': 'localhost',
    'db_user': 'bakalaurs',
    'db_passwd': 'bakalaurs',
    'db_database': 'bakalaurs'
}

config['ftp'] = {
    'ftp_address': 'localhost',
    'ftp_account': 'bakalaurs',
    'ftp_password': 'bakalaurs'
}

config['sats_setting_vars'] = {
    'unknown_face_save': 'False',
    'unknown_face_save_loc': 'unknown_faces',
    'html_save_loc': 'html_attendance_reports',
    'html_report_save_toggle': 'False',
    'recognition_tolerance_level': '0.45',
    'visualize_recognition': '1'
}

with open('./dev_settings_local.ini', 'w') as f:
    config.write(f)

print("Config .ini file successfully created..")