# -*- coding: utf-8 -*-

import os


def render(template, **data):
    text = open(os.path.join('templates', template), 'r').read()
    return text % data
