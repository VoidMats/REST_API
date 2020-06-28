#! /usr/bin/python3

class APIexception(Exception):
    
    def __init__(self, code, msg=None):
        if msg is None:
            msg = "An error occured in API"
        self.code = code
        self.msg = msg

class APImissingParameter(APIexception):

    def __init__(self, code, msg=None):
        super().__init__(code, msg=msg)

    def __str__(self):
        return "{} - {}".format(self.code, self.msg)
    
class APItokenError(APIexception):
    
    def __init__(self, code, msg=None):
        super().__init__(code, msg=msg)

    def __str__(self):
        return "{} - {}".format(self.code, self.msg)

class APIreturnError(APIexception):
    
    def __init__(self, code, msg=None):
        super().__init__(code, msg=msg)

    def __str__(self):
        return "{} - {}".format(self.code, self.msg)

class APIsqlError(APIexception):
    
    def __init__(self, code, msg=None):
        super().__init__(code, msg=msg)

    def __str__(self):
        return "{} - {}".format(self.code, self.msg)

class APIserviceExit(APIexception):
    
    def __init__(self, code=None, msg=None):
        if code is None:
            code = 600
        super().__init__(code, msg=msg)

    def __str__(self):
        return "{} - {}".format(self.code, self.msg)