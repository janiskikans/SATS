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

# Memory stats tracker. For dev purposes.
tracker = SummaryTracker()
# Sleep time variable in the case of no current lesson found.
sleep_time = 10

# Current lesson gobal variables.
lesson_id = "Null"
lessson_course_number = "Null"
lesson_auditorium = "Null"
lesson_date = "Null"
lesson_start_time = "Null"
lesson_end_time = "Null"
lesson_teacher_name = "Null"
lesson_teacher_surname = "Null"
lesson_status = False
reg_student_list = [] # Registered student id list. Empties before every new lesson.

# Register the identified student's attendance.
def register_student(student_id, auditorium, lesson_id, parser):
    # MySQL connection details.
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

# Main function that runs automatic student identification and registration.
def recognition_cam(dev_settings_loc, encodings_file = "encodings.pickle", detection_method = "hog", output = "", auditorium = "Not specified", webcam_select = 0):
    # Config file import.
    parser = ConfigParser()
    parser.read(dev_settings_loc)
    # Load the setting parameters for unknown face image saving.
    unknow_face_save = parser.get('sats_setting_vars', 'unknown_face_save')
    unknown_face_save_loc = parser.get('sats_setting_vars', 'unknown_face_save_loc')
    recognition_tolerance = parser.getfloat('sats_setting_vars', 'recognition_tolerance_level')
    visualize_recognition = parser.getint('sats_setting_vars', 'visualize_recognition')

    print("\n[INFO] Ielādē studentu informāciju...")

    # Load the data dictionaries that hold known student face encodings and IDs.
    data = pickle.loads(open(encodings_file, "rb").read())

    print("[INFO] Iegūst video straumi...")
    vs = VideoStream(src = webcam_select).start()
    writer = None
    time.sleep(2.0)

    try:
        while True:
            # Check current lesson status.
            print("\n[INFO] Pārbauda nodarbības...")
            check_lesson(parser, auditorium = auditorium)
            if lesson_status is True:
                print("[INFO] Šobrīd notiekošā nodarbība: %s (Kursa numurs: %s): \nTelpa: %s\nDatums: %s\nSakuma laiks: %s\nBeigu laiks: %s\nPasn. vārds: %s\nPasn. uzvārds: %s" % (lesson_id, lessson_course_number, lesson_auditorium, lesson_date, lesson_start_time, lesson_end_time, lesson_teacher_name, lesson_teacher_surname))

            # While there's an active lesson start student identification and registration.
            while lesson_status == True:
                # Check lesson status.
                check_lesson(parser, auditorium = auditorium)
                
                frame = vs.read()
                rgb = cv2.cvtColor(frame, cv2.COLOR_BGR2RGB)
                rgb = imutils.resize(frame, width = 450) # Resize input image from the webcam to the width of 450px.
                r = frame.shape[1] / float(rgb.shape[1]) # Rescale value.

                # Find faces in the input image rgb and get their bounding boxes.
                bounding_boxes = face_recognition.face_locations(rgb, model = detection_method)
                # Get recognized face encodings.
                encodings = face_recognition.face_encodings(rgb, bounding_boxes)

                # Initialize the list of student IDs.
                student_ids = []
                
                # While going through found faces compare them to the known encodings.
                for encoding in encodings:
                    # Compare recognized faces in the webcam stream to the known student encodings.
                    matches = face_recognition.compare_faces(data["encodings"], encoding, recognition_tolerance)
                    # Get the face encoding distances for the recognized face.
                    face_distances = face_recognition.face_distance(data["encodings"], encoding)
                    # Student ID number.
                    student_idn = "Unknown"
                    # If there's a match to a know encoding determine which is the most plausable student.
                    if True in matches:
                        matchedIdxs = [i for (i, b) in enumerate(matches) if b]
                        # Vote count dictionary.
                        counts = {}

                        # Loop over the matched indexes and maintain a count for each recognized face.
                        for i in matchedIdxs:
                            student_idn = data["ids"][i]
                            counts[student_idn] = counts.get(student_idn, 0) + 1
                    
                        # Determine the most plausable recognized student face with the largest number of votes in the counts dictionary.
                        student_idn = max(counts, key = counts.get)
                
                    # Update the list of student ids
                    student_ids.append(student_idn)

                    # Print out the distance to the closest encoding.
                    #print("[INFO] Distances: ", face_distances)
                    closest_distance = np.amin(face_distances)

                    if student_idn != "Unknown":
                        print("\n[IDENTIFIKĀCIJA] Identificētais apliecības nr.: {0} (Ar Eiklīda distanci {1:.2f})".format(student_idn, closest_distance))
                    else:
                        print("\n[IDENTIFIKĀCIJA] Identificētais apliecības nr.: {0} (Ar Eiklīda distanci no tuvākā atbilstošā studenta {1:.2f})".format(student_idn, closest_distance))

                    fetch_registered_student_list(lesson_id, parser) # Fetch current registred student list from database.

                    # Register the attendace if it's not already registered and if student ID is not unknown.
                    if student_idn not in reg_student_list and student_idn != "Unknown":
                        register_student(student_idn, auditorium, lesson_id, parser)

                    elif student_idn in reg_student_list:
                        print("[IDENTIFIKĀCIJA] Students jau ir reģistrēts apmeklējuma sarakstā!")
                    else:
                        # Save unrecognized persons face image to a .jpeg image file. Only if option is enabled.
                        if unknow_face_save == "True":
                            for face_location in bounding_boxes:
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

                # Put resolution and datetime information at the top of output image frame.
                output_image_width = rgb.shape[1]
                output_image_height = rgb.shape[0]

                date_time_output_string = ("Laiks: {0}").format(datetime.datetime.now().strftime("%Y-%m-%d %H:%M:%S"))
                resolution_output_string = ("Kadra izskirtspeja: {0}, {1}").format(output_image_width, output_image_height)
                current_lesson_status_output_string = ("Nodarbibas statuss: {0}").format(lesson_status)
                current_lesson_id_output_string = ("Nodarbibas ID: {0}").format(lesson_id)

                cv2.putText(frame, date_time_output_string, (5, 15), cv2.FONT_HERSHEY_DUPLEX, 0.5, (255, 255, 255), 1)
                cv2.putText(frame, resolution_output_string, (5, 35), cv2.FONT_HERSHEY_DUPLEX, 0.5, (255, 255, 255), 1)
                cv2.putText(frame, current_lesson_status_output_string, (5, 55), cv2.FONT_HERSHEY_DUPLEX, 0.5, (255, 255, 255), 1)
                cv2.putText(frame, current_lesson_id_output_string, (5, 75), cv2.FONT_HERSHEY_DUPLEX, 0.5, (255, 255, 255), 1)

                # Loop over the recognized faces and draw their bounding boxes and student ID number in a OpenCV window.
                for ((top, right, bottom, left), student_idn) in zip(bounding_boxes, student_ids):
                    # rescale the face coordinates
                    top = int(top * r)
                    right = int(right * r)
                    bottom = int(bottom * r)
                    left = int(left * r)

                    # Draw the predicted student ID on the frame image.
                    cv2.rectangle(frame, (left, top), (right, bottom), (0, 0, 255), 2)
                    y = top - 15 if top - 15 > 15 else top + 15
                    cv2.putText(frame, "ID:" + student_idn, (left, y), cv2.FONT_HERSHEY_DUPLEX, 0.75, (255, 255, 255), 2)

                # Write video stream to a mjpeg file if option is enabled.
                if writer is None and output is not None:
                    fourcc = cv2.VideoWriter_fourcc(*"MJPG")
                    writer = cv2.VideoWriter(output, fourcc, 20, (frame.shape[1], frame.shape[0]), True)

                if writer is not None:
                    writer.write(frame)

                # Visualize identifaction process in a OpenCV window. Only if option is enabled.
                if visualize_recognition > 0:
                    cv2.imshow("SATS | Identifikacijas procesa vizualizacija", frame)
                    key = cv2.waitKey(1) & 0xFF

                    if key == ord("q"):
                        break

                time.sleep(0)

            time.sleep(sleep_time)

    # Exit recognition process if CTRL+C ir pressed.
    except KeyboardInterrupt:
        tracker.print_diff()
        vs.stop()
        cv2.destroyAllWindows()
        pass

    if writer is not None:
        writer.release()

