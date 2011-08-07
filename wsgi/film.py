# -*- coding: utf-8 -*-

from templating import render
from errors import NotFound, Redirect

import bl


class FilmForm(object):
    def __init__(self, **data):
        for attr in ['id', 'title', 'release_year']:
            if attr in data:
                setattr(self, attr, data.get(attr, 0)[0])
            else:
                setattr(self, attr, '')
        self.errors = None

    def validate(self):
        self.errors = {}
        if not self.id.isdigit() or int(self.id) < 1:
            self.errors['id'] = "Id must be a positive integer"
        if not self.title:
            self.errors['title'] = "Title cannot be an empty string"
        if not self.release_year.isdigit() or int(self.release_year) < 1888:
            self.errors['release_year'] = \
                "Release year must be a number greater than 1887"


class FilmHandler(object):
    def __init__(self, dbconn):
        self.db = dbconn

    def dispatch(self, path, request):
        params = {}
        if path == '/':
            func = self.index
        elif path == '/new':
            func = self.new
        elif path == '/create':
            func = self.create
            params = request.vars
        elif path.startswith('/save/'):
            func = self.save
            params = {'id': path[6:]}
            params.update(request.vars)
        elif path.startswith('/delete/'):
            params = {'id': path[8:]}
            if request.method == 'GET':
                func = self.delete_conf
            else:
                func = self.delete
        elif path.startswith('/'):
            func = self.edit
            params = {'id': path[1:]}
        else:
            raise NotFound
        return (func, params)

    def form_error(self, errors):
        errlist = ['<li class="errmsg">%s: %s</li>' % (fld, msg)
                   for (fld, msg) in errors.items()]
        return '<p class="errmsg">Please correct the following errors:\n<ul>' \
            + '\n'.join(errlist) + '\n</ul></p>'

    def db_error(self, exc):
        return '<p class="errmsg">A database error has occurred: %s<p>' % \
                exc.args[0]

    def new(self):
        "Displays a form to input a new film"
        return render('film/new.html', id='', title='', release_year='',
                      errmsg='')

    def create(self, **formdata):
        "Saves the film data submitted from ``new``"
        film = FilmForm(**formdata)
        film.validate()
        if film.errors:
            return render('film/new.html', id=film.id, title=film.title,
                          release_year=film.release_year,
                          errmsg=self.form_error(film.errors))
        self.db.connect()
        try:
            bl.insert(self.db, film)
        except Exception as exc:
            self.db.conn.rollback()
            return render('film/new.html', id=film.id, title=film.title,
                          release_year=film.release_year,
                          errmsg=self.db_error(exc))
        else:
            self.db.conn.commit()
        raise Redirect('/film/')

    def index(self):
        "Lists all films"
        self.db.connect()
        film_list = bl.get_all(self.db)
        self.db.conn.rollback()
        film_tbl = ''
        for i, film in enumerate(film_list):
            film_tbl += '<tr class="row%d">\n' % (i % 2 + 1)
            film_tbl += '<th scope="row"><a href="/film/%d">%s - %d</a>' \
                '</th>\n' % (film[0], film[1], film[2])
        return render('film/list.html', film_tbl=film_tbl)

    def edit(self, id):
        "Displays a form for editing a film by id"
        if not id or not id.isdigit() or int(id) < 1:
            raise NotFound("Film id must be a positive integer: %s" % id)
        self.db.connect()
        row = bl.get_one(self.db, id)
        self.db.conn.rollback()
        if not row:
            raise NotFound("Film %d not found " % int(id))
        return render('film/edit.html', id=row[0], title=row[1],
                      release_year=row[2], errmsg='')

    def save(self, **formdata):
        "Saves the film data submitted from ``default``"
        film = FilmForm(**formdata)
        film.validate()
        if film.errors:
            return render('film/edit.html', id=film.id, title=film.title,
                          release_year=film.release_year,
                          errmsg=self.form_error(film.errors))
        self.db.connect()
        try:
            bl.update(self.db, film)
        except Exception as exc:
            self.db.conn.rollback()
            return render('film/edit.html', id=film.id, title=film.title,
                          release_year=film.release_year,
                          errmsg=self.db_error(exc))
        else:
            self.db.conn.commit()
        raise Redirect('/film/')

    def delete_conf(self, id=None):
        "Request confirmation before deleting an existing film by id"
        if not id or not id.isdigit() or int(id) < 1:
            raise NotFound("Film id must be a positive integer: %s" % id)
        self.db.connect()
        row = bl.get_one(self.db, int(id))
        self.db.conn.rollback()
        if not row:
            raise NotFound("Film %d not found " % int(id))
        return render('film/delete.html', id=int(id), film="%s - %s" % (
                row[1], row[2]))

    def delete(self, id=None):
        "Deletes an existing film by id"
        if not id or not id.isdigit() or int(id) < 1:
            raise NotFound("Film id must be a positive integer: %s" % id)
        self.db.connect()
        row = bl.get_one(self.db, int(id))
        self.db.conn.rollback()
        if not row:
            raise NotFound("Film %d not found " % int(id))
        try:
            bl.delete(self.db, int(id))
        except Exception as exc:
            self.db.conn.rollback()
            return render('film/delete.html', id=int(id), film="%s - %s" % (
                    row[1], row[2]),
                          errmsg=self.db_error(exc))
        else:
            self.db.conn.commit()
        raise Redirect('/film/')
