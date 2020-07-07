import time
import Adafruit_DHT
import datetime
import ssl
import board
from PIL import Image
import numpy as np
from picamera import PiCamera
import RPi.GPIO as GPIO
from fractions import Fraction
import secret
import random
import pymongo

client = pymongo.MongoClient(secret.connstring,
                             ssl=True,
                             ssl_cert_reqs=ssl.CERT_NONE) #connstring is a variable comming from secret.py containing mongo db connection string
db=client.test

print(time.strftime("%Y-%m-%d %H:%M:%S"),"initializing gpios")
pin = 24
ledPin=26
GPIO.setmode(GPIO.BCM)
GPIO.setup(ledPin, GPIO.OUT)
print("intializing sensor")
sensor = Adafruit_DHT.DHT22

import requests
print("importing tf")
import tensorflow as tf
print("importing keras")
from tensorflow.keras.preprocessing.image import ImageDataGenerator

print("loading model")
model = tf.keras.models.load_model('digit_model6.h5')

#preprocessing functions applied on picture to be predicted
datagen=ImageDataGenerator(
    samplewise_center=True,
    samplewise_std_normalization=True,
)
print("done")

def predict_digit(flat_digit):
    im=np.array(flat_digit).reshape(1,28,28,3)
    prediction = model.predict(datagen.flow(im))
    return int(prediction.argmax())

print(time.strftime("%Y-%m-%d %H:%M:%S"),"initializing camera")

f_out="temp_cam3.jpg"
while True:
    GPIO.output(ledPin, GPIO.HIGH)
    print(time.strftime("%Y-%m-%d %H:%M:%S"),"starting preview")
    camera=PiCamera()
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
        #camera.exposure_mode = 'off'
        print(time.strftime("%Y-%m-%d %H:%M:%S"),"capturing")
        camera.capture(f_out, resize=(1920,270),format='jpeg',quality=100)
        print(time.strftime("%Y-%m-%d %H:%M:%S"),"captured")
    finally:
        camera.close()
    GPIO.output(ledPin, GPIO.LOW)
    im = Image.open(f_out)
    padding_left=83
    padding_top=112+28+8
    offset=162
    side=112
    offset_last=32 #last digit is on my display somewhat more to the right
    predlist=[]
    capture_photo_to_db=random.random()>0.975
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
        #predict class and append to list of predicted list:
        predlist.append(predict_digit(flatDigit))
        if capture_photo_to_db:
            try:
                db.gas_digit.insert_one({"image": flatDigit,"date": timestamp,"digit_position":j})
            except pymongo.errors.ServerSelectionTimeoutError:
                print("timeout error")
    gas_reading=int("".join(str(x) for x in predlist)) #convert list of predicted digits to integer
    humidity, temperature=Adafruit_DHT.read_retry(sensor, pin)
    if humidity==None:
        humidity="None"
    if temperature==None:
        temperature="None"
    print("gas:",gas_reading,"temp:"+str(temperature) + " humidity:" + str(humidity))
    url = 'http://35.234.91.159/gas/update.php'
    myobj = {'temperature': temperature,'gas':gas_reading,'humidity':humidity}
    requests.post(url, data = myobj)
    time.sleep(600)
