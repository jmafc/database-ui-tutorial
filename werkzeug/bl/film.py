# -*- coding: utf-8 -*-


class Film(object):
    def __init__(self, id=0, title='', release_year=0):
        self.id = id
        self.title = title
        self.release_year = release_year

    def __repr__(self):
        return "%s - %d" % (self.title, self.release_year)

    def get(self, db):
        try:
            row = db.fetchone(
                "SELECT title, release_year FROM film WHERE id = %s",
                (self.id,))
        except Exception as exc:
            raise exc
        db.rollback()
        if not row:
            return None
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

    def insert(self, db):
        try:
            curs = db.execute(
                "INSERT INTO film VALUES "
                "(%(id)s, %(title)s, %(release_year)s)", self.__dict__)
        except Exception as exc:
            raise exc
        curs.close()

    def update(self, db):
        try:
            curs = db.execute(
                "UPDATE film SET title = %s, release_year = %s "
                "WHERE id = %s", (self.title, self.release_year, self.id))
        except Exception as exc:
            raise exc
        curs.close()

    def delete(self, db):
        try:
            curs = db.execute("DELETE FROM film WHERE id = %s", (self.id,))
        except Exception as exc:
            raise exc
        curs.close()
