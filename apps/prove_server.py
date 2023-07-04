import numpy as np
from PIL import Image
from tensorflow import keras

from PIL import Image
from PIL.Image import Resampling
from tensorflow.keras.preprocessing import image
from tensorflow.keras.applications.resnet50 import preprocess_input


import time


img_path = "Colline.jpg"
img = Image.open(img_path)
model = keras.applications.ResNet50()
model
input_shape = model.input.type_spec.shape[1:3]

def preprocess_and_predict(X):
    inizio = time.time()
    X = [image.img_to_array(xx.convert('RGB').resize(input_shape, Resampling.NEAREST)) for xx in X]
    X = np.array(X)
    X = preprocess_input(X)
    pred=model.predict(X)
    fine = time.time()
    print("fine: ", fine-inizio)
    return fine-inizio

t = preprocess_and_predict([img])
t2 = preprocess_and_predict([img])
t3 = preprocess_and_predict([img])
t4 = preprocess_and_predict([img])
t5 = preprocess_and_predict([img])
t6 = preprocess_and_predict([img])
t7 = preprocess_and_predict([img])
t8 = preprocess_and_predict([img])
t9 = preprocess_and_predict([img])
t10 = preprocess_and_predict([img])

print("-"*200)
print(f"t: {t}, t2: {t2}, t3: {t3}, t4: {t4}, t5: {t5}, t6: {t6}, t7: {t7}, t8: {t8}, t9: {t9}, t1>





