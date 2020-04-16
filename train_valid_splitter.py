import pymongo
import ssl
from PIL import Image
import random
import secret

client = pymongo.MongoClient(connstring) #connstring is a variable comming from secret.py containing mongo db connection string
db=client.test


# select digit
cursor=db.gas_digit.find({
    'dataset': {
        '$not': {
            '$in': [
                "training","validation"
            ]
        }
    }
})

for document in cursor:
    dataset="training"
    if random.random()>0.7:
        dataset="validation"
    id=document["_id"]
    print(document["_id"])

    db.gas_digit.update_one({"_id":id},{"$set":{"dataset":dataset}})
