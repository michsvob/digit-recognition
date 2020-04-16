# digit-recognition
Recognition of digits of an analogue gas meter with Python, Tensorflow, MongoDB and Raspberry Pi

## Project
The aim of this project is to readout the analogue gas meter using a camera, recognize digits using deep neural network and show the results on web dashboard.

## Tasks
### Mechanical set-up and wiring
Raspberry Pi Camera has been attached close to the gas meter together with LED module, which is switched using GPIO output.![alt text][camera_setup]

### Training data acquisition
This is done using the data_acquisition.py script running on Raspberry Pi 3. The camera captures image, this is then cropped and digits are extracted from fixed areas. The individual digits are resized to 28x28 pixels (x3 color channels) and uploaded to MongoDB database hosted in MondoDB Atlas Cloud as a flat list of 8-bit integers. Image of whole display is stored in the db as well in case new framing of digits was needed.

### Data labelling
Data has been labelled using some helper functions, which show the image and ask user for label or labels the samples in batch:

* labeller.py
* batch_labeller.py
* display_labeller.py

The script train_valid_splitter.py splits the labelled data into training and validation set (70/30)

### Model in Tensorflow
The script train.py defines and trains the deep neural network for image classification. The model uses 2D convolution layer followed by max_pooling layer, hidden fully connected neural network layer and output layer with softmax activation.

```python
Model: "sequential"
_________________________________________________________________
Layer (type)                 Output Shape              Param #   
=================================================================
conv2d (Conv2D)              (None, 26, 26, 64)        1792      
_________________________________________________________________
max_pooling2d (MaxPooling2D) (None, 13, 13, 64)        0         
_________________________________________________________________
flatten (Flatten)            (None, 10816)             0         
_________________________________________________________________
dense (Dense)                (None, 128)               1384576   
_________________________________________________________________
dense_1 (Dense)              (None, 10)                1290      
=================================================================
Total params: 1,387,658
Trainable params: 1,387,658
Non-trainable params: 0
_________________________________________________________________
```

The model accuracy on a validation set is around 98 %. This is very good result given the relatively poor quality of images and largely varying light conditions. On the other hand, the first 4 digits of the display did not change over the time of data acquisition, therefore the model performs great on the first 4 positions and on recognizing digits, which were displayed on these, but performs worse on the last positions.
(TODO: Confusion matrix!)

[camera_setup]: setup.jpg "Mechanical setup"
