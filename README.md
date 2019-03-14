# SATS
*Student Attendance Tracking System*

## About .py scripts
Script | Function | Status
---------|---------- | ----------
sats_**encode_faces.py** | Encodes faces from dataset images to .pickle file | **Working**
sats_**ftp_retrieve_stud_images.py** | Retrieves image references from MySQL database and then retrieves .jpg images from FTP server. MySQL and FTP server config located in **\config** folder (.ini files). | **Working**
sats_**recognize_faces_cam.py** | Uses .pickle file to recognize and identify students in a webcam stream. | **Not completed.** Needs to integrate in main .py script without run args.