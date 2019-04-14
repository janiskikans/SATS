from configparser import ConfigParser
import mysql.connector
import os
import datetime
import face_recognition
from imutils.video import VideoStream
import imutils
import pickle
import time
import cv2
import numpy as np
from pympler.tracker import SummaryTracker
from PIL import Image

tracker = SummaryTracker()
sleep_time = 10

# Current lesson vars
lesson_id = "Null"
lessson_course_number = "Null"
lesson_auditorium = "Null"
lesson_date = "Null"
lesson_start_time = "Null"
lesson_end_time = "Null"
lesson_teacher_name = "Null"
lesson_teacher_surname = "Null"
lesson_status = False
reg_student_list = [] # Registered student id list. Empties before every new class.

def register_student(student_id, auditorium, lesson_id, parser):
    # MySQL connection details
    mydb = mysql.connector.connect(
        host = parser.get('db', 'db_host'),
        user = parser.get('db', 'db_user'),
        passwd = parser.get('db', 'db_passwd'),
        database = parser.get('db', 'db_database')
    )

    mycursor = mydb.cursor()

    sql_query_insert = """INSERT INTO studentu_uzskaite (apliecibas_numurs, registracijas_laiks, telpas_numurs, nodarbibas_id)
    VALUES (%s, %s, %s, %s)"""

    current_time_date = datetime.datetime.now().strftime("%Y-%m-%d %H:%M:%S")
    values_insert = (student_id, current_time_date, auditorium, lesson_id) #2019-03-19 12:57:00

    mycursor.execute(sql_query_insert, values_insert)

    sql_query_get_student_name = """SELECT uzvards, vards FROM studenti WHERE apliecibas_numurs = %s"""
    mycursor.execute(sql_query_get_student_name, (student_id,))
    student_name = mycursor.fetchall()

    for row in student_name:
        print("[JAUNA REĢISTRĀCIJA] Reģistrācijas laiks: {0} ({1}, {2})".format(current_time_date, row[0], row[1]))

    mydb.commit()
    mydb.close()
    #print("[REGISTRATION]", mycursor.rowcount, "record inserted!")

