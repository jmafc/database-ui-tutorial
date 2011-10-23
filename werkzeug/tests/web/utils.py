# -*- coding: utf-8 -*-
"""Utility functions and classes for testing business logic"""

import os
from unittest import TestCase

from psycopg2 import connect
from psycopg2.extras import DictConnection
from psycopg2.extensions import ISOLATION_LEVEL_AUTOCOMMIT


def pgconnect(dbname, user, host, port):
    "Connect to a Postgres database using psycopg2"
    if host is None or host == '127.0.0.1' or host == 'localhost':
        host = ''
    else:
        host = 'host=%s ' % host
    if port is None or port == 5432:
        port = ''
    else:
        port = "port=%d " % port
    return connect("%s%sdbname=%s user=%s" % (
            host, port, dbname, user), connection_factory=DictConnection)


def pgexecute(dbconn, query, args=None):
    "Execute a query using a cursor"
    curs = dbconn.cursor()
    try:
        curs.execute(query, args)
    except:
        curs.close()
        dbconn.rollback()
        raise
    return curs


def pgexecute_auto(dbconn, query):
    "Execute a query using a cursor with autocommit enabled"
    isolation_level = dbconn.isolation_level
    dbconn.set_isolation_level(ISOLATION_LEVEL_AUTOCOMMIT)
    curs = pgexecute(dbconn, query)
    dbconn.set_isolation_level(isolation_level)
    return curs


TEST_DBNAME = os.environ.get("DBAPP_TEST_DB", 'dbapp_testdb')
TEST_USER = os.environ.get("DBAPP_TEST_USER", os.getenv("USER"))
TEST_HOST = os.environ.get("DBAPP_TEST_HOST", None)
TEST_PORT = os.environ.get("DBAPP_TEST_PORT", None)
ADMIN_DB = os.environ.get("DBAPP_ADMIN_DB", 'postgres')
CREATE_DDL = "CREATE DATABASE %s TEMPLATE = template0"
YAML_SPEC = os.path.normpath(os.path.join(os.getcwd(), '../../../film.yaml'))


class PostgresDb(object):
    """A PostgreSQL database connection

    This is separate from the one used by DbConnection, because the
    tests need to create and drop databases and other objects,
    independently.
    """
    def __init__(self, name, user, host, port):
        self.name = name
        self.user = user
        self.host = host
        self.port = port and int(port)
        self.conn = None

    def connect(self):
        """Connect to the database

        If we're not already connected we first connect to the admin
        database and see if the given database exists.  If it doesn't,
        we create and then connect to it.
        """
        if not self.conn:
            conn = pgconnect(ADMIN_DB, self.user, self.host, self.port)
            curs = pgexecute(conn,
                             "SELECT 1 FROM pg_database WHERE datname = '%s'" %
                             self.name)
            row = curs.fetchone()
            if not row:
                curs.close()
                curs = pgexecute_auto(conn, CREATE_DDL % self.name)
                curs.close()
            conn.close()
            self.conn = pgconnect(self.name, self.user, self.host, self.port)

    def close(self):
        "Close the connection if still open"
        if not self.conn:
            return ValueError
        self.conn.close()

    def create(self):
        "Drop the database if it exists and re-create it"
        conn = pgconnect(ADMIN_DB, self.user, self.host, self.port)
        curs = pgexecute_auto(conn, "DROP DATABASE IF EXISTS %s" % self.name)
        curs = pgexecute_auto(conn, CREATE_DDL % self.name)
        curs.close()
        conn.close()

    def drop(self):
        "Drop the database"
        conn = pgconnect(ADMIN_DB, self.user, self.host, self.port)
        curs = pgexecute_auto(conn, "DROP DATABASE %s" % self.name)
        curs.close()
        conn.close()

    def execute(self, stmt, args=None):
        "Execute a statement"
        curs = pgexecute(self.conn, stmt, args)
        curs.close()

    def execute_commit(self, stmt, args=None):
        "Execute a statement and commit"
        self.execute(stmt, args)
        self.conn.commit()

    def fetchone(self, query, args=None):
        "Execute a query and return one row"
        try:
            curs = pgexecute(self.conn, query, args)
        except Exception as exc:
            raise exc
        row = curs.fetchone()
        curs.close()
        return row


class DbAppTestCase(TestCase):
    """Base class for most test cases"""

    @classmethod
    def setUpClass(cls):
        import yaml
        from pyrseas.database import Database
        from pyrseas.dbconn import DbConnection as PyrDbConn

        cls.db = PostgresDb(TEST_DBNAME, TEST_USER, TEST_HOST, TEST_PORT)
        cls.db.connect()
        db = Database(PyrDbConn(TEST_DBNAME, TEST_USER, TEST_HOST, TEST_PORT))
        stmts = db.diff_map(yaml.load(open(YAML_SPEC)))
        for stmt in stmts:
            cls.db.execute(stmt)
        cls.db.conn.commit()

    @classmethod
    def tearDownClass(cls):
        cls.db.close()
