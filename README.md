# SATS
*Student Attendance Tracking System*

## About .py scripts
Script (:heavy_exclamation_mark: - main module) | Function | Status
---------|---------- | ----------
**sats_client.py** :heavy_exclamation_mark:| Main module of the program. Gives user menu of possible choices. Launches scripts associated with them. | **Working**
sats_**client_functions.py** | Seperated functions from **sats_client.py** for easier managing. Includes *main menu printout* and used *SATS settings* printout. | **Working**
sats_**ftp_retrieve_stud_images.py**| Retrieves image references from MySQL database and then retrieves .jpg images from FTP server. Then optionally cals **encode_faces.py** script. MySQL and FTP server config located in **\config** folder (.ini files). | **Working**
sats_**encode_faces.py** | Encodes faces from dataset images to .pickle file | **Working**
sats_**student_registration.py**| Takes webcam stream, identifies students and logs attendance details in MySQL database. | **Working**
sats_**auditorium_lesson_info.py**| Retreives info about what lessons are happening in the selected auditorium in the current day. | **Working**
sats_**manual_attendance.py**| Allows to enter attendance data manually. Currently password **is not protected** in any way. | **Working**
sats_**get_student_attendance.py**| Allows to get information about specific students attendance data, specific lesson's attendance data or all attendance data from MySQL database. | **Working**

**Last update on 14.04.19.*