import gpiozero as gp
from time import sleep
import RPi.GPIO as GPIO
import math
import threading

# This file contains only code related to the operation of the machine, NOT the user interface
# All user-interface code is in program.py (working_version.py on computer)

## Thread for Counting Tachometer Pulses
def pulseCountThread(target_pulses):

    pulse_count = 0
    nextRising = True
    
    # Start polling for pulses
    while pulse_count < target_pulses:
        if (nextRising == True and GPIO.input(23)):  # Check if the pulse pin is high (rising edge)
            pulse_count += 1
            nextRising = False
        if (nextRising == False and not GPIO.input(23)):
            nextRising = True
        
    return    

# Calculates the Required Sled Frequency to Achieve a certain mm per second
def calculateSledFreq(coilFrequency, pitch):
    rotationsPerSecond = coilFrequency / 400

    result = rotationsPerSecond * pitch * 1.84

    return result


# Calculates the Required Sled Time to Cover a Certain Distance
# NOTE: Distance given in mm
def calculateSledTime(distance, frequency):
    temp = distance * 1.84

    temp = temp / frequency

    return temp

# Calculating Steps Required for Feeder Motor
def calculateFeedSteps(feed_param):
    result = feed_param * 500
    result = result / (80 * math.pi)
    return round(result)

# Cut, Feed & Return Home Function
def cutFeed(cutterSol, feedSol, feedMotor, feed_param):
    # Initialising Counters/Target
    target_pulses = calculateFeedSteps(feed_param * 10)
    
    # Cutting Wire
    cutterSol.on()
    sleep(0.5)
    cutterSol.off()
    sleep(0.5)

    # Turning Feed Solenoid + Motor On
    feedSol.on()
    sleep(0.5)

    # Starting Thread
    feedThread = threading.Thread(target=pulseCountThread, args=(target_pulses,))
    feedThread.start()

    feedMotor.on()

    while(feedThread.is_alive()):
        sleep(0.1)

    # Switch Machinery Off
    feedMotor.off()
    feedSol.off()
    return


# Start Home Procedure - Move Forward then Return Home
def startHome(homeSensor, sled, sledDirection):
    if(homeSensor.value == 0):
        return
    
    # Adjusting for possible 'Negative Position'
    sled.value = 0.5
    sled.frequency = 100
    sledDirection.on()
    sleep(0.5)
    sled.off()
    sleep(0.1)

    # Return Home
    returnHome(homeSensor, sled, sledDirection)
    return



# Return Home Function
def returnHome(homeSensor, sled, sledDirection):
    # If Already Home, Do Nothing
    if(homeSensor.value == 0):
        return
    
    # Set Sled Direction to Inwards + Frequency to 100
    sledDirection.off()
    sled.frequency = 100
    sled.value = 0.5

    while(homeSensor.value != 0):
        sleep(0.001)

    sled.off()
    
    
    assert(homeSensor.value == 0)
    return