# -*- coding: utf-8 -*-

from wsgiref.simple_server import make_server


def main(app, port=8080):
    """A simple command line development server."""
    httpd = make_server('', port, app)

    print "Serving %r on port %s ..." % (app, port)
    try:
        httpd.serve_forever()
    except KeyboardInterrupt:
        print "Keyboard interrupt: exiting ..."

if __name__ == '__main__':
    from wsgiref.simple_server import demo_app
    main(demo_app)
