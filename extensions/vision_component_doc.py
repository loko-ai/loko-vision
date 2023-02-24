vision_doc = '''
### Description

VISION is the Loko AI component which allows to classify images either using a pre-trained Neural Networks, or using a transfer-learning model over one of them. Specifically, VISION helps you with training, predicting and managing your models.

### Configuration

The heading ***Available services*** allows user to select the VISION instance of interest (remembering that different vision-models will necessarily be found on different instances). 

If you just want to use a pre-trained Neural Network in order to classify your set of images, you can directly link a *File Reader* component to the *Predict* Inputs of VISION. 
More information about pre-trained models can be found here https://keras.io/api/applications/, where you can see details on their network structure and performances. 
If you decide to classify your image directly using one of the pre-trained Neural Networks, you should expect to receive as output one of the 1000 possible ImageNet classes.

If you want to create a transfer-learning model to customize your classifier on your own data, follow these steps:


- **Create a model:**  using the Vision Manager component, in *Create parameters* choose the name of the model you want to create (*Vision Model Name*) and select the pre-trained models to use (*Pretrained Models*). You can also add the model tag, to facilitate the recognition of the model, adding some details.Then, link a *Trigger* component to the **Create** input;

- **Fit a model:** in *Fit parameters* choose the name of the model you want to train (*Vision Model*), and use a *File Reader* to pass a zipped folder to the VISION component ***Fit*** input. You can also decide to set the model epochs, the optimizer to use and one or more metrics.

- **Get prediction with a model:** in *Predict parameters* you can set the model to use (*Vision Model*) choosing between the customized models and the pre-trained NN. Then, you can choose if you want to see directly the predicted class or the probability of each of them, setting the **Predict proba** parameters. 
If you use a customized model, you can also decide to see predictions as a **generic Multi-Class** or as a **Multi-Label model**; in the latter case, if you don't want to see the probability of belonging to each class you can set the value of the **MultiLabel Threshold**, that indicate the minimum probability value in order to assign a specific class.

- **Evaluate a model:** in the *Evaluate parameters* you can set the model to use *Vision Model*) choosing between the customized models. Then, link a **File Reader** component to the evaluate input, using a zip file, with the same structure of the one used for the model training.



### Output

For the **Fit** services the output messages will only be a sentence that confirms that the required action has been finalized, it may take a while to have the output back, depending on how much the fitting lasts.


The output for the **info** services change if the model has already been fitted or not, and based on the setting chosen regarding advanced information. In case the model has been fitted and advanced information was activated the output will be the following:

```json
{"predictor_name": name of the model chosen, 
"pretrained_model": name of the pretrained model chosen,
"top_layer": {"n_layer":1,
    "n_classes": number of classes,
    "metrics": ["accuracy"],
    "loss_function": "binary_crossentropy",
    "epochs":100},
"fitted": say if the model was trained or not}
```

In case the model *is not fitted* or *the advanced information* is not activated, the output will be the same without the "top layer" information.

The **predict** service has different output based on the settings chosen. If the field *predict proba* has been selected, we can see the probabilities next to each labels:

```json
{"fname": name of the file used for the prediction, 
"pred": [["cat",0.9996217489242554],
        ["dog",0.001642674207687378]]}
```

Otherwise, the output will be:

```json
{"fname": name of the file used for the prediction, 
"pred": "cat"}
```

If *multilabel* is selected the output will be:

```
{"fname": name of the file used for the prediction, 
"pred": ["cat", "persian","black"]}
```

The **evaluate** service output is an object containing metrics and other general information. Can be saved as ".eval" file and imported in the GUI *"Report"* section to be visualized.
  
'''


vision_manager_doc = '''
### Description

With this component you can:

### Input

- **Create a model:** using the Vision Manager component, in *Create parameters* choose the name of the model you want to create (*Vision Model Name*) and select the pre-trained models to use (*Pretrained Models*). You can also add the model tag, to facilitate the recognition of the model, adding some details.

- **Delete a model:** in the section *delete parameters* specify the model you want to delete. It's possible to delete only the customized models.

- **Get information about a model:** in *info parameters* you have to set the model name and then choose if you just want to know if the model is fitted and the pre-trained model used, or if you want **advanced** information.



### Output

For **Create and Delete** services the output messages will only be a sentence that confirms that the required action has been finalized.

The output for the **info** services change if the model has already been fitted or not, and based on the setting chosen regarding advanced information. In case the model has been fitted and advanced information was activated the output will be the following:

```json
{"predictor_name": name of the model chosen, 
"pretrained_model": name of the pretrained model chosen,
"top_layer": {"n_layer":1,
    "n_classes": number of classes,
    "metrics": ["accuracy"],
    "loss_function": "binary_crossentropy",
    "epochs":100},
"fitted": say if the model was trained or not}
```

In case the model *is not fitted* or *the advanced information* is not activated, the output will be the same without the "top layer" information.
'''