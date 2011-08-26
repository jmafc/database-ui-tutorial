# -*- coding: utf-8 -*-

import os.path

from jinja2 import Environment, FileSystemLoader


env = Environment(loader=FileSystemLoader(os.path.join(
            os.path.abspath(os.path.dirname(__file__)), 'templates')))


def render(filename, *args, **data):
    template = env.get_template(filename)
    return template.render(*args, **data)
