import logging
import zipfile
from itertools import chain

import os
import io
from pathlib import Path
from tempfile import NamedTemporaryFile

import sanic
import tensorflow as tf
from loko_extensions.business.decorators import extract_value_args
from sanic import Blueprint, text
from sanic import json, Sanic
from sanic.response import raw
from sanic_cors import CORS
from sanic_openapi import swagger_blueprint
from sanic_openapi.openapi2 import doc

from business.tf_learning import training_task, predict_task
from config.AppConfig import REPO_PATH
from dao.inmemory_dao import InMemoryDAO
from dao.predictors_dao import PredictorsDAO, PredictorDAOException
from model.mlmodel import models_mapping
from model.predictors_model import PredictorRequest
from utils.logger_utils import stream_logger, logger
from utils.model_utils import get_models_list, get_model_info
from utils.pom_utils import get_pom_major_minor

# todo: 2 - controllare tipologia immagini non supportate e gestione errori file;
#      3 - aggiustare parametri dei servizi
#      4-
#
from utils.zip_utils import make_zipfile


#
# iron["XLA_FLAGS"]="--xla_gpu_cuda_data_dir=/usr/local/cuda-11.8"

os.environ["LD_LIBRARY_PATH"]="$LD_LIBRARY_PATH:$CONDA_PREFIX/venv/lib/python3.10/site-packages/tensorrt/"


im_dao = InMemoryDAO()
pdao = PredictorsDAO()


def get_app(name):
    app = Sanic(name)
    swagger_blueprint.url_prefix = "/api"
    app.blueprint(swagger_blueprint)
    return app


name = "loko-vision"
app = get_app(name)
bp = Blueprint("default", url_prefix=f"loko_vision/{get_pom_major_minor()}/")
app.config["API_VERSION"] = get_pom_major_minor()
app.config["API_TITLE"] = name
CORS(app)

get_models_params_description = '''
<b>model_type:</b> return the type of models available for the chosen category: pre-trained, custom or both types.
'''


@bp.get("/models/")
@doc.tag('Vision')

@doc.description(get_models_params_description)
@doc.consumes(doc.String(name="model_type", choices=["all", "custom", "pretrained"], description="Default model_type='all'"))
@doc.consumes(doc.Boolean(name="info", description="Default info='False'"))
def models(request):
    model_type = request.args.get("model_type", "all")
    model_info = eval(request.args.get("info", "false").capitalize())
    models = get_models_list(model_type, model_info)
    return json(models)


delete_params_description = '''
<b>predictor_name:</b> name of the predictor to delete
'''


@bp.delete("/models/<predictor_name>")
@doc.tag('Vision')
@doc.consumes(doc.String(name="predictor_name"), location="path", required=True)
def delete_model(request, predictor_name):
    # print([m.name for m in pdao.all()])
    if predictor_name not in [m.name for m in pdao.all()]:
        return json('Model %s does not exist!' % name, status=400)
    pdao.delete(predictor_name)
    return json('Model %s deleted' % predictor_name)


create_params_description = '''
<b>predictor_name:</b> name of the predictor to create
<b>pretrained_model:</b> pre-trained model to use for the transfer-learning model
'''


@bp.post("/models/<predictor_name>")
@doc.tag('Vision')
@doc.description(create_params_description)
@doc.consumes(doc.String(name="predictor_tag"), location="query")
@doc.consumes(doc.String(name="pretrained_model", choices=list(models_mapping.keys())), location="query")
@doc.consumes(doc.String(name="predictor_name"), location="path", required=True)
def create_model(request, predictor_name):
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


@bp.post("/models/<predictor_name>/fit")
@doc.tag('Vision')
@doc.description(fit_params_description)
@doc.consumes(doc.File(name="file"), location="formData", content_type="multipart/form-data", required=True)
# @doc.consumes(doc.Boolean(name="multilabel"), location="query")
@doc.consumes(doc.String(name="predictor_name"), location="path", required=True)
def fit(request, predictor_name):
    print(predictor_name)

    if predictor_name in models_mapping:
        return json("You cannot overwrite %s, it's a pre-trained model." % predictor_name, status=400)
    if not request.files.get("file"):
        return json("There is no file to train the model", status=400)
    else:
        f = request.files["file"][0]
    # if predictor_name in [m.name for m in pdao.all()]:
    #     return json('Model %s already exist!' % predictor_name, status=400) #todo: decidere se lasciarlo
    model_info = pdao.get(predictor_name)
    training_task(f, model_info)
    return json('Model %s fitted! Data used: %s' % (predictor_name, f.name))  # , status=200)


predict_params_description = '''
<b>predictor_name:</b> name of the predictor that you want to use for your prediction. You can also decide to use one of the pre-trained models
<b>multilabel:</b> return prediction as MultiLabel model if true or as a generic MultiClass if false.
<b>multilabel_threshold:</b> threshold value to apply to each label with a MultiLabel model
<b>include_probs:</b> return labels probabilities if True, or the label predicted if False is selected. In the latter case, if Multilabel=True all the labels over the threshold value will be returned.
<b>file:</b> zipped folder or single image
'''


