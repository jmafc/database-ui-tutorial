# -*- coding: utf-8 -*-

import os.path

from jinja2 import Environment, FileSystemLoader
from werkzeug.wrappers import Response


env = Environment(loader=FileSystemLoader(os.path.join(
            os.path.abspath(os.path.dirname(__file__)), 'templates')))


def render(filename, *args, **data):
    template = env.get_template(filename)
    return Response(template.render(*args, **data), mimetype='text/html')
