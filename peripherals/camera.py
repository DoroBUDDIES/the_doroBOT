"""
Adapted code from:
https://github.com/automaticdai/rpi-object-detection/blob/master/src/face-detection/face-detection.py
"""

# Imports ---
from picamera2 import Picamera2
import cv2
import numpy as np
import time
import os

class Face_Detector:
    def __init__(self, device_id = 0, width = 320, height = 240):
        self.device_id = device_id
        self.width = width
        self.height = height
        self.fps = 0

        self.camera =  Picamera2()
        self.camera.configure(self.camera.create_preview_configuration(main={"format": 'XRGB8888', "size": (self.width, self.height)}))
        self.camera.start()

        self.base_dir = os.path.dirname(os.path.abspath(__file__))

        # Load the cascade
        self.face_cascade = cv2.CascadeClassifier(os.path.join(self.base_dir, 'haarcascade_frontalface_default.xml'))


    def visualize_fps(self, image, fps: int):
        if len(np.shape(image)) < 3:
            text_color = (255, 255, 255)  # white
        else:
            text_color = (0, 255, 0)  # green
        row_size = 20  # pixels
        left_margin = 24  # pixels

        font_size = 1
        font_thickness = 1

        # Draw the FPS counter
        fps_text = 'FPS = {:.1f}'.format(fps)
        text_location = (left_margin, row_size)
        cv2.putText(image, fps_text, text_location, cv2.FONT_HERSHEY_PLAIN,
                    font_size, text_color, font_thickness)

        return image

    def find_face(self):

        while True:
            start_time = time.time()  # START

            # Read the frames from a camera
            frame = self.camera.capture_array()

            # Convert to grayscale
            gray = cv2.cvtColor(frame, cv2.COLOR_BGR2GRAY)

            # Detect the faces
            faces = self.face_cascade.detectMultiScale(gray, 1.1, 4)

            # Draw the rectangle around each face
            for (x, y, w, h) in faces:
                cv2.rectangle(frame, (x, y), (x+w, y+h), (255, 0, 0), 2)

            # Display
            cv2.imshow('img', self.visualize_fps(frame, self.fps))

            end_time = time.time()  # END

            # calculate FPS
            seconds = end_time - start_time
            fps = 1.0 / seconds
            print("Estimated fps:{0:0.1f}".format(fps))

            # Stop if escape key is pressed
            k = cv2.waitKey(30) & 0xff
            if k==27:
                break

        # Release the VideoCapture object
        self.camera.close()