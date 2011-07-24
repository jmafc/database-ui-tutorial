# -*- coding: utf-8 -*-


def get_all(db):
    return db.fetchall(
        "SELECT id, title, release_year FROM film ORDER BY id")


def get_one(db, id):
    return db.fetchone(
        "SELECT id, title, release_year FROM film WHERE id = %s", (id,))


def insert(db, film):
    return db.execute(
        "INSERT INTO film VALUES "
        "(%(id)s, %(title)s, %(release_year)s)", film.__dict__)


def update(db, film):
    return db.execute(
        "UPDATE film SET title = %s, release_year = %s "
        "WHERE id = %s", (film.title, film.release_year, film.id))


def delete(db, id):
    return db.execute("DELETE FROM film WHERE id = %s", (id,))
