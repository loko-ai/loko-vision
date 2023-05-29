import numpy as np
from PIL import Image
from tensorflow import keras

from PIL import Image
from PIL.Image import Resampling
from tensorflow.keras.preprocessing import image

from apps.prova_applications import models_mapping
from config.FactoryConfig import FACTORY
from utils.imageutils import read_imgs

img_path = "/home/roberta/Pictures/archittettura_Loko.png"
img = Image.open(img_path)

predictor_name = "ResNet50"
pretrained_model = "ResNet50"

# model_parameters = dict(__klass__='ds4biz.KerasImagePredictor',
#                         pretrained_model=predictor_name,
#                         predictor_name=predictor_name)
# model = FACTORY(model_parameters)
# e = model.predict([img])

def preprocess_input(X):
    # send_message(self.predictor_name, "Image Pre-Processing")
    base_model = models_mapping[pretrained_model]['model']()
    ### transfer learning ###
    base_mdl_out_size = base_model.layers[-2].output.type_spec.shape[1]
    input_shape = base_model.input.type_spec.shape[1:3]
    # print(f"input shape {input_shape}")

    X = [image.img_to_array(xx.convert('RGB').resize(input_shape, Resampling.NEAREST)) for xx in X]
    X = np.array(X)
    # print(f"x:;; {X}")
    X = models_mapping[pretrained_model]['preprocess_input'](X)
    # print(f"x {X}")
    return X

model = keras.applications.ResNet50()

xx = preprocess_input([img])
pred = model.predict(xx)

