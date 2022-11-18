class House:

    def __init__(self, price):
        self._price = price

    @property
    def price(self):
        return self._price

    @price.setter
    def price(self, new_price):
        if new_price > 0 and isinstance(new_price, float):
            self._price = new_price
        else:
            raise Exception("Please enter a valid price")



class Fulvio:
    def __init__(self,name):
        self._name=name
        self._data=None

    @property
    def data(self):
        if self._data is None:
            print("Inizializzo")
            self._data=list(range(10000))
        return self._data

    @property
    def name(self):
        print("dsfds")
        return self._name

    @name.setter
    def name(self,name):
        if not name:
            raise Exception("Errore")
        self._name=name

f=Fulvio("Fulvio")

print(f.data)
print(f.data)