@bp.post("/models/<predictor_name>/predict")
@doc.tag('Vision')
@doc.description(predict_params_description)
@doc.consumes(doc.String(name="predictor_name"), location="path", required=True)
# @doc.consumes(doc.Integer(name="top"), location="query")
@doc.consumes(doc.Boolean(name="multilabel"), location="query")
@doc.consumes(doc.Float(name="multilabel_threshold"), location="query")
@doc.consumes(doc.Boolean(name="include_probs"), location="query")
@doc.consumes(doc.File(name="file"), location="formData", content_type="multipart/form-data", required=True)
def predict(request, predictor_name):
    if not request.files.get("file"):
        return json("There is no file for model prediction", status=400)
    else:
        f = request.files["file"][0]
    # print(f)
    # top = int(request.args.get('top', 3))
    proba = eval(request.args.get('include_probs', 'true').capitalize())
    multilabel = eval(request.args.get('multilabel', 'false').capitalize())
    if multilabel and predictor_name in models_mapping.keys():
        return json('You cannot use a pre-trained model (%s) as multilabel model' % predictor_name, status=400)
    mlb_threshold = float(request.args.get("multilabel_threshold", 0.5)) if multilabel else None
    preds_res = predict_task(f, predictor_name, proba, multilabel, mlb_threshold)
    return json(preds_res)  # , status=200)


@bp.get("/models/<predictor_name>/info")
@doc.tag('Vision')
@doc.consumes(doc.String(name="predictor_name"), location="path", required=True)
@doc.consumes(doc.Boolean(name="advanced_info"), location="query")
def info(request, predictor_name):
    adv_info = eval(request.args.get('advanced_info', 'false').capitalize())
    models = get_model_info(predictor_name=predictor_name, advanced_info=adv_info )
    print(json(models))
    return json(models)




@bp.get("/models/<predictor_name>/export")
@doc.tag('Vision')
@doc.summary('Download existing vision model')
@doc.consumes(doc.String(name="predictor_name"), location="path", required=True)
async def export_predictor(request,predictor_name):
    file_name = predictor_name + '.zip'
    path = Path(REPO_PATH) / predictor_name
    print(path)
    buffer = io.BytesIO()
    make_zipfile(buffer, path)
    buffer.seek(0)
    headers = {'Content-Disposition': 'attachment; filename="{}"'.format(file_name)}
    return raw(buffer.getvalue(), headers=headers)


@bp.post("/models/import")
@doc.tag('Vision')
@doc.summary('Upload existing vision model')
@doc.consumes(doc.File(name="file"), location="formData", content_type="multipart/form-data", required=True)
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


@bp.post("/loko-services/create")
@doc.tag('Loko Model Service')
@doc.summary("Save an object in 'models'")
@doc.description('''
''')
@extract_value_args(file=False)
def loko_create_model(value, args):
    predictor_name = args.get("predictor_name", "")
    if predictor_name=="":
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



@bp.post("/loko-services/info")
@doc.tag('Loko Model Service')
@doc.summary("Get info about a model")
@extract_value_args(file=False)
def loko_get_model_info(value, args):
    predictor_name = args.get("predictor_name_info")
    if predictor_name == "":
        msg = "VISION SETTINGS MISSING!!!Model of interest not selected, you have to specify one model name"
        return json(msg, status=400)
    adv_info = eval(args.get('advanced_info', 'false').capitalize())
    models = get_model_info(predictor_name=predictor_name, advanced_info=adv_info)
    print(json(models))
    return json(models)



@bp.post("/loko-services/delete")
@doc.tag('Loko Model Service')
@doc.summary("Delete model")
@extract_value_args(file=False)
def loko_delete_model(value, args):
    predictor_name = args.get("predictor_name_delete")
    if predictor_name == "":
        msg = "VISION SETTINGS MISSING!!!Model of interest not selected, you have to specify one model name"
        return json(msg, status=400)
    if predictor_name not in [m.name for m in pdao.all()]:
        return json(f'Model {predictor_name} does not exist!', status=400)
    pdao.delete(predictor_name)
    return json(f"Model {predictor_name} deleted")


@bp.post("/loko-services/fit")
@doc.tag('Loko Model Service')
@doc.summary("Fit a model")
@doc.description('''
''')
@extract_value_args(file=True)
def loko_fit_model(file, args):
    logger.debug(f"file::: {file}")
    predictor_name = args.get("predictor_name_fit")
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
    training_task(f, model_info)
    return json(f"Model '{predictor_name}' fitted! Data used: ")


@bp.post("/loko-services/predict")
@doc.tag('Loko Model Service')
@doc.summary("Predict model")
@doc.description('''
''')
@extract_value_args(file=True)
def loko_predict_model(file, args):

    logger.debug(f"args {args}")
    predictor_name = args.get("predictor_name_predict")
    if predictor_name == "":
        msg = "VISION SETTINGS MISSING!!!Model of interest not selected, you have to specify one model name"
        return json(msg, status=400)
    if not file:
        return json("There is no file for model prediction", status=400)
    else:
        f = file[0]
        # top = int(request.args.get('top', 3))
    proba = args.get('include_probs', True)
    multilabel = args.get('multilabel', False)
    if multilabel and predictor_name in models_mapping.keys():
        return json('You cannot use a pre-trained model (%s) as multilabel model' % predictor_name, status=400)
    mlb_threshold = float(args.get("multilabel_threshold", 0.5)) if multilabel else None
    preds_res = predict_task(f, predictor_name, proba, multilabel, mlb_threshold)
    return json(preds_res)  # , status=200)






if __name__ == '__main__':
    app.blueprint(bp)
    app.run("0.0.0.0", port=8080, auto_reload=True)
