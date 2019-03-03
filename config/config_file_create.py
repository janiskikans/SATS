from configparser import ConfigParser

config = ConfigParser()

config['db'] = {
    'db_host': '192.168.0.113',
    'db_user': 'bakalaurs',
    'db_passwd': 'bakalaurs',
    'db_database': 'bakalaurs'
}

config['ftp'] = {
    'ftp_address': '192.168.0.113',
    'ftp_account': 'bakalaurs',
    'ftp_password': 'bakalaurs'
}

with open('./config/dev_settings.ini', 'w') as f:
    config.write(f)

print("Config .ini file successfully created..")