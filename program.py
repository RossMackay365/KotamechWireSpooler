import PySimpleGUI as sg
import gpiozero as gp
from time import sleep, time
import RPi.GPIO as GPIO
from machine_functions import *
from signal import pause

#################################
#             GIT PULL          #
#################################





filepath = "params.txt"
run_text = "MACHINE RUNNING"
stop_text = "MACHINE STOPPED"
reset_text = "MACHINE RESETTING"

### VALUE DEFINITIONS ###
rotPerMil = 1.84 ## Number of Rotations to Move 1mm

COIL_FREQUENCY = 1600

# Maximum/Minimum Values
length_MAX = 1000
length_MIN = 1

feed_MAX = 100
feed_MIN = 12

strokeLen_MAX = 165
strokeLen_MIN = 50

x0_MAX = 155
x0_MIN = 0

strokeDiff_MAX = 60
strokeDiff_MIN = 0

pitch_MAX = 10
pitch_MIN = 0.5


# Parameter Values Displayed to User
length_param = 0
feed_param = 0
strokeLen_param = 0 # CALLED STROKE END FOR USER
x0_param = 0        # CALLED STROKE START FOR USER
strokeDiff_param = 0
pitch_param = 0

# Layout Functionality
layout_length =     [[sg.Button('+', size=(10,2), key='length-UP')],
                     [sg.VPush()],
                     [sg.Text(str(length_param) + "m", font=('Calibri',18), key='length')],
                     [sg.VPush()],
                     [sg.Button('-', size=(10,2), key='length-DOWN')]]

layout_feed =       [[sg.Button('+', size=(10,2), key='feed-UP')],
                     [sg.VPush()],
                     [sg.Text(str(feed_param) + "cm", font=('Calibri',18), key='feed')],
                     [sg.VPush()],
                     [sg.Button('-', size=(10,2), key='feed-DOWN')]]

layout_strokeLen =    [[sg.Button('+', size=(10,2), key='strokeLen-UP')],
                     [sg.VPush()],
                     [sg.Text(str(strokeLen_param) + "mm", font=('Calibri',18), key='strokeLen')],
                     [sg.VPush()],
                     [sg.Button('-', size=(10,2), key='strokeLen-DOWN')]]

layout_x0 =         [[sg.Button('+', size=(10,2), key='x0-UP')],
                     [sg.VPush()],
                     [sg.Text(str(x0_param) + "mm", font=('Calibri',18), key='x0')],
                     [sg.VPush()],
                     [sg.Button('-', size=(10,2), key='x0-DOWN')]]

layout_strokeDiff = [[sg.Button('+', size=(10,2), key='strokeDiff-UP')],
                     [sg.VPush()],
                     [sg.Text(str(strokeDiff_param) + "mm", font=('Calibri',18), key='strokeDiff')],
                     [sg.VPush()],
                     [sg.Button('-', size=(10,2), key='strokeDiff-DOWN')]]

layout_pitch =      [[sg.Button('+', size=(10,2), key='pitch-UP')],
                     [sg.VPush()],
                     [sg.Text(str(pitch_param) + "mm", font=('Calibri',18), key='pitch')],
                     [sg.VPush()],
                     [sg.Button('-', size=(10,2), key='pitch-DOWN')]]

user_layout = [[sg.VPush()],
          [sg.Frame("Wire Length", layout_length, size=(200, 180), element_justification='center', vertical_alignment='center', font = ('Calibri', 16)), sg.Push(), sg.Frame("Stroke Start", layout_x0, size=(200, 180), element_justification='center', vertical_alignment='center', font = ('Calibri', 16)), sg.Push(), sg.Frame("Feed Length", layout_feed, size=(200, 180), element_justification='center', vertical_alignment='center', font = ('Calibri', 16))],
          [sg.VPush()],
          [sg.Frame("Stroke Differential", layout_strokeDiff, size=(200, 180), element_justification='center', vertical_alignment='center', font = ('Calibri', 16)), sg.Push(), sg.Frame("Stroke End", layout_strokeLen, size=(200, 180), element_justification='center', vertical_alignment='center', font = ('Calibri', 16)), sg.Push(), sg.Frame("Stroke Pitch", layout_pitch, size=(200, 180), element_justification='center', vertical_alignment='center', font = ('Calibri', 16))],
          [sg.VPush()],
          [sg.Push(), sg.Button('CONFIRM', size=(15,2), disabled=True), sg.Push()],
          [sg.VPush()]]

