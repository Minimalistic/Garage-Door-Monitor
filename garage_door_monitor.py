#!/usr/bin/env python3
import RPi.GPIO as GPIO
import time
import sys

# import URL and private key to send notifications to IFTTT
from config import IFTTT_URL

# For determining time of day, whether to send an alert

#for sending get to IFTTT
import urllib3
http = urllib3.PoolManager()

garageOPEN = False

# Get a distance reading from sonar sensor
def garageDoorSensor():
    # TODO Surely there's a better way to do this without declaring global variables like this.
    global distance
    global garageOPEN
    try:
        GPIO.setwarnings(False) # GPIO pins will probably complain from last time this script was run
        GPIO.setmode(GPIO.BOARD)

        PIN_TRIGGER = 7
        PIN_ECHO = 11

        GPIO.setup(PIN_TRIGGER, GPIO.OUT)
        GPIO.setup(PIN_ECHO, GPIO.IN)
        GPIO.output(PIN_TRIGGER, GPIO.LOW)

        time.sleep(5)
        GPIO.output(PIN_TRIGGER, GPIO.HIGH)

        time.sleep(0.00001)

        GPIO.output(PIN_TRIGGER, GPIO.LOW)
        
        while GPIO.input(PIN_ECHO)==0:
            pulse_start_time = time.time()
        while GPIO.input(PIN_ECHO)==1:
            pulse_end_time = time.time()

        pulse_duration = pulse_end_time - pulse_start_time
        distance = round(round(pulse_duration * 17150, 2)/2.54, 2)
        if distance > 60: # shorter distance = garage open due to door top
                          # being closer to sensor.
            garageOPEN = False
            print("Garage door is closed.")
        else:
            garageOPEN = True
    finally:
        GPIO.cleanup()

def alertIFTTT():
    http.request('GET', IFTTT_URL, timeout=15)

def garageMinion():
    timeOpen = 0
    try:
        garageDoorSensor()
        print("Sonar sensor returned " + str(distance) + " inches")
        time.sleep(5)

        if garageOPEN == True:
            timeOpen += 1
            print("Garage door open for the last " + str(timeOpen) + " seconds.")
            if timeOpen == 1200: # Door needs to be open for more than 20 minutes
                try:
                    alertIFTTT()
                    #Resetting timer to ensure there's a repeated alert every 30 mins
                    time.sleep(1)
                    timeOpen = 0 
                    print("Garage door appears to have been closed, resetting timer.")
                except:
                    print("some sorta error")
        else:
            timeOpen = 0

    except KeyboardInterrupt:
        print("Ending script")
        sys.exit()

garageMinion()