# Checks what lesson is happening in selected auditorium at the time.
def check_lesson(parser, auditorium):
    global lesson_id
    global lessson_course_number
    global lesson_auditorium
    global lesson_date
    global lesson_start_time
    global lesson_end_time
    global lesson_status
    global lesson_teacher_name
    global lesson_teacher_surname
    
    # MySQL connection details.
    mydb = mysql.connector.connect(
        host = parser.get('db', 'db_host'),
        user = parser.get('db', 'db_user'),
        passwd = parser.get('db', 'db_passwd'),
        database = parser.get('db', 'db_database')
    )

    lesson_check_cursor = mydb.cursor()
    sql_query = "SELECT n.nodarbibas_id, n.kursa_numurs, n.telpa, n.datums, n.sakuma_laiks, n.beigu_laiks, p.pasniedzeja_vards, p.pasniedzeja_uzvards FROM macisanas_saraksts AS m INNER JOIN nodarbibas AS n ON m.nodarbibas_id = n.nodarbibas_id INNER JOIN pasniedzeji AS p ON m.pasniedzeja_id = p.pasniedzeja_id WHERE n.datums = %s AND %s BETWEEN SUBTIME(n.sakuma_laiks, '0:10:0.000000') AND n.beigu_laiks AND n.telpa = %s"
    current_date = datetime.datetime.now().strftime("%Y-%m-%d")
    current_time = datetime.datetime.now().strftime("%H:%M:%S")

    values = (current_date, current_time, auditorium)

    lesson_check_cursor.execute(sql_query, values)
    myresult = lesson_check_cursor.fetchall()

    # Print out lesson details if an actual lesson is found in the selected auditorium.
    if lesson_check_cursor.rowcount > 0:
        lesson_status = True
        for row in myresult:
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

# Clear global lesson variables if lesson changes.
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

# Retrieve already registered student ID list from MySQL data base.
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