# , sg.Button('EXIT', size=(15,2)), sg.Push() ADD TO CONFIRM BUTTON LINE FOR EXIT BUTTON


run_layout = [[sg.VPush()],
              [sg.Push(), sg.Text(run_text, font=('Calibri', 50), key='RUN-TEXT'), sg.Push()],
              [sg.VPush()]]

window = sg.Window('Program', user_layout, size = (800,480), finalize = True)
run_window = sg.Window('Program', run_layout, size = (800, 480), finalize = True)
current_window = window
run_window.Hide()
window.Maximize()
window.TKroot["cursor"] = "none"



### FUNCTION DEFINITIONS ###

## Reading Values from File, and Setting Parameters Equal
def readParamsFile(path):
    param_file = open(path, "r")
    value_String = param_file.readline()
    values = value_String.split(", ")
    param_file.close()
    return values

## Writing Values to File, Based on Parameters Current Value
def writeParamsFile(path):
    param_file = open(path, "w")

    update = str(length_param) + ", " + str(feed_param) + ", " + str(strokeLen_param) + ", " + str(x0_param) + ", " + str(strokeDiff_param) + ", " + str(pitch_param)
    param_file.write(update)
    param_file.close()

# Increments the Value of a User Parameter, & Displays On-Screen
# Enables Decrement Button, Disables Increment Button if Needed
def incrementValue(current_val, min_val, max_val, key):
    window['CONFIRM'].update(disabled=False)
    window[key].update(text_color = 'red')
    if current_val - 1 == min_val:
        window[key + "-DOWN"].update(disabled=False)
    if current_val == max_val:
        window[key + "-UP"].update(disabled=True)

    if(key == 'length'):
        window[key].update(str(current_val) + "m")
    elif(key == 'feed'):
        window[key].update(str(current_val) + "cm")
    else:
        window[key].update(str(current_val) + "mm")
    return


# Decrements the Value of a User Parameter, & Displays On-Screen
# Enables Increment Button, Disables Decrement Button if Needed
def decrementValue(current_val, min_val, max_val, key):
    window['CONFIRM'].update(disabled=False)
    window[key].update(text_color = 'red')
    if current_val + 1 == max_val:
        window[key + "-UP"].update(disabled=False)
    if current_val == min_val:
        window[key + "-DOWN"].update(disabled=True)

    if(key == 'length'):
        window[key].update(str(current_val) + "m")
    elif(key == 'feed'):
        window[key].update(str(current_val) + "cm")
    else:
        window[key].update(str(current_val) + "mm")
    return

def resetTextColor():
    window['length'].update(text_color = 'white')
    window['feed'].update(text_color = 'white')
    window['strokeLen'].update(text_color = 'white')
    window['x0'].update(text_color = 'white')
    window['strokeDiff'].update(text_color = 'white')
    window['pitch'].update(text_color = 'white')

# Switch Window - Hide Old One, Show New One & Maximise
def switchWindows(old, new):
    new.UnHide()
    new.Maximize()
    old.Hide()
    global current_window
    current_window = new
    return

# Initialisation Function to Deactivate Necessary Buttons
def initialButtonActivation():
    if length_param <= length_MIN:
        window['length-DOWN'].update(disabled=True)
    if length_param >= length_MAX:
        window['length-UP'].update(disabled=True)

    if feed_param <= feed_MIN:
        window['feed-DOWN'].update(disabled=True)
    if feed_param >= feed_MAX:
        window['feed-UP'].update(disabled=True)

    if strokeLen_param <= strokeLen_MIN:
        window['strokeLen-DOWN'].update(disabled=True)
    if strokeLen_param >= strokeLen_MAX:
        window['strokeLen-UP'].update(disabled=True)

    if strokeDiff_param <= strokeDiff_MIN:
        window['strokeDiff-DOWN'].update(disabled=True)
    if strokeDiff_param >= strokeDiff_MAX:
        window['strokeDiff-UP'].update(disabled=True)

    if x0_param <= x0_MIN:
        window['x0-DOWN'].update(disabled=True)
    if x0_param >= x0_MAX:
        window['x0-UP'].update(disabled=True)

    if pitch_param <= pitch_MIN:
        window['pitch-DOWN'].update(disabled=True)
    if pitch_param >= pitch_MAX:
        window['pitch-UP'].update(disabled=True)
    return



### GPIO PIN OPERATION ###
## Display Functions

