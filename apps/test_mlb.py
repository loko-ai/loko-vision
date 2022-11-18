import numpy as np
import requests
from sklearn.datasets import make_multilabel_classification
# define dataset
from tensorflow.keras import Sequential
from tensorflow.keras.layers import Dense
from sklearn.model_selection import train_test_split

from business.tf_learning import training_task
from dao.predictors_dao import PredictorsDAO

pdao = PredictorsDAO()
X, y = make_multilabel_classification(n_samples=1000, n_features=2048, n_classes=3, n_labels=2, random_state=1)
# summarize dataset shape
print(X.shape, y.shape)
# summarize first few examples
for i in range(10):
	print(X[i], y[i])

n_inputs = X.shape[1]
n_outputs = y.shape[1]


URL = 'http://0.0.0.0:8080/ds4biz_vision/0.0/models/'
MODEL_NAME = "joe"
PRETRAINED_MODEL = dict(pretrained_model=("ResNet50"))
requests.post(URL+MODEL_NAME,json=PRETRAINED_MODEL  )
# requests.post(URL+MODEL_NAME+"/fit", )

X_train, X_test, y_train, y_test = train_test_split(X,y,train_size=0.8)
model_info = pdao.get(predictor_name=MODEL_NAME)
training_task(X= X_train, y = y_train, model_info=model_info )

# # define the model
# model = Sequential()
# model.add(Dense(20, input_dim=n_inputs, kernel_initializer='he_uniform', activation='relu'))
# model.add(Dense(n_outputs, activation='sigmoid'))
# model.compile(loss='binary_crossentropy', optimizer='adam')
#
# def get_model(n_inputs, n_outputs):
# 	model = Sequential()
# 	model.add(Dense(20, input_dim=n_inputs, kernel_initializer='he_uniform', activation='relu'))
# 	model.add(Dense(n_outputs, activation='sigmoid'))
# 	model.compile(loss='binary_crossentropy', optimizer='adam')
# 	return model

#
# print("train ",X_train.shape, y_train.shape)
# print("test ",X_test.shape, y_test.shape)
#
# model = get_model(n_inputs, n_outputs)
# model.fit(X_train, y_train, verbose=0, epochs=100)
# yhat = model.predict(X_test)
# print(np.round(yhat,2))