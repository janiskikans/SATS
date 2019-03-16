# SATS main client program. 
import datetime
import sats_client_functions
from sats_student_registration import recognition_cam

print("\nSATS Main Client By Janis Kikans\n", datetime.datetime.now().strftime('%Y-%m-%d %H:%M:%S'), sep=" | ")

loop = True
while loop:
    sats_client_functions.print_menu()
    choice = input("Enter your choice [1-3]:")
    choice = int(choice)

    if choice == 1:
        print("Starting script...\n")
    elif choice == 2:
        print("Starting script...\n")
        auditorium_input = input("[INPUT] Enter auditorium number:")
        auditorium_input = str(auditorium_input)
        recognition_cam(encodings_file = "encodings.pickle", display = 0, detection_method = "hog", auditorium = auditorium_input)
        break
    elif choice == 3:
        loop = False
    else:
        print("Wrong option selection. Enter any key to try again..")