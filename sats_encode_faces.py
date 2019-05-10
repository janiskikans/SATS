from imutils import paths
import face_recognition
import pickle
import cv2
import os

# Encode the retrieved student face images and save them in a .pickle file.
def encode_faces(dataset_dir = "dataset", encodings_file = "encodings.pickle", detection_method = "hog"):
    # Retrieve the list of retrieved image file paths.
    print("\n[MĒRĪJUMU IEGUVE] Skaita bildes...")
    imagePaths = list(paths.list_images(dataset_dir))

    # Initialize the lists of know face encodings and known student IDs.
    knownEncodings = []
    knownIDS = []

    # Loop over all the found dataset images, get their associated student ID numbers, get face locations and encodings.
    for (i, imagePath) in enumerate(imagePaths):
        # Getting student ID from the image path.
        print("[MĒRĪJUMU IEGUVE] Apstrādā attēlu {}/{} ar apliecības numuru '{}'".format(i + 1, len(imagePaths), imagePath.split(os.path.sep)[-2]))
        student_id = imagePath.split(os.path.sep)[-2]

        # Load the input image and convert it from BGR color space RGB color space for dlib.
        image = cv2.imread(imagePath)
        rgb = cv2.cvtColor(image, cv2.COLOR_BGR2RGB)

        # Detect coordinates (x, y) of bounding boxes for each recognized face in the image.
        # CNN method - slower, but more accurate; HOG method - faster, but less accurate.
        bounding_boxes = face_recognition.face_locations(rgb, model = detection_method)

        # Compute the facial embedding for the recognized faces in the image.
        encodings = face_recognition.face_encodings(rgb, bounding_boxes)

        # Loop over the retrieved encodings.
        for encoding in encodings:
            # Append the knownEncodings and knownIDS lists with corresponding values.
            knownEncodings.append(encoding)
            knownIDS.append(student_id)

    # Seriaize knownEncodings and knownIDS lists to a .pickle file.
    print("[MĒRĪJUMU IEGUVE] Serializē kodējumus...")
    data = {"encodings": knownEncodings, "ids": knownIDS} # Create dictionary with "encodings" and "ids" keys.

    # Dump data dictionary to .pickle file.
    f = open(encodings_file, "wb")
    f.write(pickle.dumps(data))
    f.close()

    print("[MĒRĪJUMU IEGUVE] Pabeigts!")

if __name__ == "__main__":
    encode_faces()