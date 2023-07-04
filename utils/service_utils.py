import os
import traceback

import requests

from config.AppConfig import GATEWAY_EMIT_URL
from loguru import logger

def check_predict_params(proba, proba_threshold, multilabel, mlb_threshold):
    if proba:
        proba_value_error_msg = "Probability threshold value error. This value must be a float number between 0 and 0.9999. Example: 0.2"
        if proba_threshold is not None and (proba_threshold == "" or proba_threshold.isspace):
            proba_threshold = 0.00
        else:
            try:
                proba_threshold = float(proba_threshold)
            except ValueError:
                raise Exception(proba_value_error_msg)
        if proba_threshold > 0.9999 or proba_threshold < 0.000000:
            raise Exception(proba_value_error_msg)
    if multilabel:
        mlb_value_error_msg = "Multilabel threshold value error. This value must be a float number between 0 and 0.9999. Example: 0.2"

        if mlb_threshold is not None and (mlb_threshold == "" or mlb_threshold.isspace):
            mlb_threshold = 0.5
        else:
            try:
                mlb_threshold = float(mlb_threshold)
            except ValueError:
                raise Exception(mlb_value_error_msg)
        if mlb_threshold > 0.9999 or mlb_threshold < 0.000000:
            raise Exception(mlb_value_error_msg)
    return proba_threshold, mlb_threshold


def send_message(name, msg):
    if GATEWAY_EMIT_URL:
        try:
            url = GATEWAY_EMIT_URL
            data = dict(event_name='event_ds4biz', #fisso
                        content=dict(msg=msg,
                                     type='vision', #chiedere a pisu
                                     name=name)) #nome modello
            resp = requests.post(url, json=data)
            logger.debug(f'RESP: {resp}')
            print(dict(event_name='event_ds4biz',
                       content=dict(msg=msg,
                                    type='vision',
                                    name=name)))
        except:
            logger.debug('GATEWAY ERROR')
            logger.debug('TracebackERROR: \n' + traceback.format_exc() + '\n\n')