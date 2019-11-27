#----------------------------------------------------------------------------#
# Imports
#----------------------------------------------------------------------------#
# Starter Code
import json
import dateutil.parser
import babel
from flask import Flask, render_template, request, Response, flash, redirect, url_for, jsonify, abort
from flask_moment import Moment
from flask_sqlalchemy import SQLAlchemy
import logging
from logging import Formatter, FileHandler
from flask_wtf import Form
from forms import *
# Added
from flask_migrate import Migrate
import config
import models
from sqlalchemy import func
#----------------------------------------------------------------------------#
# App Config.
#----------------------------------------------------------------------------#

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

#----------------------------------------------------------------------------#
# Filters.
#----------------------------------------------------------------------------#

def format_datetime(value, format='medium'):
  date = dateutil.parser.parse(value)
  if format == 'full':
      format="EEEE MMMM, d, y 'at' h:mma"
  elif format == 'medium':
      format="EE MM, dd, y h:mma"
  return babel.dates.format_datetime(date, format)

app.jinja_env.filters['datetime'] = format_datetime

#----------------------------------------------------------------------------#
# Controllers.
#----------------------------------------------------------------------------#

@app.route('/')
def index():
  return render_template('pages/home.html')

#  Venues
#  ----------------------------------------------------------------

@app.route('/venues')
def venues():
  # DONE: replace with real venues data.
  # DONE: num_shows should be aggregated based on number of upcoming shows per venue.
  areas = [] # areas is an array to house each state/city combination and show the venues located in that city as well as the # of upcoming shows that they have
  venues = Venue.query.all() # retrieve all venues
  # Loop through each venue distinct city/state combo
  for v in db.session.query(Venue.city, Venue.state).distinct():
    venue_array = []
    for v_sub in db.session.query(Venue).filter_by(city = v.city).filter_by(state = v.state):
      venue_array.append({'id' : v_sub.id, 'name' : v_sub.name, 'num_upcoming_shows' : v_sub.upcoming_show_count()})
    obj = {'city' : v.city, 'state' : v.state, 'venues' : venue_array}
    areas.append(obj)
  return render_template('pages/venues.html', areas=areas)

@app.route('/venues/search', methods=['POST'])
def search_venues():
  # DONE: implement search on artists with partial string search. Ensure it is case-insensitive.
  # TESTED: seach for Hop should return "The Musical Hop".
  # TESTED: search for "Music" should return "The Musical Hop" and "Park Square Live Music & Coffee"

  search_term = request.form.get('search_term', '')
  relevant_venues = db.session.query(Venue).filter(Venue.name.ilike('%' + search_term + '%')).all()
  response={
    'count': len(relevant_venues),   
    "data": relevant_venues
  }
  return render_template('pages/search_venues.html', results=response, search_term=request.form.get('search_term', ''))

@app.route('/venues/<int:venue_id>')
def show_venue(venue_id):
  # shows the venue page with the given venue_id
  # DONE: replace with real venue data from the venues table, using venue_id

  venue = Venue.query.get(venue_id)
  # If no venue is returned by above, return a 404 error
  if (not bool(venue)):
    return render_template('errors/404.html')
  venue.past_shows = venue.past_shows()
  venue.upcoming_shows = venue.upcoming_shows()
  venue.past_shows_count = len(venue.past_shows)
  venue.upcoming_shows_count = len(venue.upcoming_shows)

  return render_template('pages/show_venue.html', venue=venue)

#  Create Venue
#  ----------------------------------------------------------------

@app.route('/venues/create', methods=['GET'])
def create_venue_form():
  form = VenueForm()
  return render_template('forms/new_venue.html', form=form)

@app.route('/venues/create', methods=['POST'])
def create_venue_submission():
  # DONE: insert form data as a new Venue record in the db, instead
  error = False
  body = {}
  # Retrieve posted info from view
  name = request.form.get('name', '')
  city = request.form.get('city', '')
  state = request.form.get('state', '')
  address = request.form.get('address', '')
  phone = request.form.get('phone', '')
  facebook_link = request.form.get('facebook_link', '')
  completed = False
  try:
    # Create a new Venue object based on posted values
    new_venue = Venue(name=name, city=city, state=state, address=address, phone=phone, facebook_link=facebook_link)
    db.session.add(new_venue)
    db.session.commit()
    body['name'] = new_venue.name
    body['error'] = ''
  except:
    db.session.rollback()
    error=True
    print(sys.exc_info()) # Print system execution info
    body['name'] = ''
    body['error'] = 'Ooops...something went wrong.'
  finally:
    db.session.close()
  if not error:
    # DONE: modify data to be the data object returned from db insertion
    # return jsonify(body)
    # on successful db insert, flash success
    flash('Venue ' + new_venue.name + ' was successfully listed!')
  else:
    # DONE: on unsuccessful db insert, flash an error instead.
    flash('An error occurred. Venue ' + data.name + ' could not be listed. Please try again. If this issue persists, call support.')

  # see: http://flask.pocoo.org/docs/1.0/patterns/flashing/
  return render_template('pages/home.html')

