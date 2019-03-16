from imutils.video import VideoStream
import face_recognition
import argparse
import imutils
import pickle
import time
import cv2

def cam_recognition(encodings_file = "encodings.pickle", display = 1, detection_method = "hog", output = ""):
    # Loading the know faces and embeddings
    print("[RECOGNITION] Loading encodings...")
    data = pickle.loads(open(encodings_file, "rb").read())

    print("[RECOGNITION] Starting video stream...")
    vs = VideoStream(src = 0).start()
    writer = None
    time.sleep(2.0)

    while True:
        frame = vs.read()
        rgb = cv2.cvtColor(frame, cv2.COLOR_BGR2RGB)
        rgb = imutils.resize(frame, width = 450)
        r = frame.shape[1] / float(rgb.shape[1])

        boxes = face_recognition.face_locations(rgb, model = detection_method)
        encodings = face_recognition.face_encodings(rgb, boxes)

        names = []
        
        for encoding in encodings:
            matches = face_recognition.compare_faces(data["encodings"], encoding)
            name = "Unknown"

            if True in matches:
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
            print("Recognized id:", name)

        # Loop over the recognized faces
        for ((top, right, bottom, left), name) in zip(boxes, names):
            # rescale the face coordinates
            top = int(top * r)
            right = int(right * r)
            bottom = int(bottom * r)
            left = int(left * r)

            # Draw the predicted face name on the image
            cv2.rectangle(frame, (left, top), (right, bottom), (0, 255, 0), 2)
            y = top - 15 if top - 15 > 15 else top + 15
            cv2.putText(frame, "ID:" + name, (left, y), cv2.FONT_HERSHEY_SIMPLEX, 0.75, (0, 255, 0), 2)

        if writer is None and output is not None:
            fourcc = cv2.VideoWriter_fourcc(*"MJPG")
            writer = cv2.VideoWriter(output, fourcc, 20, (frame.shape[1], frame.shape[0]), True)

        if writer is not None:
            writer.write(frame)

        if display > 0:
            cv2.imshow("Frame", frame)
            key = cv2.waitKey(1) & 0xFF

            if key == ord("q"):
                break

    cv2.destroyAllWindows()
    vs.stop()

    if writer is not None:
        writer.release()

if __name__ == "__main__":
    cam_recognition()