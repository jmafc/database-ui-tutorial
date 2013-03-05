# -*- coding: utf-8 -*-

from pyrseas.relation import Attribute, RelVar
from pyrseas.relation import ProjAttribute, Projection, JoinRelation


def film_repr(tup):
    return "%s - %d" % (tup.title, tup.release_year)


Film_RV = RelVar('film', [
    Attribute('id', int),
    Attribute('title'),
    Attribute('release_year', int)],
    key=['id'])

Film_List = JoinRelation([
    Projection('film',
               [ProjAttribute('id', int),
                ProjAttribute('title'),
                ProjAttribute('release_year', int)])])
