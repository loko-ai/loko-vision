import logging
from pathlib import Path
from typing import List, Union, Dict

import numpy as np
import tensorflow as tf
from tensorflow import keras
import tensorflow.keras
from sklearn.preprocessing import MultiLabelBinarizer

from tensorflow.keras.models import load_model

from config.AppConfig import REPO_PATH
from config.genericConfig import PREDICTOR_H5_FILENAME
from utils.logger_utils import logger

repo = Path(REPO_PATH)
#todo: cambiare print in log

class NNClassifierWrapperException(Exception):
    pass


class NNClassifierWrapper:
    '''
    Neural Network class for Image Classification. Using the sigmoid function a Multi-label model will be built.

    '''

    def __init__(self,
                 model: tensorflow.keras.Sequential = None,
                 # task: {"regression", "classification"},
                 optimizer: tensorflow.keras.activations or str = "sigmoid",
                 # factory = None,
                 epochs: int = 1000,
                 loss: str = None,
                 metrics: List[str] = None,
                 loss_weights: Union[List[float], Dict] = None,
                 steps_per_execution: int = 252,
                 run_eagerly: bool = True,
                 target_vectorizer=None,
                 **compile_kwargs
                 ):
        self.model = model
        self.epochs = epochs
        self.optimizer = optimizer
        self.loss = loss
        self.metrics = metrics
        self.loss_weights = loss_weights
        self.steps_per_execution = steps_per_execution
        self.run_eagerly = run_eagerly
        self.compile_kwargs = compile_kwargs
        self.target_vectorizer = target_vectorizer
        self.multilabel = False
        if self.model is not None and self.model.layers != []:
            if self.model.layers[-1].activation.__name__ == "sigmoid":
                self.multilabel = True
                self.target_vectorizer = target_vectorizer or MultiLabelBinarizer()
        else:
            logger.warn("The NN predictor model is empty or None")


    @property
    def classes_(self):
        return self.target_vectorizer.classes_

    def _cast_target_to_numpy(self, data):
        return np.array(data)

    def get_config(self):
        return self.model.get_config()

    def update_model_from_config(self, config):
        self.model = tf.keras.Sequential().from_config(config)

    def fit(self, X, y, callbacks=None, batch_size=64):
        logger.debug("nnfit....")
        # try:
        if self.multilabel:
            logger.debug("transforming target variable...")
            y = self.target_vectorizer.fit_transform(y)
        logger.debug("casting data to numpy")
        logger.debug(f"Y val pre:::: {y}")

        y = self._cast_target_to_numpy(y)
        logger.debug(f"Y val:::: {y}")

        X = self._cast_target_to_numpy(X)
        logger.debug("compiling and fitting model...")
        self.model.compile(optimizer=self.optimizer, loss=self.loss, metrics=self.metrics)
        self.model.fit(X, y, epochs=self.epochs, batch_size=batch_size, callbacks=callbacks)
        # print(self.model.layers[-1].get_weights())
        # except Exception as inst:
        #     print(inst)

    def predict_proba(self, X):
        X = self._cast_target_to_numpy(X)
        # print(X)
        res = [[float(pred) for pred in el] for el in self.model.predict(X)]
        logger.debug(f"predictor NN predict-proba: {res}",)
        return res

    def evaluate(self, X, y):
        logger.debug("NN evaluate")
        logger.debug(f"Y pre val:::: {y}")

        X = self._cast_target_to_numpy(X)
        if self.multilabel:
            logger.debug("transforming target variable...")
            y = self.target_vectorizer.fit_transform(y)
        y = self._cast_target_to_numpy(y)
        # logger.debug(X)
        logger.debug(f"Y val:::: {y}")
        eval = self.model.evaluate(X, y)
        logger.debug(f"eval::: {eval}")
        metrics_name = self.model.metrics_names
        logger.debug(f"metrics_name = {metrics_name}")
        eval_res = {m_name: m_value for m_value, m_name in zip(eval, metrics_name)}
        logger.debug(f"eval_res: {eval_res}")
        logger.debug(f"keras {keras.__version__}")
        logger.debug(f"tf {tf.__version__}")
        if "loss" in eval_res:
            logger.debug(f"los---- {self.loss}")
            logger.debug(f"losses {self.model.losses}")
            loss_name = self.loss
            eval_res[loss_name] = eval_res.pop("loss")
        logger.debug(f"evaluate res::::: -----> {eval_res}")
        return eval_res

    def save(self, path):
        self.predictor_name = path.name
        self.model.save(path / PREDICTOR_H5_FILENAME)

    def load_model(self, predictor_name):
        path = repo / predictor_name / PREDICTOR_H5_FILENAME
        self.model = load_model(path)
        if self.model.layers[-1].activation.__name__ == "sigmoid":
            self.multilabel = True
        logger.debug(f"loaded model... model class: {self.model}")



    def __getstate__(self):
        logger.debug("I'm a NN and I'm being pickled")
        return dict(epochs=self.epochs, optimizer=self.optimizer, loss=self.loss, metrics=self.metrics,
                    loss_weights=self.loss_weights, steps_per_execution=self.steps_per_execution,
                    run_eagerly=self.run_eagerly, multilabel=self.multilabel, target_vectorizer=self.target_vectorizer,
                    predictor_name=self.predictor_name)

    def __setstate__(self, d):
        logger.debug("I'm a NN and I'm being unpickled with these values: " + repr(d))
        self.__init__(**d)
        self.load_model(predictor_name=d["predictor_name"])