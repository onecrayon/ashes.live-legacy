class ApiError(Exception):
    status_code = 400

    def __init__(self, message=None, status_code=None):
        Exception.__init__(self)
        self.message = message
        if status_code is not None:
            self.status_code = status_code

    def to_dict(self):
        response = {'error': self.message}
        return response

class Redirect(Exception):
    status_code = 301

    def __init__(self, url=None, status_code=None):
        Exception.__init__(self)
        self.url = url
        if status_code is not None:
            self.status_code = status_code
    
    def to_dict(self):
        response = {'redirect': self.url}
