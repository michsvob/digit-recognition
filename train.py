import tensorflow as tf
import numpy as np
import matplotlib.pyplot as plt
import time
import pymongo
import ssl
from tensorflow.keras.preprocessing.image import ImageDataGenerator
import secret

client = pymongo.MongoClient(connstring) #connstring is a variable comming from secret.py containing mongo db connection string
db=client.test
print("loading data")
cursor=db.gas_digit.find({
    'label': {
            '$in': [
                0, 1, 2, 3, 4, 5, 6, 7, 8, 9
            ]
    },
    'dataset':{
            '$in': [
                'training','validation'
            ]
    }
},{"image":1,"date":1,"label":1,'digit_position':1,'dataset':1})

train_images=[]
train_labels=[]
train_positions=[]

validation_images=[]
validation_labels=[]
validation_positions=[]

n_training=0
n_validation=0
for document in cursor:
    if document['dataset']=='training':
        train_images.append(np.array(document['image']).reshape(28,28,3))
        train_labels.append(document['label'])
        train_positions.append(document['digit_position'])
        n_training+=1
    else:
        validation_images.append(np.array(document['image']).reshape(28,28,3))
        validation_labels.append(document['label'])
        validation_positions.append(document['digit_position'])
        n_validation+=1

print("data loaded")
print("training images:",n_training)
print("validation images:",n_validation)

validation_images=np.array(validation_images)
train_images=np.array(train_images)
validation_labels=np.array(validation_labels)
train_labels=np.array(train_labels)

#preprocess data
train_images=(train_images-train_images.min())/(train_images.max()-train_images.min())#normalize
train_images=train_images/train_images.max() #scale to 0-1
validation_images=(validation_images-validation_images.min())/(validation_images.max()-validation_images.min())#normalize
validation_images=validation_images/validation_images.max() #scale to 0-1


model = tf.keras.Sequential([
    tf.keras.layers.Convolution2D(64,(3,3),input_shape=(28,28,3)),
    tf.keras.layers.MaxPool2D((2,2)),
    tf.keras.layers.Flatten(),
    tf.keras.layers.Dense(128, activation='relu'),
    tf.keras.layers.Dense(10,activation='softmax')
])

model_save_path="model/digit_model3"

class Stopper(tf.keras.callbacks.Callback):
        def on_epoch_end(self,epoch,logs):
            print(logs)
            if logs.get('acc')>=0.998:
                print("model good enough, stopping training...")
                self.model.stop_training=True

model.compile(optimizer='adam', loss='sparse_categorical_crossentropy', metrics=['accuracy'])

stopper=Stopper() #create callback object
print(model.summary())
model.fit(x=train_images,y=train_labels,epochs=10)#for some reason does not work: ,callbacks=[stopper])

test_loss, test_acc = model.evaluate(validation_images,  validation_labels, verbose=1)

print('\nTest accuracy:', test_acc," Loss:",test_loss)

predictions = model.predict(validation_images)

model.save(model_save_path)
