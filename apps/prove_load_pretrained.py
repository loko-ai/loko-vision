import json

from PIL import Image
from keras.applications.imagenet_utils import CLASS_INDEX

from tensorflow import keras
#
from keras.utils import data_utils
CLASS_INDEX_PATH = (
    "https://storage.googleapis.com/download.tensorflow.org/"
    "data/imagenet_class_index.json"
)

fpath = data_utils.get_file(
    "imagenet_class_index.json",
    CLASS_INDEX_PATH,
    cache_subdir="models",
    file_hash="c2c37ea517e94d9795004a39431a14cb",
)
with open(fpath) as f:
    CLASS_INDEX = json.load(f)
# print(f"CLASSSSSSS {CLASS_INDEX}")
cl = [CLASS_INDEX[cl_k][1] for cl_k in CLASS_INDEX]
# for cl in CLASS_INDEX:
#     print(cl)
print(cl)
# es = keras.applications.ResNet50()
# img_path = "/home/roberta/vision_data_&_tutorial/license.jpg"
# img = Image.open(img_path)
#
# res = es.predict([img])
# print(res)
# predictor_name = "ResNet50"
# pretrained_model = "ResNet50"

# model_parameters = dict(__klass__='ds4biz.KerasImagePredictor',
#                         pretrained_model=predictor_name,
#                         predictor_name=predictor_name)
# model = FACTORY(model_parameters)
# e = model.predict([img])
#
# def preprocess_input(X):
#     # send_message(self.predictor_name, "Image Pre-Processing")
#     base_model = models_mapping[pretrained_model]['model']()
#     ### transfer learning ###
#     base_mdl_out_size = base_model.layers[-2].output.type_spec.shape[1]
#     input_shape = base_model.input.type_spec.shape[1:3]
#     print(f"input shape {input_shape}")
#
#     X = [image.img_to_array(xx.convert('RGB').resize(input_shape, Resampling.NEAREST)) for xx in X]
#     X = np.array(X)
#     print(f"x:;; {X}")
#     X = models_mapping[pretrained_model]['preprocess_input'](X)
#     print(f"x {X}")
#     return X
#
# model = models_mapping[pretrained_model]['model']()
#
# xx = preprocess_input([img])
# pred = model.predict(xx)
# print(pred)