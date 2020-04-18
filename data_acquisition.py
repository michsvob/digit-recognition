import time
import Adafruit_DHT
import pymongo
import datetime
import ssl
import board

from PIL import Image
import numpy as np
from picamera import PiCamera
#from io import BytesIO
import RPi.GPIO as GPIO
from fractions import Fraction

import secret

print("connecting to db")
client = pymongo.MongoClient(secret.connstring) #connstring is a variable comming from secret.py containing mongo db connection string
db=client.test
print("connected")

print("initializing camera")
#stream = BytesIO()
camera = PiCamera()
camera.zoom=(0.45,0.4,0.25,0.25)
camera.rotation=180
camera.resolution = (2592,1944)
#https://picamera.readthedocs.io/en/release-1.10/recipes1.html#capturing-in-low-light
camera.framerate = Fraction(1, 6)
camera.shutter_speed = 1000000
camera.exposure_mode = 'off'
camera.iso = 800
print("initialized")

print("initializing gpios")
pin = 24
ledPin=3
GPIO.setup(ledPin, GPIO.OUT)
print("done")
print("intializing sensor")
sensor = Adafruit_DHT.DHT22
print("done")

for i in range(100):
    GPIO.output(ledPin, GPIO.HIGH)
    print("starting preview")
    camera.start_preview()
    time.sleep(5)
    print("capturing")
    camera.capture("temp_cam.jpg", format='jpeg',quality=100)
    print("captured")
    camera.stop_preview()
    print("preview stopped")
    GPIO.output(ledPin, GPIO.LOW)
    #https://picamera.readthedocs.io/en/latest/recipes1.html#capturing-to-a-file
    im = Image.open("temp_cam.jpg")
    window=(left, upper, right, lower) = (480, 640, 1830, 859)
    cropped = im.crop(window)

    timestamp=datetime.datetime.now()

    padding_left=55
    padding_top=35
    offset=155
    side=112
    offset_last=32 #last digit is on my display somewhat more to the right

    for j in range(8):
        #extract digits and save flattened image data 28x28x3 to db
        window=(padding_left+j*offset+int(j==7)*offset_last,
                padding_top,
                padding_left+j*offset+side+int(j==7)*offset_last,
                padding_top+side)
        digit=cropped.crop(window)
        digit=digit.resize((28,28))
        digit.save("digit"+str(j+1)+".png")
        flatDigit=np.array(digit.getdata()).flatten()
        flatDigit=[k.item() for k in flatDigit] #convert numpy.int to int
        try:
            db.gas_digit.insert_one({"image": flatDigit,"date": timestamp,"digit_position":j})
        except pymongo.errors.ServerSelectionTimeoutError:
            print("timeout error")

    #insert image of the whole display to db (resized from 2400 x 390 to 240 x 39)
    flatFull=np.array(cropped.resize((240,39)).getdata()).flatten()
    flatFull=[k.item() for k in flatFull] #convert numpy.int to int
    try:
        db.gas_full.insert_one({"image": flatFull,"date": timestamp})
    except pymongo.errors.ServerSelectionTimeoutError:
        print("timeout error")

    humidity, temperature=Adafruit_DHT.read_retry(sensor, pin)
    print("temp:"+str(temperature) + " humidity:" + str(humidity))
    try:
        db.measurements.insert_one({"temperature":temperature, "humidity":humidity, "date": timestamp})
    except pymongo.errors.ServerSelectionTimeoutError:
        print("timeout error")
    time.sleep(600)

camera=0
