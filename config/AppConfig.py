import json
import os
from pathlib import Path

from utils.env_utils import EnvInit
from keras.utils import data_utils


#os.environ["CUDA_DEVICE_ORDER"]="PCI_BUS_ID" #If the line below doesn't work, uncomment this line (make sure to comment the line below); it should help.
# os.environ['CUDA_VISIBLE_DEVICES'] = '1'

env = EnvInit()
REPO_PATH = env.REPO or '../repo'
GATEWAY = env.GATEWAY
PROCESS_WORKERS = env.get("PROCESS_WORKERS", 4)

GATEWAY_EMIT_URL = os.path.join(GATEWAY, 'emit') if GATEWAY else None
MODEL_CACHE_TIMEOUT = env.MODEL_CACHE_TIMEOUT or 60*60*4

# HERMES_URL = env.HERMES_URL or 'http://0.0.0.0:8082/'
# HERMES_EMIT_URL = os.path.join(HERMES_URL, *'/ds4biz/hermes/0.0/emit'.split('/'))
# GATEWAY_URL = env.GATEWAY_URL or 'http://0.0.0.0:8080'
# GATEWAY_EMIT_URL = os.path.join(GATEWAY_URL, *'/emit'.split('/'))
# print(GATEWAY_EMIT_URL)

KERAS_PRETRAINED_MODELS = [
    "ConvNeXtBase",
    "ConvNeXtLarge",
    "ConvNeXtSmall",
    "ConvNeXtTiny",
    "ConvNeXtXLarge",
    "DenseNet121",
    "DenseNet169",
    "DenseNet201",
    "EfficientNetB0",
    "EfficientNetB1",
    "EfficientNetB2",
    "EfficientNetB3",
    "EfficientNetB4",
    "EfficientNetB5",
    "EfficientNetB6",
    "EfficientNetB7",
    "EfficientNetV2B0",
    "EfficientNetV2B1",
    "EfficientNetV2B2",
    "EfficientNetV2B3",
    "EfficientNetV2L",
    "EfficientNetV2M",
    "EfficientNetV2S",
    "InceptionResNetV2",
    "InceptionV3",
    "MobileNet",
    "MobileNetV2",
    "NASNetLarge",
    "NASNetMobile",
    "RegNetX002",
    "RegNetX004",
    "RegNetX006",
    "RegNetX008",
    "RegNetX016",
    "RegNetX032",
    "RegNetX040",
    "RegNetX064",
    "RegNetX080",
    "RegNetX120",
    "RegNetX160",
    "RegNetX320",
    "RegNetY002",
    "RegNetY004",
    "RegNetY006",
    "RegNetY008",
    "RegNetY016",
    "RegNetY032",
    "RegNetY040",
    "RegNetY064",
    "RegNetY080",
    "RegNetY120",
    "RegNetY160",
    "RegNetY320",
    "ResNet101",
    "ResNet101V2",
    "ResNet152",
    "ResNet152V2",
    "ResNet50",
    "ResNet50V2",
    "ResNetRS101",
    "ResNetRS152",
    "ResNetRS200",
    "ResNetRS270",
    "ResNetRS350",
    "ResNetRS420",
    "ResNetRS50",
    "VGG16",
    "VGG19",
    "Xception"
]


PRETRAINED_CLASS_INDEX_PATH = (
    "https://storage.googleapis.com/download.tensorflow.org/"
    "data/imagenet_class_index.json"
)

fpath = data_utils.get_file(
    "imagenet_class_index.json",
    PRETRAINED_CLASS_INDEX_PATH,
    cache_subdir="models",
    file_hash="c2c37ea517e94d9795004a39431a14cb",
)
with open(fpath) as f:
    PRETRAINED_CLASS_INDEX = json.load(f)

PRETRAINED_CLASSES = [PRETRAINED_CLASS_INDEX[cl_k][1] for cl_k in PRETRAINED_CLASS_INDEX]
