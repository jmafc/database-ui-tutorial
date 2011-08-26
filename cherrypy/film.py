# -*- coding: utf-8 -*-

import cherrypy

from templating import render
from bl.film import Film


class FilmForm(object):
    def __init__(self, **data):
        for attr in ['id', 'title', 'release_year']:
            if attr in data:
                setattr(self, attr, data.get(attr, 0))
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

    def db_error(self, exc):
        return 'A database error has occurred: %s' % exc.args[0]

    @cherrypy.expose
    def new(self):
        "Displays a form to input a new film"
        return render('film/new.html', id='')

    @cherrypy.expose
    def create(self, **formdata):
        "Saves the film data submitted from ``new``"
        form = FilmForm(**formdata)
        form.validate()
        errors = form.errors
        if not errors:
            film = Film(form.id, form.title, form.release_year)
            try:
                film.insert(self.db)
            except Exception as exc:
                errors = {None: self.db_error(exc)}
            else:
                self.db.commit()
        if errors:
            return render('film/new.html', id=form.id, title=form.title,
                          release_year=form.release_year, errors=errors)
        raise cherrypy.HTTPRedirect('/film/')

    @cherrypy.expose
    def index(self):
        "Lists all films"
        errors = {}
        try:
            film_list = Film().all(self.db)
        except Exception as exc:
            film_list = []
            errors = {None: self.db_error(exc)}
        return render('film/list.html', films=film_list, errors=errors)

    @cherrypy.expose
    def default(self, id=None):
        "Displays a form for editing a film by id"
        if not id or not id.isdigit() or int(id) < 1:
            raise cherrypy.NotFound(
                "Film id must be a positive integer: %s" % id)
        film = Film(int(id))
        try:
            row = film.get(self.db)
        except Exception as exc:
            return render('film/edit.html', id=film.id,
                          errors={None: self.db_error(exc)})
        if not row:
            raise cherrypy.NotFound("Film %d not found " % film.id)
        return render('film/edit.html', id=film.id, title=film.title,
                      release_year=film.release_year)

    @cherrypy.expose
    def save(self, save_id=None, **formdata):
        "Saves the film data submitted from ``default``"
        form = FilmForm(**formdata)
        form.validate()
        errors = form.errors
        film = Film(form.id, form.title, form.release_year)
        if not errors:
            try:
                film.update(self.db)
            except Exception as exc:
                errors = {None: self.db_error(exc)}
            else:
                self.db.commit()
        if errors:
            return render('film/edit.html', id=film.id, title=film.title,
                          release_year=film.release_year, errors=errors)
        raise cherrypy.HTTPRedirect('/film/')

    @cherrypy.expose
    def delete(self, id=None):
        "Deletes an existing film by id"
        if not id or not id.isdigit() or int(id) < 1:
            raise cherrypy.NotFound(
                "Film id must be a positive integer: %s" % id)
        film = Film(int(id))
        try:
            row = film.get(self.db)
        except Exception as exc:
            return render('film/edit.html', id=film.id,
                          errors={None: self.db_error(exc)})
        if not row:
            raise cherrypy.NotFound("Film %d not found " % film.id)
        if cherrypy.request.method != 'POST':
            return render('film/delete.html', id=film.id, film="%r" % (film))
        try:
            film.delete(self.db)
        except Exception as exc:
            return render('film/delete.html', id=film.id, film="%r" % film,
                          errors={None: self.db_error(exc)})
        else:
            self.db.commit()
        raise cherrypy.HTTPRedirect('/film/')
