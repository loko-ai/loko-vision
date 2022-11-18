class Foo(object):
    def __init__(self, n=100):
        self.n = n
        self.data = list(range(self.n))

    def init(self):
        self.data=list(range(self.n))

    def __getstate__(self):
        print("I'm being pickled")
        return dict(pippo=self.n)

    def __setstate__(self, d):
        print("I'm being unpickled with these values: " + repr(d))
        self.__dict__ = d
        self.init()


import pickle

f = Foo(10000)
f_data = pickle.dumps(f)

print(pickle.dumps(f.__getstate__()))
print(f_data)
f_new = pickle.loads(f_data)
