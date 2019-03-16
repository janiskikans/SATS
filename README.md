# SATS
*Student Attendance Tracking System*

## About .py scripts
Script (:heavy_exclamation_mark: - main modules) | Function | Status
---------|---------- | ----------
sats_**encode_faces.py** | Encodes faces from dataset images to .pickle file | **Working**
sats_**ftp_retrieve_stud_images.py** :heavy_exclamation_mark: | Retrieves image references from MySQL database and then retrieves .jpg images from FTP server. Then optionally cals **encode_faces.py** script. MySQL and FTP server config located in **\config** folder (.ini files). | **Working**
sats_**recognize_faces_cam.py** | Uses .pickle dump to recognize and identify students in a webcam stream. | **Completed. Not in use.**
**sats_client.py** :heavy_exclamation_mark:| Main module of the program. Gives user menu of possible choices. Launches scripts associated with them. | **Working. In progress.**
sats_**client_functions.py** | Seperated functions from **sats_client.py** for easier managing. | **Working. In progress.**
sats_**student_registration.py** :heavy_exclamation_mark:| Takes webcam stream, identifies students and logs attendance details in MySQL database. | **Working. In progress.**