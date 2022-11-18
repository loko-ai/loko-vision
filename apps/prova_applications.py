import tensorflow.keras.applications as models
from tensorflow.keras.applications.resnet import preprocess_input
import tensorflow.keras as keras
models_mapping = {}
for name in dir(models):
    if name[0].isupper():
        m = getattr(models, name)
        a = '.'.join(m._keras_api_names[0].split('.')[:-1])
        if 'preprocess_input' in dir(eval(a)) and 'decode_predictions' in dir(eval(a)):
            pi = eval(a+'.preprocess_input')
            dp = eval(a + '.decode_predictions')
            models_mapping[name] = dict(model=m, preprocess_input=pi, decode_prediction=dp)

print(models_mapping)


