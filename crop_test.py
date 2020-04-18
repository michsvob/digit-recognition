import time
import datetime
from PIL import Image
import numpy as np


im = Image.open("temp_cam.jpg")
window=(left, upper, right, lower) = (480, 640, 1830, 859)
cropped = im.crop(window)
cropped.save('cropped%s.jpg' %"test")

padding_left=55
padding_top=35
offset=155
side=112
offset_last=32

for j in range(8):
    #extract digits and save flattened image data 28x28x3 to db
    window=(padding_left+j*offset+int(j==7)*offset_last,
            padding_top,
            padding_left+j*offset+side+int(j==7)*offset_last,
            padding_top+side)
    digit=cropped.crop(window)
    #digit=digit.resize((28,28))
    digit.save("digit"+str(j+1)+".png")

#insert image of the whole display to db (resized from 2400 x 390 to 240 x 39)
#1350x210


im.resize((240,39))
