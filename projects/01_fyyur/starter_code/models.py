
# import json
# import dateutil.parser
# import babel
from flask import Flask
from flask_moment import Moment
from flask_sqlalchemy import SQLAlchemy
# import logging
# from logging import Formatter, FileHandler
# from flask_wtf import Form
# from forms import *
# Added
from flask_migrate import Migrate
# import config
from sqlalchemy import func

app = Flask(__name__)
moment = Moment(app)
app.config.from_object('config')
db = SQLAlchemy(app)
# DONE: connect to a local postgresql database

migrate = Migrate(app, db)

#----------------------------------------------------------------------------#
# Models.
#----------------------------------------------------------------------------#

class Venue(db.Model):
    __tablename__ = 'venues'

    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String)
    city = db.Column(db.String(120))
    state = db.Column(db.String(120))
    address = db.Column(db.String(120))
    phone = db.Column(db.String(120))
    image_link = db.Column(db.String(500))
    facebook_link = db.Column(db.String(120))
    # genres = *-*
    website = db.Column(db.String(120))
    seeking_talent = db.Column(db.Boolean())
    seeking_description = db.Column(db.String(1000), nullable = True)
    shows = db.relationship('Show', backref='venue', lazy=True, cascade = 'delete-orphan')

    def upcoming_shows(self):
      shows = db.session.query(Show).filter(Show.venue_id == self.id).filter(Show.start_time >= func.current_date()).all()
      for s in shows:
        artist = Artist.query.get(s.artist_id)
        s.artist_name = artist.name
        s.artist_image_link = artist.image_link
        s.start_time = str(s.start_time)
      return shows
    def past_shows(self):
      shows = db.session.query(Show).filter(Show.venue_id == self.id).filter(Show.start_time < func.current_date()).all()
      for s in shows:
        artist = Artist.query.get(s.artist_id)
        s.artist_name = artist.name
        s.artist_image_link = artist.image_link
        s.start_time = str(s.start_time)
      return shows
    def upcoming_show_count(self):
      return len(self.upcoming_shows())
    def past_show_count(self):
      return len(self.past_shows())
    
    def __repr__(self):
      return f'<Venue ID: {self.id}, Name: {self.name}>'

    # DONE: implement any missing fields, as a database migration using Flask-Migrate

class Artist(db.Model):
    __tablename__ = 'artists'

    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String)
    city = db.Column(db.String(120))
    state = db.Column(db.String(120))
    phone = db.Column(db.String(120))
    genres = db.Column(db.String(120))
    image_link = db.Column(db.String(500))
    facebook_link = db.Column(db.String(120))
    # genres = *-*
    website = db.Column(db.String(120))
    seeking_venue = db.Column(db.Boolean())
    seeking_description = db.Column(db.String(1000), nullable = True)
    # past_shows = derived
    # upcoming_shows = derived
    # past_shows_count = derived
    # upcoming_shows_count = derived
    shows = db.relationship('Show', backref='artist', lazy=True, cascade = 'delete-orphan')

    def upcoming_shows(self):
      shows = db.session.query(Show).filter(Show.artist_id == self.id).filter(Show.start_time >= func.current_date()).all()
      for s in shows:
        venue = Venue.query.get(s.venue_id)
        s.venue_name = venue.name
        s.venue_image_link = venue.image_link
        s.start_time = str(s.start_time)
      return shows
    def past_shows(self):
      shows = db.session.query(Show).filter(Show.artist_id == self.id).filter(Show.start_time < func.current_date()).all()
      for s in shows:
        venue = Venue.query.get(s.venue_id)
        s.venue_name = venue.name
        s.venue_image_link = venue.image_link
        s.start_time = str(s.start_time)
      return shows

    # DONE: implement any missing fields, as a database migration using Flask-Migrate

class Show(db.Model): # May need to restructure this as an association table?
  __tablename__ = 'shows'

  venue_id = db.Column(db.ForeignKey('venues.id'), primary_key = True)
  artist_id = db.Column(db.ForeignKey('artists.id'), primary_key = True)
  
  start_time = db.Column(db.DateTime(), primary_key = True)

# DONE Implement Show and Artist models, and complete all model relationships and properties, as a database migration.