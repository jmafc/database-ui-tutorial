exports.config =
  # See http://brunch.io/#documentation for docs.
  modules:
    definition: false
    wrapper: false
  paths:
    jadeCompileTrigger: '.compile-jade'
  files:
    javascripts:
      joinTo:
        'js/app.js': /^app/
        'js/vendor.js': /^bower_components/
    stylesheets:
      joinTo:
        'css/app.css': /^(app|bower_components|vendor)/
    templates:
      joinTo:
        '.compile-jade': /^app/
  plugins:
    jade:
      pretty: yes
    jade_angular:
      modules_folder: 'templates'
