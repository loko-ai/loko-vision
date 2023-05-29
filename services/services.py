import asyncio
import functools
import logging
import traceback
import zipfile
from itertools import chain

from loguru import logger
import os
import io
from pathlib import Path
from tempfile import NamedTemporaryFile

import sanic
import tensorflow as tf
from loko_extensions.business.decorators import extract_value_args
from sanic_ext.extensions.openapi import openapi

from sanic import Blueprint, text
from sanic import json, Sanic
from sanic.exceptions import SanicException, NotFound
from sanic.response import raw
from sanic_cors import CORS
from sanic_ext import Config
from sanic import Sanic
# from sanic_openapi.openapi2 import doc
from sanic_ext.extensions.openapi.definitions import Parameter
from sanic_ext.extensions.openapi.types import String

from business.evaluate_report import compute_reports
from business.tf_learning import training_task, predict_task, evaluate_task
from config.AppConfig import REPO_PATH, POOL
from dao.inmemory_dao import InMemoryDAO
from dao.predictors_dao import PredictorsDAO, PredictorDAOException
from model.mlmodel import models_mapping
from model.predictors_model import PredictorRequest
from utils.model_utils import get_models_list, get_model_info
from utils.pom_utils import get_pom_major_minor

# todo: 2 - controllare tipologia immagini non supportate e gestione errori file;
#      3 - aggiustare parametri dei servizi
#      4-
#


# todo (25/11/2022):
#  - gestire re-training modelli gia' trainati; FATTO !!!!
#  - gestire apertura modelli una volta "spento" il progetto e "riacceso"; ???? non vedo più lo stesso problema al momento
#  - gestire evaluate di modelli pre-trainati;
#  - dare piu' info nel servizio evaluate;
#  - gestire fit nel caso di nome modello non piu' presente; FATTO!!!!!

from utils.zip_utils import make_zipfile

#
# os.environ["XLA_FLAGS"]="--xla_gpu_cuda_data_dir=/usr/local/cuda-11.8"

# os.environ["LD_LIBRARY_PATH"]="$LD_LIBRARY_PATH:$CONDA_PREFIX/venv/lib/python3.10/site-packages/tensorrt/"


im_dao = InMemoryDAO()
pdao = PredictorsDAO()


def file(name='file'):
    def tmp(f):
        content = {"multipart/form-data": {
            "schema": {"type": "object", "properties": {name: {"type": "string", "format": "binary"}}}}}
        return openapi.body(content, required=True)(f)

    return tmp


def get_app(name):
    app = Sanic(name)
    app_config = Config(oas_url_prefix="/api", oas_ui_default="swagger",
                        swagger_ui_configuration=dict(DocExpansion=None))
    # blueprint.url_prefix = "/api"
    # app.blueprint(blueprint)
    app.extend(config=app_config)
    return app


name = "loko-vision"
app = get_app(name)
# url_prefix = f"loko_vision/{get_pom_major_minor()}/"
bp = Blueprint("default")  # , url_prefix=url_prefix)
# app.config["API_VERSION"] = get_pom_major_minor()
app.config["API_TITLE"] = name
CORS(app)
app.static("/web", "/frontend/dist")

# loko_vision/0.0/
get_models_params_description = '''
<b>model_type:</b> return the type of models available for the chosen category: pre-trained, custom or both types.
'''

#
@app.listener("before_server_start")
async def before_server_start(app: Sanic, loop):
    app.ctx.loop = loop
    # app.executor = ProcessPoolExecutor()




@app.get("/models/")
@openapi.tag('Vision')
@openapi.description(get_models_params_description)
@openapi.parameter(
    parameter=Parameter(name="model_type", schema=String(enum=["all", "custom", "pretrained"]), location="query"))
@openapi.parameter(name="info", description="Default info='False'", schema=str, location="query")
async def models(request):
    logger.debug("dentro get models")
    model_type = request.args.get("model_type", "all")
    model_info = eval(request.args.get("info", "false").capitalize())
    models = get_models_list(model_type, model_info)
    return json(models)


delete_params_description = '''
<b>predictor_name:</b> name of the predictor to delete
'''


