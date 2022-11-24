from loko_extensions.model.components import Input, Output, Dynamic, AsyncSelect, Component, save_extensions
from loko_extensions.model.components import Arg

from extensions.vision_component_doc import vision_doc

custom_model_list = "http://localhost:9999/routes/loko-vision/loko_vision/0.0/models?info=false&model_type=custom"
custom_and_pretrained_model_list = "http://localhost:9999/routes/loko-vision/loko_vision/0.0/models"
pretrained_list = "http://localhost:9999/routes/loko-vision/loko_vision/0.0/models?model_type=pretrained"

create_service = "loko_vision/0.0/loko-services/create"
info_service = "loko_vision/0.0/loko-services/info"
delete_service = "loko_vision/0.0/loko-services/delete"

fit_service = "loko_vision/0.0/loko-services/fit"
predict_service = "loko_vision/0.0/loko-services/predict"
evaluate_service = "loko_vision/0.0/loko-services/evaluate"

################################## ARGS ####################################

######### create args
create_group = "Create Parameters"
predictor_name = Arg(name="predictor_name",
                     type="text",
                     label="Vision Model Name",
                     group=create_group,
                     helper='Name of the model you want to use for fitting/predicting')

pretrained_model = AsyncSelect(name='pretrained_model',
                               url=pretrained_list,
                               label='Pretrained model',
                               group=create_group,
                               helper='choose your pretrained NN')

model_tag = Arg(name="predictor_tag",
                type="text",
                # parent="service",
                label="Model tag",
                group=create_group,
                helper='Create a tag that helps you to recognize the aim of the model',
                )

create_args = [predictor_name, pretrained_model, model_tag]
######### fit args

fit_group = "Fit parameters"

pred_name = AsyncSelect(name="predictor_name_fit", label="Vision Model", url=custom_model_list, group=fit_group,
                        helper='Name of the model you want to use for fitting')

fit_args_list = [pred_name]

######### predict args

predict_group = "Predict parameters"

pred_name_pred = AsyncSelect(name="predictor_name_predict", url=custom_and_pretrained_model_list, label="Vision Model",
                             group=predict_group, helper='Name of the model you want to use for predicting')

pred_proba = Arg(name='include_probs',
                 type='boolean',
                 label='Predict proba',
                 group=predict_group,
                 value=False,
                 helper="")

probability_th = Dynamic(name="probability_th",
                         label="Probability Threshold",
                         dynamicType="number",
                         group=predict_group,
                         value=0.01,
                         parent="include_probs",
                         condition="{parent}===true",
                         description='The probability threshold level represents the miminum probability that a class needs to have in order to be "shown" in the results',
                         helper="Set this value to 0.0 if you want to have all the model's classes"
                         )

multilabel = Arg(name='multilabel',
                 type='boolean',
                 label='Multilabel',
                 group=predict_group,
                 value=False,
                 description='If True the results will be seen as a MultiLabel problem, otherwise as a MultiClass')

multilabel_th = Dynamic(name='multilabel_threshold',
                        options=["0.5", "0.6", "0.7", "0.8", "0.9"],
                        label='Multilabel Threshold',
                        group=predict_group,
                        dynamicType="select",
                        parent="multilabel",
                        condition="{parent}===true", value="0.5",
                        helper='Threshold rate to decide the belongings to one class for the MultiLabel')

predict_args_list = [pred_name_pred, pred_proba,probability_th, multilabel, multilabel_th]

######### evaluate args

eval_group = "Evaluate Parameters"
eval_name_pred = AsyncSelect(name="predictor_name_eval", url=custom_and_pretrained_model_list, label="Vision Model",
                             group=eval_group, helper='Name of the model you want to evaluate')

eval_args_list = [eval_name_pred]

######### info args

info_group = 'Info parameters'
info_predictor = AsyncSelect(name="predictor_name_info",
                             label="Vision Model",
                             group=info_group,
                             url=custom_model_list,
                             helper='Name of the model you want to know details about')

adv_info = Arg(name='adv_info',
               type='boolean',
               label='Advanced information',
               group=info_group,
               helper="")

info_args = [info_predictor, adv_info]

######### delete args

delete_group = 'Delete parameters'

delete_predictor = AsyncSelect(name="predictor_name_delete",
                               label="Vision Model",
                               group='Delete parameters',
                               url=custom_model_list,
                               helper='Name of the model you want to delete')

delete_args = [delete_predictor]
################################ INPUT & OUTPUT ################################
vision_input = [Input(id="fit", label="fit", to="fit", service=fit_service),
                Input(id="predict", label="predict", to="predict", service=predict_service),
                Input(id="evaluate", label="evaluate", to="evaluate", service=evaluate_service)
                ]

vision_output = [Output(id="fit", label="fit"),
                 Output(id="predict", label="predict"),
                 Output(id="evaluate", label="evaluate")
                 ]

manager_input = [Input(id="create", label="create", to="create", service=create_service),
                 Input(id="info", label="info", to="info", service=info_service),
                 Input(id="delete", label="delete", to="delete", service=delete_service)
                 ]

manager_output = [Output(id="create", label="create"),
                  Output(id="info", label="info"),
                  Output(id="delete", label="delete")
                  ]

vision_args = fit_args_list + predict_args_list + eval_args_list

manager_args = create_args + info_args + delete_args

vision_component = Component(name="Vision", description=vision_doc, inputs=vision_input,
                             outputs=vision_output, args=vision_args, icon="RiImage2Fill", group='ComputerVision')

vision_manager = Component(name="Vision Manager", description=vision_doc, inputs=manager_input, outputs=manager_output,
                           args=manager_args, icon="RiSettings5Fill", group='ComputerVision')
# "RiFileTextFill"
if __name__ == '__main__':
    save_extensions([vision_component, vision_manager])
