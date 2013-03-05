# -*- coding: utf-8 -*-
"""Test web responses"""

from xml.dom.minidom import parseString

from werkzeug.test import Client
from werkzeug.wrappers import BaseResponse

from dbapp import create_app
from utils import DbAppTestCase


TEST_DATA = {'title': "A test movie", 'release_year': 1929}


class WebFilmTestCase(DbAppTestCase):
    """Test film web responses"""

    def setUp(self):
        self.pgdb.execute_commit("TRUNCATE TABLE film")
        self.pgdb.execute_commit("ALTER SEQUENCE film_id_seq RESTART 1")
        self.key = 1
        self.client = Client(create_app(self.pgdb.name), BaseResponse)

    def insert_one(self):
        self.pgdb.execute_commit("INSERT INTO film (title, release_year) "
                                 "VALUES (%s, %s)", ("A test movie", 1929))

    def insert_100(self):
        self.pgdb.execute_commit(
            "INSERT INTO film (title, release_year) "
            "SELECT 'Movie ' || i AS title, 1900 + i AS release_year "
            "FROM generate_series(1, 100) i")

    def get_one(self):
        return self.pgdb.fetchone("SELECT xmin, * FROM film WHERE id = %s",
                                  (self.key,))

    def test_new(self):
        "Select 'New' film link"
        resp = self.client.get('/film/new')
        assert resp.status_code == 200
        dom = parseString(resp.data)
        form = dom.getElementsByTagName('form')[0]
        assert form.getAttribute('action') == '/film/create'
        assert form.getAttribute('method') == 'post'
        inp = dom.getElementsByTagName('input')[0]
        assert inp.getAttribute('id') == 'title'
        inp = dom.getElementsByTagName('input')[1]
        assert inp.getAttribute('id') == 'release_year'

    def test_create(self):
        "Create a new film"
        resp = self.client.post(path='/film/create', data=TEST_DATA)
        row = self.get_one()
        assert row['title'] == TEST_DATA['title']
        assert row['release_year'] == 1929
        assert resp.status_code == 302
        assert resp.headers['Location'].endswith('/films')

    def test_validate_input(self):
        "Validate input fields"
        resp = self.client.post(path='/film/create', data={
            'id': '-123', 'release_year': '1876'})
        assert resp.status_code == 200
        dom = parseString(resp.data)
        for div in dom.getElementsByTagName('div'):
            if div.getAttribute('class') == 'errmsg':
                txt = div.childNodes[0].data
                if txt.startswith('Id'):
                    assert 'positive integer' in txt
                elif txt.startswith('Title'):
                    assert 'cannot be an empty string' in txt
                elif txt.startswith('Release year'):
                    assert 'number greater than 1887' in txt

    def test_dup_insert(self):
        "Insert a duplicate"
        self.insert_one()
        resp = self.client.post(path='/film/create', data=TEST_DATA)
        assert resp.status_code == 200
        dom = parseString(resp.data)
        for div in dom.getElementsByTagName('div'):
            if div.getAttribute('class') == 'errmsg':
                assert 'duplicate key' in div.childNodes[0].data

    def test_edit(self):
        "Select a film for editing"
        self.insert_one()
        resp = self.client.get('/film/%d' % self.key)
        assert resp.status_code == 200
        dom = parseString(resp.data)
        form = dom.getElementsByTagName('form')[0]
        assert form.getAttribute('action') == '/film/%d/save' % self.key
        assert form.getAttribute('method') == 'post'
        inp = dom.getElementsByTagName('input')[0]
        assert inp.getAttribute('type') == 'hidden'
        inp = dom.getElementsByTagName('input')[1]
        assert inp.getAttribute('value') == TEST_DATA['title']
        inp = dom.getElementsByTagName('input')[2]
        assert inp.getAttribute('value') == str(TEST_DATA['release_year'])

    def test_edit_fail(self):
        "Attempt to edit a non-existent film"
        resp = self.client.get('/film/%d' % self.key)
        assert resp.status_code == 404
        assert ("Film %d not found" % self.key) in resp.data

    def test_save(self):
        "Save a changed film"
        self.insert_one()
        data = TEST_DATA
        data.update(title="A test movie - changed")
        data.update(rowver=self.get_one()['xmin'])
        resp = self.client.post(path='/film/%d/save' % self.key, data=data)
        row = self.get_one()
        assert row['title'] == data['title']
        assert resp.status_code == 302
        assert resp.headers['Location'].endswith('/films')

    def test_delete_prompt(self):
        "Prompt to delete a film"
        self.insert_one()
        resp = self.client.get('/film/%d/delete' % self.key)
        assert resp.status_code == 200
        dom = parseString(resp.data)
        p = dom.getElementsByTagName('p')[0]
        assert p.childNodes[0].data.startswith(
            "Are you sure you want to delete")
        form = dom.getElementsByTagName('form')[0]
        assert form.getAttribute('method') == 'post'

    def test_delete(self):
        "Delete a film"
        self.insert_one()
        resp = self.client.post(path='/film/%d/delete' % self.key)
        assert self.get_one() is None
        assert resp.status_code == 302
        assert resp.headers['Location'].endswith('/films')

    def test_delete_fail(self):
        "Attempt to delete a non-existent film"
        resp = self.client.post(path='/film/%d/delete' % self.key)
        assert resp.status_code == 404

    def test_list(self):
        "Select fifth page of list of films"
        self.insert_100()
        resp = self.client.get(path='/films?p=5')
        assert resp.status_code == 200
        dom = parseString(resp.data)
        th = dom.getElementsByTagName('th')[2]
        assert th.childNodes[0].childNodes[0].data == 'Movie 41'
        span1 = dom.getElementsByTagName('span')[0]
        assert span1.getAttribute('class') == 'this-page'
        assert span1.childNodes[0].data == '5'
        span2 = dom.getElementsByTagName('span')[1]
        assert span2.childNodes[0].data == '100 films'

    def test_list_search(self):
        "Search for films by title and release year"
        self.insert_100()
        # input: title='movie 7', release_year='>= 1970'
        qs = 'title=movie+7&release_year=%3E%3D+1970'
        resp = self.client.get(path='/films', query_string=qs)
        assert resp.status_code == 200
        dom = parseString(resp.data)
        th = dom.getElementsByTagName('th')[2]
        assert th.childNodes[0].childNodes[0].data == 'Movie 70'
        span2 = dom.getElementsByTagName('span')[1]
        assert span2.childNodes[0].data == '10 films'
