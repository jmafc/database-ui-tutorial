# -*- coding: utf-8 -*-

from bl.film import Film


class FilmForm(object):
    def __init__(self, **data):
        for attr in ['id', 'title', 'release_year']:
            if attr in data:
                setattr(self, attr, data.get(attr, 0))
            else:
                setattr(self, attr, '')

    def get_key(self):
        id = 0
        while True:
            id = raw_input("Id: ")
            if not id.isdigit() or int(id) < 1:
                print("Id must be a positive integer")
                continue
            break
        return id

    def edit(self, upd=False):
        while True:
            if not upd:
                id = raw_input("Id [%s]: " % self.id).lstrip()
                if not id:
                    id = str(self.id)
                if not id.isdigit() or int(id) < 1:
                    print "Id must be a positive integer"
                    continue
                self.id = int(id)
            title = raw_input("Title [%s]: " % self.title).lstrip()
            if not title:
                title = self.title
            if not title:
                print "Title cannot be an empty string"
                continue
            self.title = title
            release_year = raw_input("Release year [%s]: " % self.release_year)
            if not release_year:
                release_year = str(self.release_year)
            if not release_year.isdigit() or not int(release_year) >= 1888:
                print "Release year must be a number greater than 1887"
                continue
            self.release_year = int(release_year)
            break
        return self


class FilmHandler(object):
    def __init__(self, dbconn):
        self.db = dbconn

    def db_error(self, exc):
        return 'A database error has occurred: %s' % exc.args[0]

    def menu(self):
        retcmd = None
        while True:
            for cmd in ['Add', 'List', 'Update', 'Delete', 'End', 'Quit']:
                print('  %s - %s' % (cmd[:1], cmd))
            cmd = raw_input("Command? ").upper()[:1]
            if cmd == 'A':
                self.create()
            elif cmd == 'L':
                self.list()
            elif cmd == 'U':
                self.update()
            elif cmd == 'D':
                self.delete()
            elif cmd == 'E':
                break
            elif cmd == 'Q':
                retcmd = cmd
                break
            else:
                print("Invalid choice")
        return retcmd

    def list(self):
        errors = {}
        try:
            film_list = Film().all(self.db)
        except Exception as exc:
            film_list = []
            errors = {None: self.db_error(exc)}
        if errors:
            print("%s" % errors[None])
            return
        print("    Id %-32s Year" % 'Title')
        for film in film_list:
            print("%6d %-32s %4d" % (film.id, film.title, film.release_year))

    def create(self):
        form = FilmForm().edit()
        errors = {}
        film = Film(form.id, form.title, form.release_year)
        try:
            film.insert(self.db)
        except Exception as exc:
            errors = {None: self.db_error(exc)}
        else:
            self.db.commit()
        if errors:
            print("%s" % errors[None])
            return
        print("Film '%r' added" % film)

    def update(self):
        id = FilmForm().get_key()
        old_film = Film(int(id))
        try:
            row = old_film.get(self.db)
        except Exception as exc:
            errors = {None: self.db_error(exc)}
        if not row:
            print("Film %d not found " % old_film.id)
            return
        print "Updating '%r'" % old_film
        form = FilmForm(**old_film.__dict__).edit(True)
        errors = {}
        film = Film(form.id, form.title, form.release_year)
        try:
            film.update(self.db)
        except Exception as exc:
            errors = {None: self.db_error(exc)}
        else:
            self.db.commit()
        if errors:
            print("%s" % errors[None])
            return
        print("Film '%r' updated" % film)

    def delete(self):
        id = FilmForm().get_key()
        old_film = Film(int(id))
        try:
            row = old_film.get(self.db)
        except Exception as exc:
            errors = {None: self.db_error(exc)}
        if not row:
            print("Film %d not found " % old_film.id)
            return
        confirm = raw_input("Delete film '%r' (y/n) [n]: " % old_film)
        if not confirm.lower()[:1] == 'y':
            return
        errors = {}
        try:
            old_film.delete(self.db)
        except Exception as exc:
            errors = {None: self.db_error(exc)}
        else:
            self.db.commit()
        if errors:
            print("%s" % errors[None])
            return
        print("Film '%r' deleted" % old_film)
