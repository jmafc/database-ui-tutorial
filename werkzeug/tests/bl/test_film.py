# -*- coding: utf-8 -*-
"""Test business logic"""

import unittest

from psycopg2 import IntegrityError, DatabaseError

from bl.film import Film

from utils import DbAppTestCase


class BLFilmTestCase(DbAppTestCase):
    """Test film business logic operations"""

    def setUp(self):
        self.db.execute_commit("TRUNCATE TABLE film")
        self.db.execute_commit("ALTER SEQUENCE film_id_seq RESTART 1")
        self.key = 1

    def insert_one(self):
        self.db.execute_commit("INSERT INTO film (title, release_year) "
                               "VALUES (%s, %s)", ("A test movie", 1929))

    def insert_100(self):
        self.db.execute_commit(
            "INSERT INTO film (title, release_year) "
            "SELECT 'Movie ' || i AS title, 1900 + i AS release_year "
            "FROM generate_series(1, 100) i")

    def delete_one(self):
        self.db.execute_commit("DELETE FROM film WHERE id = %s", (self.key,))

    def get_one(self):
        return self.db.fetchone("SELECT * FROM film WHERE id = %s",
                                (self.key,))

    def test_insert(self):
        "Insert a film"
        newfilm = Film(self.key, "A test movie", 1929)
        db = self.connection()
        newfilm.insert(db)
        db.commit()
        row = self.get_one()
        self.assertEqual(row['title'], newfilm.title)
        self.assertEqual(row['release_year'], newfilm.release_year)

    def test_dup_insert(self):
        "Insert a duplicate"
        self.insert_one()
        newfilm = Film(self.key, "A test movie", 1929)
        self.assertRaises(IntegrityError, newfilm.insert, self.connection())

    def test_update(self):
        "Update a film"
        self.insert_one()
        db = self.connection()
        film = Film(self.key).get(db)
        film.title = "A test movie - changed"
        film.update(db, film)
        db.commit()
        row = self.get_one()
        self.assertEqual(row['title'], film.title)

    def test_update_missing(self):
        "Update a film that has been deleted"
        self.insert_one()
        db = self.connection()
        film = Film(self.key).get(db)
        self.delete_one()
        film.title = "A test movie - changed"
        self.assertRaises(DatabaseError, film.update, db, film)

    def test_delete(self):
        "Delete a film"
        self.insert_one()
        db = self.connection()
        film = Film(self.key).get(db)
        film.delete(db)
        db.commit()
        row = self.get_one()
        self.assertEqual(row, None)

    def test_delete_missing(self):
        "Delete a film that has already been deleted"
        self.insert_one()
        db = self.connection()
        film = Film(self.key).get(db)
        self.delete_one()
        self.assertRaises(DatabaseError, film.delete, db)

    def test_get_one(self):
        "Get a single film"
        self.insert_one()
        db = self.connection()
        film = Film(self.key).get(db)
        self.assertEqual(film.title, "A test movie")
        self.assertEqual(film.release_year, 1929)

    def test_get_one_fail(self):
        "Fail to get a single film"
        db = self.connection()
        film = Film(self.key).get(db)
        self.assertEqual(film, None)

    def test_get_several(self):
        "Get several films"
        self.insert_one()
        self.db.execute("INSERT INTO film (title, release_year) "
                               "VALUES (%s, %s)", ("A second movie", 1945))
        self.db.execute_commit("INSERT INTO film (title, release_year) "
                               "VALUES (%s, %s)", ("A third movie", 1978))
        db = self.connection()
        films = Film().subset(db)
        self.assertEqual(len(films), 3)
        self.assertEqual(films[0].title, "A test movie")
        self.assertEqual(films[2].release_year, 1978)

    def test_get_none(self):
        "Get several films but find none"
        db = self.connection()
        films = Film().subset(db)
        self.assertEqual(len(films), 0)

    def test_get_slice(self):
        "Get a slice of rows"
        self.insert_100()
        db = self.connection()
        numrows = Film().count(db)
        films = Film().subset(db, 10, 30)
        self.assertEqual(numrows, 100)
        self.assertEqual(len(films), 10)
        self.assertEqual(films[0].title, 'Movie 31')
        self.assertEqual(films[9].release_year, 1940)

    def test_search_title(self):
        "Get a subset of rows by title"
        self.insert_100()
        db = self.connection()
        films = Film().subset(db, qry_args={'title': '7'})
        self.assertEqual(len(films), 19)
        self.assertEqual(films[2].title, 'Movie 27')

    def test_search_title_year(self):
        "Get a subset of rows by title and year"
        self.insert_100()
        db = self.connection()
        films = Film().subset(db, qry_args={'title': 'Movie 7',
                                            'release_year': '> 1975'})
        self.assertEqual(len(films), 4)
        self.assertEqual(films[0].title, 'Movie 76')


def suite():
    tests = unittest.TestLoader().loadTestsFromTestCase(BLFilmTestCase)
    return tests

if __name__ == '__main__':
    unittest.main(defaultTest='suite')
