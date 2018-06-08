'''Dotable class for using period attribute accessor syntax on Python dicts

Created by Andy Hayden: https://hayd.github.io/2013/dotable-dictionaries
'''

class Dotable(dict):

    __getattr__= dict.__getitem__

    def __init__(self, d):
        self.update(**dict((k, self.parse(v))
                           for k, v in d.items()))

    @classmethod
    def parse(cls, v):
        if isinstance(v, dict):
            return cls(v)
        elif isinstance(v, list):
            return [cls.parse(i) for i in v]
        else:
            return v
