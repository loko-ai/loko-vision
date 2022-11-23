import json
from pathlib import Path

import numpy as np
import tensorflow.keras.applications as models
from PIL import Image
from PIL.Image import Resampling
from tensorflow.keras.preprocessing import image
from tensorflow.python.keras import Model
from tensorflow import keras

from config.AppConfig import REPO_PATH
from config.genericConfig import PRETRAINED_TH_PREDICTION
from model.callbacks import ClassifierWrapper
from utils.logger_utils import logger
from utils.prediction_utils import inverse_sigmoid, softmax
# from utils.service_utils import send_message

repo = Path(REPO_PATH)

models_mapping = {}
for name in dir(models):
    if name[0].isupper():
        mdl_name = getattr(models, name)
        mdl_api_name = '.'.join(mdl_name._keras_api_names[0].split('.')[:-1])
        if 'preprocess_input' in dir(eval(mdl_api_name)) and 'decode_predictions' in dir(eval(mdl_api_name)):
            pi = eval(mdl_api_name + '.preprocess_input')
            dp = eval(mdl_api_name + '.decode_predictions')
            models_mapping[name] = dict(model=mdl_name, preprocess_input=pi, decode_predictions=dp)


class ImagePredictor:
    def predict(self, X, **kwargs):
        pass

    def fit(self, X, y, **kwargs):
        pass


class KerasImagePredictor(ImagePredictor):
    def __init__(self, predictor_name, pretrained_model="ResNet50", predictor_tag=None,top_layer=None, mlb=False, h5=False):
        self.predictor_name = predictor_name
        self.pretrained_model = pretrained_model
        self.predictor_tag = predictor_tag
        self._base_model = None
        self.mlb = mlb
        self.h5 = False
        if top_layer:
            if 'sklearn' in top_layer.__class__.__module__:
                top_layer = ClassifierWrapper(predictor=top_layer)
            else:
                self.h5 = True
        self.top_layer = top_layer

    @property
    def base_model(self):
        if not self._base_model:
            self._base_model = models_mapping[self.pretrained_model]['model']()
            ### transfer learning ###
            self.base_mdl_out_size = self._base_model.layers[-2].output.type_spec.shape[1]
            if self.top_layer:
                self._base_model = Model(self._base_model.input, self._base_model.layers[-2].output)
        return self._base_model

    def _preprocess_input(self, X):
        # send_message(self.predictor_name, "Image Pre-Processing")
        input_shape = self.base_model.input.type_spec.shape[1:3]
        X = [image.img_to_array(xx.convert('RGB').resize(input_shape, Resampling.NEAREST)) for xx in X]
        X = np.array(X)
        X = models_mapping[self.pretrained_model]['preprocess_input'](X)
        return X

    def _check_model_input_shape(self):
        '''
        Function that check and eventually correct the input size of the new tf models,
        based on the output size of the pretrained model chosen.
        '''
        mdl_config = self.top_layer.get_config()
        mdl_input_shape = mdl_config["layers"][0]["config"]["batch_input_shape"]
        if mdl_input_shape != self.base_mdl_out_size:
            mdl_config["layers"][0]["config"]["batch_input_shape"] = (None, self.base_mdl_out_size)
            self.top_layer.update_model_from_config(mdl_config)

    def fit(self, X, y, callbacks=None, **kwargs):
        # send_message(self.predictor_name, "Model Fitting")
        X = self._preprocess_input(X)
        if self.h5:
            self._check_model_input_shape()
        vecs = self.base_model.predict(X)
        self.top_layer.fit(vecs, y, callbacks=callbacks)


    def predict(self, X, multilabel=False, **kwargs):
        # print(top)
        #todo: gestire casi in cui una delle pred==1 e Multilabel=False
        #
        def get_preds_with_class(preds, top=None):
            top = top or len(self.top_layer.classes_)
            preds = zip(self.top_layer.classes_, preds)
            print("Preds")
            return sorted(preds, key=lambda x: x[1], reverse=True)[:top]

        ### transfer learning ###
        X = self._preprocess_input(X)
        if self.top_layer:
            # send_message(self.predictor_name, "Starts prediction")
            logger.debug("creating input vector using pre-trained model")
            vecs = self.base_model.predict(X)
            logger.debug('computing predictions...')
            preds = self.top_layer.predict_proba(vecs)
            if not multilabel:
                logger.debug("transforming prediction form multilabel to multiclass...")
                preds_inv_sig = [inverse_sigmoid(np.array(el_pred)) for el_pred in preds]
                preds = [softmax(el_pred).tolist() for el_pred in preds_inv_sig]
            logger.debug("getting prediction...")
            return [get_preds_with_class(el) for el in preds]
        else:
            # send_message(self.predictor_name, "Starts prediction")
            logger.debug("starting predictions...")
            preds = self.base_model.predict(X)
            n_classes = len(preds[0])
            logger.debug("decoding prediction classes..")
            preds = models_mapping[self.pretrained_model]['decode_predictions'](preds, top=n_classes)  # , top=top)
            p = [[(x[1], float(x[2])) for x in y if float(x[2]) > PRETRAINED_TH_PREDICTION] for y in preds]
            return p

    def __getstate__(self):
        logger.debug("I'm being pickled")
        if self.h5:
            self.top_layer.save(path=repo / self.predictor_name)
            self.top_layer.model = None
            return dict(pretrained_model=self.pretrained_model, top_layer=self.top_layer, h5=self.h5, mlb=self.mlb,
                        predictor_name=self.predictor_name)  # , target_vectorizer=self.top_layer.target_vectorizer)
        return dict(pretrained_model=self.pretrained_model, top_layer=self.top_layer, h5=self.h5, mlb=self.mlb,
                    predictor_name=self.predictor_name)

    def __setstate__(self, d):
        logger.debug(f"I'm being unpickled with these values: {d}" )
        self.__dict__ = d
        self.__init__(**d)
