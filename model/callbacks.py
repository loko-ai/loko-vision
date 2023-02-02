import os
import traceback

import requests
from tensorflow import keras
from datetime import datetime
from sklearn.metrics import accuracy_score
from tensorflow.keras.callbacks import EarlyStopping



#todo: cancellare e passare a predictor_base
from utils.logger_utils import logger


class LogsCallback(keras.callbacks.Callback):

    def __init__(self, epochs=None, url=None, model_name=None, **kwargs):
        super().__init__(**kwargs)
        self.epochs = epochs
        self.url = url
        self.model_name = model_name
        self.epoch_start = None
        self.epoch_end = None
        self.train_start = None
        self.train_end = None

    def _send_message(f):
        def send(self, *args, **kwargs):
            msg = f(self, *args, **kwargs)
            logger.debug(msg)
            print(self.url)
            if self.url:
                try:

                    data = dict(event_name='event_ds4biz',  # fisso
                                content=dict(msg=msg,
                                             type='vision',  # chiedere a pisu
                                             name=self.model_name))  # nome modello
                    resp = requests.post(self.url, json=data)
                    logger.debug(f'RESP: {resp}')
                    print(dict(event_name='event_ds4biz',
                               content=dict(msg=msg,
                                            type='vision',
                                            name=self.model_name)))
                except:
                    logger.debug('GATEWAY ERROR')
                    logger.debug('TracebackERROR: \n' + traceback.format_exc() + '\n\n')
        return send

    @_send_message
    def on_train_begin(self, logs=None):
        self.train_start = datetime.now()
        return 'Training start'

    @_send_message
    def on_train_end(self, logs=None):
        self.train_end = datetime.now()
        seconds = (self.train_end - self.train_start).total_seconds()
        return 'Training end - %fs' % seconds

    def on_epoch_begin(self, epoch, logs=None):
        self.epoch_start = datetime.now()

    @_send_message
    def on_epoch_end(self, epoch, logs=None):
        self.epoch_end = datetime.now()
        infos = ' - '.join(['%s: %s' % (str(k), str(v)) for k, v in logs.items()])
        seconds = (self.epoch_end - self.epoch_start).total_seconds()
        return f'Ep {epoch+1}/{self.epochs} - loss: {round(logs.get("loss"), 3)}'
        # return 'Epoch %d/%d - %ss - ' % (epoch + 1, self.epochs, seconds) + infos


class PredictorWrapper:

    def __init__(self, predictor):
        # if not (hasattr(predictor, 'max_iter') and hasattr(predictor, 'warm_start')):
        #     raise Exception('Predictor not available!')
        self.predictor = predictor
        self.predictor.max_iter = 10
        self.predictor.warm_start = True
        self.stop_training = False

    def predict(self, X):
        return self.predictor.predict(X)


class ClassifierWrapper(PredictorWrapper):

    @property
    def classes_(self):
        return self.predictor.classes_

    def fit(self, X, y, epochs=100, callbacks=None):
        logger.debug("entro in un altro ft")
        callbacks = callbacks or []

        # for c in callbacks:
        #     c.model = self
        #     c.on_train_begin()

        for epoch in range(epochs):
            # for c in callbacks:
            #     c.on_epoch_begin(epoch)
            self.predictor.fit(X, y)
            loss = accuracy_score(y, self.predictor.predict(X))
            iters = self.predictor.n_iter_
            # for c in callbacks:
            #     c.on_epoch_end(epoch, logs=dict(loss=loss, iterations=iters))

            if self.stop_training:
                break

        # for c in callbacks:
        #     c.on_train_end()

    def predict_proba(self, X):
        return self.predictor.predict_proba(X)


if __name__ == '__main__':
    def prova1():
        from sklearn.linear_model import LogisticRegression
        from sklearn.datasets import make_classification

        X, y = make_classification(n_samples=10000, n_features=20, n_classes=2)
        clf = ClassifierWrapper(predictor=LogisticRegression())
        cb = LogsCallback(epochs=10, url='http://0.0.0.0:8080/ds4biz/hermes/0.0/emit', model_name='ciccio')
        es = EarlyStopping(monitor='loss', patience=2)
        clf.fit(X, y, epochs=10, callbacks=[cb, es])


    def prova2():
        from sklearn.datasets import make_classification
        from keras.models import Sequential
        from keras.layers import Dense

        X, y = make_classification(n_samples=10000, n_features=20, n_classes=2)

        model = Sequential()
        model.add(Dense(60, input_dim=20, activation='relu'))
        model.add(Dense(1, activation='sigmoid'))
        # Compile model
        model.compile(loss='binary_crossentropy', optimizer='adam', metrics=['accuracy'])
        cb = LogsCallback(epochs=10, url='http://0.0.0.0:8080/ds4biz/hermes/0.0/emit', model_name='ciccio')

        model.fit(X, y,
                  batch_size=100,
                  epochs=10,
                  callbacks=[cb])


    prova1()
    prova2()
