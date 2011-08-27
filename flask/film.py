# -*- coding: utf-8 -*-

from flask import g, abort, render_template, request, redirect

from main import app
from dblib import DbConnection
from bl.film import Film


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


def db_error(exc):
    return 'A database error has occurred: %s' % exc.args[0]


@app.before_request
def before_request():
    if not hasattr(g, 'db'):
        g.db = DbConnection(app.config['DBNAME'])


@app.route('/film/new')
def new():
    "Displays a form to input a new film"
    return render_template('film/new.html', id='')


@app.route('/film/create', methods=['POST'])
def create():
    "Saves the film data submitted from ``new``"
    form = FilmForm(**request.form)
    form.validate()
    errors = form.errors
    if not errors:
        film = Film(form.id, form.title, form.release_year)
        try:
            film.insert(g.db)
        except Exception as exc:
            errors = {None: db_error(exc)}
        else:
            g.db.commit()
    if errors:
        return render_template('film/new.html', id=form.id, title=form.title,
                      release_year=form.release_year, errors=errors)
    return redirect('/film/')


@app.route('/film/')
def list():
    "Lists all films"
    errors = {}
    try:
        film_list = Film().all(g.db)
    except Exception as exc:
        film_list = []
        errors = {None: db_error(exc)}
    return render_template('film/list.html', films=film_list, errors=errors)


@app.route('/film/<int:id>')
def edit(id):
    "Displays a form for editing a film by id"
    if id < 1:
        abort(404)
    film = Film(int(id))
    try:
        row = film.get(g.db)
    except Exception as exc:
        return render_template('film/edit.html', id=film.id,
                      errors={None: db_error(exc)})
    if not row:
        abort(404)
    return render_template('film/edit.html', id=film.id, title=film.title,
                  release_year=film.release_year)


@app.route('/film/save/<int:id>', methods=['POST'])
def save(id):
    "Saves the film data submitted from ``default``"
    form = FilmForm(**request.form)
    form.validate()
    errors = form.errors
    film = Film(form.id, form.title, form.release_year)
    if not errors:
        try:
            film.update(g.db)
        except Exception as exc:
            errors = {None: db_error(exc)}
        else:
            g.db.commit()
    if errors:
        return render_template('film/edit.html', id=film.id, title=film.title,
                      release_year=film.release_year, errors=errors)
    return redirect('/film/')


@app.route('/film/delete/<int:id>', methods=['GET', 'POST'])
def delete(id=None):
    "Deletes an existing film by id"
    if id < 1:
        abort(404)
    film = Film(int(id))
    try:
        row = film.get(g.db)
    except Exception as exc:
        return render_template('film/edit.html', id=film.id,
                      errors={None: db_error(exc)})
    if not row:
        abort(404)
    if request.method != 'POST':
        return render_template('film/delete.html', id=film.id,
                               film="%r" % (film))
    try:
        film.delete(g.db)
    except Exception as exc:
        return render_template('film/delete.html', id=film.id,
                               film="%r" % film, errors={None: db_error(exc)})
    else:
        g.db.commit()
    return redirect('/film/')
