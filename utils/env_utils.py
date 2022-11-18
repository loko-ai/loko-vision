import ast
import os

from abc import abstractmethod


def guess_convert(s):
    if s is None:
        return None
    try:
        value = ast.literal_eval(s)
    except Exception:
        return s
    else:
        return value


class Init(object):
    def __getattr__(self ,k):
        return self.get(k ,None)

    @abstractmethod
    def get(self ,k ,default=None):
        pass

class EnvInit(Init):
    def __init__(self, conv=guess_convert):
        self.conv = conv

    def get(self, k, default=None):
        temp = os.environ.get(k, default)
        if self.conv:
            temp = self.conv(temp)
        return temp