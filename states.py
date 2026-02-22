import smach as sm
import pygame
from datetime import datetime
import time

from globals import PossibleOutcomes, CLOCK_TIMEOUT_SEC
# from peripherals.display import FaceDetectorLCD
from thread_func import CameraThread
from peripherals.display import LCD

POMODORO_SECONDS = 50 * 60

class IdleState(sm.State):
    """
    The Idle State operates as the hub for all activities of the DoroBOT.
    """

    def __init__(self, sound = None):
        sm.State.__init__(
            self, 
            outcomes = [
                PossibleOutcomes.IDLE.value, 
                PossibleOutcomes.LOCKEDIN.value
            ],
            # input_keys = ['user_input', 'lcd']
        )
        
        self.sound = sound


    def execute(self, userdata):
        # self.sound.play()

        # lcd = LCD()
        # lcd.load_gif("assets/doroEYES.gif")

        # userdata.user_input = 
        match int(input("Where would you like to go? (1. Idle 2. Clock 3. Tasks 4. Pomodoro): ")):
            case 1:
                return PossibleOutcomes.IDLE.value
            case 2:
                return PossibleOutcomes.IDLE.value
            case 3:
                return PossibleOutcomes.IDLE.value
            case 4:
                return PossibleOutcomes.LOCKEDIN.value
            case _:
                return PossibleOutcomes.IDLE.value

class PomodoroLockedInState(sm.State):
    """
    """

    def __init__(self):
        sm.State.__init__(
            self, 
            outcomes = [PossibleOutcomes.IDLE.value, PossibleOutcomes.LOCKEDIN.value],
            # input_keys = ['user_input','lcd']
        )

        # self.lcd.load_gif("assets/doroEYES.gif")

    def execute(self, userdata):
        print("Starting Pomodoro timer for 50 minutes. Press Ctrl+C to stop.")
        end_t = time.monotonic() + POMODORO_SECONDS
        last_draw = 0.0
        lcd = LCD()

        try:
            c_thread = CameraThread()
            while True:
                now = time.monotonic()
                remaining = int(end_t - now)

                # finish
                if remaining <= 0:
                    lcd.show_timer(0, title="DONE")
                    time.sleep(2)
                    return PossibleOutcomes.IDLE.value

                # draw ~4 fps (smooth enough, not wasteful)
                if now - last_draw >= 0.25:
                    lcd.show_timer(remaining, title="LOCKED IN (50m)")
                    last_draw = now

                warning_seconds = 10
                while(c_thread.no_face_detected):
                    lcd.show_warning(seconds_left=warning_seconds, title="GIT OVER HERE >:(")
                    last_draw = now
                    time.sleep(1)
                    warning_seconds -= 1

                    if warning_seconds <= 0:
                        while(True):
                            lcd.play_gif_frame()
                            print("You are a poo poo pee pee head :P")
                            time.sleep(0.1)
                        break

                # small sleep to reduce CPU
                time.sleep(0.05)

        except KeyboardInterrupt:
            # allow user to break out
            self.camera.close()

        match int(input("Where would you like to go? (1. Idle 2. Clock 3. Tasks 4. Pomodoro): ")):
            case 1:
                return PossibleOutcomes.IDLE.value
            case 2:
                return PossibleOutcomes.IDLE.value
            case 3:
                return PossibleOutcomes.IDLE.value
            case 4:
                return PossibleOutcomes.LOCKEDIN.value
            case _:
                return PossibleOutcomes.IDLE.value


