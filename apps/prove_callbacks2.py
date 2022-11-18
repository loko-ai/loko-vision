from sklearn.linear_model import LogisticRegression
from sklearn.metrics import accuracy_score
from sklearn.datasets import make_classification



if __name__ == '__main__':
    X, y = make_classification(n_samples=10000, n_features=20, n_classes=2)
    clf = LogisticRegression(max_iter=10, warm_start=True)
    for i in range(100):
        clf.fit(X, y)
        acc = accuracy_score(y, clf.predict(X))
        iters = clf.n_iter_
        print('iter %d: score=%f actual iters=%d'%(i, acc, iters))


    # clf = LogisticRegression(max_iter=10, warm_start=True)
    # clf.fit(X, y)
    # acc = accuracy_score(y, clf.predict(X))
    # iters = clf.n_iter_
    # print('score=%f actual iters=%d' % (acc, iters))
    #####