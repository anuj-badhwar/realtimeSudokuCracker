import keras
from keras.models import Sequential
from keras.models import load_model
from keras.layers import Dense, Dropout, Flatten
from keras.layers import Conv2D, MaxPooling2D
import numpy as np

def loadModel():
    classifier = load_model('mnistTrained.h5')
    return classifier

def predictDigit(classifier, input):

    inp = np.array(input)
    nd = inp.shape[0]
    input = inp.reshape((nd,28,28,1))
    digits = classifier.predict_classes(input,verbose=True)
    for d in digits:
        if d==0:
            d=8
    return digits
