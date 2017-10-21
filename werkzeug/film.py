# -*- coding: utf-8 -*-

from werkzeug.routing import Map, Rule
from werkzeug.exceptions import HTTPException, NotFound
from werkzeug.utils import redirect

from templating import render
from bl.film import Film_RV, Film_List


def film_repr(tup):
    return "%s - %d" % (tup.title, tup.release_year)


class FilmForm(object):
    def __init__(self, **data):
        for attr in ['rowver', 'id', 'title', 'release_year']:
            if attr in data:
                setattr(self, attr, data.get(attr, 0)[0])
            else:
                setattr(self, attr, '')
        self.errors = None

    def validate(self):
        self.errors = {}
        if not self.title:
            self.errors['title'] = "Title cannot be an empty string"
        if not self.release_year.isdigit() or int(self.release_year) < 1888:
            self.errors['release_year'] = \
                "Release year must be a number greater than 1887"


class FilmHandler(object):
    def __init__(self, dbconn):
        self.db = dbconn
        self.relvar = Film_RV
        self.relvar.connect(dbconn)
        self.relation = Film_List
        self.relation.connect(self.db)
        self.url_map = Map([
            Rule('/films', endpoint='index'),
            Rule('/film/new', endpoint='new'),
            Rule('/film/create', endpoint='create'),
            Rule('/film/<int:id>', endpoint='edit'),
            Rule('/film/<int:id>/save', endpoint='save'),
            Rule('/film/<int:id>/delete', endpoint='delete')])

    def dispatch(self, request):
        adapter = self.url_map.bind_to_environ(request.environ)
        try:
            endpoint, values = adapter.match()
            return getattr(self, endpoint)(request, **values)
        except NotFound as exc:
            raise exc
        except HTTPException as exc:
            return exc

    def db_error(self, exc):
        return 'A database error has occurred: %s' % exc.args[0]

    def new(self, request):
        "Displays a form to input a new film"
        return render('film/new.html', film=self.relvar.default_tuple())

    def create(self, request):
        "Saves the film data submitted from 'new'"
        form = FilmForm(**request.form)
        form.validate()
        errors = form.errors
        if not errors:
            film = self.relvar.tuple(title=form.title,
                                     release_year=int(form.release_year))
            try:
                self.relvar.insert_one(film)
            except Exception as exc:
                errors = {None: self.db_error(exc)}
            self.db.commit()
        if errors:
            return render('film/new.html', film=form,  errors=errors)
        return redirect('/films')

    def add_args(self, names, req_args):
        args = {}
        for name in names:
            if name in req_args and req_args[name]:
                args.update({name: req_args[name]})
        return args

    def index(self, request):
        "Lists all films"
        errors = {}
        p = int(request.args.get('p', 1))
        qry_args = self.add_args(['title', 'release_year'], request.args)
        maxlines = 10
        try:
            numrows = self.relation.count(qry_args)
            film_list = self.relation.subset(maxlines, (p - 1) * maxlines,
                                             qry_args)
        except KeyError as exc:
            numrows = 0
            film_list = []
            errors = {None: exc}
        except Exception as exc:
            numrows = 0
            film_list = []
            errors = {None: self.db_error(exc)}
        more = 1 if (numrows % maxlines) else 0
        return render('film/list.html', films=film_list, curr_page=p,
                      numrows=numrows, numpages=numrows // maxlines + more,
                      qry_args=qry_args, errors=errors)

    def edit(self, request, id):
        "Displays a form for editing a film by id"
        if id < 1:
            raise NotFound("Film id must be a positive integer: %s" % id)
        try:
            row = self.relvar.get_one(self.relvar.key_tuple(id))
        except Exception as exc:
            return render('film/edit.html', id=id,
                          errors={None: self.db_error(exc)})
        if not row:
            raise NotFound("Film %d not found " % id)
        return render('film/edit.html', film=row)

    def save(self, request, id=None):
        "Saves the film data submitted from 'edit'"
        form = FilmForm(**request.form)
        form.validate()
        errors = form.errors
        if not errors:
            film = self.relvar.tuple(int(id), form.title,
                                     int(form.release_year))
            film._tuple_version = int(form.rowver)
            try:
                self.relvar.update_one(film, self.relvar.key_tuple(int(id)))
            except Exception as exc:
                errors = {None: self.db_error(exc)}
            self.db.commit()
        if errors:
            return render('film/edit.html', id=id, film=film, errors=errors)
        return redirect('/films')

    def delete(self, request, id=None):
        "Deletes an existing film by id"
        if id < 1:
            raise NotFound("Film id must be a positive integer: %s" % id)
        keytuple = self.relvar.key_tuple(id)
        try:
            row = self.relvar.get_one(keytuple)
        except Exception as exc:
            return render('film/edit.html', id=id,
                          errors={None: self.db_error(exc)})
        if not row:
            raise NotFound("Film %d not found " % id)
        if request.method != 'POST':
            return render('film/delete.html', id=id, film=film_repr(row))
        try:
            self.relvar.delete_one(keytuple, row)
        except Exception as exc:
            return render('film/delete.html', id=row.id, film=film_repr(row),
                          errors={None: self.db_error(exc)})
        self.db.commit()
        return redirect('/films')