@app.delete("/models/<predictor_name>")
@openapi.tag('Vision')
@openapi.parameter(name="predictor_name", location="path", required=True)
async def delete_model(request, predictor_name):
    # print([m.name for m in pdao.all()])
    if predictor_name not in [m.name for m in pdao.all()]:
        return json('Model %s does not exist!' % name, status=400)
    pdao.delete(predictor_name)
    return json('Model %s deleted' % predictor_name)


create_params_description = '''
<b>predictor_name:</b> name of the predictor to create
<b>pretrained_model:</b> pre-trained model to use for the transfer-learning model
'''


@app.post("/models/<predictor_name>")
@openapi.tag('Vision')
@openapi.description(create_params_description)
@openapi.parameter(name="predictor_tag", location="query")
@openapi.parameter(
    parameter=Parameter(name="pretrained_model", schema=String(enum=list(models_mapping.keys())), location="query"))
@openapi.parameter(name="predictor_name", location="path", required=True)
async def create_model(request, predictor_name):
    logger.debug(f"predictor creation {predictor_name}")
    if predictor_name == "":
        msg = "VISION SETTINGS MISSING!!!Model name not setted, you have to specify it"
        return json(msg, status=400)
    if predictor_name in models_mapping.keys():
        raise Exception("You cannot use this name for a custom model")
    if predictor_name in get_models_list(models_type="custom"):
        return json('Model %s already exist!' % predictor_name, status=400)

    pretrained_model = request.args.get("pretrained_model", 'ResNet50')
    predictor_tag = request.args.get("predictor_tag", None)

    psr = PredictorRequest(predictor_name=predictor_name, pretained_model=pretrained_model, predictor_tag=predictor_tag)
    try:
        pdao.save(psr)
    except PredictorDAOException as inst:
        logging.exception(inst)
        return json('Model %s already exist!' % predictor_name, status=400)
    return json('Model %s created' % (predictor_name))  # , status=200)



fit_params_description = '''
<b>predictor_name:</b> name of the predictor that you want to fit
<b>file:</b> zipped folder or single image
'''


@app.post("/models/<predictor_name>/fit")
@openapi.tag('Vision')
@openapi.description(fit_params_description)
# @openapi.parameter(doc.Boolean(name="multilabel"), location="query")
@openapi.parameter(name="optimizer", schema=str, value="adam", location="query")
@openapi.parameter(name="epochs", schema=int, location="query")
@openapi.parameter(name="metrics", schema=str, value="accuracy,", location="query")
@openapi.parameter(name="predictor_name", location="path", required=True)
@file()
async def fit(request, predictor_name):
    print(predictor_name)
    if predictor_name not in [m.name for m in pdao.all()]:
        return json(f"Model '{predictor_name}' doesn't exists", status=404)
    if predictor_name in models_mapping:
        return json("You cannot overwrite %s, it's a pre-trained model." % predictor_name, status=400)
    if not request.files.get("file"):
        return json("There is no file to train the model", status=400)
    else:
        f = request.files["file"][0]

    optimizer = request.args.get("optimizer", 'adam')

    epochs = request.args.get("epochs", 150)
    logger.debug(f"n. epochs {epochs}... optimizer chosen {optimizer}")

    metrics = request.args.get("metrics", "accuracy")
    logger.debug(f"metrics pre:: {metrics}")
    metrics = [el for el in metrics.split(",") if (not el.isspace()) & (len(el) > 0)]
    logger.debug(f"metrics post:: {metrics}")

    # if predictor_name in [m.name for m in pdao.all()]:
    #     return json('Model %s already exist!' % predictor_name, status=400) #todo: decidere se lasciarlo
    model_info = pdao.get(predictor_name)
    model_obj = model_info.model_obj
    if model_obj != None:
        return json("Predictor already fitted", status=400)

    training_task(f, model_info, epochs, optimizer, metrics)
    #
    # loop = asyncio.get_event_loop()
    #
    # async def run_executor_train():
    #     result = await loop.run_in_executor(POOL, functools.partial(training_task), f, model_info, epochs, optimizer,
    #                                         metrics)
    #
    # loop.create_task(run_executor_train())
    return json('Model %s fitted! Data used: %s' % (predictor_name, f.name))  # , status=200)


