Brunch and Bower
================

Until Bower support is released for Brunch, some manual steps are
necessary:

 - Delete the file ``.bowerrc`` (or rename it, e.g., ``.bowerrc.hide``).

 - Invoke ``bower install``.  This will create the ``components``
   directory and fetch the AngularJS and Twitter Bootstrap components
   specified in ``bower.json`` into the new directory (JQuery will
   also be there, as a side effect of requiring Bootstrap).

 - ALTERNATIVE: Instead of the two steps above, keep ``.bowerrc`` and
   run ``bower install``, but then you will have to rename ``vendor``
   to ``components`` and will not be able to run ``bower install`` (or
   ``bower ls``) again.

 - Create the ``vendor`` directories::

    mkdir vendor/scripts vendor/styles

 - Copy components to the vendor directories::

    cp components/angular/angular.js vendor/scripts/
    cp components/angular-resource/angular-resource.js vendor/scripts/
    cp components/bootstrap/docs/assets/js/bootstrap.js vendor/scripts/
    cp components/bootstrap/docs/assets/css/bootstrap.css vendor/styles/
    cp components/jquery/jquery.js vendor/scripts/

Now you are ready to continue with ``brunch build`` and ``brunch watch
--server``.
