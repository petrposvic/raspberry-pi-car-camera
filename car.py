#!/usr/bin/python
import os
import subprocess
import time
import picamera
import gps
import RPi.GPIO as GPIO

# Where to save records (directory must exist and end with slash)
basedir = "/home/pi/"

# Set to None if you don't want use camera
camera = picamera.PiCamera()
if camera != None:
    #camera.resolution = (640, 480)
    camera.resolution = (1280, 720)
    #camera.resolution = (1640, 922) # Full Field of View
    camera.framerate = 15

# Video length (in seconds)
VIDEO_MAX_LENGTH = 120

GPIO.setmode(GPIO.BCM)
GPIO.setwarnings(True)
GPIO.setup(10, GPIO.IN)
GPIO.setup(17, GPIO.OUT)
GPIO.output(17, False)

filename = None
count = 0
part = 0

try:
  while True:

      # Blink LED in case of low space
      free_space = subprocess.check_output(
          ["/bin/df /home/pi | tail -1 | /usr/bin/awk '{print $5}' | /bin/sed 's/%//'"],
          shell=True
      )
      if int(free_space) > 95:
          print("Low space on disk")
          if (GPIO.input(17) == False):
              GPIO.output(17, True)
          else:
              GPIO.output(17, False)

      # Check button state
      if (GPIO.input(10) == False):
          os.system('date')

          if (filename == None):
              filename = time.strftime("%Y-%m-%d_%H-%M-%S")
              count = 0
              part = 1

              # Turn on LED
              GPIO.output(17, True)

              # Start recording
              if camera != None:
                  print("starting camera recording...")
                  camera.start_recording(basedir + filename + "_" + str(part) + ".h264")

              # Connect to GPS daemon
              os.system('/usr/sbin/gpsd /dev/ttyS0 -F /var/run/gpsd.sock')
              for i in range(0, 4):
                  print("waiting for GPS daemon...")
                  time.sleep(1)
              session = gps.gps("localhost", "2947")
              session.stream(gps.WATCH_ENABLE | gps.WATCH_NEWSTYLE)

              print("new filename " + filename)
          else:
              filename = None

              # Turn off LED
              GPIO.output(17, False)

              # Stop recording
              if camera != None:
                  try:
                      print("stopping camera recording...")
                      camera.stop_recording()
                  except picamera.exc.PiCameraNotRecording:
                      pass

              # Disconnect from GPS daemon
              os.system('/usr/bin/killall gpsd')
              session = None
      else:
          pass

      if filename != None:

          # Continue recording in new file (if needed)
          if camera != None:
              count = count + 1
              if count > VIDEO_MAX_LENGTH:
                  count = 0
                  part = part + 1
                  print("video part #" + str(part))

                  try:
                      print("stopping camera recording...")
                      camera.stop_recording()
                  except picamera.exc.PiCameraNotRecording:
                      pass

                  print("starting camera recording...")
                  camera.start_recording(basedir + filename + "_" + str(part) + ".h264")

          # Check GPS
          if session != None:
              try:
                  report = session.next()
                  # print report
                  if report['class'] == 'TPV':
                      if hasattr(report, 'time') and hasattr(report, 'alt') and hasattr(report, 'lat') and hasattr(report, 'lon'):
                          print report.time, report.lat, report.lon
                          with open(basedir + filename + ".txt", "a") as f:
                             f.write(report.time + ' ' + str(report.alt) + ' ' + str(report.lat) + ' ' + str(report.lon) + '\r\n')
              except KeyError:
                  pass
              except StopIteration:
                  session = None
                  print("GPSD has terminated")

      time.sleep(1)
except KeyboardInterrupt:
    print("Exit by keyboard interrupt")

    # Turn off LED
    GPIO.output(17, False)

    # Release camera
    if camera != None:
        try:
            print("stopping camera recording...")
            camera.stop_recording()
        except picamera.exc.PiCameraNotRecording:
            pass

    # Shut down GPS daemon
    os.system('/usr/bin/killall gpsd')

    quit()

