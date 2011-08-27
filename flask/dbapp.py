# -*- coding: utf-8 -*-

from optparse import OptionParser

from flask import render_template

from main import app


@app.route('/')
def index():
    return render_template('home.html')


@app.errorhandler(404)
def error404(msg=''):
    return render_template('error/404.html', msg=msg)


import film

if __name__ == '__main__':
    parser = OptionParser("usage: %prog [options] dbname")
    parser.add_option('-p', '--port', dest='port', type='int',
                      help="port number to listen to (default %default)")
    parser.set_defaults(port=8080)
    (options, args) = parser.parse_args()
    if len(args) != 1:
        parser.error("Database name not specified")

    app.config['DBNAME'] = args[0]
    app.run(port=options.port, debug=True)
