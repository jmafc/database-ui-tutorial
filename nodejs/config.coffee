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
          'vendor/jquery/jquery.js'
          'vendor/angular/angular.js'
          'vendor/angular-resource/angular-resource.js'
          'vendor/bootstrap/docs/assets/js/bootstrap.js'
        ]
    stylesheets:
      joinTo:
        'css/app.css': /^(app|vendor)/
