# -*- coding: utf-8 -*-

from psycopg2 import DatabaseError


class Film(object):
    def __init__(self, id=0, title='', release_year=0):
        self.rowver = 0
        self.id = id
        self.title = title
        self.release_year = release_year

    def __repr__(self):
        return "%s - %d" % (self.title, self.release_year)

    def get(self, db):
        keys = {'id': self.id}
        try:
            row = db.fetchone(
                "SELECT xmin, title, release_year FROM film "
                "WHERE id = %(id)s", keys)
        except Exception as exc:
            raise exc
        db.rollback()
        if not row:
            return None
        self.rowver = row['xmin']
        self.title = row['title']
        self.release_year = row['release_year']
        return self

    @classmethod
    def _where_clause(cls, qry_args=None):
        if not qry_args:
            return ('', {})
        subclauses = []
        params = {}
        if 'title' in qry_args:
            subclauses.append("title ILIKE %(title)s")
            params.update({'title': '%%%s%%' % qry_args['title']})
        if 'release_year' in qry_args:
            arg = qry_args['release_year'].strip()
            oper = '='
            if arg[:2] in ['>=', '!=', '<=']:
                oper = arg[:2]
                arg = arg[2:].strip()
            elif arg[:1] in ['>', '<']:
                oper = arg[:1]
                arg = arg[1:].strip()
            if not arg.isdigit() or int(arg) < 1888:
                raise KeyError(
                    "Release year must be a number greater than 1887")
            subclauses.append("release_year " + oper + " %(release_year)s")
            params.update({'release_year': int(arg)})
        return (" WHERE %s" % " AND ".join(subclauses), params)

    @classmethod
    def count(cls, db, qry_args=None):
        (where, params) = cls._where_clause(qry_args)
        try:
            row = db.fetchone("SELECT COUNT(*) FROM film" + where, params)
        except Exception as exc:
            raise exc
        db.rollback()
        return row[0]

    @classmethod
    def subset(cls, db, limit='ALL', offset=0, qry_args=None):
        (where, params) = cls._where_clause(qry_args)
        slice = " LIMIT %s OFFSET %d" % (limit, offset)
        query = "SELECT id, title, release_year FROM film" + where + \
            " ORDER BY id" + slice
        try:
            rows = db.fetchall(query, params)
        except Exception as exc:
            raise exc
        db.rollback()
        return [Film(r['id'], r['title'], r['release_year']) for r in rows]

    def insert(self, db):
        try:
            curs = db.execute(
                "INSERT INTO film (title, release_year) VALUES "
                "(%(title)s, %(release_year)s)", self.__dict__)
        except Exception as exc:
            raise exc
        if curs.rowcount != 1:
            raise DatabaseError("Failed to add film %r" % self)
        curs.close()

    def update(self, db, old):
        try:
            curs = db.execute(
                "UPDATE film SET title = %s, release_year = %s "
                "WHERE id = %s AND xmin = %s", (
                    self.title, self.release_year, self.id, old.rowver))
        except Exception as exc:
            raise exc
        if curs.rowcount != 1:
            raise DatabaseError("Failed to update film %r" % self)
        curs.close()

    def delete(self, db):
        try:
            curs = db.execute("DELETE FROM film WHERE id = %s AND xmin = %s", (
                    self.id, self.rowver))
        except Exception as exc:
            raise exc
        if curs.rowcount != 1:
            raise DatabaseError("Failed to delete film %r" % self)
        curs.close()
