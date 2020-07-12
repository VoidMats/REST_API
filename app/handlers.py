

class Const(object):
    """
    Class to make variable constant in Python 
    * Example:
    ```python
        c = Const(ONE=1, PI=3.14259)
        print(c.ONE)
        c.ONE = 22 # Will trigger ValueError
    ```
    * Return: 
        * All python datatypes
    * Exception: 
        * ValueError
    """
    def __init__(self, *args, **kwargs):
        self._d = dict(*args, **kwargs)

    def __iter__(self):
        return iter(self._d)

    def __len__(self):
        return len(self._d)

    def __getattr__(self, name):
        return self._d[name]

    def __setattr__(self, name, value):
        if (name[0] == '_'):
            super(Const, self).__setattr__(name, value)
        else:
            raise ValueError("setattr while locked", self)