# -*- coding: utf-8 -*-

import os.path
import tempfile

from mako.lookup import TemplateLookup


lookup = TemplateLookup(
    directories=os.path.join(os.path.abspath(os.path.dirname(__file__)),
                             'templates'),
    module_directory=os.path.join(tempfile.gettempdir(), 'mako', 'dbapp'),
    filesystem_checks=True, collection_size=50,
    output_encoding='utf-8')


def render(filename, *args, **data):
    template = lookup.get_template(filename)
    return template.render(*args, **data)
