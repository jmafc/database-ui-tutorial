Node.js
=======

Before using the application, you need to have `Node.js
<http://nodejs.org>`_ installed.  Visit http://nodejs.org/download/
and get the version for your operating system.  Once ``node`` and
``npm`` are available, install the Node.js packages, from the
directory of this README, as follows::

 npm install

This will create the ``node_modules`` subdirectory and install the
packages under it.  If you prefer, you can install Express globally.
Instead of the above, use::

 npm install -g install express
 npm link express
 npm install

Brunch
======

Install Brunch globally, using::

 npm install -g brunch

Bower
=====

Install Bower globally and then install Bower components, using::

 npm install -g bower
 bower install

Note: The latter command requires that Git be on your path, so on
Windows you may want to invoke it from a Git Bash window.

``bower install`` will create the ``bower_components`` directory and
fetch the AngularJS and Twitter Bootstrap components specified in
``bower.json`` into the new directory.

Note: Due to a problem in Brunch 1.7.0, you currently have to manually
copy the Bootstrap CSS file to a ``vendor`` directory.  In addition,
to make auto-reload work properly in the browser, you need to copy
``auto-reload.js`` to another ``vendor`` directory.  Do the following::

 mkdir -p vendor/styles vendor/scripts
 cp bower_components/bootstrap/docs/assets/css/bootstrap.css vendor/styles/
 cp node_modules/auto-reload-brunch/vendor/auto-reload.js vendor/scripts

Brunch will then concatenate ``bootstrap.css`` before the application
stylesheet (it will also copy it to ``public/css`` but this can be
disregarded).

Run the Application
===================

Use the following::

  brunch build
  brunch watch --server

The first command (which can be abbreviated to ``brunch b``) is not
entirely necessary, but after invoking it you can verify that the
``public`` directory has been created with a structure such as the
following::

 public/
 ├── css
 │   └── app.css
 ├── index.html
 └── js
     ├── app.js
     └── vendor.js

Instead of the two ``brunch`` commands you can use::

 npm start

Open the URL http://localhost:3333/ in your web browser.

Test the auto-reload feature by editing either
``app/assets/index.html`` (add something to the text of the ``<h1>``
tag) or ``app/app.js`` (change the text of the message).  You should
see an "info: compiled in ..." message from Brunch and the browser
should reflect your changes almost immediately.

Node-postgres
=============

In order to test this, you'll need to have `PostgreSQL
<http://www.postgresql.org/>`_ installed.  Any recent version should
work.  Create a test database and test table as follows::

 createdb moviesdev
 psql moviesdev

 moviesdev=> CREATE TABLE film (
    id serial PRIMARY KEY,
    title character varying(32) UNIQUE NOT NULL,
    release_year integer NOT NULL CHECK (release_year >= 1888));

Alternatively, if you have Pyrseas installed, you can issue the
``createdb`` command and then (assuming you're in the ``nodejs``
directory)::

 yamltodb -u moviesdev ../film.yaml

After running ``npm start``, you should be able to access
``http://localhost:3333/api/films`` to view or update the
table. Initially, of course, the URL above should show an empty
array. ``http://localhost:3333/api/films/count`` should display::

 {
   "count": 0
 }

To add, update or delete rows you'll need to use ``curl``, e.g.::

 curl -X POST -d "title=Seven Samurai" -d "release_year=1954" http://localhost:3333/api/films
 curl -X PUT -d "title=Sichinin no Samurai" -d "release_year=1954" http://localhost:3333/api/films/1
 curl -X DELETE http://localhost:3333/api/films/1

Alternatively, you can use a browser REST extension.
