class APIException(Exception):
    """Base exceptions for all api calls"""
    def __init__(self, *args, **kwargs):
        self.http_code = kwargs.pop('http_code', None)
