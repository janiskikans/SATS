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

