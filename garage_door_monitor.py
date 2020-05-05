#!/usr/bin/env python3
import RPi.GPIO as GPIO
import time
import sys

# Used to send to gmail
from config import \
    email_sender_account, \
    email_sender_username, \
    email_sender_password, \
    email_smtp_server,      \
    email_smtp_port,        \
    email_recipients

import urllib.request
import smtplib
from email.mime.multipart import MIMEMultipart
from email.mime.text import MIMEText
garageOPEN = False

# Get a distance reading from sonar sensor
def garageDoorSensor():
    global distance
    global garageOPEN
    try:
        GPIO.setmode(GPIO.BOARD)

        PIN_TRIGGER = 7
        PIN_ECHO = 11

        GPIO.setup(PIN_TRIGGER, GPIO.OUT)
        GPIO.setup(PIN_ECHO, GPIO.IN)

        GPIO.output(PIN_TRIGGER, GPIO.LOW)

        # print("Waiting for sensor to settle")

        time.sleep(2)

        # print("Calculating distance")

        GPIO.output(PIN_TRIGGER, GPIO.HIGH)

        time.sleep(0.00001)

        GPIO.output(PIN_TRIGGER, GPIO.LOW)
        
        while GPIO.input(PIN_ECHO)==0:
            pulse_start_time = time.time()
        while GPIO.input(PIN_ECHO)==1:
            pulse_end_time = time.time()

        pulse_duration = pulse_end_time - pulse_start_time
        distance = round(round(pulse_duration * 17150, 2)/2.54, 2)
        if distance < 10:
            garageOPEN = True
        else:
            garageOPEN = False
    finally:
        GPIO.cleanup()
        
# Pass an alert via email
def emailAlert():
    try:
        # Login to email service
        server = smtplib.SMTP(email_smtp_server, email_smtp_port)
        server.ehlo()
        server.starttls()
        server.login(email_sender_username, email_sender_password)

        # Send emails to all recipients listed in config.py
        print("Sending email to " + recipient)
        message = MIMEMultipart('alternative')
        message['From'] = email_sender_account
        message['To'] = recipient
        message['Subject'] = "Garage door has been left open! ID#59174592743"
        message['Content-Type'] = 'text/html'

        # This looks rather clunky
        email_body = "Alert!"
        message.attach(MIMEText(email_body, 'html'))
        text = message.as_string()
        server.sendmail(email_sender_account, recipient, text)
        server.quit()
        
    except:
        print("exception on emailAlert")

def garageMinion():
    while True:
        try:
            garageDoorSensor()
            # print(str(distance))
            time.sleep(0.1)
            if garageOPEN == True:
                print("Start counting to prep to send notification")
            else:
                print("Nothing to report.")
        except KeyboardInterrupt:
            print("Ending script")
            sys.exit()

garageMinion()

#emailAlert()