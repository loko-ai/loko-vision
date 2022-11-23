from config.FactoryConfig import FACTORY
from dao.predictors_dao import PredictorsDAO
from model.mlmodel import models_mapping
from utils.logger_utils import logger

pdao = PredictorsDAO()


def get_models_list(models_type, info=False):
    if models_type == "custom":
        models = [m.name for m in pdao.all()]
        print(models)
    elif models_type == "pretrained":
        models = [k for k in models_mapping.keys()]
    else:
        if info:
            custom_models = [dict(name=m.name, type="custom") for m in pdao.all()]
            pretrained_models = [dict(name=m, type="pretrained") for m in models_mapping.keys()]
            models = custom_models + pretrained_models
        else:
            models = [custom_mod.name for custom_mod in pdao.all()] + [p_mod for p_mod in models_mapping.keys()]
    return models


def get_model_info(predictor_name, advanced_info=False):  # , model_info=False):
    p = pdao.get(predictor_name)
    logger.debug(f"pppppp::: {p.model_parameters}")

    tl_params = p.model_parameters
    res = dict(predictor_name=p.predictor_name, pretrained_model=p.pretained_model, predictor_tag=p.predictor_tag,
               fitted=p.fitted)
    if tl_params is not None:
        if tl_params["__klass__"] == 'ds4biz.NNpredictor':
            m = FACTORY(p.model_parameters)
            if advanced_info:
                n_classes = m.model.layers[-1].units
                n_layer = len(m.model.layers)
                metrics = m.metrics
                loss_function = m.loss
                epochs = m.epochs
                top_layer_info = dict(n_layer=n_layer, n_classes=n_classes, metrics=metrics,
                                      loss_function=loss_function,
                                      epochs=epochs)
                res["top_layer"] = top_layer_info
    return res
