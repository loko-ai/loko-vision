import numpy as np



def inverse_sigmoid(pred):
    mask1 = pred==1
    mask2 = pred==0

    res = np.log(pred / (1 - pred))
    print(res)
    return res

def softmax(pred):
    print("pred:::::::::::::::: ", pred)
    # if pred>=0.99:
    #     return 1
    pred_exp = np.exp(pred)
    res = pred_exp / pred_exp.sum()
    print("res: ", res)
    return res