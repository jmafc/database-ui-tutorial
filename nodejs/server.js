var express = require('express'),
    http = require('http'),
    path = require('path');

var app = express();

app.use(express.static(path.join(__dirname, 'public')));
app.use(express.bodyParser());

exports.startServer = function(port, path, callback) {
  var server = http.createServer(app);
  return server.listen(process.env.PORT || port);
};

exports.startServer();
