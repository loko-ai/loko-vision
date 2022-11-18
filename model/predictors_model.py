
BLUEPRINT_FILENAME= "blueprint.json"
PREDICTOR_NAME_LBL = "predictor_name"
PRETRAINED_MODEL_LBL = "pretrained_model"
MODEL_OBJ_LBL = "model_obj"
MODEL_PARAMETERS_LBL = "model_parameters"
PREDICTOR_TAG_LBL = "predictor_tag"

class PredictorRequest:
    def __init__(self, predictor_name, pretained_model, predictor_tag=None, model_obj=None, model_parameters=None):
        self.predictor_name = predictor_name
        self.pretained_model = pretained_model
        self.predictor_tag = predictor_tag
        self.model_obj = model_obj
        self.model_parameters = model_parameters

