# from sanic import Sanic
from sanic.response import json
#
# from sanic_openapi import openapi3_blueprint
#
# app = Sanic("Hello_world")
# app.blueprint(openapi3_blueprint)
#
#
# @app.route("/")
# async def test(request):
#     return json({"hello": "world"})
#
#
from sanic import Sanic, Blueprint, file
from sanic_ext.extensions.openapi import openapi
from sanic_ext.extensions.openapi.definitions import Parameter
from sanic_ext.extensions.openapi.types import String, Object

from model.mlmodel import models_mapping

app = Sanic("MyHelloWorldApp")

app.extend(config={"oas_url_prefix": "/api", "oas_ui_default": "swagger"})

bp = Blueprint("default", url_prefix=f"ds4biz/vv")
# print(f"eeeee: {list(models_mapping.keys())}")
a = list(models_mapping.keys())
def file(name='file'):
    def tmp(f):
        content = {"multipart/form-data": {"schema": {"type": "object", "properties": {name: {"type": "string", "format": "binary"}}}}}
        return openapi.body(content, required=True)(f)
    return tmp


@app.route("/ciao", methods=["POST"])
# @openapi.parameter(name="model_type", content=["all", "custom", "pretrained"], description="Default model_type='all'")
@openapi.parameter(name="model_type",type=String(enum=["all", "custom", "pretrained"]), description="Default model_type='all'")
@openapi.parameter(parameter=Parameter(name="type", schema=String(enum=["vocabulary", "patterns"]),
                                       location="path"))
@openapi.parameter(name="CIAONE", type=Object(properties={"file": {"type": "string", "format": "binary"}}))
async def test(request):
    return json({"hello": "world"})


# @bp.post("/models/<predictor_name>/evaluate")
@app.route("/models/<predictor_name>/evaluate", methods=["POST"] )
@openapi.tag('Vision')
@openapi.description("fit_params_description")
# @openapi.body(name="file", location="formData", type="file" ,content_type="multipart/form-data", required=True)
# @openapi.body(content="multipart/form-data", body_argument="file", required=True)
@openapi.parameter(name="model_type", content=["all", "custom", "pretrained"], description="Default model_type='all'")
# @openapi.parameter(parameter=Parameter(name="pretrained_model", schema=String(enum=list(models_mapping.keys()))), location="query")
@openapi.parameter(parameter=Parameter(name="type", schema=String(enum=["vocabulary", "patterns"]),
                                       location="path"))
@openapi.parameter(parameter=Parameter(name="type2", schema=String(enum=list(models_mapping.keys())),
                                       location="query"))
# @openapi.parameter(doc.Boolean(name="multilabel"), location="query")
@openapi.parameter(name="predictor_name", location="path", required=True)
@file()
async def evaluate_model(request, predictor_name):
    # print(predictor_name)
    #
    # if not request.files.get("file"):
    #     return json("There is no file to train the model", status=400)
    # else:
    #     f = request.files["file"][0]
    # # if predictor_name in [m.name for m in pdao.all()]:
    # #     return json('Model %s already exist!' % predictor_name, status=400) #todo: decidere se lasciarlo
    # res = evaluate_task(f, predictor_name)
    res = {"ciao":"word"}
    return json(res)  # , status=200)


@app.route("/extract",  methods=["POST"])
@openapi.summary(' ')
@openapi.tag('extract services')
@openapi.response(content={"application/json": {}, "plain/text": {}},
                  description="If plain is selected the entire ocr-doc will be returned, otherwise the response will be a json which separates each page. Default='application/json'")
@openapi.parameter(name="postprocessing_configs", location="query")
@openapi.parameter(name="analyzer_configs", location="query")
@openapi.parameter(name="preprocessing_configs", location="query", schema=bool)
@openapi.parameter(name="force_ocr_extraction", description="Available only for .pdf files. Default=False",
                   location="query", schema=bool)
async def convert(request):
    fn = "file."
    return fn

if __name__ == "__main__":
    app.run(host="0.0.0.0", port=8085)