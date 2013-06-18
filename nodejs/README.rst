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

Install Bower globally, using::

 npm install -g bower

Until Bower support is released for Brunch, some manual steps are
necessary:

 - Invoke ``bower install``.  This will create the ``components``
   directory and fetch the AngularJS and Twitter Bootstrap components
   specified in ``bower.json`` into the new directory (JQuery will
   also be there, as a side effect of requiring Bootstrap).

 - Create the ``vendor`` directories::

    mkdir -p vendor/scripts vendor/styles

 - Copy components to the vendor directories::

    cp components/angular/angular.js vendor/scripts/
    cp components/angular-resource/angular-resource.js vendor/scripts/
    cp components/bootstrap/docs/assets/js/bootstrap.js vendor/scripts/
    cp components/bootstrap/docs/assets/css/bootstrap.css vendor/styles/
    cp components/jquery/jquery.js vendor/scripts/

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
 │   └── app.css
 ├── index.html
 └── js
     ├── app.js
     └── vendor.js

Open the URL http://localhost:3333/ in your web browser.
