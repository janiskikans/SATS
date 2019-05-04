from imutils import paths
import face_recognition
import pickle
import cv2
import os

def encode_faces(dataset_dir = "dataset", encodings_file = "encodings.pickle", detection_method = "hog"):
    # Grab the paths to data set input images
    print("\n[MĒRĪJUMU IEGUVE] Skaita bildes...")
    imagePaths = list(paths.list_images(dataset_dir)) # Makes a list of all imagePaths contained in data set directory

    # Initialize the lists of know encodings and known IDS
    knownEncodings = []
    knownIDS = []

    # Looping over all the found dataset images
    for (i, imagePath) in enumerate(imagePaths):
        # Getting student id's from the image path
        print("[MĒRĪJUMU IEGUVE] Apstrādā bildi {}/{} ar apliecības numuru '{}'".format(i + 1, len(imagePaths), imagePath.split(os.path.sep)[-2]))
        student_id = imagePath.split(os.path.sep)[-2]

        # Load the input image and convert it from BGR color space to dlib ordering (RGB). Dlib expects RGB
        image = cv2.imread(imagePath)
        rgb = cv2.cvtColor(image, cv2.COLOR_BGR2RGB)

        # Detect the (x, y) coordinates of the bounding boxes corresponding to each face in the input image
        # CNN method - slower, more accurate; HOG method - faster, less accurate
        boxes = face_recognition.face_locations(rgb, model = detection_method)

        # Compute the facial embedding for the face
        encodings = face_recognition.face_encodings(rgb, boxes)

        # Loop over the encodings 
        for encoding in encodings:
            # Add each encoding + student id to our set of known IDS and encodings
            knownEncodings.append(encoding)
            knownIDS.append(student_id)

    # Facial encoding + student id dump to a file
    print("[MĒRĪJUMU IEGUVE] Serializē kodējumus...")
    data = {"encodings": knownEncodings, "ids": knownIDS} # Constructs dictionaries with 2 keys
    f = open(encodings_file, "wb")
    f.write(pickle.dumps(data))
    print("[MĒRĪJUMU IEGUVE] Pabeigts!")
    f.close()

if __name__ == "__main__":
    encode_faces()