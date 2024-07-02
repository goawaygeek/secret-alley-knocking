import RPi.GPIO as GPIO
import time
import subprocess
import signal
from qhue import Bridge
import random
import sys
 
SENSOR_PIN = 23
SERVO_PIN = 18
CONT_SERVO_PIN = 17

BRIDGE_IP = "192.168.1.239"
HUE_USERNAME = "tR2GS5P3eyxsNPBmBZ861JwTJB-26XUqjcnukASI"
HUE_LIGHTS = [4]
 
GPIO.setmode(GPIO.BCM)
GPIO.setup(SENSOR_PIN, GPIO.IN)

GPIO.setup(SERVO_PIN, GPIO.OUT)
GPIO.setup(CONT_SERVO_PIN, GPIO.OUT)

p = GPIO.PWM(SERVO_PIN, 50) # GPIO 18 for PWM with 50Hz
p.start(0) # Initialization

pwm = GPIO.PWM(CONT_SERVO_PIN, 50)  # 50 Hz (20 ms period)
# Start PWM with 0% duty cycle (i.e. off)
pwm.start(0)
# the continuous servo we are using (spring SM4306R) seems to run off
# a duty cycle of 12 and takes about .17 seconds to move 90 degrees

# setup videos
VIDEO_ONE = '/home/ally/alley/loop.mp4'
VIDEO_TWO = '/home/ally/alley/rats.mp4'
motion = False

def flicker(bridge, elapsed_time, lights_list = [], transition = 10):
    start_time= time.time()
    while (time.time() - start_time < elapsed_time):
        for light in lights_list:
            bridge.lights[light].state(bri=random.randint(50,130),on=True)
        time.sleep(random.uniform(0,0.5))
        for light in lights_list:
            bridge.lights[light].state(transitiontime=random.randint(0, transition), on=False)
        time.sleep(random.uniform(0,0.5))

def play_video(video_path, loop):
    if loop:
        return subprocess.Popen(['cvlc', '--loop', '--no-video-title-show', '--fullscreen', video_path], stdout=subprocess.DEVNULL, stderr=subprocess.DEVNULL)
        command = f"cvlc --loop --no-video-title-show {video_path}" #--fullscreen
    else:
        return subprocess.Popen(['cvlc', '--play-and-exit', '--no-video-title-show', '--fullscreen', video_path], stdout=subprocess.DEVNULL, stderr=subprocess.DEVNULL)
        command = f"cvlc --play-and-exit --no-video-title-show {video_path}"
    return subprocess.Popen(command, shell=True)

def move_cont_servo():
    pwm.ChangeDutyCycle(12)
    time.sleep(0.30)  # circa 90 degrees for our servo
    # Set the duty cycle to 0 to stop the servo
    pwm.ChangeDutyCycle(0)

def open_servo():
    print('turning on servo!')
    degree = 180
    value = degree / 18 + 2
    p.ChangeDutyCycle(value)
    # p.ChangeDutyCycle(5)  # Change duty cycle to open (adjust this value if needed)
    time.sleep(0.5)
    p.ChangeDutyCycle(0)
    time.sleep(1)  # Wait for servo to open

def close_servo():
    print('turning off servo!')
    p.ChangeDutyCycle(2)  # Change duty cycle to close (adjust this value if needed)
    time.sleep(0.5)  # Wait for servo to close
    p.ChangeDutyCycle(0)  # Change duty cycle to close (adjust this value if needed)

def motion_detected(channel):
    # Here, alternatively, an application / command etc. can be started.
    # we need to work out the logic for whether to move the standard servo
    # or continuous servo
    print('There was a movement!')
    global motion
    motion = True
    # open_servo()
    # close_servo()
    # move_cont_servo()
 
try:
    b = Bridge(BRIDGE_IP, HUE_USERNAME)
    GPIO.add_event_detect(SENSOR_PIN , GPIO.RISING, callback=motion_detected)
    video_process = play_video(VIDEO_ONE, True)  # Start playing the first video on loop
    while True:
        if motion:
            if video_process:
                print('video process exists attempting to quit')
                video_process.terminate()
                #subprocess.call(['vlc',name,'vlc://quit'])
                #video_process.send_signal(signal.SIGINT)  # Send interrupt signal to the video process
                video_process.wait()  # Wait for the process to terminatevideo_process = play_video(video_two, False)  # Play the second video once
            video_process = play_video(VIDEO_TWO, False)  # Play the second video once
            time.sleep(3)  # Wait for the second video to start
            flicker(b, 0.5, HUE_LIGHTS, transition=1)
            b.lights[4].state(bri=255, on=True)
            time.sleep(18.5) # wait until you open the first servo
            flicker(b, 6.0, HUE_LIGHTS, transition=1)
            b.lights[4].state(bri=255, on=True)
            time.sleep(13) # wait until you open the first servo
            flicker(b, 1.0, HUE_LIGHTS, transition=1)
            open_servo() # takes 1.5 seconds
            close_servo() # takes 0.5 seconds
            time.sleep(1)
            move_cont_servo() # takes 0.3 seconds
            while video_process.poll() is None:  # Wait for the second video to finish
                time.sleep(0.5)
            video_process = play_video(VIDEO_ONE, True)  # Switch back to playing the first video on loop   
            time.sleep(1) # wait for video to start
            # turn lights back on
            for light in HUE_LIGHTS:
                b.lights[light].state(bri=255, on=True)
            motion = False
        time.sleep(0.1)
except KeyboardInterrupt:
    p.stop()
    pwm.stop()
    GPIO.cleanup()
    if video_process:
        video_process.send_signal(signal.SIGINT)  # Send interrupt signal to the video process
        video_process.wait()  # Wait for the process to terminate
    print('Finish...')