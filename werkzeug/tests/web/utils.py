# -*- coding: utf-8 -*-
"""Utility functions and classes for testing business logic"""

import os
from unittest import TestCase

from pyrseas.lib.dbconn import DbConnection
from pyrseas.lib.dbutils import PostgresDb


TEST_DBNAME = os.environ.get("DBAPP_TEST_DB", 'dbapp_testdb')
TEST_USER = os.environ.get("DBAPP_TEST_USER", os.getenv("USER"))
TEST_HOST = os.environ.get("DBAPP_TEST_HOST", None)
TEST_PORT = os.environ.get("DBAPP_TEST_PORT", None)
ADMIN_DB = os.environ.get("DBAPP_ADMIN_DB", 'postgres')
CREATE_DDL = "CREATE DATABASE %s TEMPLATE = template0"
YAML_SPEC = os.path.normpath(os.path.join(os.path.dirname(__file__),
                                          '../../../film.yaml'))


class DbAppTestCase(TestCase):
    """Base class for most test cases"""

    @classmethod
    def setUpClass(cls):
        import yaml
        from pyrseas.database import Database

        cls.pgdb = PostgresDb(TEST_DBNAME, TEST_USER, TEST_HOST, TEST_PORT)
        cls.pgdb.connect()
        db = Database(TEST_DBNAME, TEST_USER, None, TEST_HOST, TEST_PORT)

        class Opts:
            pass
        opts = Opts()
        opts.schemas = []
        opts.quote_reserved = False
        stmts = db.diff_map(yaml.load(open(YAML_SPEC)), opts)
        for stmt in stmts:
            cls.pgdb.execute(stmt)
        cls.pgdb.conn.commit()

    @classmethod
    def tearDownClass(cls):
        cls.pgdb.close()

    def connection(self):
        return DbConnection(self.pgdb.name, self.pgdb.user, None,
                            self.pgdb.host, self.pgdb.port)
