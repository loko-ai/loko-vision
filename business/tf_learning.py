from itertools import chain

# from config.AppConfig import GATEWAY_EMIT_URL
import sanic
from sanic.exceptions import SanicException

from config.FactoryConfig import FACTORY
from config.genericConfig import MODEL_EPOCHS
from dao.predictors_dao import PredictorsDAO
from model.mlmodel import models_mapping
from model.predictors_model import PredictorRequest
from utils.imageutils import read_imgs
# from utils.service_utils import send_message
from utils.logger_utils import logger

pdao = PredictorsDAO()


def training_task(f, model_info: PredictorRequest):
    pretrained_model = model_info.pretained_model
    predictor_name = model_info.predictor_name
    predictor_tag = model_info.predictor_tag
    X, y, fnames = read_imgs(f)

    # print(len(X[0]))
    # print(len(X))
    # print(len(y))
    print(f"============> y {y}")
    n_outputs_lbl = len(set(chain.from_iterable(y)))
    parameters = dict(__klass__='ds4biz.KerasImagePredictor',
                      top_layer=dict(__klass__='ds4biz.NNpredictor',

                                     model=dict(__klass__='tfkeras.Sequential',
                                                layers=[dict(__klass__="tfkeras.Dense", units=n_outputs_lbl,
                                                             activation="sigmoid",
                                                             input_dim=2048)]),
                                     optimizer="adam", loss="binary_crossentropy", metrics=["accuracy"],
                                     epochs=MODEL_EPOCHS),
                      pretrained_model=pretrained_model,
                      predictor_name=predictor_name,
                      predictor_tag=predictor_tag,
                      mlb=True,
                      )
    model = FACTORY(parameters)
    # print(m.top_layer)
    msg = 'model factorized'
    logger.debug(msg)
    # send_message(predictor_name, msg)
    # print(url)
    # cb = LogsCallback(epochs=MODEL_EPOCHS, url=GATEWAY_EMIT_URL, model_name=predictor_name)
    model_info.model_parameters = parameters
    model_info.model_parameters["fitted"] = "Training"
    pdao.save(model_info)
    model.fit(X, y, epochs=MODEL_EPOCHS)  # , callbacks=[cb])
    logger.debug('%s model fitted with pretrained model %s...' % (predictor_name, pretrained_model))
    model_info.model_parameters = parameters
    model_info.model_obj = model
    model_info.model_parameters["fitted"] = True
    pdao.save(model_info)


def predict_task(f, predictor_name, proba, multilabel, mlb_threshold, proba_threshold):
    X, y, fnames = read_imgs(f)
    ### use custom model ###

    ### use custom model ###
    if predictor_name not in models_mapping.keys():
        logger.debug("using custom model")
        pr = pdao.get(predictor_name)
        model = pr.model_obj
        if model is None:
            msg = f"Predictor '{predictor_name}' not yet fitted, you have to train the model first"
            logger.error(msg)
            raise SanicException(msg, status_code=400)
    else:
        ## use pretrained model ###
        logger.debug("using pretrained model")

        model_parameters = dict(__klass__='ds4biz.KerasImagePredictor',
                                pretrained_model=predictor_name,
                                predictor_name=predictor_name)
        model = FACTORY(model_parameters)
    preds = model.predict(X, multilabel=multilabel)
    logger.debug(f"================================================\n{preds}")
    logger.debug("len preds %s, len files %s" % (str(len(preds)), str(len(fnames))))
    if not proba:
        if mlb_threshold != None:
            logger.debug("prediction without predict_proba, mlb threshold!=none : %s " % str(preds))
            preds = [[label[0] for label in p if label[1] >= mlb_threshold] for p in preds]  # [0]
        else:
            logger.debug("prediction without predict_proba, mlb threshold==none : %s " % str(preds))

            preds = [[pp[0] for pp in p][0] for p in preds]  # [0]
            logger.debug(len(preds))
    else:
        preds = [ [(label[0], label[1]) for label in p if label[1]>=proba_threshold] for p in preds]
    preds_res = [dict(fname=fn, pred=p) for fn, p in zip(fnames, preds)]

    # if mlb_threshold != None:
    #     preds = [dict(fname=p["fname"], pred=1) if p["pred"]>mlb_threshold else dict(fname=p["fname"], pred=0) for p in preds ]
    logger.debug('preds: %s' % str(preds_res))
    return preds_res




def evaluate_task(f, predictor_name):
    X, y, fnames = read_imgs(f)

    if predictor_name not in models_mapping.keys():
        logger.debug("using custom model")

        pr = pdao.get(predictor_name)
        model = pr.model_obj
        if model is None:
            msg = f"Predictor '{predictor_name}' not yet fitted, you have to train the model first"
            logger.error(msg)
            raise SanicException(msg, status_code=400)
    else:
        logger.debug("using pretrained model")

        ## use pretrained model ###
        model_parameters = dict(__klass__='ds4biz.KerasImagePredictor',
                                pretrained_model=predictor_name,
                                predictor_name=predictor_name)
        model = FACTORY(model_parameters)

    res = model.evaluate(X, y)
    return res


