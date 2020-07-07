import pymongo
import ssl
import numpy as np
import matplotlib.pyplot as plt
import secret

client = pymongo.MongoClient(secret.connstring,
                             ssl=True,
                             ssl_cert_reqs=ssl.CERT_NONE) #connstring is a variable comming from secret.py containing mongo db connection string
db=client.test

# select digit which does not contain label yet
cursor=db.gas_digit.find({
    'label': {
        '$in': [
            0, 1, 2, 3, 4, 5, 6, 7, 8, 9
        ]
    },
    'model1_prediction':{
        '$in': [
            0, 1, 2, 3, 4, 5, 6, 7, 8, 9
        ]
    }
},{"label":1,"digit_position":1,"model1_prediction":1})

misclassified=np.zeros((8,10))
ground_true=np.zeros((8,10))

for document in cursor:
    id=document["_id"]
    label=document["label"]
    pos=document["digit_position"]
    pred=document["model1_prediction"]

    ground_true[pos][label]+=1
    if label!=pred:
        misclassified[pos][label]+=1

print(ground_true.astype("int"))
print(misclassified.astype("int"))
conf_m=misclassified/ground_true
print(conf_m.round(2))
