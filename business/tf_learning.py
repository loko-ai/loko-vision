from itertools import chain

# from config.AppConfig import GATEWAY_EMIT_URL

from sanic.exceptions import SanicException

from business.evaluate_report import compute_reports
from config.AppConfig import PRETRAINED_CLASSES, GATEWAY_EMIT_URL
from config.FactoryConfig import FACTORY
from dao.predictors_dao import PredictorsDAO
from model.callbacks import LogsCallback
from model.mlmodel import models_mapping
from model.predictors_model import PredictorRequest
from utils.imageutils import read_imgs
# from utils.service_utils import send_message
from loguru import logger
from utils.service_utils import send_message

pdao = PredictorsDAO()



def training_task(f, model_info: PredictorRequest, epochs=100, optimizer="adam", metrics: list = ["accuracy"]):
    pretrained_model = model_info.pretained_model
    predictor_name = model_info.predictor_name
    predictor_tag = model_info.predictor_tag
    X, y, fnames = read_imgs(f, predictor_name)

    n_outputs_lbl = len(set(chain.from_iterable(y)))
    if n_outputs_lbl < 2:
        send_message(predictor_name, "Error: you cannot train a model with only one label.")
        raise Exception("Error: you cannot train a model with only one label.")
    parameters = dict(__klass__='ds4biz.KerasImagePredictor',
                      top_layer=dict(__klass__='ds4biz.NNpredictor',
                                     model=dict(__klass__='tfkeras.Sequential',
                                                layers=[dict(__klass__="tfkeras.Dense", units=n_outputs_lbl,
                                                             activation="sigmoid",
                                                             input_dim=2048)]),
                                     optimizer=optimizer, loss="binary_crossentropy", metrics=metrics,
                                     epochs=epochs),
                      pretrained_model=pretrained_model,
                      predictor_name=predictor_name,
                      predictor_tag=predictor_tag,
                      mlb=True,
                      )
    model = FACTORY(parameters)
    # print(m.top_layer)
    msg = 'Model Factorized'
    logger.debug(msg)
    send_message(predictor_name, msg)
    # print(url)
    cb = LogsCallback(epochs=epochs, url=GATEWAY_EMIT_URL, model_name=predictor_name)
    model_info.model_parameters = parameters
    model_status =  "Training"
    model_info.model_parameters["fitted"] = model_status
    pdao.save(model_info)
    logger.debug("model status correctly updated to {model_status}")
    model.fit(X, y, epochs=epochs, callbacks=[cb])
    logger.debug('%s model fitted with pretrained model %s...' % (predictor_name, pretrained_model))
    model_info.model_parameters = parameters
    model_info.model_obj = model
    model_info.model_parameters["fitted"] = True
    pdao.save(model_info)


def predict_task(f, predictor_name, proba, multilabel, mlb_threshold, proba_threshold):
    X, y, fnames = read_imgs(f, predictor_name)
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
        model = pdao.get(predictor_name, custom_model=False)
        # model_parameters = dict(__klass__='ds4biz.KerasImagePredictor',
        #                         pretrained_model=predictor_name,
        #                         predictor_name=predictor_name)
        #
        # # model = FACTORY(model_parameters)
        # model = f_cached(**model_parameters)
    preds = model.predict(X, multilabel=multilabel)
    logger.debug("len preds %s, len files %s" % (str(len(preds)), str(len(fnames))))
    if not proba:
        if mlb_threshold != None:
            # logger.debug("prediction without predict_proba, mlb threshold!=none : %s " % str(preds))
            preds = [[label[0] for label in p if label[1] >= mlb_threshold] for p in preds]  # [0]
        else:
            # logger.debug("prediction without predict_proba, mlb threshold==none : %s " % str(preds))

            preds = [[pp[0] for pp in p][0] for p in preds]  # [0]
            logger.debug(len(preds))
    else:
        preds = [[(label[0], label[1]) for label in p if label[1] >= proba_threshold] for p in preds]
    preds_res = [dict(fname=fn, pred=p) for fn, p in zip(fnames, preds)]

    # if mlb_threshold != None:
    #     preds = [dict(fname=p["fname"], pred=1) if p["pred"]>mlb_threshold else dict(fname=p["fname"], pred=0) for p in preds ]
    # logger.debug('preds: %s' % str(preds_res))
    return preds_res


def evaluate_task(f, predictor_name):
    X, y, fnames = read_imgs(f, predictor_name)

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
        model = pdao.get(predictor_name, custom_model=False)
        ## use pretrained model ###
        # model_parameters = dict(__klass__='ds4biz.KerasImagePredictor',
        #                         pretrained_model=predictor_name,
        #                         predictor_name=predictor_name)
        # model = FACTORY(model_parameters)
    if model.top_layer is None:
        ytrue_labels = list(set(y))
        if ytrue_labels not in PRETRAINED_CLASSES:
            pretrained_labels_site = "https://storage.googleapis.com/download.tensorflow.org/data/imagenet_class_index.json"
            msg = f"The ground truth labels must belong to the Imagenet labels list. You can check the list here: {pretrained_labels_site}"
            raise SanicException(msg, status_code=400)
    # if model.top_layer is not None:
    #     res = model.evaluate(X, y)
    # logger.debug(f"evaluate metrics: {res}")
    logger.debug("computing prediction for report")
    preds = model.predict(X, multilabel=False)
    preds = [[pp[0] for pp in p][0] for p in preds]

    logger.debug("computing report")
    y = [el[0] for el in y]
    if model.top_layer:
        labels = sorted(model.top_layer.classes_)
    else:
        labels = None
    report = compute_reports(y_true=y, y_pred=preds, labels=labels)

    logger.debug(f"report::: {report}")
    return report