@app.route('/venues/<venue_id>', methods=['DELETE'])
def delete_venue(venue_id):
  # WIP: Complete this endpoint for taking a venue_id, and using
  # SQLAlchemy ORM to delete a record. Handle cases where the session commit could fail.
  venue_to_be_deleted = Venue.query.get(venue_id)
  response = {'venue' : venue_to_be_deleted}
  error = False
  try:
    Venue.query.filter_by(id=venue_id).delete()
    db.session.commit()
  except:
    db.session.rollback()
    error = True
  finally:
    db.session.close()
  if error:
    response['message'] = 'Failed to delete ' + venue_to_be_deleted.name + '.'
  else:
    response['message'] = venue_to_be_deleted.name + ' successfully deleted.'

  # DONE BONUS CHALLENGE: Implement a button to delete a Venue on a Venue Page, have it so that
  # clicking that button delete it from the db then redirect the user to the homepage
  return render_template('pages/home.html')

#  Artists
#  ----------------------------------------------------------------
@app.route('/artists')
def artists():
  artists = db.session.query(Artist.id, Artist.name).distinct()
  # DONE: replace with real data returned from querying the database

  return render_template('pages/artists.html', artists=artists)

@app.route('/artists/search', methods=['POST'])
def search_artists():

  # DONE: implement search on artists with partial string search. Ensure it is case-insensitive.
  # TESTED: seach for "A" should return "Guns N Petals", "Matt Quevado", and "The Wild Sax Band".
  # TESTED: search for "band" should return "The Wild Sax Band".
  search_term = request.form.get('search_term', '')
  relevant_artists = db.session.query(Artist).filter(Artist.name.ilike('%' + search_term + '%')).all()
  response={
    'count': len(relevant_artists),   
    "data": relevant_artists
  }
  return render_template('pages/search_artists.html', results=response, search_term=request.form.get('search_term', ''))


@app.route('/artists/<int:artist_id>')
def show_artist(artist_id):
  # shows the venue page with the given venue_id
  # DONE: replace with real venue data from the venues table, using venue_id
  artist = Artist.query.get(artist_id)
  if (not bool(artist)):
    return render_template('errors/404.html')
  artist.past_shows = artist.past_shows()
  artist.upcoming_shows = artist.upcoming_shows()
  artist.past_shows_count = len(artist.past_shows)
  artist.upcoming_shows_count = len(artist.upcoming_shows)

  return render_template('pages/show_artist.html', artist=artist)

#  Update
#  ----------------------------------------------------------------
@app.route('/artists/<int:artist_id>/edit', methods=['GET'])
def edit_artist(artist_id):
  artist = Artist.query.get(artist_id)
  form = ArtistForm(obj=artist)
  if (not bool(artist)):
    return render_template('errors/404.html')
  # DONE?: populate form with fields from artist with ID <artist_id>
  return render_template('forms/edit_artist.html', form=form, artist=artist)

@app.route('/artists/<int:artist_id>/edit', methods=['POST'])
def edit_artist_submission(artist_id):
  try:
    name = request.form.get('name', '')
    city = request.form.get('city', '')
    state = request.form.get('state', '')
    phone = request.form.get('phone', '')
    facebook_link = request.form.get('facebook_link', '')
    artist = Artist.query.get(artist_id)
    artist.name = name
    artist.city = city
    artist.state = state
    artist.phone = phone
    artist.facebook_link = facebook_link
    db.session.commit()
  except:
    db.session.rollback()
  finally:
    db.session.close()

  # DONE: take values from the form submitted, and update existing
  # artist record with ID <artist_id> using the new attributes

  return redirect(url_for('show_artist', artist_id=artist_id))

@app.route('/venues/<int:venue_id>/edit', methods=['GET'])
def edit_venue(venue_id):
  venue = Venue.query.get(venue_id)
  form = VenueForm(obj=venue)
  if (not bool(venue)):
    return render_template('errors/404.html')
  # DONE?: populate form with fields from venue with ID <venue_id>
  return render_template('forms/edit_venue.html', form=form, venue=venue)

@app.route('/venues/<int:venue_id>/edit', methods=['POST'])
def edit_venue_submission(venue_id):
  try:
    name = request.form.get('name', '')
    city = request.form.get('city', '')
    state = request.form.get('state', '')
    phone = request.form.get('phone', '')
    facebook_link = request.form.get('facebook_link', '')
    venue = Venue.query.get(venue_id)
    venue.name = name
    venue.city = city
    venue.state = state
    venue.phone = phone
    venue.facebook_link = facebook_link
    db.session.commit()
  except:
    db.session.rollback()
  finally:
    db.session.close()

  # DONE: take values from the form submitted, and update existing
  # venue record with ID <venue_id> using the new attributes

  return redirect(url_for('show_venue', venue_id=venue_id))

