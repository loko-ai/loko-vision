import os
from pathlib import Path

from utils.env_utils import EnvInit

env = EnvInit()
REPO_PATH = env.REPO or '../repo'
MODEL_CACHE_TIMEOUT = env.MODEL_CACHE_TIMEOUT or 60
# HERMES_URL = env.HERMES_URL or 'http://0.0.0.0:8082/'
# HERMES_EMIT_URL = os.path.join(HERMES_URL, *'/ds4biz/hermes/0.0/emit'.split('/'))
GATEWAY_URL = env.GATEWAY_URL or 'http://0.0.0.0:8080'
GATEWAY_EMIT_URL = os.path.join(GATEWAY_URL, *'/emit'.split('/'))
print(GATEWAY_EMIT_URL)

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
