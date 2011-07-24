#!/usr/bin/python
# -*- coding: utf-8 -*-

import os
import cgi
from optparse import OptionParser

from dblib import DbConnection
from templating import render
from errors import NotFound, Redirect

from film import FilmHandler


class Request(object):
    def __init__(self, environ):
        self.method = environ['REQUEST_METHOD']
        self.path_info = environ['PATH_INFO']
        self.length = environ['CONTENT_LENGTH']
        if self.length:
            body = environ['wsgi.input'].read(int(self.length))
            self.vars = cgi.parse_qs(body)


class Response(object):
    def __init__(self, body, content_type='text/html', status=200):
        self.body = body
        self.content_type = content_type
        self.headers = {}
        if status == 200:
            self.status = '200 OK'
        elif status == 404:
            self.status = '404 Not Found'
        elif status == 303:
            self.status = '303 See other'
        if status != 303:
            self.headers['Content-type'] = content_type


class DatabaseApp(object):
    def __init__(self, dbname):
        self.dbconn = DbConnection(dbname)
        self.handler = FilmHandler(self.dbconn)

    def index(self):
        return render('home.html')

    def error404(self, msg=''):
        return render('error/404.html', msg=msg)

    def serve_css(self, path, resp):
        text = None
        if path.startswith('/static/'):
            try:
                st = os.stat(os.path.join('static', path[8:]))
            except:
                raise NotFound
        from email.utils import formatdate
        resp.headers['Last-modified'] = formatdate(st.st_mtime, usegmt=True)
        resp.body = open(os.path.join('static', path[8:]), 'r').read()

    def dispatch(self, path, request):
        params = {}
        if path == '/':
            func = self.index
        elif path.startswith('/film/'):
            (func, params) = self.handler.dispatch(path[5:], request)
        else:
            raise NotFound
        return (func, params)

    def __call__(self, environ, start_response):
        req = Request(environ)
        html = True
        if req.path_info.endswith('.css'):
            try:
                resp = Response('', 'text/css')
                self.serve_css(req.path_info, resp)
            except NotFound:
                resp = Response('', status=404)
        else:
            try:
                (func, params) = self.dispatch(req.path_info, req)
                resp = Response(func(**params))
            except NotFound, exc:
                resp = Response(self.error404(exc), status=404)
            except Redirect, exc:
                resp = Response('', status=303)
                resp.headers['Location'] = str(exc)
        start_response(resp.status, resp.headers.items())
        return resp.body

if __name__ == '__main__':
    from server import main
    parser = OptionParser("usage: %prog [options] dbname")
    parser.add_option('-p', '--port', dest='port', type='int',
                      help="port number to listen to (default %default)")
    parser.set_defaults(port=8080)
    (options, args) = parser.parse_args()
    if len(args) != 1:
        parser.error("Database name not specified")

    main(DatabaseApp(args[0]), options.port)