def recognition_cam(dev_settings_loc, encodings_file = "encodings.pickle", display = 1, detection_method = "hog", output = "", auditorium = "Not specified", webcam_select = 0):
    # Config file import
    parser = ConfigParser()
    parser.read(dev_settings_loc)

    unknow_face_save = parser.get('sats_setting_vars', 'unknown_face_save')
    unknown_face_save_loc = parser.get('sats_setting_vars', 'unknown_face_save_loc')

    print("\n[INFO] Ielādē kodējumus...")

    # Loading the known faces and encodings from pickle dump
    data = pickle.loads(open(encodings_file, "rb").read())

    print("[INFO] Iegūst video straumi...")
    vs = VideoStream(src = webcam_select).start()
    writer = None
    time.sleep(2.0)

    try:
        while True:
            print("\n[INFO] Pārbauda nodarbības...")
            check_lesson(parser, auditorium = auditorium)
            if lesson_status is True:
                print("[INFO] Šobrīd notiekošā nodarbība: %s (Kursa numurs: %s): \nTelpa: %s\nDatums: %s\nSakuma laiks: %s\nBeigu laiks: %s\nPasn. vārds: %s\nPasn. uzvārds: %s" % (lesson_id, lessson_course_number, lesson_auditorium, lesson_date, lesson_start_time, lesson_end_time, lesson_teacher_name, lesson_teacher_surname))

            while lesson_status == True:
                check_lesson(parser, auditorium = auditorium)
                
                frame = vs.read()
                rgb = cv2.cvtColor(frame, cv2.COLOR_BGR2RGB)
                rgb = imutils.resize(frame, width = 450)
                r = frame.shape[1] / float(rgb.shape[1]) # Rescale

                boxes = face_recognition.face_locations(rgb, model = detection_method)
                encodings = face_recognition.face_encodings(rgb, boxes)

                names = []
                
                for encoding in encodings:
                    matches = face_recognition.compare_faces(data["encodings"], encoding)
                    face_distances = face_recognition.face_distance(data["encodings"], encoding)
                    name = "Unknown"

                    if True in matches:
                        matchedIdxs = [i for (i, b) in enumerate(matches) if b]
                        counts = {}

                        # Loop over the matched indexes and maintain a count for each recognized face
                        for i in matchedIdxs:
                            name = data["ids"][i]
                            counts[name] = counts.get(name, 0) + 1
                    
                        # Determine the recognized face with the largest number of votes (note: in the event of unlikely tie Python will select firt entry in the dictionary)
                        name = max(counts, key = counts.get)
                
                    # Update the list of student ids
                    names.append(name)

                    #print("[INFO] Distances: ", face_distances)
                    closestImage = np.amin(face_distances)

                    if name != "Unknown":
                        print("\n[IDENTIFIKĀCIJA] Identificētais apliecības nr.: {0} (Ar Eiklīda distanci {1:.2f})".format(name, closestImage))
                    else:
                        print("\n[IDENTIFIKĀCIJA] Identificētais apliecības nr.: {0} (Ar Eiklīda distanci no tuvākā atbilstošā studenta {1:.2f})".format(name, closestImage))

                    fetch_registered_student_list(lesson_id, parser) # Fetch current registred student list

                    if name not in reg_student_list and name != "Unknown":
                        #reg_student_list.append(name)
                        register_student(name, auditorium, lesson_id, parser)

                    elif name in reg_student_list:
                        print("[IDENTIFIKĀCIJA] Students jau ir reģistrēts apmeklējuma sarakstā!")
                    else:
                        if unknow_face_save == "True":
                            for face_location in boxes:
                                top, right, bottom, left = face_location
                                face_image = rgb[top:bottom, left:right]
                                pil_image = Image.fromarray(face_image)

                                current_time = datetime.datetime.now()
                                file_name = "nezinams_" + current_time.strftime("%Y%m%d_%H%M%S") + "_" + auditorium + ".jpeg"
                                
                                os.chdir("%s" %str(unknown_face_save_loc))
                                pil_image.save(file_name, "JPEG")
                                os.chdir('..')

                                print("[IMAGE SAVE] Attēls {0} saglabāts!".format(file_name))

                        print("[IDENTIFIKĀCIJA] Nav identificēts!")

                # Loop over the recognized faces
                for ((top, right, bottom, left), name) in zip(boxes, names):
                    # rescale the face coordinates
                    top = int(top * r)
                    right = int(right * r)
                    bottom = int(bottom * r)
                    left = int(left * r)

                    # Draw the predicted face name on the image
                    cv2.rectangle(frame, (left, top), (right, bottom), (0, 0, 255), 2)
                    y = top - 15 if top - 15 > 15 else top + 15
                    cv2.putText(frame, "ID:" + name, (left, y), cv2.FONT_HERSHEY_DUPLEX, 0.75, (255, 255, 255), 2)

                if writer is None and output is not None:
                    fourcc = cv2.VideoWriter_fourcc(*"MJPG")
                    writer = cv2.VideoWriter(output, fourcc, 20, (frame.shape[1], frame.shape[0]), True)

                if writer is not None:
                    writer.write(frame)

                if display > 0:
                    cv2.imshow("Frame", frame)
                    key = cv2.waitKey(1) & 0xFF

                    if key == ord("q"):
                        break

                time.sleep(1)

            time.sleep(sleep_time)

    except KeyboardInterrupt:
        tracker.print_diff()
        vs.stop()
        cv2.destroyAllWindows()
        pass

    if writer is not None:
        writer.release()


