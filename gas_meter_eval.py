import tensorflow as tf
import numpy as np
import matplotlib.pyplot as plt
from PIL import Image
import pymongo
import ssl
import secret
from tensorflow.keras.preprocessing.image import ImageDataGenerator

client = pymongo.MongoClient(secret.connstring) #connstring is a variable comming from secret.py containing mongo db connection string
db=client.test

print(tf.__version__)
print(np.__version__)

model = tf.keras.models.load_model('model/digit_model4')

#preprocessing functions applied on picture to be predicted
datagen=ImageDataGenerator(
    samplewise_center=True,
    samplewise_std_normalization=True,
)

print("loading data")
cursor=db.gas_digit.find({
    'label': {
            '$in': [
                0, 1, 2, 3, 4, 5, 6, 7, 8, 9
            ]
    },
    'dataset':{
            '$in': [
                'validation','training'
            ]
    }
},{"image":1,"date":1,"label":1,'digit_position':1,'dataset':1})


def predict_class(im):
    prediction = model.predict(datagen.flow(im))
    return int(prediction.argmax())#convert numpy int64 to python int in order to be able to write to database later on

def showimage(image):
    #preprocess picture for display
    image=(image-image.min())/(image.max()-image.min())#normalize
    image=image/image.max() #scale to 0-1

    #plt.figure()
    #plt.imshow(image[0])
    #plt.colorbar()
    #plt.grid(False)
    #plt.ion()
    #plt.show()
    #plt.pause(0.1)
    #plt.close()

for document in cursor:
    id=document['_id']
    image=np.array(document['image']).reshape(1,28,28,3)
    label=document['label']
    position=document['digit_position']
    prediction=predict_class(image)
    error=""
    if prediction!=label:
        error=" bad prediction!"
    print("prediction:",predict_class(image),"label:",label,"position:",position," ",error)
    db.gas_digit.update_one({"_id":id},{"$set":{"model1_prediction":prediction}})
    showimage(image)
