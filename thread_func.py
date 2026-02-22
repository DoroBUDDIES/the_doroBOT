import threading
from time import sleep

from picamera2 import Picamera2
import cv2
import numpy as np
import time
import os

class SafeThread:
    """
    Wrapper class to instantiate thread functions with automatic destructor to clean up threads and their processes.
    """
    def __init__(self, target_func):
        # Member variable that is used to stop the function running in thread
        self.thread_func_stop = False
        self.target_func = target_func
        
        # Create thread object with target function and start thread
        self.thread = threading.Thread(target = self.thread_callback)
        self.thread.start() 

    # Stops thread functions and joins threads
    def stop(self):
        # Stop function in thread
        self.thread_func_stop = True
        
        # Join thread
        self.thread.join()

    # Wrapper function to repeatedly call target function until destructor
    def thread_callback(self):
        while(not self.thread_func_stop):
            self.target_func()

        return

class TimerThread(SafeThread):
    """
    """

    # Timer constructor
    def __init__(self, **kwargs):
        # Initialize timer length
        self.seconds = kwargs.get('seconds', 30)
        self.seconds_passed = 0

        # Intialize base class
        super().__init__(target_func = self.timer_callback_func)

    # Timer stop function also stops inherited thread class
    def stop(self):
        # Call base class destructor
        super().stop()

    # Callback function for timer
    def timer_callback_func(self):
        sleep(1)
        print(self.seconds_passed)
        self.seconds_passed += 1
        if(self.seconds_passed == self.seconds):
            self.thread_func_stop = True

        return

class CameraThread(SafeThread):
    """
    """
    
    # Camera constructor
    def __init__(self, **kwargs):
        # Intializing device
        self.device_id = kwargs.get('device_id', 0)

        # Initializing frame dimensions
        self.width = kwargs.get('width', 320)
        self.height = kwargs.get('height', 240)

        self.fps = 0
        
        self.camera = None
        self.no_face_detected = False
        
        # Intialize base class
        super().__init__(self.face_detection_callback)
        
             

    def stop(self):
        # Release the VideoCapture object
        if self.camera:
            self.camera.stop()  # MUST call stop() before close()
            self.camera.close()
            self.camera = None

        # Call base class destructor
        super().stop()

    def face_detection_callback(self):
        if self.camera is None:
            # Initialize camera object to begin to collect facial data
            self.camera = Picamera2()
            self.camera.configure(self.camera.create_preview_configuration(main={"format": 'XRGB8888', "size": (self.width, self.height)}))
            self.camera.start()

            # Path to training data
            self.base_dir = os.path.dirname(os.path.abspath(__file__))

            # Load training data to be able to detect faces
            self.face_cascade = cv2.CascadeClassifier(os.path.join(self.base_dir, 'peripherals', 'haarcascade_frontalface_default.xml'))
            
            # Initializ boolean variable for face detetion
            self.face_detected = False

            self.thread_lock = threading.Lock()
        else:
            with self.thread_lock:
                # Read the frames from a camera
                frame = self.camera.capture_array()

                # Convert to grayscale
                gray = cv2.cvtColor(frame, cv2.COLOR_BGR2GRAY)

                # Detect the faces
                faces = self.face_cascade.detectMultiScale(gray, 1.1, 4)

                # No faces means user is gone or looking down (BAD)
                self.no_face_detected = (len(faces) == 0)
        
# WIP - I havent implemented it yet
class WhisperThread(SafeThread):
    """
    """
    
    def __init__(self, **kwargs):
        # Collecting .wav Files in Directory
        audioFiles = [file for file in os.listdir() if file.endswith(".wav")]

        model = whisper.load_model("medium")
        
        # Transcribing Each File
        for audio in audioFiles:
            print(f"Transcribing: {audio}")

            result = model.transcribe(
                audio,
                language = "en",
                task = "transcribe",
                condition_on_previous_text = False,
                hallucination_silence_threshold = 0.3
            )

            # Saving To .json File
            output = f"{os.path.splitext(audio)[0]}.json"
            with open(output, "w", encoding = "utf-8") as f:
                json.dump(result, f, ensure_ascii = False, indent = 2)

            print(f"Successfully Transcribed {audio}")
        
        return 0

class ScreenThread(SafeThread):
    """
    """