"""
globals.py holds all global variables used in this project.
"""
from enum import Enum
from queue import Queue

CLOCK_TIMEOUT_SEC = 10

IS_DEBUG = True

voice_queue = Queue()

class PossibleOutcomes(Enum):
    IDLE = 'GotoIdle'
    TASK = 'GotoTask'
    CLOCK = 'GotoClock'
    VIBE = 'GotoPomodoroVibe'
    LOCKEDIN = 'GotoPomodoroLockedIn'

class WhisperOutcomes(Enum):
    IDLE = 'GotoIdle'
    TASK = 'GotoTask'
    CLOCK = 'GotoClock'
    VIBE = 'GotoPomodoroVibe'
    LOCKEDIN = 'GotoPomodoroLockedIn'
    ADDTASK = 'AddTask'
    DELTASK = 'DelTask'
    STOPPOMO = 'StopPomo'

