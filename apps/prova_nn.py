from tensorflow import keras
#
model = keras.Sequential()
model.add(keras.layers.Input(10))
model.add(keras.layers.Dense(1))
model.build()
# print(model.summary())
# # print(model.layers[0]._build_input_shape[1])
conf_mdl = model.get_config()
print(model.get_config())
conf_mdl["layers"][0]["config"]["batch_input_shape"]=(None,20)
new_model = keras.models.model_from_config(conf_mdl)
print(new_model.summary())
conf_mdl["layers"][0]["config"]["batch_input_shape"]=(None,20)
new_model = keras.Sequential().from_config(conf_mdl)
print(new_model.summary())
# model.add(keras.layers.Input(11))
# model.layers.pop(0)
# print(model.layers[0].batch_input_shape[1])
#
# print(model.summary())
# input_shape = keras.layers.Input(batch_shape=(0,20))
# out_shape = model(input_shape)
# mdl = keras.Model(input_shape,out_shape)
# print("=============================")
# print(mdl.summary())
# print(mdl.layers[0].__dict__)
#
# # model.layers[0]._build_input_shape[1]=5
# model.layers[0].input._type_spec.shape = (None, 35)
# print(model.layers[0].input.__dict__)
# from model.mlmodel import models_mapping
#
# print(models_mapping)
# for mdl in models_mapping:
#     base_model =  models_mapping[mdl]['model']()
#     n_output = base_model.layers[-2].output.type_spec.shape[1]
#     print("Model:", mdl ," +++++++++ N output: ", n_output)