# -*- coding: utf-8 -*-

from pyrseas.relation import Attribute, RelVar
from pyrseas.relation import ProjAttribute, Projection, JoinRelation


Film_RV = RelVar('film', [
    Attribute('id', int, sysdefault=True),
    Attribute('title'),
    Attribute('release_year', int)],
    key=['id'])

Film_List = JoinRelation([
    Projection('film',
               [ProjAttribute('id', int),
                ProjAttribute('title'),
                ProjAttribute('release_year', int)])])
