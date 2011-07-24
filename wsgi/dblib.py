# -*- coding: utf-8 -*-

from psycopg2 import connect as pgconnect


def connect(dbname):
    return pgconnect("dbname=%s" % dbname)


def fetchall(dbconn, query):
    curs = dbconn.cursor()
    try:
        curs.execute(query)
    except Exception, exc:
        curs.close()
        dbconn.rollback()
        print "ERROR: ", exc.args[0]
        return None
    rows = curs.fetchall()
    curs.close()
    dbconn.commit()
    return rows


def fetchone(dbconn, query, args):
    curs = dbconn.cursor()
    try:
        curs.execute(query, args)
    except Exception, exc:
        curs.close()
        dbconn.rollback()
        print "ERROR: ", exc.args[0]
        return None
    row = curs.fetchone()
    curs.close()
    dbconn.commit()
    return row


def execute(dbconn, query, args):
    curs = dbconn.cursor()
    try:
        curs.execute(query, args)
    except Exception, exc:
        curs.close()
        dbconn.rollback()
        print "ERROR: ", exc.args[0]
        return False
    curs.close()
    dbconn.commit()
    return True
