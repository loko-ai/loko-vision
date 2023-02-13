# :computer: Loko-vision
### Loko component for Image Classification



This component allows to perform Transfer Learning to classify images, using Keras pre-trained Neural Networks models. 


It's also possible to classify images using directly Keras pre-trained Neural Network, without having to train your own model. In this case the available labels are the ones of the ImageNet Dataset (you can find the complete list [here](https://gist.github.com/yrevar/942d3a0ac09ec9e5eb3a)) 


Installing this project extension on your LOKO AI software will make available two new components, Vision Manager and Vision, and a GUI. In details, their 

**1. Vision Manager:** allows to manage Creation, Delete of custom models and get info about them;
2. **Vision:** it's the main component of this LOKO AI extension, since it's the one that let you to fit a custom model, using **Transfer Learning** techniques, make predictions and evaluate a custom model;
3. **Vison GUI:** Vision offers a simple GUI which, among other tasks, allows to carry on the same tasks of the Vision Manager components (create, delete, get info about custom model), so it's up to you deciding if it's more convenient to use directly the component or the GUI, according to your needs. Through this interface you can also import/export models, check the pre-trained models list available for you, and take a look to an evaluation report.![Screenshot of the GUI](resources/vision_gui_img.png)