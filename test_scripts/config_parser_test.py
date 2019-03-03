from configparser import ConfigParser

parser = ConfigParser()
parser.read('./config/dev_settings.ini')

print(parser.sections()) # Prints out all sections in the .ini file.
print(parser.options('ftp')) # Gets all the selected sections values.
print('db' in parser) # Checks if there's a thing in the selected section.
print("FTP account: ", parser.get('ftp', 'ftp_account')) # Gets a selected value.