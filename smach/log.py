#!/usr/bin/env python3
import smach
from globals import IS_DEBUG

__all__ = ['set_loggers','loginfo','logwarn','logerr','logdebug']

def loginfo(msg):
    if IS_DEBUG:
        print("[  INFO ] : "+str(msg))

def logwarn(msg):
    if IS_DEBUG:
        print("[  WARN ] : "+str(msg))

def logdebug(msg):
    if IS_DEBUG:
        print("[ DEBUG ] : "+str(msg))

def logerr(msg):
    if IS_DEBUG:
        print("[ ERROR ] : "+str(msg))

def set_loggers(info,warn,debug,error):
    """Override the SMACH logging functions."""
    smach.loginfo = info
    smach.logwarn = warn
    smach.logdebug = debug
    smach.logerr = error

