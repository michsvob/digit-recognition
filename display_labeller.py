import time
import pymongo
import ssl
from PIL import Image
import numpy as np
import matplotlib.pyplot as plt
import secret

client = pymongo.MongoClient(secret.connstring) #connstring is a variable comming from secret.py containing mongo db connection string
db=client.test


# select digit which does not contain label yet
cursor=db.gas_full.find({
    'label': {
        '$not': {
            '$in': [
                11,1
            ]
        }
    }
},{"image":1,"date":1,"label":1})

# if uncommented, delete everything...
## for document in cursor:
##    db.gas_digit.delete_one({"_id":document["_id"]})

for document in cursor:
    if(document.get("label")==10):# I use label 10 for data to be deleted
        db.gas_full.delete_one({"_id":document["_id"]})
        continue

    print(document["_id"],document["date"],document["image"][0:5])

    # reshape data so that they can be displayed as picture
    # 28 px x 28 px x 3 channels
    print()
    pic=np.array(document["image"]).reshape(39,240,3)
    id=document["_id"]

    # display image
    plt.figure()
    plt.imshow(pic)
    plt.colorbar()
    plt.grid(False)
    plt.ion()
    plt.show()
    plt.pause(0.5)
    plt.close()

    # read label
    label=input("This number is: ")
    label=int(label)
    if(label==10):
        # if you set label 10, delete record
        print("record deleted")
        db.gas_full.delete_one({"_id":id})
    else:
        # update database record
        db.gas_full.update_one({"_id":id},{"$set":{"label":label}})