#  Create Artist
#  ----------------------------------------------------------------

@app.route('/artists/create', methods=['GET'])
def create_artist_form():
  form = ArtistForm()
  return render_template('forms/new_artist.html', form=form)

@app.route('/artists/create', methods=['POST'])
def create_artist_submission():
  # called upon submitting the new artist listing form
  # TODO: insert form data as a new Venue record in the db, instead
  # TODO: modify data to be the data object returned from db insertion

  # on successful db insert, flash success
  flash('Artist ' + request.form['name'] + ' was successfully listed!')
  # TODO: on unsuccessful db insert, flash an error instead.
  # e.g., flash('An error occurred. Artist ' + data.name + ' could not be listed.')
  return render_template('pages/home.html')


#  Shows
#  ----------------------------------------------------------------

@app.route('/shows')
def shows():
  # displays list of shows at /shows
  # TODO: replace with real venues data.
  #       num_shows should be aggregated based on number of upcoming shows per venue.
  data=[{
    "venue_id": 1,
    "venue_name": "The Musical Hop",
    "artist_id": 4,
    "artist_name": "Guns N Petals",
    "artist_image_link": "https://images.unsplash.com/photo-1549213783-8284d0336c4f?ixlib=rb-1.2.1&ixid=eyJhcHBfaWQiOjEyMDd9&auto=format&fit=crop&w=300&q=80",
    "start_time": "2019-05-21T21:30:00.000Z"
  }, {
    "venue_id": 3,
    "venue_name": "Park Square Live Music & Coffee",
    "artist_id": 5,
    "artist_name": "Matt Quevedo",
    "artist_image_link": "https://images.unsplash.com/photo-1495223153807-b916f75de8c5?ixlib=rb-1.2.1&ixid=eyJhcHBfaWQiOjEyMDd9&auto=format&fit=crop&w=334&q=80",
    "start_time": "2019-06-15T23:00:00.000Z"
  }, {
    "venue_id": 3,
    "venue_name": "Park Square Live Music & Coffee",
    "artist_id": 6,
    "artist_name": "The Wild Sax Band",
    "artist_image_link": "https://images.unsplash.com/photo-1558369981-f9ca78462e61?ixlib=rb-1.2.1&ixid=eyJhcHBfaWQiOjEyMDd9&auto=format&fit=crop&w=794&q=80",
    "start_time": "2035-04-01T20:00:00.000Z"
  }, {
    "venue_id": 3,
    "venue_name": "Park Square Live Music & Coffee",
    "artist_id": 6,
    "artist_name": "The Wild Sax Band",
    "artist_image_link": "https://images.unsplash.com/photo-1558369981-f9ca78462e61?ixlib=rb-1.2.1&ixid=eyJhcHBfaWQiOjEyMDd9&auto=format&fit=crop&w=794&q=80",
    "start_time": "2035-04-08T20:00:00.000Z"
  }, {
    "venue_id": 3,
    "venue_name": "Park Square Live Music & Coffee",
    "artist_id": 6,
    "artist_name": "The Wild Sax Band",
    "artist_image_link": "https://images.unsplash.com/photo-1558369981-f9ca78462e61?ixlib=rb-1.2.1&ixid=eyJhcHBfaWQiOjEyMDd9&auto=format&fit=crop&w=794&q=80",
    "start_time": "2035-04-15T20:00:00.000Z"
  }]
  return render_template('pages/shows.html', shows=data)

@app.route('/shows/create')
def create_shows():
  # renders form. do not touch.
  form = ShowForm()
  return render_template('forms/new_show.html', form=form)

@app.route('/shows/create', methods=['POST'])
def create_show_submission():
  # called to create new shows in the db, upon submitting new show listing form
  # TODO: insert form data as a new Show record in the db, instead

  # on successful db insert, flash success
  flash('Show was successfully listed!')
  # TODO: on unsuccessful db insert, flash an error instead.
  # e.g., flash('An error occurred. Show could not be listed.')
  # see: http://flask.pocoo.org/docs/1.0/patterns/flashing/
  return render_template('pages/home.html')

@app.errorhandler(404)
def not_found_error(error):
    return render_template('errors/404.html'), 404

@app.errorhandler(500)
def server_error(error):
    return render_template('errors/500.html'), 500


if not app.debug:
    file_handler = FileHandler('error.log')
    file_handler.setFormatter(
        Formatter('%(asctime)s %(levelname)s: %(message)s [in %(pathname)s:%(lineno)d]')
    )
    app.logger.setLevel(logging.INFO)
    file_handler.setLevel(logging.INFO)
    app.logger.addHandler(file_handler)
    app.logger.info('errors')

#----------------------------------------------------------------------------#
# Launch.
#----------------------------------------------------------------------------#

# Default port:
if __name__ == '__main__':
    app.run(debug=True)

# Or specify port manually:
'''
if __name__ == '__main__':
    port = int(os.environ.get('PORT', 5000))
    app.run(host='0.0.0.0', port=port)
'''