def check_lesson(parser, auditorium): # Checks what lesson is happening in selected auditorium at the time
    global lesson_id
    global lessson_course_number
    global lesson_auditorium
    global lesson_date
    global lesson_start_time
    global lesson_end_time
    global lesson_status
    global lesson_teacher_name
    global lesson_teacher_surname
    
    # MySQL connection details
    mydb = mysql.connector.connect(
        host = parser.get('db', 'db_host'),
        user = parser.get('db', 'db_user'),
        passwd = parser.get('db', 'db_passwd'),
        database = parser.get('db', 'db_database')
    )

    lesson_check_cursor = mydb.cursor()
    #sql_query = "SELECT nodarbibas_id, kursa_numurs, telpa, datums, sakuma_laiks, beigu_laiks FROM bakalaurs.nodarbibas WHERE datums = %s AND %s BETWEEN SUBTIME(sakuma_laiks, '0:10:0.000000') AND beigu_laiks AND telpa = %s"
    sql_query = "SELECT n.nodarbibas_id, n.kursa_numurs, n.telpa, n.datums, n.sakuma_laiks, n.beigu_laiks, p.pasniedzeja_vards, p.pasniedzeja_uzvards FROM macisanas_saraksts AS m INNER JOIN nodarbibas AS n ON m.nodarbibas_id = n.nodarbibas_id INNER JOIN pasniedzeji AS p ON m.pasniedzeja_id = p.pasniedzeja_id WHERE n.datums = %s AND %s BETWEEN SUBTIME(n.sakuma_laiks, '0:10:0.000000') AND n.beigu_laiks AND n.telpa = %s"
    current_date = datetime.datetime.now().strftime("%Y-%m-%d")
    current_time = datetime.datetime.now().strftime("%H:%M:%S")

    values = (current_date, current_time, auditorium)

    lesson_check_cursor.execute(sql_query, values)
    myresult = lesson_check_cursor.fetchall()
    #print("[TEST] Last query:", lesson_check_cursor.statement)
    #print('[MYSQL] Lessons found:', lesson_check_cursor.rowcount)

    if lesson_check_cursor.rowcount > 0:
        lesson_status = True
        for row in myresult:
            #print(row[0], row[1], row[2], row[3], row[4], row[5]) 
            lesson_id = row[0]
            lessson_course_number = row[1]
            lesson_auditorium = row[2]
            lesson_date = row[3]
            lesson_start_time = row[4]
            lesson_end_time = row[5]
            lesson_teacher_name = row[6]
            lesson_teacher_surname = row[7]
    else:
        lesson_status = False
        clear_current_class_vars()
        print("[INFO] Netika atrasta šobrīd notiekoša nodarbība! Netiek veikta apmeklējuma uzskaite. Nav aktīvs uz  %s sekundēm.." %(int(sleep_time)))

    mydb.close()

def clear_current_class_vars():
    global lesson_id
    global lessson_course_number
    global lesson_auditorium
    global lesson_date
    global lesson_start_time
    global lesson_end_time
    global lesson_status
    global lesson_teacher_name
    global lesson_teacher_surname
    global reg_student_list

    reg_student_list.clear()
    lesson_id = "Null"
    lessson_course_number = "Null"
    lesson_auditorium = "Null"
    lesson_date = "Null"
    lesson_start_time = "Null"
    lesson_end_time = "Null"
    lesson_teacher_name = "Null"
    lesson_teacher_surname = "Null"

def fetch_registered_student_list(lesson_id, parser):
    global reg_student_list

    mydb = mysql.connector.connect(
        host = parser.get('db', 'db_host'),
        user = parser.get('db', 'db_user'),
        passwd = parser.get('db', 'db_passwd'),
        database = parser.get('db', 'db_database')
    )

    reg_student_list_cursor = mydb.cursor()
    sql_query = """SELECT apliecibas_numurs FROM studentu_uzskaite WHERE nodarbibas_id = %s"""

    reg_student_list_cursor.execute(sql_query, (lesson_id,))
    rows = reg_student_list_cursor.fetchall()

    reg_student_list.clear()

    for row in rows:
        reg_student_list.append(row[0])

    mydb.close()


def print_list(input_list):
    for items in input_list:
        print(items, sep='\n')

if __name__ == "__main__":
    recognition_cam()
    register_student()
    check_lesson()
    print_list()
    clear_current_class_vars()