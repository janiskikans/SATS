import face_recognition
import argparse
import pickle
import cv2

# Arg parsing
arg_parser = argparse.ArgumentParser()
arg_parser.add_argument("-e", "--encodings", required = True, help = "Path to database of serialized facial encodings")
arg_parser.add_argument("-i", "--image", required = True, help = "Path to the image of recognizable people")
arg_parser.add_argument("-d", "--detection-method", type = str, default = "cnn", help = "Face detection model to be used ('cnn' or 'hog'")
args = vars(arg_parser.parse_args())

# Loading the know faces and embeddings
print("[RECOGNITION] Loading encodings...")
data = pickle.loads(open(args["encodings"], "rb").read())

# Loading the input image and converting from BGR to RGB
image = cv2.imread(args["image"])
rgb = cv2.cvtColor(image, cv2.COLOR_BGR2RGB)

# Detect coordinates of the boudning boxes corresponding to each face in the input image then complete facial embeddings for each face
print("[RECOGNITION] Identifying faces...")
boxes = face_recognition.face_locations(rgb, model = args["detection_method"])
encodings = face_recognition.face_encodings(rgb, boxes)

# Initalizing the list of student ids for each face detected
names = []

# Looping over the facial embeddings
for encoding in encodings:
    # Attempt to match each face in the input image to our know encodings
    matches = face_recognition.compare_faces(data["encodings"], encoding)
    name = "Unkown"

    # Check if match found
    if True in matches:
        # Find the indexes of all matched faces then initialize a dictionary to count the total number of times each face was matched
        matchedIdxs = [i for (i, b) in enumerate(matches) if b]
        counts = {}

        # Loop over the matched indexes and maintain a count for each recognized face
        for i in matchedIdxs:
            name = data["ids"][i]
            counts[name] = counts.get(name, 0) + 1
        
        # Determine the recognized face with the largest number of votes (note: in the event of unlikely tie Python will select firt entry in the dictionary)
        name = max(counts, key=counts.get)
    
    # Update the list of student ids
    names.append(name)

# Loop over the recognized faces
for ((top, right, bottom, left), name) in zip(boxes, names):
	# Draw the predicted face name on the image
	cv2.rectangle(image, (left, top), (right, bottom), (0, 255, 0), 2)
	y = top - 15 if top - 15 > 15 else top + 15
	cv2.putText(image, "ID:" + name, (left, y), cv2.FONT_HERSHEY_SIMPLEX, 0.75, (0, 255, 0), 2)
# Show output image
cv2.imshow("Image", image)
cv2.waitKey(0)