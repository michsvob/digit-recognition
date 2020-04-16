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

client = pymongo.MongoClient(connstring) #connstring is a variable comming from secret.py containing mongo db connection string
db=client.test


#stream = BytesIO()
camera = PiCamera()
camera.zoom=(0.5,0.44,0.14,0.14)
camera.exposure_mode="night"
camera.rotation=180
camera.resolution = (2592,1944)
#https://picamera.readthedocs.io/en/release-1.10/recipes1.html#capturing-in-low-light
camera.framerate = Fraction(1, 6)
camera.shutter_speed = 1000000
camera.exposure_mode = 'off'
camera.iso = 800

pin = 24
ledPin=3
GPIO.setup(ledPin, GPIO.OUT)

sensor = Adafruit_DHT.DHT22

for i in range(1000):
    GPIO.output(ledPin, GPIO.HIGH)
    camera.start_preview()
    time.sleep(5)
    camera.capture("temp_cam.jpg", format='jpeg',quality=100)
    camera.stop_preview()
    GPIO.output(ledPin, GPIO.LOW)
    # "Rewind" the stream to the beginning so we can read its content
    #https://picamera.readthedocs.io/en/latest/recipes1.html#capturing-to-a-file
    #stream.seek(0)
    im = Image.open("temp_cam.jpg")
#    window=(left, upper, right, lower) = (58, 247, 714, 330)
    window=(left, upper, right, lower) = (170, 900, 2570, 1290)
    cropped = im.crop(window)
    cropped.save('/home/pi/gas_images/cropped%s.jpg' %i)

    timestamp=datetime.datetime.now()

    padding_left=100
    padding_top=100
    offset=280
    side=200
#    padding_top=5
#    padding_left=9
#    offset=80
#    side=60

    for j in range(8):
        #extract digits and save flattened image data 28x28x3 to db
        window=(padding_left+j*offset,padding_top,padding_left+j*offset+side,padding_top+side)
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
