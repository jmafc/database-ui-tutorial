# -*- coding: utf-8 -*-

from psycopg2 import connect


class DbConnection(object):
    def __init__(self, dbname):
        self.dbname = dbname
        self.conn = None

    def connect(self):
        if not self.conn:
            self.conn = connect("dbname=%s" % self.dbname)

    def fetchall(self, query):
        try:
            curs = self.execute(query)
        except Exception as exc:
            print "ERROR: ", exc.args[0]
            return None
        rows = curs.fetchall()
        curs.close()
        return rows

    def fetchone(self, query, args):
        try:
            curs = self.execute(query, args)
        except Exception as exc:
            print "ERROR: ", exc.args[0]
            return None
        row = curs.fetchone()
        curs.close()
        return row

    def execute(self, query, args=None):
        curs = self.conn.cursor()
        try:
            curs.execute(query, args)
        except Exception as exc:
            exc.args += (query, )
            curs.close()
            raise
        return curs
