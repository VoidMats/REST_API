#! /usr/bin/python3

class APIexception(Exception):
    
    def __init__(self, code, name, msg=None):
        if msg is None:
            msg = "An error occured in API"
        self.code = code
        self.name = name
        self.msg = msg

class APImissingParameter(APIexception):

    def __init__(self, code, name, msg=None):
        super().__init__(code, name, msg=msg)

    def __str__(self):
        return "{} - {}".format(self.code, self.msg)
    
class APItokenError(APIexception):
    
    def __init__(self, code=None, name=None, msg=None):
        if code is None:
            code = 401
        if name is None:
            name = "Unauthorized"
        super().__init__(code, name, msg=msg)

    def __str__(self):
        return "{} - {}".format(self.code, self.msg)

class APIreturnError(APIexception):
    
    def __init__(self, code, name, msg=None):
        super().__init__(code, name, msg=msg)

    def __str__(self):
        return "{} - {}".format(self.code, self.msg)

class APIsqlError(APIexception):
    
    def __init__(self, code=None, name=None, msg=None):
        if code is None:
            code = 500
        if name is None:
            name = "An internal error occured"
        super().__init__(code, name, msg=msg)

    def __str__(self):
        return "{} - {}".format(self.code, self.msg)

class APIserviceExit(APIexception):
    
    def __init__(self, code=None, name=None, msg=None):
        if code is None:
            code = 500
        if name is None:
            name = "An internal error occured"
        super().__init__(code, name, msg=msg)

    def __str__(self):
        return "{} - {}".format(self.code, self.msg)

class APIonewireError(APIexception):

    def __init__(self, code, name, msg=None):
        super().__init__(code, name, msg=msg)

    def __str__(self):
        return "{} - {}".format(self.code, self.msg)