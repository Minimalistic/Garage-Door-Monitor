# Garage Door Monitor

## Description
A script for a simple sonar equipped RPi Zero W in my garage to let me know if the garage door has been left open for more than half an hour (ultimately will add customizations to config.py) Currently I rely on an IFTTT webhook trigger `door_left_open` to send me a notification in IFTTT. 
This was a project primarily for learning, I used a sonar sensor connected to a RPi Zero W, built it a Lego enclosure and articulating sensor mount and mounted it to the garage door motor in my garage. 

To make this script run 24/7, I have it run at boot of the Rpi using crontab -e