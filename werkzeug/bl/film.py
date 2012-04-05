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
        try:
            row = db.fetchone(
                "SELECT xmin, title, release_year FROM film WHERE id = %s",
                (self.id,))
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
    def all(cls, db):
        try:
            rows = db.fetchall(
                "SELECT id, title, release_year FROM film ORDER BY id")
        except Exception as exc:
            raise exc
        db.rollback()
        return [Film(r['id'], r['title'], r['release_year']) for r in rows]

    @classmethod
    def slice(cls, db, limit='ALL', offset=0):
        try:
            rows = db.fetchall(
                "SELECT id, title, release_year FROM film ORDER BY id "
                "LIMIT %s OFFSET %d" % (limit, offset))
        except Exception as exc:
            raise exc
        db.rollback()
        return [Film(r['id'], r['title'], r['release_year']) for r in rows]

    @classmethod
    def count(cls, db):
        try:
            row = db.fetchone("SELECT COUNT(*) FROM film")
        except Exception as exc:
            raise exc
        db.rollback()
        return row[0]

    def insert(self, db):
        try:
            curs = db.execute(
                "INSERT INTO film VALUES "
                "(%(id)s, %(title)s, %(release_year)s)", self.__dict__)
        except Exception as exc:
            raise exc
        if curs.rowcount != 1:
            raise DatabaseError("Failed to add film with id %d" % self.id)
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
            raise DatabaseError("Failed to update film with id %d" % self.id)
        curs.close()

    def delete(self, db):
        try:
            curs = db.execute("DELETE FROM film WHERE id = %s AND xmin = %s", (
                    self.id, self.rowver))
        except Exception as exc:
            raise exc
        if curs.rowcount != 1:
            raise DatabaseError("Failed to delete film with id %d" % self.id)
        curs.close()
