import joblib
import keras
import numpy as np
from PIL import Image
from tensorflow.python.keras.models import load_model
from tensorflow.keras.preprocessing import image
from PIL.Image import Resampling
from tensorflow.keras.applications.resnet50 import preprocess_input
from tensorflow.python.keras import Model

from utils.prediction_utils import inverse_sigmoid, softmax

model_path = "/home/roberta/loko/projects/loko-vision/repo/license_registration/"
model = "license_registration"
fileh5 = "NNpredictor.h5"

### loading the model (which is a kerasImagePredictor class)
#
# model_obj = joblib.load(model_path + model)
# print(f"this file contains a {type(model_obj)} object")
#
# ### predicting img class
#
# img_path = "/home/roberta/loko/data/vision/patente_test.jpg"
# with Image.open(img_path) as img:
#     prediction = model_obj.predict([img])
#     print(prediction)

### loading the h5 model


model = load_model(model_path + fileh5)

print(f"this model is of type {type(model)}")

pretrained_model = keras.applications.ResNet50()  # pretrained model used
input_shape = pretrained_model.input.type_spec.shape[1:3]  # input shape of the model of the pretrained model
base_model = Model(pretrained_model.input, pretrained_model.layers[
    -2].output)  # model to use for the transfer learning (we are excluding the top layer, to add ours)

img_path = "/home/roberta/loko/data/vision/patente_test.jpg"
with Image.open(img_path) as img:
    X = [image.img_to_array(xx.convert('RGB').resize(input_shape, Resampling.NEAREST)) for xx in [img]]
    X = np.array(X)
    X = preprocess_input(X)
    pretrained_vec_pred = base_model.predict(X)
    transfer_learning_pred = model.predict(pretrained_vec_pred)
    # we trained all the loko-vision models as if it was multilabel, since in this case the model is not a multilabel we apply an invers transformation and the softmax to make the actual prediction
    preds_inv_sig = [inverse_sigmoid(np.array(el_pred)) for el_pred in transfer_learning_pred]
    preds = [softmax(el_pred).tolist() for el_pred in preds_inv_sig]

print("prediction results starting from the h5 model:", preds)
