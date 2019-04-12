# SATS main client program. 
import datetime
import sats_client_functions
from sats_student_registration import recognition_cam
from get_student_attendance import get_all_attendance_data, get_attendance_by_lesson_id, get_all_attendance_of_student
from sats_ftp_retrieve_stud_images import ftp_retrieve_stud_images_main
import sats_manual_attendance # Enter attendance data manually.
import sats_auditorium_lesson_info # Information about what lessons are happening in selected auditorium today.

# Globals
config_file_loc = './config/dev_settings_lnb.ini'

# Main script start
print("\nSATS Main Client By Janis Kikans", datetime.datetime.now().strftime('%Y-%m-%d %H:%M:%S'), sep=" | ")

loop = True
while loop:
    sats_client_functions.print_menu()
    choice = input("Ievadiet Jūsu izvēli [1-8]:")
    choice = int(choice)

    if choice == 1:
        ftp_retrieve_stud_images_main(config_file_loc)
    elif choice == 2:
        # Jāievieto pārbaude par to vai ir pieejams "encodings.pickle" fails. Ja nē, tad izmet uz galveno loop ar error message.

        #auditorium_input = input("[INPUT] Enter auditorium number:")
        auditorium_input = input("[IEVADE] Ievadiet telpas numuru:")
        auditorium_input = str(auditorium_input)
        
        while True:
            try:
                webcam_input = int(input("\n[IEVADE] Izvēlieties ieejas kameru (Iebūvētā kamera - 0; Ārējā kamera - 1):"))
                break
            except:
                print("[KĻŪDA] Nepareiza ievade")
                
            if (webcam_input == 0) or (webcam_input == 1):
                continue
            else:
                print("[KĻŪDA] Nepareiza kameras izvēle!")

        recognition_cam(config_file_loc, encodings_file = "encodings.pickle", display = 0, detection_method = "hog", auditorium = auditorium_input, webcam_select = webcam_input)
        
    elif choice == 3:
        sats_manual_attendance.manual_attendance(config_file_loc)
    elif choice == 4:
        get_all_attendance_data(config_file_loc)
    elif choice == 5:
        lesson_id_input = str(input("\n[IEVADE] Ievadiet nodarbības ID:"))
        get_attendance_by_lesson_id(lesson_id_input, config_file_loc)
        """ try:
            lesson_id_input = str(input("\n[INPUT] Enter lesson ID:"))
            get_attendance_by_lesson_id(lesson_id_input)
        except:
            print("[ERROR] There was a problem retrieving attendance data. Try again.") """
    elif choice == 6:
        student_id_input = input("\n[IEVADE] Ievadiet studenta ID:")
        student_id_input = str(student_id_input)
        get_all_attendance_of_student(student_id_input, config_file_loc)
    elif choice == 7:
        auditorium_input = input("\n[IEVADE] Ievadiet telpas numuru:")
        auditorium_input = str(auditorium_input)

        sats_auditorium_lesson_info.get_auditorium_lesson_list(auditorium_input, config_file_loc)
    elif choice == 8:
        print("[INFO] Iziet no SATS..")
        loop = False
    else:
        print("[KĻŪDA] Nepareiza izvēle. Mēģiniet vēlreiz!")