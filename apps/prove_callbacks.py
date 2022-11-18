import sys
import time
from io import StringIO
from sklearn.linear_model import SGDClassifier
from sklearn.svm import SVC
from sklearn.ensemble import RandomForestClassifier
from sklearn.datasets import load_breast_cancer


import threading
import sys
import os

class Capturing():
    def __init__(self):
        self._stdout = None
        self._stderr = None
        self._r = None
        self._w = None
        self._thread = None
        self._on_readline_cb = None

    def _handler(self):
        while not self._w.closed:
            try:
                while True:
                    line = self._r.readline()
                    if len(line) == 0: break
                    if self._on_readline_cb: self._on_readline_cb(line)
            except:
                break

    def print(self, s, end=""):
        print(s, file=self._stdout, end=end)

    def on_readline(self, callback):
        self._on_readline_cb = callback

    def start(self):
        self._stdout = sys.stdout
        self._stderr = sys.stderr
        r, w = os.pipe()
        r, w = os.fdopen(r, 'r'), os.fdopen(w, 'w', 1)
        self._r = r
        self._w = w
        sys.stdout = self._w
        sys.stderr = self._w
        self._thread = threading.Thread(target=self._handler)
        self._thread.start()

    def stop(self):
        self._w.close()
        if self._thread: self._thread.join()
        self._r.close()
        sys.stdout = self._stdout
        sys.stderr = self._stderr

capturing = Capturing()

def on_read(line):
    # do something with the line
    capturing.print("got line: "+line)

X, y = load_breast_cancer(return_X_y=True)
capturing.on_readline(on_read)
capturing.start()
clf = RandomForestClassifier(verbose=True)
clf.fit(X, y)
capturing.stop()

# X, y = load_breast_cancer(return_X_y=True)
#
# old_stdout = sys.stdout
# sys.stdout = mystdout = StringIO()
#
# clf = SVC(verbose=True)
# clf.fit(X, y)
# sys.stdout = old_stdout
# loss_history = mystdout.getvalue()
# print('LOSS HISTORY:', loss_history.split('\n'))