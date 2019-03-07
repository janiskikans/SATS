# SATS main client program. 
import datetime
import sats_client_functions

print("SATS Main Client By Janis Kikans", datetime.datetime.now().strftime('%Y-%m-%d %H:%M:%S'), sep=" | ")

loop = True
while loop:
    sats_client_functions.print_menu()
    choice = input("Enter your choice [1-2]:")
    choice = int(choice)

    if choice == 1:
        print("Running sats_rec_model_training.py")
    elif choice == 2:
        loop = False
    else:
        print("Wrong option selection. Enter any key to try again..")