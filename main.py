"""
"""
import smach as sm
import pygame

from states import *
from globals import PossibleOutcomes

def main():
    """
    Main function
    """
    # Sound 
    pygame.init()
    pygame.mixer.init(frequency=44100, size=-16, channels=1, buffer=512)
    sound = pygame.mixer.Sound('assets/Hello_Ready_To_Study.wav')
    
    doroFSM = sm.StateMachine(outcomes=[])

    with doroFSM:
        sm.StateMachine.add(
            'Idle', 
            IdleState(sound),
            transitions = {PossibleOutcomes.IDLE.value: 'Idle',
                        #    PossibleOutcomes.CLOCK.value: 'Clock',
                           PossibleOutcomes.LOCKEDIN.value: 'Pom - Locked'},
            # remapping={'input': 'user_input', 'lcd': 'lcd'}
        )

        sm.StateMachine.add(   
            'Pom - Locked', 
            PomodoroLockedInState(),
            transitions = {PossibleOutcomes.IDLE.value: 'Idle',
                           PossibleOutcomes.LOCKEDIN.value: 'Pom - Locked'},
            # remapping={'lcd': 'lcd'}
        )

        # doroFSM.userdata.user_input = 1 
        doroFSM.execute()

if __name__ == '__main__':
    main()