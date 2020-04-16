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
cursor=db.gas_digit.find({
    'label': {
#        '$not': {
            '$in': [
                0, 1, 2, 3, 4, 5, 6, 7, 8, 9
            ]
#        }
    }
},{"image":1,"date":1,"label":1})

# if uncommented, delete everything...
## for document in cursor:
##    db.gas_digit.delete_one({"_id":document["_id"]})

for document in cursor:
    #if(document.get("label")==10):# I use label 10 for data to be deleted
    db.gas_digit.delete_one({"_id":document["_id"]})
    #continue
