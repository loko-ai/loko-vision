from model.mlmodel import KerasImagePredictor
from model.nn_model import NNClassifierWrapper
from utils.factory_utils import BaseFactory, ClassByNameLoader

FACTORY = BaseFactory()

FACTORY.register("ds4biz.KerasImagePredictor", KerasImagePredictor)
FACTORY.register("ds4biz.NNpredictor", NNClassifierWrapper)


def filter_modules(klasses, modules):
    return {x for x in klasses if x.__module__ not in modules}


for name, kl in ClassByNameLoader("sklearn").klasses.items():
    kl = filter_modules(kl, ["sklearn.utils.tests.test_pprint", "sklearn.ensemble._gb_losses"])
    if len(kl) == 1:
        # print("Single",name,kl)
        FACTORY.register("sk." + name, list(kl)[0])

for name, kl in ClassByNameLoader("tensorflow.keras").klasses.items():
    kl = filter_modules(kl, ["tensorflow.keras"])  # aggiungere filtri di keras
    if len(kl) == 1:
        # print("Single",name,kl)
        FACTORY.register("tfkeras." + name, list(kl)[0])

if __name__ == '__main__':
    obj = dict(__klass__='ds4biz.KerasImagePredictor', last_layer=dict(__klass__='sk.SGDClassifier'))
    mdl = FACTORY(obj)
    print(mdl.__dict__)
