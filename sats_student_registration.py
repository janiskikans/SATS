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
from pympler.tracker import SummaryTracker

tracker = SummaryTracker()
sleep_time = 10

# Config file import
parser = ConfigParser()
parser.read('./config/dev_settings_local.ini')

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

def register_student(student_id, auditorium, lesson_id):
    # MySQL connection details
    mydb = mysql.connector.connect(
        host = parser.get('db', 'db_host'),
        user = parser.get('db', 'db_user'),
        passwd = parser.get('db', 'db_passwd'),
        database = parser.get('db', 'db_database')
    )

    mycursor = mydb.cursor()

    sql_query = """INSERT INTO studentu_uzskaite (apliecibas_numurs, registracijas_laiks, telpas_numurs, nodarbibas_id)
    VALUES (%s, %s, %s, %s)"""
    current_time_date = datetime.datetime.now().strftime("%Y-%m-%d %H:%M:%S")
    print("[REGISTRATION] Registration time:", current_time_date)
    values = (student_id, current_time_date, auditorium, lesson_id) #2019-03-19 12:57:00

    mycursor.execute(sql_query, values)
    mydb.commit()
    mydb.close()
    print("[REGISTRATION]", mycursor.rowcount, "record inserted!")

def recognition_cam(encodings_file = "encodings.pickle", display = 1, detection_method = "hog", output = "", auditorium = "Not specified", webcam_select = 0):
    print("\n[INFO] Loading encodings...")

    # Loading the known faces and encodings from pickle dump
    data = pickle.loads(open(encodings_file, "rb").read())

    print("[INFO] Starting video stream...")
    vs = VideoStream(src = webcam_select).start()
    writer = None
    time.sleep(2.0)

    try:
        while True:
            print("\n[INFO] Checking lesson...")
            check_lesson(auditorium = auditorium)
            if lesson_status is True:
                print("[INFO] Current lesson: %s (Kursa numurs: %s): \nTelpa: %s\nDatums: %s\nSakuma laiks: %s\nBeigu laiks: %s\nPasn. vārds: %s\nuPasn. uzvārds: %s" % (lesson_id, lessson_course_number, lesson_auditorium, lesson_date, lesson_start_time, lesson_end_time, lesson_teacher_name, lesson_teacher_surname))

            while lesson_status == True:
                check_lesson(auditorium = auditorium)
                
                frame = vs.read()
                rgb = cv2.cvtColor(frame, cv2.COLOR_BGR2RGB)
                rgb = imutils.resize(frame, width = 450)
                r = frame.shape[1] / float(rgb.shape[1]) # Rescale

                boxes = face_recognition.face_locations(rgb, model = detection_method)
                encodings = face_recognition.face_encodings(rgb, boxes)

                names = []
                
                for encoding in encodings:
                    matches = face_recognition.compare_faces(data["encodings"], encoding)
                    name = "Unknown"

                    if True in matches:
                        matchedIdxs = [i for (i, b) in enumerate(matches) if b]
                        counts = {}

                        # Loop over the matched indexes and maintain a count for each recognized face
                        for i in matchedIdxs:
                            name = data["ids"][i]
                            counts[name] = counts.get(name, 0) + 1
                    
                        # Determine the recognized face with the largest number of votes (note: in the event of unlikely tie Python will select firt entry in the dictionary)
                        name = max(counts, key=counts.get)
                
                    # Update the list of student ids
                    names.append(name)
                    print("\n[RECOGNITION] Recognized ID:", name)

                    if name not in reg_student_list and name != "Unknown":
                        reg_student_list.append(name)
                        register_student(name, auditorium, lesson_id)
                    elif name in reg_student_list:
                        print("[RECOGNITION] Student already in list!")
                    else:
                        print("[RECOGNITION] Not recognized!")

                # Loop over the recognized faces
                for ((top, right, bottom, left), name) in zip(boxes, names):
                    # rescale the face coordinates
                    top = int(top * r)
                    right = int(right * r)
                    bottom = int(bottom * r)
                    left = int(left * r)

                    # Draw the predicted face name on the image
                    cv2.rectangle(frame, (left, top), (right, bottom), (0, 255, 0), 2)
                    y = top - 15 if top - 15 > 15 else top + 15
                    cv2.putText(frame, "ID:" + name, (left, y), cv2.FONT_HERSHEY_SIMPLEX, 0.75, (0, 255, 0), 2)

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

            time.sleep(sleep_time)

    except KeyboardInterrupt:
        tracker.print_diff()
        vs.stop()
        pass

    cv2.destroyAllWindows()

    if writer is not None:
        writer.release()


def check_lesson(auditorium): # Checks what lesson is happening in selected auditorium at the time
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
    #print("[TEST] Current time and date, auditorium:", str(current_date), str(current_time), auditorium)
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
        print("[INFO] No current lesson found! Not checking attendance. Sleeping for %s seconds..." %(int(sleep_time)))

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

def print_list(input_list):
    for items in input_list:
        print(items, sep='\n')

if __name__ == "__main__":
    recognition_cam()
    register_student()
    check_lesson()
    print_list()
    clear_current_class_vars()