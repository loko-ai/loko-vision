import time
import timeit

import tensorflow as tf

from business.tf_learning import predict_task
from model.mlmodel import KerasImagePredictor
from PIL import Image
import io

# tf.keras.backend.clear_session() ## to clear other sessions in the environment

# tf.config.optimizer.set_jit(False)
# img_path = "../apps/Colline.jpg"
img_path= "/home/roberta/Downloads/fronte_patente.jpg"
img = Image.open(img_path)



def image_to_byte_array(image: Image) -> bytes:
  # BytesIO is a file-like buffer stored in memory
  imgByteArr = io.BytesIO()
  # image.save expects a file-like as a argument
  image.save(imgByteArr, format=image.format)
  # Turn the BytesIO object back into a bytes object
  imgByteArr = imgByteArr.getvalue()
  return imgByteArr

img_bytes = image_to_byte_array(img)

class A():
  pass

a = A()
a.name="colline.jpg"
a.body = img_bytes
predictor_name="ConvNeXtTiny"



# i1 = time.time()
# predict_task(a, predictor_name, True, False, None, 0.0001)
# f1 = time.time()
# v1 = f1-i1
#
#
# def m2():
#   i2 = time.time()
#   img = Image.open(img_path)
#   kp = KerasImagePredictor(predictor_name=predictor_name, pretrained_model=predictor_name)
#   kp.predict([img])
#   f2=time.time()
#   print(f2-i2)
#   return f2-i2

# print(f"method 1: {f1-i1}----------- #method 2: {f2-i2}")

# def foo():
#   i1 = time.time()
#   predict_task(a, predictor_name, True, False, None, 0.0001)
#   f1 = time.time()
#   v2 = f1 - i1
#   print(v2)
#   return v2

# t = []
# for i in range(100):
#   t.append(foo())
#
# print(t)

# print("fooo",timeit.timeit(foo, number=20))

# print("m2 ",timeit.timeit(m2, number=20))

# ee = []
# for i in range(100):
#   ee.append(m2())
#
# print(ee)
#
predictor_name="ConvNeXtTiny"
# i1 = time.time()
# predict_task(a, predictor_name, True, False, None, 0.0001)
# f1 = time.time()
# v2 = f1-i1
#
# i1 = time.time()
# predict_task(a, predictor_name, True, False, None, 0.0001)
# f1 = time.time()
# v3 = f1-i1
#
# i1 = time.time()
# predict_task(a, predictor_name, True, False, None, 0.0001)
# f1 = time.time()
# v4 = f1-i1


i2 = time.time()
img = Image.open(img_path)
kp = KerasImagePredictor(predictor_name=predictor_name, pretrained_model=predictor_name)
kp.predict([img])
f2=time.time()
v1 = f2-i2


i1 = time.time()
predict_task(a, predictor_name, True, False, None, 0.0001)
f1 = time.time()
v4 = f1-i1


i2 = time.time()
img = Image.open(img_path)
kp = KerasImagePredictor(predictor_name=predictor_name, pretrained_model=predictor_name)
kp.predict([img])
f2=time.time()
v2 = f2-i2

i1 = time.time()
predict_task(a, predictor_name, True, False, None, 0.0001)
f1 = time.time()
v3 = f1-i1
print(f"ptlast {v3},kp {v1}, pt {v4},kp {v2}")

# print(f"v 1: {v1}----------- v 2: {v2} ----------- v 3: {v3} ----------- v 3: {v4} ")

