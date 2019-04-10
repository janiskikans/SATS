# SATS main client program. 
import datetime
import sats_client_functions
from sats_student_registration import recognition_cam
from get_student_attendance import get_all_attendance_data, get_attendance_by_lesson_id
from sats_ftp_retrieve_stud_images import ftp_retrieve_stud_images_main
import sats_manual_attendance # Enter attendance data manually.
import sats_auditorium_lesson_info # Information about what lessons are happening in selected auditorium today.

# Main script start
print("\nSATS Main Client By Janis Kikans", datetime.datetime.now().strftime('%Y-%m-%d %H:%M:%S'), sep=" | ")

loop = True
while loop:
    sats_client_functions.print_menu()
    choice = input("Enter your choice [1-7]:")
    choice = int(choice)

    if choice == 1:
        print("[INFO] Starting script..\n")
        ftp_retrieve_stud_images_main()
    elif choice == 2:
        # Jāievieto pārbaude par to vai ir pieejams "encodings.pickle" fails. Ja nē, tad izmet uz galveno loop ar error message.

        print("[INFO] Starting script..\n")
        auditorium_input = input("[INPUT] Enter auditorium number:")
        auditorium_input = str(auditorium_input)
        
        while True:
            try:
                webcam_input = int(input("\n[INPUT] Select input webcam (In-built webcam - 0; External webcam - 1):"))
                break
            except:
                print("[ERROR] Invalid input")
                
            if (webcam_input == 0) or (webcam_input == 1):
                continue
            else:
                print("[ERROR] Invalid webcam selection!")

        recognition_cam(encodings_file = "encodings.pickle", display = 0, detection_method = "hog", auditorium = auditorium_input, webcam_select = webcam_input)
    elif choice == 3:
        print("[INFO] Starting script..\n")
        sats_manual_attendance.manual_attendance()
    elif choice == 4:
        print("[INFO] Starting script..\n")
        get_all_attendance_data()
    elif choice == 5:
        print("[INFO] Starting script..\n")
        lesson_id_input = str(input("\n[INPUT] Enter lesson ID:"))
        get_attendance_by_lesson_id(lesson_id_input)
        """ try:
            lesson_id_input = str(input("\n[INPUT] Enter lesson ID:"))
            get_attendance_by_lesson_id(lesson_id_input)
        except:
            print("[ERROR] There was a problem retrieving attendance data. Try again.") """
    elif choice == 6:
        print("\n[INFO] Starting script..")
        auditorium_input = input("\n[INPUT] Enter auditorium number:")
        auditorium_input = str(auditorium_input)

        sats_auditorium_lesson_info.get_auditorium_lesson_list(auditorium_input)
    elif choice == 7:
        print("[INFO] Exitting SATS..")
        loop = False
    else:
        print("[ERROR] Invalid option selection. Enter any key to try again..")