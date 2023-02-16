# app.py

from flask import Flask, request
from flask_restx import Api, Resource
from flask_sqlalchemy import SQLAlchemy
from marshmallow import Schema, fields

app = Flask(__name__)
app.config['SQLALCHEMY_DATABASE_URI'] = 'sqlite:///test.db'
app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = False
db = SQLAlchemy(app)

api = Api(app)
movie_ns = api.namespace('movies')
director_ns = api.namespace('director')
genre_ns = api.namespace('genre')


class Movie(db.Model):
    __tablename__ = 'movie'
    id = db.Column(db.Integer, primary_key=True)
    title = db.Column(db.String(255))
    description = db.Column(db.String(255))
    trailer = db.Column(db.String(255))
    year = db.Column(db.Integer)
    rating = db.Column(db.Float)
    genre_id = db.Column(db.Integer, db.ForeignKey("genre.id"))
    genre = db.relationship("Genre")
    director_id = db.Column(db.Integer, db.ForeignKey("director.id"))
    director = db.relationship("Director")


class Director(db.Model):
    __tablename__ = 'director'
    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String(255))


class Genre(db.Model):
    __tablename__ = 'genre'
    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String(255))


class MovieSchema(Schema):
    id = fields.Int()
    title = fields.Str()
    description = fields.Str()
    trailer = fields.Str()
    year = fields.Int()
    rating = fields.Float()
    genre_id = fields.Int()
    director_id = fields.Int()


class DirectorSchema(Schema):
    id = fields.Int()
    name = fields.Str()


class GenreSchema(Schema):
    id = fields.Int()
    name = fields.Str()


movie_schema = MovieSchema()
movies_schema = MovieSchema(many=True)

genre_schema = GenreSchema()

director_schema = DirectorSchema()


@movie_ns.route('/')
class MoviesView(Resource):
    def get(self):
        director_id = request.args.get('director_id')
        genre_id = request.args.get('genre_id')
        if director_id and genre_id:
            if Movie.query.join(Director, Genre,
                                Movie.genre_id == Genre.id and Movie.director_id == Director.id).filter(
                Director.id == director_id and Genre.id == genre_id):
                movies = Movie.query.join(Director, Genre).filter(Director.id == director_id,
                                                                  Genre.id == genre_id).all()
                return movies_schema.dump(movies), 200
            else:
                return "Error", 404
        elif director_id:
            if Movie.query.join(Director, Director.id == Movie.director_id).filter(Director.id == director_id):
                movies = Movie.query.join(Director).filter(Director.id == director_id).all()
                return movies_schema.dump(movies), 200
            else:
                return "Error", 404
        elif genre_id:
            if Movie.query.join(Genre, Genre.id == Movie.genre_id).filter(Genre.id == genre_id):
                movies = Movie.query.join(Genre).filter(Genre.id == genre_id).all()
                return movies_schema.dump(movies), 200
            else:
                return "Error", 404
        movies = Movie.query.all()
        return movies_schema.dump(movies)


@movie_ns.route('/<int:uid>')
class MovieView(Resource):
    def get(self, uid):
        movie = Movie.query.get(uid)
        return movie_schema.dump(movie)


@genre_ns.route('/')
class GenresView(Resource):
    def post(self):
        req_json = request.json()
        genre = Genre(**req_json)
        with db.session.begin():
            db.session.add(genre)


@genre_ns.route('/<int:uid>')
class GenreView(Resource):
    def put(self, uid):
        req_json = request.json
        genre = db.session.query(Genre).get(uid)
        if not genre:
            return '', 404
        genre.name = req_json.get('name')
        with db.session.begin():
            db.session.add(genre)
            db.session.commit()

    def delete(self, uid):
        genre = db.session.query(Genre).get(uid)
        if not genre:
            return '', 404
        db.session.delete(genre)
        db.session.commit()


@director_ns.route('/')
class DirectorsView(Resource):
    def post(self):
        req_json = request.json()
        director = Director(**req_json)
        with db.session.begin():
            db.session.add(director)


@director_ns.route('/<int:uid>')
class DirectorView(Resource):
    def put(self, uid):
        req_json = request.json
        director = db.session.query(Director).get(uid)
        if not director:
            return '', 404
        director.name = req_json.get('name')
        with db.session.begin():
            db.session.add(director)
            db.session.commit()

    def delete(self, uid):
        director = db.session.query(Director).get(uid)
        if not director:
            return '', 404
        db.session.delete(director)
        db.session.commit()


if __name__ == '__main__':
    app.run(debug=True)
