# SATS main client program. 
import datetime
import sats_client_functions

print("SATS Main Client By Janis Kikans", datetime.datetime.now().strftime('%Y-%m-%d %H:%M:%S'), sep=" | ")

loop = True
while loop:
    sats_client_functions.print_menu()
    choice = input("Enter your choice [1-3]:")
    choice = int(choice)

    if choice == 1:
        print("Menu 1 has been selected")
    elif choice == 2:
        print("Menu 2 has been selected")
    elif choice == 3:
        loop = False
    else:
        print("Wrong option selection. Enter any key to try again..")