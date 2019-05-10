import mysql.connector
from configparser import ConfigParser
from imutils import paths

# Get the last image ID number in database.
def getLastImageID(parser):
    mydb = mysql.connector.connect(
        host = parser.get('db', 'db_host'),
        user = parser.get('db', 'db_user'),
        passwd = parser.get('db', 'db_passwd'),
        database = parser.get('db', 'db_database')
    )

    mycursor = mydb.cursor()
    query = """SELECT MAX(bildes_id) FROM bakalaurs.profila_bildes;"""
    mycursor.execute(query)
    myresult = mycursor.fetchall()

    last_number = myresult[0][0]

    mydb.close()

    return last_number

def fill_profila_bildes_table(parser, ref_link_base, image_count, next_number):
    image_ref_link_list = [""] * image_count

    i = 1
    for position in range(len(image_ref_link_list)):
        ref_link_full = "{}_{}.jpg".format(ref_link_base, i)
        image_ref_link_list[position] = str(ref_link_full)
        i = i + 1

    print("\n[INFO] Image_ref_link_list:")
    print_list(image_ref_link_list)

    mydb = mysql.connector.connect(
        host = parser.get('db', 'db_host'),
        user = parser.get('db', 'db_user'),
        passwd = parser.get('db', 'db_passwd'),
        database = parser.get('db', 'db_database')
    )

    i = next_number
    for position in range(len(image_ref_link_list)):
        mycursor = mydb.cursor()
        sql = """INSERT INTO profila_bildes (bildes_id, ref_link) VALUES (%s, %s)"""
        values = (i, image_ref_link_list[position])

        mycursor.execute(sql, values)
        mydb.commit()
        i = i + 1
    mydb.close()

def fill_bildes_savienojumi_table(parser, image_id, student_id):
    mydb = mysql.connector.connect(
        host = parser.get('db', 'db_host'),
        user = parser.get('db', 'db_user'),
        passwd = parser.get('db', 'db_passwd'),
        database = parser.get('db', 'db_database')
    )

    mycursor = mydb.cursor()

    sql = """INSERT INTO bildes_savienojumi (apliecibas_numurs, bildes_id) VALUES (%s, %s)"""
    values = (student_id, image_id)

    mycursor.execute(sql, values)
    mydb.commit()
    mydb.close()

def print_list(input_list):
    for item in input_list:
        print(item)

def main():
    parser = ConfigParser()
    parser.read("./config/dev_settings.ini")
    empty = False

    if empty == False:
        next_number = getLastImageID(parser) + 1
    else:
        next_number = 1
    print("\n[INFO] Next number:", next_number)

    student_id = input("\n[IEVADE] Ievadiet studenta apliecības numuru:")
    ref_link_base = input("\n[IEVADE] Ievadiet atsauces linka sākumu bez numerācijas:")
    image_count = int(input("\n[IEVADE] Ievadiet attēlu skaitu:"))

    fill_profila_bildes_table(parser, ref_link_base, image_count, next_number)
    print("\n[INFO] Records inserted in profila_bildes.")

    image_id = next_number
    for i in range(image_count):
        fill_bildes_savienojumi_table(parser, image_id, student_id)
        image_id = image_id + 1
    print("\n[INFO] Records inserted in bildes_savienojumi.")

    print("\n[INFO] Success!")

main()