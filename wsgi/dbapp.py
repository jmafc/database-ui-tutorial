#!/usr/bin/python

from optparse import OptionParser

from dblib import connect
from bl import get_all, get_one
from bl import insert, update, delete


class Film(object):
    def __init__(self, id=0, title='', release_year=0):
        self.id = id
        self.title = title
        self.release_year = release_year

    def __repr__(self):
        return "%s - %d" % (self.title, self.release_year)


def edit(film, upd=False):
    while True:
        if not upd:
            id = raw_input("Id [%d]: " % film.id)
            if not id:
                id = str(film.id)
            if not id.isdigit() or int(id) < 1:
                print "Id must be a positive integer"
                continue
            film.id = int(id)
        title = raw_input("Title [%s]: " % film.title).lstrip()
        if not title:
            title = film.title
        if not title:
            print "Title cannot be an empty string"
            continue
        film.title = title
        release_year = raw_input("Release year [%s]: " % film.release_year)
        if not release_year:
            release_year = str(film.release_year)
        if not release_year.isdigit() or not int(release_year) >= 1888:
            print "Release year must be a number greater than 1887"
            continue
        film.release_year = int(release_year)
        break
    return film


def get_by_key(dbconn):
    while True:
        id = raw_input("Id: ")
        if not id.isdigit() or int(id) < 1:
            print "Id must be a positive integer"
            continue
        break
    row = get_one(dbconn, id)
    if not row:
        print "Film not found"
        return None
    return Film(row[0], row[1], row[2])


def dbapp():
    (opts, args) = OptionParser("usage: %prog dbname").parse_args()
    dbconn = connect(args[0])
    while True:
        for cmd in ['Add', 'List', 'Update', 'Delete', 'Quit']:
            print '  ', cmd[:1], '-', cmd
        cmd = raw_input("Command? ").upper()[:1]
        if cmd == 'Q':
            break
        elif cmd == 'A':
            film = edit(Film())
            if insert(dbconn, film):
                print "Film '%r' added" % film
        elif cmd == 'L':
            rows = get_all(dbconn)
            print "    Id %-32s Year" % 'Title'
            for row in rows:
                print "%6d %-32s %4d" % (row[0], row[1], row[2])
        elif cmd == 'U':
            old_film = get_by_key(dbconn)
            if not old_film:
                continue
            print "Updating '%r'" % old_film
            film = edit(old_film, True)
            if update(dbconn, film):
                print "Film '%r' updated" % film
        elif cmd == 'D':
            old_film = get_by_key(dbconn)
            if not old_film:
                continue
            confirm = raw_input("Delete film '%r' (y/n) [n]: " % old_film)
            if not confirm.lower()[:1] == 'y':
                continue
            if delete(dbconn, old_film.id):
                print "Film '%r' deleted" % old_film
        else:
            print "Invalid choice"
    dbconn.close()
    print "Done"

if __name__ == '__main__':
    dbapp()
