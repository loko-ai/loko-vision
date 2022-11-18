import keras
from keras.applications.resnet import ResNet50
from tensorflow.python.keras.applications.mobilenet import MobileNet
from tensorflow.python.keras.applications.xception import Xception

# mn = MobileNet(weights="imagenet")
# print(len(mn.layers))
# xcp = Xception(weights="imagenet")
# print(xcp.count_params())
# print(xcp.summary())

import tensorflow.keras.applications as models
from tensorflow.keras.applications.resnet import preprocess_input
import tensorflow.keras as keras
models_mapping = {}
mm = dir(models)
print(mm)
# mm[0].

m = getattr(models, mm[0])
a = '.'.join(m._keras_api_names[0].split('.')[:-1])
dp = eval(a + '.decode_predictions')
print(dp)
#count params: model.count_params()