predict_params_description = '''
<b>predictor_name:</b> name of the predictor that you want to use for your prediction. You can also decide to use one of the pre-trained models
<b>multilabel:</b> return prediction as MultiLabel model if true or as a generic MultiClass if false.
<b>multilabel_threshold:</b> threshold value to apply to each label with a MultiLabel model
<b>include_probs:</b> return labels probabilities if True, or the label predicted if False is selected. In the latter case, if Multilabel=True all the labels over the threshold value will be returned.
<b>file:</b> zipped folder or single image
'''


@app.post("/models/<predictor_name>/predict")
@openapi.tag('Vision')
@openapi.description(predict_params_description)
@openapi.parameter(name="predictor_name", location="path", required=True)
# @openapi.parameter(doc.Integer(name="top"), location="query")
@openapi.parameter(name="multilabel", schema=bool, location="query")
@openapi.parameter(name="multilabel_threshold", schema=float, location="query")
@openapi.parameter(name="proba_threshold", schema=float, location="query")
@openapi.parameter(name="include_probs", schema=bool, location="query")
@file()
async def predict(request, predictor_name):
    if not request.files.get("file"):
        return json("There is no file for model prediction", status=400)
    else:
        f = request.files["file"][0]
    # print(f)
    # top = int(request.args.get('top', 3))
    if predictor_name not in get_models_list(models_type="all"):
        return json(f"Model '{predictor_name}' doesn't exists", status=404)
    proba = eval(request.args.get('include_probs', 'true').capitalize())
    multilabel = eval(request.args.get('multilabel', 'false').capitalize())
    if multilabel and predictor_name in models_mapping.keys():
        return json('You cannot use a pre-trained model (%s) as multilabel model' % predictor_name, status=400)
    mlb_threshold = float(request.args.get("multilabel_threshold", 0.5)) if multilabel else None
    proba_threshold = float(request.args.get("proba_threshold", 0.0001))
    preds_res = predict_task(f, predictor_name, proba, multilabel, mlb_threshold, proba_threshold)
    return json(preds_res)  # , status=200)


@app.get("/models/<predictor_name>/info")
@openapi.tag('Vision')
@openapi.parameter(name="predictor_name", location="path", required=True)
@openapi.parameter(name="advanced_info", schema=bool, location="query")
async def info(request, predictor_name):
    logger.debug(f"getting info on {predictor_name}")
    if predictor_name == "":
        msg = "VISION SETTINGS MISSING!!!Model of interest not selected, you have to specify one model name"
        return json(msg, status=400)
    if predictor_name not in [m.name for m in pdao.all()]:
        msg = f'Model {predictor_name} does not exist!'
        logger.error(f"PROBLEM::: {msg}")
        return json(msg, status=400)
    adv_info = eval(request.args.get('advanced_info', 'false').capitalize())
    logger.debug(f"adv info {adv_info}")

    models = get_model_info(predictor_name=predictor_name, advanced_info=adv_info)
    logger.debug(f"getting info on {predictor_name}::: models {models}")
    # print(json(models))
    return json(models)



@app.get("/models/<predictor_name>/export")
@openapi.tag('Vision')
@openapi.summary('Download existing vision model')
@openapi.parameter(name="predictor_name", location="path", required=True)
async def export_predictor(request, predictor_name):
    file_name = predictor_name + '.zip'
    path = Path(REPO_PATH) / predictor_name
    print(path)
    buffer = io.BytesIO()
    make_zipfile(buffer, path)
    buffer.seek(0)
    headers = {'Content-Disposition': 'attachment; filename="{}"'.format(file_name)}
    return raw(buffer.getvalue(), headers=headers)


@app.post("/models/import")
@openapi.tag('Vision')
@openapi.summary('Upload existing vision model')
@file()
async def import_predictor(request):
    path = Path(REPO_PATH)
    print(path)
    file = request.files.get('file')

    if file.name.endswith('.zip'):
        with NamedTemporaryFile(suffix=".zip") as temp_file:
            print(temp_file.name)
            temp_file.write(file.body)
            temp_file.seek(0)
            with zipfile.ZipFile(temp_file.name, 'r') as zip_ref:
                zip_ref.extractall(path)
                print("ok")
    else:
        raise Exception("Error")

    return sanic.json('Done')