# Stop Button Pressed
def stopButtonPressed():
    # If not in run mode, do nothing
    if(current_window == window):
        return

    # Update Warning on Run Page
    run_window['RUN-TEXT'].update(stop_text)

    # Switching Steppers Off
    coil.off()
    sled.off()

    while(stopButton.is_pressed):
        if(resetButton.is_pressed):
            resetButtonPressed()
            return
        sleep(0.001)

    run_window['RUN-TEXT'].update(run_text)

    coil.value = 0.5
    sled.value = 0.5

    return

# Reset Button Pressed
def resetButtonPressed():
    # If not in run mode, do nothing
    if(current_window == window):
        return
    
    # Setting Page to Reset Text
    run_window['RUN-TEXT'].update(reset_text)
    # Switching Coil Off
    coil.off()
    sled.off()
    
    # RESET MACHINE FUNCTIONALITY
    # Cut/Feed Wire
    cutFeed(cutterSol, feedSol, feedMotor, feed_param)
    sleep(0.5)
    # Return Home
    returnHome(homeSensor, sled, sledDirection)

    coil.off()
    sled.off()

    # Change Screen Back to Normal
    run_window['RUN-TEXT'].update(run_text)
    switchWindows(run_window, window)

    return

# Start Button Pressed
def startButtonPressed():
    global x0_param, strokeLen_param, strokeDiff_param, length_param

    ### PRE-OPERATION CHECKS ###
    # If stop button is pressed, do not start
    if(stopButton.value == 1):
        return
    # If already in run mode, do nothing
    if(current_window == run_window):
        return
    
    # If parameters not saved, abort
    if(window['CONFIRM'].Disabled == False):
        return
    
    # If initial position is further than stroke length, return
    if(x0_param > strokeLen_param):
        return
    
    ## Switch to Run Mode
    run_window['RUN-TEXT'].update(run_text)
    switchWindows(window, run_window)
    startHome(homeSensor, sled, sledDirection)
    sleep(0.5)

    # Move to Initial Position
    initialTime = calculateSledTime(x0_param, 100)
    sled.value = 0.5
    sled.frequency = 100
    sledDirection.on()

    initialStart = time()
    initialEnd = initialStart + initialTime

    ## Move Sled - Poll for Interrupts
    while(time() < initialEnd):
        if(stopButton.is_pressed):
            remTime = initialEnd - time()
            stopButtonPressed()
            initialEnd = time() + remTime
        if(resetButton.is_pressed):
            resetButtonPressed()
            return
        sleep(0.001)
    # Turn Off Sled
    sled.off()
    sleep(1)


    ### Regular Operation ###
    currentStrokeLen = strokeLen_param - x0_param
    passNum = 0

    # Starting Pulse Count Thread
    target_pulses = calculateFeedSteps(length_param * 1000) # Conversion from m to mm
    tachoThread = threading.Thread(target=pulseCountThread, args=(target_pulses,))
    tachoThread.start()

    coil.value = 0.5
    coil.frequency = COIL_FREQUENCY

    sledFreq = calculateSledFreq(COIL_FREQUENCY, pitch_param)

    while(tachoThread.is_alive()):
        ## POLLING BUTTONS
        if(stopButton.is_pressed):
            stopButtonPressed()
        if(resetButton.is_pressed):
            resetButtonPressed()
            return

        ## Turn Machines On, Complete Correct Distance Loop, Turn Machines Off
        runtime = calculateSledTime(currentStrokeLen, sledFreq)
        sled.frequency = sledFreq
        sled.value = 0.5
        
        ## Move Sled - Poll for Interrupts
        startTime = time()
        endTime = startTime + runtime
        while(time() < endTime):
            if(stopButton.is_pressed):
                remTime = endTime - time()
                stopButtonPressed()
                endTime = time() + remTime
            if(resetButton.is_pressed):
                resetButtonPressed()
                return
            sleep(0.001)

        sled.off()

        ## PREPARE FOR NEXT PASS ##
        # Update Next Stroke Length
        currentStrokeLen = strokeLen_param - x0_param - (passNum * strokeDiff_param)
        
        # Reverse Sled Direction
        if(passNum % 2 == 0):
            sledDirection.off()
        else:
            sledDirection.on()

        # If Current Stroke Length is Negative - Break While Loop
        if(currentStrokeLen <= 0):
            break
        passNum = passNum + 1
        sleep(0.1)

    coil.off()

    sleep(1)

    # Cut / Feed / Reset Process
    resetButtonPressed()
    return


    



### Machine Initialising
## Stepper Motors - each stepper has three GPIO pins
    # Enable
    # Direction
    # Pull (i.e. Pulse Width Modulation Applied Here)
    # Low = Enabled
