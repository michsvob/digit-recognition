# Gas meter digit recognition
Recognition of digits of an analogue gas meter with Python, Tensorflow, MongoDB and Raspberry Pi

## Project
The aim of this project is to readout the analogue gas meter using a camera, recognize digits using deep neural network and show the results on web dashboard.

## Tasks
### Mechanical set-up and wiring
Raspberry Pi Camera has been attached close to the gas meter together with LED module, which is switched using GPIO output.![alt text][camera_setup]

### Training data acquisition
This is done using the data_acquisition.py script running on Raspberry Pi 3. The camera captures image, this is then cropped and digits are extracted from fixed areas. The individual digits are resized to 28x28 pixels (x3 color channels) and uploaded to MongoDB database hosted in MondoDB Atlas Cloud as a flat list of 8-bit integers. Image of whole display is stored in the db as well in case new framing of digits was needed.

#### Training data
Image captured by Raspberry camera looks like this:

![alt text][display_whole]

Extracted display portion:

![alt text][display_extracted]

Extracted digits look like this:

![alt text][digit1]
![alt text][digit2]
![alt text][digit3]
![alt text][digit4]
![alt text][digit5]
![alt text][digit6]
![alt text][digit7]
![alt text][digit8]


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
Data has been pre-processed by centering pixel values for each sample around 0 and divided by their standard deviations. Also data augmentation has been used to account for horizontal and especially vertical variation in the position of the digits.

The model accuracy on a validation set is around 98 % and with the used optimizer parameters the model converges to optimal parameters very quickly. This is very good result given the relatively poor quality of images and largely varying light conditions.

Learning curves:

![alt text][learning_curves]
![alt text][learning_curves_loss]

On the other hand, the first 4 digits of the display did not change over the time of data acquisition, therefore the model performs great on the first 4 positions and on recognizing digits, which were displayed on these, but performs worse on the last positions.

```
Number of labelled samples (digit vs. position):

          0    1    2    3    4    5    6    7    8    9
---------------------------------------------------------
pos.1 [ 971    0    0    0    0    0    0    0    0    0]
pos.2 [   0    0    0    0    0    0  990    0    0    0]
pos.3 [   0 1007    0    0    0    0    0    0    0    0]
pos.4 [   0    0    0    0    0    0    0    0 1002    0]
pos.5 [   0    0    0    0    0    0  172  730   99    0]
pos.6 [ 612   48   27    4    4    7    8   26  116  151]
pos.7 [  21   78   42   43   14   61  515   76   52  101]
pos.8 [  34   78   11   76  491   78   20    8  131   53]

Misclassified ratio:

          0    1    2    3    4    5    6    7    8    9
---------------------------------------------------------
pos.1 [0.    nan  nan  nan  nan  nan  nan  nan  nan  nan]
pos.2 [ nan  nan  nan  nan  nan  nan 0.04  nan  nan  nan]
pos.3 [ nan 0.    nan  nan  nan  nan  nan  nan  nan  nan]
pos.4 [ nan  nan  nan  nan  nan  nan  nan  nan 0.    nan]
pos.5 [ nan  nan  nan  nan  nan  nan 0.01 0.   0.    nan]
pos.6 [0.   0.   0.   0.   0.   0.   0.   0.   0.   0.05]
pos.7 [0.05 0.   0.   0.   0.07 0.02 0.01 0.   0.02 0.01]
pos.8 [0.12 0.04 0.18 0.12 0.   0.   0.25 0.   0.05 0.  ]
```
## Feedback
If you find this project interesting, please let me know about that! Also if you have some questions to how this has been done or you want to do it yourself, don't hesitate to ask.

TODO: deployment
TODO: web dashboard

[camera_setup]: setup.jpg "Mechanical setup"
[learning_curves]: learning_curves.png "Learning curves - accuracy"
[learning_curves_loss]: learning_curves_loss.png "Learning curves - loss"
[digit1]: digit1.png "Digit1"
[digit2]: digit2.png "Digit2"
[digit3]: digit3.png "Digit3"
[digit4]: digit4.png "Digit4"
[digit5]: digit5.png "Digit5"
[digit6]: digit6.png "Digit6"
[digit7]: digit7.png "Digit7"
[digit8]: digit8.png "Digit8"
[display_whole]: temp_cam.jpg "Display (whole)"
[display_extracted]: croppedtest.jpg "Display (extracted portion)"
