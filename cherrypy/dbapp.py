#!/usr/bin/python
# -*- coding: utf-8 -*-

import os.path
from optparse import OptionParser

import cherrypy

from dblib import DbConnection
from templating import render
from film import FilmHandler


class DatabaseApp(object):
    def __init__(self, dbname):
        self.dbconn = DbConnection(dbname)
        self.film = FilmHandler(self.dbconn)

    @cherrypy.expose
    def index(self):
        return render('home.html')


def error404(status, message, traceback, version):
    return render('error/404.html', msg=str(message))


if __name__ == '__main__':
    parser = OptionParser("usage: %prog [options] dbname")
    parser.add_option('-p', '--port', dest='port', type='int',
                      help="port number to listen to (default %default)")
    parser.set_defaults(port=8080)
    (options, args) = parser.parse_args()
    if len(args) != 1:
        parser.error("Database name not specified")

    cherrypy.config.update(
        {'error_page.404': error404,
         'tools.staticdir.on': True,
         'tools.staticdir.root': os.path.join(os.path.dirname(
                    os.path.abspath(__file__)), 'static'),
         'tools.staticdir.dir': ''})

    cherrypy.tree.mount(DatabaseApp(args[0]), '/', 'dbapp.conf')
    cherrypy.engine.start()
    cherrypy.engine.block()
