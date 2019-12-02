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
from sqlalchemy import func
#----------------------------------------------------------------------------#
# App Config.
#----------------------------------------------------------------------------#

from models import *

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
    flash('An error occurred. Venue ' + body['name'] + ' could not be listed. Please try again. If this issue persists, call support.')

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
  return jsonify(response)

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

  artist.display_genres = []
  for g in artist.genres:
    artist.display_genres.append(Genre.query.get(g.genre_id).name)

  return render_template('pages/show_artist.html', artist=artist)

@app.route('/artists/<artist_id>', methods=['DELETE'])
def delete_artist(artist_id):
  # WIP: Complete this endpoint for taking a artist_id, and using
  # SQLAlchemy ORM to delete a record. Handle cases where the session commit could fail.
  # artist_to_be_deleted = Artist.query.get(artist_id)
  # response = {'artist' : artist_to_be_deleted}
  response = {}
  error = False
  try:
    ArtistGenre.query.filter_by(artist_id = artist_id).delete()
    Artist.query.filter_by(id = artist_id).delete()
    db.session.commit()
  except:
    db.session.rollback()
    error = True
  finally:
    db.session.close()
  if error:
    response['message'] = 'Failed to delete Artist.'
  else:
    response['message'] = 'Artist successfully deleted.'

  return jsonify(response)

#  Update
#  ----------------------------------------------------------------
@app.route('/artists/<int:artist_id>/edit', methods=['GET'])
def edit_artist(artist_id):
  artist = Artist.query.get(artist_id)
  artist.display_genres = []
  for g in artist.genres:
    artist.display_genres.append(Genre.query.get(g.genre_id).name)
  form = ArtistForm(obj=artist)
  if (not bool(artist)):
    return render_template('errors/404.html')
  # DONE?: populate form with fields from artist with ID <artist_id>
  # return ' - '.join(artist.display_genres)
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

    # Delete all artist_genre rows that were not selected. Then loop through genres and add artist_genre rows where applicable.
    genres = request.form.getlist('display_genres') # This will be list of string values
    # return ' ~ '.join(request.form.getlist('display_genres')) 
    
    previous_genres = ArtistGenre.query.filter_by(artist_id = artist_id).all() # Will be list of ArtistGenre objects
    previous_genre_ints = [] # List of ints
    genre_ints = [] # List of ints
    for pg in previous_genres:
      previous_genre_ints.append(pg.genre_id)
    # return str(previous_genre_ints[0])
    for g in genres:
      genre_obj = db.session.query(Genre).filter_by(name = g).first()
      genre_ints.append(genre_obj.id)
    # return str(len(genre_ints))
    for pgi in previous_genre_ints:
      if (pgi not in genre_ints):
        ArtistGenre.query.filter_by(artist_id = artist_id).filter_by(genre_id = pgi).delete()
    for gi in genre_ints:
      if (gi not in previous_genre_ints):
        new_ArtistGenre = ArtistGenre(artist_id = artist_id, genre_id = gi)
        db.session.add(new_ArtistGenre)
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
  error = False
  body = {}
  # Retrieve posted info from view
  name = request.form.get('name', '')
  city = request.form.get('city', '')
  state = request.form.get('state', '')
  address = request.form.get('address', '')
  phone = request.form.get('phone', '')
  facebook_link = request.form.get('facebook_link', '')
  genres = request.form.getlist('display_genres') # This will be list of string values
  genre_ints = []
  for g in genres:
    genre_obj = db.session.query(Genre).filter_by(name = g).first()
    genre_ints.append(genre_obj.id)
  # return str(len(genre_ints))
  try:
    # Create a new Artist object based on posted values
    new_artist = Artist(name=name, city=city, state=state, phone=phone, facebook_link=facebook_link)
    db.session.add(new_artist)
    db.session.commit()
    artist_obj = Artist.query.filter_by(name = new_artist.name).first()
    for gi in genre_ints:
      new_ArtistGenre = ArtistGenre(artist_id = artist_obj.id, genre_id = gi)
      db.session.add(new_ArtistGenre)
    db.session.commit()
    body['name'] = new_artist.name
    body['error'] = ''
  except:
    db.session.rollback()
    error=True
    body['name'] = ''
    body['error'] = 'Ooops...something went wrong.'
  finally:
    db.session.close()
  if not error:
    flash('Artist ' + new_artist.name + ' was successfully listed!')
  else:
    flash('An error occurred. Artist ' + body['name'] + ' could not be listed. Please try again. If this issue persists, call support.')

  # DONE: on unsuccessful db insert, flash an error instead.
  return render_template('pages/home.html')

#  Shows
#  ----------------------------------------------------------------

@app.route('/shows')
def shows():
  # displays list of shows at /shows

  shows = Show.query.all()
  for s in shows:
    s.start_time = str(s.start_time)
    artist = Artist.query.filter_by(id=s.artist_id).first()
    s.artist_name = artist.name
    s.artist_image_link = artist.image_link
    venue = Venue.query.filter_by(id=s.venue_id).first()
    s.venue_name = venue.name

  # DONE: replace with real shows data.
  return render_template('pages/shows.html', shows=shows)

@app.route('/shows/create')
def create_shows():
  form = ShowForm()
  return render_template('forms/new_show.html', form=form)

@app.route('/shows/create', methods=['POST'])
def create_show_submission():
  # called to create new shows in the db, upon submitting new show listing form
  # DONE: insert form data as a new Show record in the db, instead
  error = False
  body = {}
  # Retrieve posted info from view
  artist_id = request.form.get('artist_id', '')
  venue_id = request.form.get('venue_id', '')
  start_time = request.form.get('start_time', '')
  try:
    # Create a new Show object based on posted values
    new_show = Show(artist_id=artist_id, venue_id=venue_id, start_time=start_time)
    db.session.add(new_show)
    db.session.commit()
    body['error'] = ''
  except:
    db.session.rollback()
    error=True
    print(sys.exc_info()) # Print system execution info
    body['error'] = 'Ooops...something went wrong.'
  finally:
    db.session.close()
  if not error:
    flash('Show was successfully listed!')
  else:
    # DONE: on unsuccessful db insert, flash an error instead.
    flash('An error occurred. Show could not be listed. Please try again. If this issue persists, call support.')
  
  return render_template('pages/home.html')

# NEW FUNCTIONALITY
@app.route('/shows/search', methods=['POST'])
def search_shows():
  search_term = request.form.get('search_term', '')
  relevant_shows = []
  all_shows = Show.query.all()
  for s in all_shows:
    s.start_time = str(s.start_time)
    artist = Artist.query.filter_by(id=s.artist_id).first()
    s.artist_name = artist.name
    s.artist_image_link = artist.image_link
    venue = Venue.query.filter_by(id=s.venue_id).first()
    s.venue_name = venue.name
    if (search_term.lower() in artist.name.lower()):
      relevant_shows.append(s)
      continue
    if (search_term.lower() in venue.name.lower()):
      relevant_shows.append(s)
      continue
      
  # relevant_shows = db.session.query(Venue).filter(Venue.name.ilike('%' + search_term + '%')).all()
  response={
    'count': len(relevant_shows),   
    "data": relevant_shows
  }
  return render_template('pages/search_shows.html', results=response, search_term=request.form.get('search_term', ''))

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
