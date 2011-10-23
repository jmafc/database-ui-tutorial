# -*- coding: utf-8 -*-
"""Test web responses"""

import unittest
from xml.dom.minidom import parseString

from werkzeug.test import Client
from werkzeug.wrappers import BaseResponse

from dbapp import create_app
from utils import DbAppTestCase


TEST_DATA = {'id': 123, 'title': "A test movie", 'release_year': 1929}


class WebFilmTestCase(DbAppTestCase):
    """Test film web responses"""

    def setUp(self):
        self.db.execute_commit("TRUNCATE TABLE film")
        self.client = Client(create_app(self.db.name), BaseResponse)
        self.key = TEST_DATA['id']

    def insert_one(self):
        self.db.execute_commit("INSERT INTO film VALUES (%(id)s, "
                               "%(title)s, %(release_year)s)", (TEST_DATA))

    def get_one(self):
        return self.db.fetchone("SELECT * FROM film WHERE id = %s",
                                (self.key,))

    def test_new(self):
        "Select 'New' film link"
        resp = self.client.get('/film/new')
        self.assertEqual(resp.status_code, 200)
        dom = parseString(resp.data)
        form = dom.getElementsByTagName('form')[0]
        self.assertEqual(form.getAttribute('action'), '/film/create')
        self.assertEqual(form.getAttribute('method'), 'post')
        inp = dom.getElementsByTagName('input')[0]
        self.assertEqual(inp.getAttribute('id'), 'id')
        inp = dom.getElementsByTagName('input')[1]
        self.assertEqual(inp.getAttribute('id'), 'title')
        inp = dom.getElementsByTagName('input')[2]
        self.assertEqual(inp.getAttribute('id'), 'release_year')

    def test_create(self):
        "Create a new film"
        resp = self.client.post(path='/film/create', data=TEST_DATA)
        row = self.get_one()
        self.assertEqual(row['title'], TEST_DATA['title'])
        self.assertEqual(row['release_year'], 1929)
        self.assertEqual(resp.status_code, 302)
        self.assertTrue(resp.headers['Location'].endswith('/films'))

    def test_validate_input(self):
        "Validate input fields"
        resp = self.client.post(path='/film/create', data={
                'id': '-123', 'release_year': '1876'})
        self.assertEqual(resp.status_code, 200)
        dom = parseString(resp.data)
        for div in dom.getElementsByTagName('div'):
            if div.getAttribute('class') == 'errmsg':
                txt = div.childNodes[0].data
                if txt.startswith('Id'):
                    self.assertTrue('positive integer' in txt)
                elif txt.startswith('Title'):
                    self.assertTrue('cannot be an empty string' in txt)
                elif txt.startswith('Release year'):
                    self.assertTrue('number greater than 1887' in txt)

    def test_dup_insert(self):
        "Insert a duplicate"
        self.insert_one()
        resp = self.client.post(path='/film/create', data=TEST_DATA)
        self.assertEqual(resp.status_code, 200)
        dom = parseString(resp.data)
        for div in dom.getElementsByTagName('div'):
            if div.getAttribute('class') == 'errmsg':
                self.assertTrue('duplicate key' in div.childNodes[0].data)

    def test_edit(self):
        "Select a film for editing"
        self.insert_one()
        resp = self.client.get('/film/%d' % self.key)
        self.assertEqual(resp.status_code, 200)
        dom = parseString(resp.data)
        form = dom.getElementsByTagName('form')[0]
        self.assertEqual(form.getAttribute('action'), '/film/%d/save' %
                         self.key)
        self.assertEqual(form.getAttribute('method'), 'post')
        inp = dom.getElementsByTagName('input')[0]
        self.assertTrue(inp.hasAttribute('readonly'))
        self.assertEqual(inp.getAttribute('value'), str(TEST_DATA['id']))
        inp = dom.getElementsByTagName('input')[1]
        self.assertEqual(inp.getAttribute('value'), TEST_DATA['title'])
        inp = dom.getElementsByTagName('input')[2]
        self.assertEqual(inp.getAttribute('value'),
                         str(TEST_DATA['release_year']))

    def test_edit_fail(self):
        "Attempt to edit a non-existent film"
        resp = self.client.get('/film/%d' % self.key)
        self.assertEqual(resp.status_code, 404)
        self.assertTrue(("Film %d not found" % self.key) in resp.data)

    def test_save(self):
        "Save a changed film"
        self.insert_one()
        data = TEST_DATA
        data.update(title="A test movie - changed")
        resp = self.client.post(path='/film/%d/save' % self.key, data=data)
        row = self.get_one()
        self.assertEqual(row['title'], data['title'])
        self.assertEqual(resp.status_code, 302)
        self.assertTrue(resp.headers['Location'].endswith('/films'))

    def test_delete_prompt(self):
        "Prompt to delete a film"
        self.insert_one()
        resp = self.client.get('/film/%d/delete' % self.key)
        self.assertEqual(resp.status_code, 200)
        dom = parseString(resp.data)
        p = dom.getElementsByTagName('p')[0]
        self.assertTrue(p.childNodes[0].data.startswith(
                "Are you sure you want to delete"))
        form = dom.getElementsByTagName('form')[0]
        self.assertEqual(form.getAttribute('method'), 'post')

    def test_delete(self):
        "Delete a film"
        self.insert_one()
        resp = self.client.post(path='/film/%d/delete' % self.key)
        self.assertTrue(self.get_one() is None)
        self.assertEqual(resp.status_code, 302)
        self.assertTrue(resp.headers['Location'].endswith('/films'))

    def test_delete_fail(self):
        "Attempt to delete a non-existent film"
        resp = self.client.post(path='/film/%d/delete' % self.key)
        self.assertEqual(resp.status_code, 404)


def suite():
    tests = unittest.TestLoader().loadTestsFromTestCase(WebFilmTestCase)
    return tests

if __name__ == '__main__':
    unittest.main(defaultTest='suite')
