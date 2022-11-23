BLUEPRINT_FILENAME = "blueprint.json"
PREDICTOR_NAME_LBL = "predictor_name"
PRETRAINED_MODEL_LBL = "pretrained_model"
MODEL_OBJ_LBL = "model_obj"
MODEL_PARAMETERS_LBL = "model_parameters"
PREDICTOR_TAG_LBL = "predictor_tag"
FITTED_STATUS_LBL = "fitted"


# class ModelParameters:
#     def __init__(self, __klass__ ,  top_layer:dict, pretrained_model: str, predictor_name:str, predictor_tag:str, mlb:bool, fitted: Union[str, bool]):
#         self.__klass__ = __klass__
#         self.top_layer = top_layer
#         self.pretrained_model = pretrained_model
#         self.predictor_name = predictor_name
#         self.predictor_tag = predictor_tag
#         self.mlb = mlb
#         self.fitted = fitted
#
#
#     def to_dict(self):
#         return self.__dict__

class PredictorRequest:
    def __init__(self, predictor_name, pretained_model, predictor_tag=None, model_obj=None, model_parameters=None,
                 fitted: bool = False):
        self.predictor_name = predictor_name
        self.pretained_model = pretained_model
        self.predictor_tag = predictor_tag
        self.model_obj = model_obj
        self.model_parameters = model_parameters
        self.fitted = fitted