coilEnable = gp.OutputDevice(26, False)
coilDirection = gp.OutputDevice(16, False)
coil = gp.PWMOutputDevice(12)

# High = Outwards, Low = Inwards
# Initial Direction is Outwards
sledEnable = gp.OutputDevice(6, False)
## ON IS OUTWARDS, OFF IS INWARDS - THIS KEEPS SWITCHING FUCK ME
sledDirection = gp.DigitalOutputDevice(9, False)
sled = gp.PWMOutputDevice(13)


# Enabling Steppers
coilEnable.on()
sledEnable.on()

coilDirection.off()


# Home Sensor - 0 when home, 1 when not
homeSensor = gp.InputDevice(8, False)


## Feeder + Motor Devices
feedMotor = gp.OutputDevice(22)
feedSol = gp.OutputDevice(27)
cutterSol = gp.OutputDevice(17)


# Pulse Sensor Setup
GPIO.setmode(GPIO.BCM)
GPIO.setup(23, GPIO.IN, pull_up_down=GPIO.PUD_DOWN)

### NON-MACHINE GPIO Pin Initialisation
## Buttons
stopButton = gp.Button(18, False)
stopButton.when_pressed = stopButtonPressed

startButton = gp.Button(15, False)
startButton.when_pressed = startButtonPressed

resetButton = gp.Button(14, False)
resetButton.when_pressed = resetButtonPressed








### ACTUAL PROGRAM OPERATION ###

# Initialising Values & Button Status
saved_values = readParamsFile(filepath)
length_param = int(saved_values[0])
window['length'].update(str(length_param) + "m")
feed_param = int(saved_values[1])
window['feed'].update(str(feed_param) + "cm")
strokeLen_param = int(saved_values[2])
window['strokeLen'].update(str(strokeLen_param) + "mm")
x0_param = int(saved_values[3])
window['x0'].update(str(x0_param) + "mm")
strokeDiff_param = int(saved_values[4])
window['strokeDiff'].update(str(strokeDiff_param) + "mm")
pitch_param = float(saved_values[5])
window['pitch'].update(str(pitch_param) + "mm")

startHome(homeSensor, sled, sledDirection)
initialButtonActivation()


while True:
    event, values = current_window.read()
    ## Button Activation
    if event == 'length-UP':
        length_param += 1
        incrementValue(length_param, length_MIN, length_MAX, 'length')
    if event == 'length-DOWN':
        length_param -= 1
        decrementValue(length_param, length_MIN, length_MAX, 'length')
    if event == 'strokeLen-UP':
        strokeLen_param += 1
        incrementValue(strokeLen_param, strokeLen_MIN, strokeLen_MAX, 'strokeLen')
    if event == 'strokeLen-DOWN':
        strokeLen_param -= 1
        decrementValue(strokeLen_param, strokeLen_MIN, strokeLen_MAX, 'strokeLen')
    if event == 'strokeDiff-UP':
        strokeDiff_param += 1
        incrementValue(strokeDiff_param, strokeDiff_MIN, strokeDiff_MAX, 'strokeDiff')
    if event == 'strokeDiff-DOWN':
        strokeDiff_param -= 1
        decrementValue(strokeDiff_param, strokeDiff_MIN, strokeDiff_MAX, 'strokeDiff')
    if event == 'feed-UP':
        feed_param += 1
        incrementValue(feed_param, feed_MIN, feed_MAX, 'feed')
    if event == 'feed-DOWN':
        feed_param -= 1
        decrementValue(feed_param, feed_MIN, feed_MAX, 'feed')
    if event == 'x0-UP':
        x0_param += 1
        incrementValue(x0_param, x0_MIN, x0_MAX, 'x0')
    if event == 'x0-DOWN':
        x0_param -= 1
        decrementValue(x0_param, x0_MIN, x0_MAX, 'x0')
    if event == 'pitch-UP':
        pitch_param += 0.5
        incrementValue(pitch_param, pitch_MIN, pitch_MAX, 'pitch')
    if event == 'pitch-DOWN':
        pitch_param -= 0.5
        decrementValue(pitch_param, pitch_MIN, pitch_MAX, 'pitch')
    
    if event == 'CONFIRM':
        writeParamsFile(filepath)
        resetTextColor()
        window['CONFIRM'].update(disabled=True)

    
    # This should be removed before final operation
    if event == 'EXIT':
        exit()
    if event == sg.WIN_CLOSED:
        break

window.close()