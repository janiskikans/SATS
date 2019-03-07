from imutils import paths
import face_recognition
import argparse
import pickle
import cv2
import os

# Argument parser and parsing command line arguments
arg_parser = argparse.ArgumentParser()
arg_parser.add_argument("-i", "--dataset", required = True, help = "Path to dataset directory")
arg_parser.add_argument("-e", "--encodings", required = True, help = "Path to serialized database of facial encodings")
arg_parser.add_argument("-d", "--detection-method", type = str, default = "cnn", help = "Desired face detecton model (hog/cnn)")
args = vars(arg_parser.parse_args())

# Grab the paths to data set input images
print("[ENCODING] Quantifying dataset images...")
imagePaths = list(paths.list_images(args["dataset"])) # Makes a list of all imagePaths contained in data set directory

# Initialize the lists of know encodings and known IDS
knowEncodings = []
knowIDS = []

# Looping over all the found dataset images
for (i, imagePath) in enumerate(imagePaths):
    # Getting student id's from the image path
    print("[ENCODING] Processing image {}/{}".format(i + 1, len(imagePaths)))
    student_id = imagePath.split(os.path.sep)[-2]

    # Load the input image and convert it from BGR color space to dlib ordering (RGB). Dlib expects RGB
    image = cv2.imread(imagePath)
    rgb = cv2.cvtColor(image, cv2.COLOR_BGR2RGB)

    # Detect the (x, y) coordinates of the bounding boxes corresponding to each face in the input image
    # CNN method - slower, more accurate; HOG method - faster, less accurate
    boxes = face_recognition.face_locations(rgb, model = args["detection_method"])

    # Compute the facial embedding for the face
    encodings = face_recognition.face_encodings(rgb, boxes)

    # Loop over the encodings 
    for encoding in encodings:
        # Add each encoding + student id to our set of known IDS and encodings
        knowEncodings.append(encoding)
        knowIDS.append(student_id)

# Facial encoding + student id dump to a file
print("[ENCODING] Serializing encodings...")
data = {"encodings": knowEncodings, "ids": knowIDS} # Constructs dictionaries with 2 keys
f = open(args["encodings"], "wb")
f.write(pickle.dumps(data))
print("[ENCODING] Done!")
f.close()