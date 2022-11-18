import os
import traceback

import requests

from config.AppConfig import GATEWAY_URL
from utils.logger_utils import logger


def send_message(name, msg):
    if GATEWAY_URL:
        try:
            url = os.path.join(GATEWAY_URL, *'/emit'.split('/'))
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