@app.post("/loko-services/create")
@openapi.tag('Loko Model Service')
@openapi.summary("Save an object in 'models'")
@openapi.description('''
''')
@extract_value_args(file=False)
async def loko_create_model(value, args):
    logger.debug(f"CREATE MODEL SERVICE... args:::: {args}")

    predictor_name = args.get("predictor_name", "")
    if predictor_name == "":
        msg = "VISION SETTINGS MISSING!!!Model name not setted, you have to specify it"
        return json(msg, status=400)
    if predictor_name in models_mapping.keys():
        raise Exception("You cannot use this name for a custom model")
    if predictor_name in get_models_list(models_type="custom"):
        return json('Model %s already exist!' % predictor_name, status=400)
    pretrained_model = args.get("pretrained_model", 'ResNet50')
    predictor_tag = args.get("predictor_tag", None)
    psr = PredictorRequest(predictor_name=predictor_name, pretained_model=pretrained_model, predictor_tag=predictor_tag)
    try:
        pdao.save(psr)
    except PredictorDAOException as inst:
        logging.exception(inst)
        return json('Model %s already exist!' % predictor_name, status=400)
    return json('Model %s created' % (predictor_name))  # , status=200)


@app.post("/loko-services/info")
@openapi.tag('Loko Model Service')
@openapi.summary("Get info about a model")
@extract_value_args(file=False)
async def loko_get_model_info(value, args):
    logger.debug(f"GET INFO SERVICE... args:::: {args}")
    predictor_name = args.get("predictor_name_info")
    if predictor_name == "":
        msg = "VISION SETTINGS MISSING!!!Model of interest not selected, you have to specify one model name"
        return json(msg, status=400)
    if predictor_name not in [m.name for m in pdao.all()]:
        msg = f'Model {predictor_name} does not exist!'
        logger.error(f"PROBLEM::: {msg}")
        return json(msg, status=400)
    adv_info = args.get('adv_info', False)
    logger.debug(f"adv info {adv_info}")
    models = get_model_info(predictor_name=predictor_name, advanced_info=adv_info)
    print(json(models))
    return json(models)


@app.post("/loko-services/delete")
@openapi.tag('Loko Model Service')
@openapi.summary("Delete model")
@extract_value_args(file=False)
async def loko_delete_model(value, args):
    logger.debug(f"DELETE MODEL SERVICE... args:::: {args}")

    predictor_name = args.get("predictor_name_delete")
    if predictor_name == "":
        msg = "VISION SETTINGS MISSING!!!Model of interest not selected, you have to specify one model name"
        logger.error(f"PROBLEM::: {msg}")
        return json(msg, status=400)

    if predictor_name not in [m.name for m in pdao.all()]:
        msg = f'Model {predictor_name} does not exist!'
        logger.error(f"PROBLEM::: {msg}")
        return json(msg, status=400)
    pdao.delete(predictor_name)
    return json(f"Model {predictor_name} deleted")


@app.post("/loko-services/fit")
@openapi.tag('Loko Model Service')
@openapi.summary("Fit a model")
@openapi.description('''
''')
@extract_value_args(file=True)
async def loko_fit_model(file, args):
    # logger.debug(f"file::: {file}")
    logger.debug(f"FITTING SERVICE... ARGS: {args}")
    predictor_name = args.get("predictor_name_fit")
    if predictor_name not in [m.name for m in pdao.all()]:
        return json(f"Model '{predictor_name}' doesn't exists", status=404)
    if predictor_name == "":
        msg = "VISION SETTINGS MISSING!!!Model of interest not selected, you have to specify one model name"
        return json(msg, status=400)
    if predictor_name in models_mapping:
        return json("You cannot overwrite %s, it's a pre-trained model." % predictor_name, status=400)
    if not file:
        return json("There is no file for model prediction", status=400)
    else:
        f = file[0]
    # if predictor_name in [m.name for m in pdao.all()]:
    #     return json('Model %s already exist!' % predictor_name, status=400) #todo: decidere se lasciarlo
    model_info = pdao.get(predictor_name)
    logger.debug(f"model info:: {model_info}")
    model_obj = model_info.model_obj
    epochs = int(args.get("epochs", 100))
    optimizer = args.get("optimizer", "adam").lower()
    logger.debug(f"n. epochs {epochs}... optimizer chosen {optimizer}")
    metrics = args.get("metrics", "accuracy")
    logger.debug(f"metrics pre:: {metrics}")
    metrics = [el for el in metrics.split(",") if (not el.isspace()) & (len(el) > 0)]
    logger.debug(f"metrics post:: {metrics}")
    if model_obj != None:
        logger.debug(f"model obj: {model_obj}")
        return json("Predictor already fitted", status=400)


    # loop = asyncio.get_running_loop()

    async def run_executor_train():
        result = await app.loop.run_in_executor(POOL, functools.partial(training_task), f, model_info, epochs, optimizer,
                                            metrics)
    #
    app.loop.create_task(run_executor_train())
    return json(f"Model '{predictor_name}' is fitting! Data used: {f.name} ")


