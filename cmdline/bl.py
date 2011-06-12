# -*- coding: utf-8 -*-

from dblib import fetchall, fetchone, execute


def get_all(dbconn):
    return fetchall(
        dbconn, "SELECT id, title, release_year FROM film ORDER BY id")


def get_one(dbconn, id):
    return fetchone(
        dbconn, "SELECT id, title, release_year FROM film WHERE id = %s",
        (id,))


def insert(dbconn, film):
    return execute(
        dbconn, "INSERT INTO film VALUES "
        "(%(id)s, %(title)s, %(release_year)s)", film.__dict__)


def update(dbconn, film):
    return execute(
        dbconn, "UPDATE film SET title = %s, release_year = %s "
        "WHERE id = %s", (film.title, film.release_year, film.id))


def delete(dbconn, id):
    return execute(dbconn, "DELETE FROM film WHERE id = %s", (id,))
