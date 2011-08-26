# -*- coding: utf-8 -*-

import os

from psycopg2 import connect, DatabaseError
from psycopg2.extensions import register_type, UNICODE
from psycopg2.extras import DictConnection


class DbConnection(object):
    def __init__(self, dbname, user=None, pswd=None, host=None, port=None):
        self.dbname = dbname
        if user is None:
            self.user = ''
        else:
            self.user = " user=%s" % user
        if pswd is None:
            self.pswd = ''
        else:
            self.pswd = " password=%s" % pswd
        if host is None or host == '127.0.0.1' or host == 'localhost':
            self.host = ''
        else:
            self.host = "host=%s " % host
        if port is None or port == 5432:
            self.port = ''
        else:
            self.port = "port=%d " % port
        self.conn = None

    def connect(self):
        register_type(UNICODE)
        dsn = '%s%sdbname=%s%s%s' % (self.host, self.port, self.dbname,
                                   self.user, self.pswd)
        try:
            self.conn = connect(dsn, connection_factory=DictConnection)
        except Exception as exc:
            raise exc

    def commit(self):
        self.conn.commit()

    def rollback(self):
        self.conn.rollback()

    def fetchall(self, query):
        try:
            curs = self.execute(query)
        except Exception as exc:
            raise exc
        rows = curs.fetchall()
        curs.close()
        return rows

    def fetchone(self, query, args=None):
        try:
            curs = self.execute(query, args)
        except Exception as exc:
            raise exc
        row = curs.fetchone()
        curs.close()
        return row

    def execute(self, query, args=None):
        if self.conn is None:
            self.connect()
        curs = self.conn.cursor()
        try:
            curs.execute(query, args)
        except Exception as exc:
            self.conn.rollback()
            curs.close()
            raise exc
        return curs
