import gpiozero as gp
from time import sleep, time
import RPi.GPIO as GPIO
import math
import threading

# This file contains only code related to the operation of the machine, NOT the user interface
# All user-interface code is in program.py (working_version.py on computer)


'''
If there is no more wire, there will be no more spikes
Count when nextRising is True, but GPIO.input(23) is low -> once count reaches threshold, do something

The something:
    SET FLAG -> PASS BACK TO PROGRAM FUNCTION THAT CALLED IT
'''

## Thread for Counting Tachometer Pulses
def pulseCountThread(target_pulses, resultFlag):

    pulse_count = 0
    nextRising = True
    timeout = time() + 2
    
    # Start polling for pulses
    while pulse_count < target_pulses:
        # If currently low, and input is high, increment count, set current to high
        if (nextRising == True and GPIO.input(23)): 
            pulse_count += 1
            nextRising = False
            continue
        # If currently high, and input is low, set current to low, and reset timeout
        if (nextRising == False and not GPIO.input(23)):
            nextRising = True
            timeout = time() + 2
            continue
        # If currently low, and input is still low, increment timeout_count
        if (nextRising == True and not GPIO.input(23)):
            # If reached threshold, set resultflag to false and return
            if(timeout < time()):
                resultFlag[0] = False
                return
        
    resultFlag[0] = True
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
    threadCompleted = [True]
    feedThread = threading.Thread(target=pulseCountThread, args=(target_pulses, threadCompleted))
    feedThread.start()

    feedMotor.on()

    while(feedThread.is_alive()):
        sleep(0.1)

    # Switch Machinery Off
    feedMotor.off()
    feedSol.off()

    ## Return the value of ThreadCompleted
        # If True - Thread Executed As Expected
        # If False - No More Wire Warning Should be Thrown
    return threadCompleted[0]


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