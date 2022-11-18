import logging
from pathlib import Path
from typing import List, Union, Dict

import numpy as np
import tensorflow as tf
import tensorflow.keras
from sklearn.preprocessing import MultiLabelBinarizer

from tensorflow.keras.models import load_model

from config.AppConfig import REPO_PATH
from config.genericConfig import PREDICTOR_H5_FILENAME

predictor_name = "modello2"
predictor_path = Path(REPO_PATH)
path = predictor_path / predictor_name / PREDICTOR_H5_FILENAME

model = load_model(path)
print("model: ", model.summary())

