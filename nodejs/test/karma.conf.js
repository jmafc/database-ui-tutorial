var sharedConfig = require('./karma-shared.conf');

module.exports = function(config) {
  sharedConfig(config);

  config.set({
    frameworks: ['jasmine'],
    files: [
      'bower_components/angular/angular.js',
      'bower_components/angular-*/angular-*.js',
      'app/*.coffee',
      'test/unit/**/*.coffee'
    ],
    autoWatch: true
  });
};
