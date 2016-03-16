# -*- coding: utf-8 -*-
class APIException(Exception):
    msg = ''

    """Base exceptions for all api calls"""
    def __init__(self, msg=None):
        if msg:
            self.msg = msg

    def __str__(self):
        return self.msg


class GoogleCaptchaAPIException(APIException):
    msg = 'кажется, гугл нас раскрыл и просит капчу'


class DirtyCantLoginException(APIException):
    msg = 'неверный логин и/или пароль'
