import tensorflow as tf
import numpy as np
import matplotlib.pyplot as plt
import time
import pymongo
import ssl
from tensorflow.keras.preprocessing.image import ImageDataGenerator
import secret

client = pymongo.MongoClient(secret.connstring) #connstring is a variable comming from secret.py containing mongo db connection string
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
train_datagen=ImageDataGenerator(
    samplewise_center=True,
    samplewise_std_normalization=True,
    width_shift_range=0.1,
    height_shift_range=0.2
)
validation_datagen=ImageDataGenerator(
    samplewise_center=True,
    samplewise_std_normalization=True,
)

model = tf.keras.Sequential([
    tf.keras.layers.Convolution2D(64,(3,3),input_shape=(28,28,3)),
    tf.keras.layers.MaxPool2D((2,2)),
    tf.keras.layers.Flatten(),
    tf.keras.layers.Dense(128, activation='relu'),
    tf.keras.layers.Dense(10,activation='softmax')
])

model_save_path="model/digit_model4"

class Stopper(tf.keras.callbacks.Callback):
        def on_epoch_end(self,epoch,logs):
            if logs.get('accuracy')>=0.998:
                print("model good enough, stopping training...")
                self.model.stop_training=True

model.compile(optimizer='adam', loss='sparse_categorical_crossentropy', metrics=['accuracy'])

stopper=Stopper() #create callback object
print(model.summary())
history=model.fit(train_datagen.flow(x=train_images,
                                     y=train_labels,
                                     batch_size=32),
                    steps_per_epoch=len(train_images)/32,
                    epochs=40,
                    validation_data=validation_datagen.flow(x=validation_images,
                                                       y=validation_labels,
                                                       batch_size=16),
                    callbacks=[stopper])

model.save(model_save_path)

#plot training progress
import matplotlib.pyplot as plt
acc = history.history['accuracy']
val_acc = history.history['val_accuracy']
loss = history.history['loss']
val_loss = history.history['val_loss']

epochs = range(len(acc))

plt.plot(epochs, acc, 'r', label='Training accuracy')
plt.plot(epochs, val_acc, 'b', label='Validation accuracy')
plt.title('Training and validation accuracy')
plt.legend(loc=0)

plt.show()
plt.plot(epochs, loss, 'r', label='Training loss')
plt.plot(epochs, val_loss, 'b', label='Validation loss')
plt.title('Training and validation loss')
plt.legend(loc=0)
plt.show()
