import datetime
from configparser import ConfigParser
import sats_client_functions # Main menu printout and currently used settings printout.
from sats_student_registration import recognition_cam # Runs automatic student recognition using face recognition from webcam.
from get_student_attendance import get_all_attendance_data, get_attendance_by_lesson_id, get_all_attendance_of_student # Retrieve student attendance data from MySQL database.
from sats_ftp_retrieve_stud_images import ftp_retrieve_stud_images_main # Retrieve student images from FTP server.
import sats_manual_attendance # Enter attendance data manually. Delete specific attendance record.
import sats_auditorium_lesson_info # Information about what lessons are happening in selected auditorium today.

# Globals
config_file_loc = './config/dev_settings.ini'

# Main script start
print("\nSATS Main Client By Janis Kikans", datetime.datetime.now().strftime('%Y-%m-%d %H:%M:%S'), sep=" | ")

loop = True
while loop:
    # Print menu items.
    sats_client_functions.print_menu()
    choice = input("Ievadiet Jūsu izvēli [1-10]: ")

    choice = int(choice)

    if choice == 1:
        # Retrieve student images from FTP server and suggest retrieved face encoding.
        ftp_retrieve_stud_images_main(config_file_loc)
    elif choice == 2:
        # Initiate automatic student recognition and registration.
        auditorium_input = input("[IEVADE] Ievadiet telpas numuru: ")
        auditorium_input = str(auditorium_input)
        
        while True:
            try:
                webcam_input = int(input("\n[IEVADE] Izvēlieties ieejas kameru (Iebūvētā kamera - 0; Ārējā kamera - 1): "))
                break
            except:
                print("[KĻŪDA] Nepareiza ievade")
                
            if (webcam_input == 0) or (webcam_input == 1):
                continue
            else:
                print("[KĻŪDA] Nepareiza kameras izvēle!")

        recognition_cam(config_file_loc, encodings_file = "encodings.pickle", detection_method = "hog", auditorium = auditorium_input, webcam_select = webcam_input)
    elif choice == 3:
        # Call script to enter attendance data manually.
        sats_manual_attendance.manual_attendance(config_file_loc)
    elif choice == 4:
        # Call script to retrieve all attendance data from database without filtering.
        parser = ConfigParser()
        parser.read(config_file_loc)

        html_save_loc = parser.get('sats_setting_vars', 'html_save_loc')
        html_report_save_toggle = parser.get('sats_setting_vars', 'html_report_save_toggle')

        get_all_attendance_data(config_file_loc, html_save_loc, html_report_save_toggle)
    elif choice == 5:
        # Call script to retrieve attendance information of specific lesson.
        parser = ConfigParser()
        parser.read(config_file_loc)

        html_save_loc = parser.get('sats_setting_vars', 'html_save_loc')
        html_report_save_toggle = parser.get('sats_setting_vars', 'html_report_save_toggle')

        lesson_id_input = str(input("\n[IEVADE] Ievadiet nodarbības ID: "))

        get_attendance_by_lesson_id(lesson_id_input, config_file_loc, html_save_loc, html_report_save_toggle)
    elif choice == 6:
        # Call script to retrieve attendance information of specific student.
        parser = ConfigParser()
        parser.read(config_file_loc)

        html_save_loc = parser.get('sats_setting_vars', 'html_save_loc')
        html_report_save_toggle = parser.get('sats_setting_vars', 'html_report_save_toggle')

        student_id_input = input("\n[IEVADE] Ievadiet studenta ID: ")
        student_id_input = str(student_id_input)

        get_all_attendance_of_student(student_id_input, config_file_loc, html_save_loc, html_report_save_toggle)
    elif choice == 7:
        # Call script to retrieve information about what lessons are happening today in the selected auditorium.
        auditorium_input = input("\n[IEVADE] Ievadiet telpas numuru: ")
        auditorium_input = str(auditorium_input)

        sats_auditorium_lesson_info.get_auditorium_lesson_list(auditorium_input, config_file_loc)
    elif choice == 8:
        # Call script to delete specific attendance record by it's ID.
        attendance_record_id_input = int(input("\n[IEVADE] Ievadiet dzēšamā apmeklējuma ieraksta ID: "))

        sats_manual_attendance.delete_attendance_record(attendance_record_id_input, config_file_loc)
    elif choice == 9:
        # Call script to printout currently used settings.
        sats_client_functions.print_used_settings(config_file_loc)
    elif choice == 10:
        # Terminate application.
        print("[INFO] Iziet no SATS..\n")
        loop = False
    else:
        print("[KĻŪDA] Nepareiza izvēle. Mēģiniet vēlreiz!")