@app.post("/loko-services/predict")
@openapi.tag('Loko Model Service')
@openapi.summary("Predict model")
@openapi.description('''
''')
@extract_value_args(file=True)
async def loko_predict_model(file, args):
    logger.debug(f"PREDICT SERVICE... args {args}")
    predictor_name = args.get("predictor_name_predict")
    if predictor_name == "":
        msg = "VISION SETTINGS MISSING!!!Model of interest not selected, you have to specify one model name"
        return json(msg, status=400)
    if not file:
        return json("There is no file for model prediction", status=400)
    else:
        f = file[0]
        # top = int(request.args.get('top', 3))
    if predictor_name not in get_models_list(models_type="all"):
        return json(f"Model '{predictor_name}' doesn't exists", status=404)
    proba = args.get('include_probs', True)
    proba_threshold = float(args.get("probability_th", 0.00)) if proba else None
    multilabel = args.get('multilabel', False)
    if multilabel and predictor_name in models_mapping.keys():
        return json('You cannot use a pre-trained model (%s) as multilabel model' % predictor_name, status=400)
    mlb_threshold = float(args.get("multilabel_threshold", 0.5)) if multilabel else None
    preds_res = await app.loop.run_in_executor(POOL, functools.partial(predict_task), f, predictor_name, proba,
                                               multilabel, mlb_threshold, proba_threshold)

    # preds_res = predict_task(f, predictor_name, proba, multilabel, mlb_threshold, proba_threshold=proba_threshold)
    return json(preds_res)  # , status=200)


@app.post("/loko-services/evaluate")
@openapi.tag('Loko Model Service')
@openapi.summary("Evaluate model")
@openapi.description('''
''')
@extract_value_args(file=True)
async def loko_evaluate_model(file, args):
    logger.debug(f"EVALUATE SERVICE... args {args}")
    predictor_name = args.get("predictor_name_eval")
    if predictor_name == "":
        msg = "VISION SETTINGS MISSING!!!Model of interest not selected, you have to specify one model name"
        return json(msg, status=400)
    if not file:
        return json("There is no file for model prediction", status=400)
    else:
        f = file[0]
    # res = evaluate_task(f, predictor_name)
    res = await app.loop.run_in_executor(POOL, functools.partial(evaluate_task), f, predictor_name)
    return json(res)


@app.post("/models/<predictor_name>/evaluate")
@openapi.tag('Vision')
@openapi.description(fit_params_description)
# @openapi.parameter(doc.Boolean(name="multilabel"), location="query")
@openapi.parameter(name="predictor_name", location="path", required=True)
@file()
async def evaluate_model(request, predictor_name):
    print(predictor_name)

    if not request.files.get("file"):
        return json("There is no file to train the model", status=400)
    else:
        f = request.files["file"][0]
    # if predictor_name in [m.name for m in pdao.all()]:
    #     return json('Model %s already exist!' % predictor_name, status=400) #todo: decidere se lasciarlo
    res = evaluate_task(f, predictor_name)

    return json(res)  # , status=200)


@app.exception(Exception)
async def manage_exception(request, exception):
    status_code = getattr(exception, "status_code", None) or 500
    logger.debug(f"status_code:::: {status_code}")
    if isinstance(exception, SanicException):
        return sanic.json(dict(error=str(exception)), status=status_code)

    e = dict(error=f"{exception.__class__.__name__}: {exception}")

    if isinstance(exception, NotFound):
        return sanic.json(e, status=404)
    # logger.error(f"status code {status_code}")
    logger.error('TracebackERROR: \n' + traceback.format_exc() + '\n\n', exc_info=True)
    return sanic.json(e, status=status_code)


if __name__ == '__main__':
    app.blueprint(bp)
    app.run("0.0.0.0", port=8080, auto_reload=False, single_process=True)
