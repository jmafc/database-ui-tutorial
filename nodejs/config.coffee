exports.config =
  # See http://brunch.io/#documentation for docs.
  modules:
    definition: false
    wrapper: false
  files:
    javascripts:
      joinTo:
        'js/app.js': /^app/
        'js/vendor.js': /^vendor/
      order:
        before: [
          'vendor/scripts/jquery.js'
          'vendor/scripts/angular.js'
          'vendor/scripts/angular-resource.js'
          'vendor/scripts/bootstrap.js'
        ]
    stylesheets:
      joinTo:
        'css/app.css': /^(app|vendor)/
  server:
    path: 'server.js'
