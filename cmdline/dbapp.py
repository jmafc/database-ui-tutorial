#!/usr/bin/python

from optparse import OptionParser

from dblib import DbConnection
from film import FilmHandler


class DatabaseApp(object):
    def __init__(self, dbname):
        self.dbconn = DbConnection(dbname)
        self.film = FilmHandler(self.dbconn)

    def menu(self):
        while True:
            for cmd in ['Films', 'Quit']:
                print('  %s - %s' % (cmd[:1], cmd))
            cmd = raw_input("Command? ").upper()[:1]
            if cmd == 'Q':
                break
            elif cmd == 'F':
                if self.film.menu() == 'Q':
                    break
            else:
                print("Invalid choice")
        self.dbconn.close()
        print "Done"


if __name__ == '__main__':
    parser = OptionParser("usage: %prog dbname")
    (options, args) = parser.parse_args()
    if len(args) != 1:
        parser.error("Database name not specified")

    dbapp = DatabaseApp(args[0])
    dbapp.menu()
