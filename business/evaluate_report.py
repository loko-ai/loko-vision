# sklearn.metrics.confusion_matrix¶
import time
from collections import Counter

from keras.losses import BinaryCrossentropy
from sklearn.metrics import confusion_matrix, multilabel_confusion_matrix, accuracy_score
from sklearn.metrics import classification_report

def compute_reports(y_true, y_pred, labels=None):
    # print(f"labels inside {labels}")
    cm = confusion_matrix(y_true, y_pred, labels=labels)
    cm = cm.tolist()
    true_distro = dict(hist=dict(Counter(y_true)))
    pred_distro = dict(hist=dict(Counter(y_pred)))
    dt = time.time()
    # print(f"y true: {y_true} ")
    metrics = classification_report(y_true, y_pred, output_dict=True, labels=labels)
    accuracy = accuracy_score(y_true, y_pred)
    # print(f"accuracy {accuracy}")
    report = dict(true_dist=true_distro, pred_dist=pred_distro, confusion_matrix=cm, datetime=dt, metrics=metrics, accuracy=accuracy)
    return report

