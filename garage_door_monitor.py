#!/usr/bin/env python3
import RPi.GPIO as GPIO
from datetime import datetime
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

        time.sleep(2)
        GPIO.output(PIN_TRIGGER, GPIO.HIGH)

        time.sleep(0.00001)

        GPIO.output(PIN_TRIGGER, GPIO.LOW)
        
        while GPIO.input(PIN_ECHO)==0:
            pulse_start_time = time.time()
        while GPIO.input(PIN_ECHO)==1:
            pulse_end_time = time.time()

        pulse_duration = pulse_end_time - pulse_start_time
        distance = round(round(pulse_duration * 17150, 2)/2.54, 2)
        if distance > 40: # shorter distance = garage open due to door top
                          # being closer to sensor.
            garageOPEN = False
        else:
            garageOPEN = True
    finally:
        GPIO.cleanup()

def alertIFTTT():
    http.request('GET', IFTTT_URL, timeout=15)

def garageMinion():
    timeOpen = 0
    while True:
        try:
            garageDoorSensor()
            if garageOPEN == True:
                timeOpen += 2 # adding 2 because sensor sampling rate is currently about 2 seconds due to the need to wait for sensor settling.
                print(str(datetime.now()) + " Garage door has been open for the last " + str(timeOpen) + " seconds.")
                if timeOpen == 900: # Door needs to be open for more than 15 minutes
                    try:
                        alertIFTTT()
                        #Resetting timer to ensure there's a repeated alert every 30 mins
                        timeOpen = 0 
                        print("Garage door alert has been sent, resetting timer.")
                    except:
                        print("some sorta error")
                else:
                    garageDoorSensor()
            else:
                print(str(datetime.now()) + " Sensor reading: " + str(distance) + " inches. Garage door is closed, timer reset.")
                timeOpen = 0
                sys.exit()

        except KeyboardInterrupt:
            print("Ending script")
            sys.exit()

garageMinion()
