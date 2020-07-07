import time
import pymongo
import datetime
import ssl
import board
from PIL import Image
import numpy as np
from picamera import PiCamera
import RPi.GPIO as GPIO
import secret

print(time.strftime("%Y-%m-%d %H:%M:%S"),"connecting to db")
client = pymongo.MongoClient(secret.connstring,
                             ssl=True,
                             ssl_cert_reqs=ssl.CERT_NONE) #connstring is a variable comming from secret.py containing mongo db connection string
db=client.test
print(time.strftime("%Y-%m-%d %H:%M:%S"),"connected")
ledPin=26
GPIO.setup(ledPin, GPIO.OUT)

while True:
    GPIO.output(ledPin, GPIO.HIGH)
    print(time.strftime("%Y-%m-%d %H:%M:%S"),"starting preview")
    camera=PiCamera()
    f_out="temp_cam.jpg" #temporary file with image of display
    try:
        camera.zoom=(25.22/51,8.1/18.5,8.99/51,0.89/18.5) # extract field of view with display
        camera.rotation=180
        camera.resolution =(1920,1080)
#        camera.exposure_mode = 'night'
#        camera.sensor_mode=3
#        print("starting preview")
#        camera.start_preview()
#        print("preview started")
        time.sleep(10)
        camera.exposure_mode = 'off'
        print(time.strftime("%Y-%m-%d %H:%M:%S"),"capturing")
        camera.capture(f_out, resize=(1920,270),format='jpeg',quality=100)
        print(time.strftime("%Y-%m-%d %H:%M:%S"),"captured")
    finally:
        camera.close()
    GPIO.output(ledPin, GPIO.LOW)
    im = Image.open(f_out)
    padding_left=83
    padding_top=112
    offset=162
    side=112
    offset_last=32 #last digit is on my display somewhat more to the right
    timestamp=datetime.datetime.now()
    for j in range(8):
        #extract digits and save flattened image data 28x28x3 to db
        window=(padding_left+j*offset+int(j==7)*offset_last,
                padding_top,
                padding_left+j*offset+side+int(j==7)*offset_last,
                padding_top+side)
        digit=im.crop(window)
        digit=digit.resize((28,28))
        digit.save("digit"+str(j+1)+".png")
        flatDigit=np.array(digit.getdata()).flatten()
        flatDigit=[k.item() for k in flatDigit] #convert numpy.int to int
        try:
            db.gas_digit.insert_one({"image": flatDigit,"date": timestamp,"digit_position":j})
        except pymongo.errors.ServerSelectionTimeoutError:
            print("timeout error")
    time.sleep(600)