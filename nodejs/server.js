var express = require('express'),
    http = require('http'),
    path = require('path'),
    pg = require('pg').native;

var app = express();

app.use(express.static(path.join(__dirname, 'public')));
app.use(express.bodyParser());

var conString = "pg://localhost/moviesdev";

var execute = function(query, args, callback) {
  pg.connect(conString, function(err, client, done) {
    if (err) {
      console.log(err);
      return callback(err);
    }
    client.query(query, args, function(err, result) {
      done();
      if (err)
        console.log(err);
      callback(err, result);
    });
  });
};

app.get('/api/films', function(req, res) {
  execute("SELECT id, title, release_year FROM film", [],
          function(err, result) {
            if (err)
              res.json(err.message);
            else
              res.json(result.rows);
          });
});

app.get('/api/films/count', function(req, res) {
  execute("SELECT COUNT(*) FROM film", [], function(err, result) {
    if (err)
      res.json(err.message);
    else
      res.json(result.rows[0]);
  });
});

app.get('/api/films/:id', function(req, res) {
  execute(
    "SELECT id, title, release_year FROM film WHERE id = $1",
    [req.params.id],
    function(err, result) {
      if (err)
        res.json(err.message);
      else if (result.rowCount != 1) {
        res.statusCode = 404;
        err = new Error("No film with id " + req.params.id);
        console.log(err);
        res.json(err.message);
      } else
        res.json(result.rows[0]);
    });
});

app.post('/api/films', function(req, res) {
  execute(
    "INSERT INTO film (title, release_year) VALUES($1, $2) RETURNING id",
    [req.body.title, req.body.release_year],
    function(err, result) {
      if (err)
        res.json(err.message);
      else if (result.rowCount != 1) {
        err = new Error("Failed to add film '" + req.body.title + "'");
        console.log(err);
        res.json(err.message);
      } else
        res.redirect('/api/films/' + result.rows[0].id);
    });
});

app.put('/api/films/:id', function(req, res) {
  execute(
    "UPDATE film SET title = $1, release_year = $2 WHERE id = $3",
    [req.body.title, req.body.release_year, req.params.id],
    function(err, result) {
      if (err)
        res.json(err.message);
      else if (result.rowCount != 1) {
        err = new Error("Failed to update film id " + req.params.id);
        console.log(err);
        res.statusCode = 404;
        res.json(err.message);
      } else
        res.redirect('/api/films/' + req.params.id);
    });
});

app.del('/api/films/:id', function(req, res) {
  execute(
    "DELETE FROM film WHERE id = $1", [req.params.id],
    function(err, result) {
      if (err)
        res.json(err.message);
      else if (result.rowCount != 1) {
        err = new Error("Failed to delete film id " + req.params.id);
        console.log(err);
        res.statusCode = 404;
        res.json(err.message);
      } else
        res.redirect('/api/films');
    });
});

exports.startServer = function(port, path, callback) {
  var server = http.createServer(app);
  return server.listen(process.env.PORT || port);
};

exports.startServer();
