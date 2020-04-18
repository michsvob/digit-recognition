import time
import pymongo
import ssl
from PIL import Image
import numpy as np
import matplotlib.pyplot as plt
from datetime import datetime
import secret

client = pymongo.MongoClient(secret.connstring) #connstring is a variable comming from secret.py containing mongo db connection string
db=client.test


# select digit
cursor=db.gas_digit.find({
    'digit_position': {
        #'$not': {
            '$in': [
                0,1,2,3,4,5,6,7 #set label position!!!!!
            ]
        #}
    },
    'label': {
        '$not': {
            '$in': [
                1,2,3,4,5,6,7,8,9,0
            ]
        }
    }
},{"image":1,"date":1,"label":1})


for document in cursor:
    pic=np.array(document["image"]).reshape(28,28,3)
    id=document["_id"]

    #preprocess picture
    pic=(pic-pic.min())/(pic.max()-pic.min())#normalize
    pic=pic/pic.max() #scale to 0-1

    if document['date']>datetime.strptime("2020-04-16 21:00","%Y-%m-%d %H:%M") and document['date']<datetime.strptime("2020-04-17 11:00","%Y-%m-%d %H:%M"):
        print(document['date'])
        # display image
        plt.figure()
        plt.imshow(pic)
        plt.colorbar()
        plt.grid(False)
        plt.ion()
        plt.show()
        plt.pause(0.05)
        plt.close()
        label=1# Set label!!!!!!!
        db.gas_digit.delete_one({"_id":id})
        #db.gas_digit.update_one({"_id":id},{"$set":{"label":label}})
