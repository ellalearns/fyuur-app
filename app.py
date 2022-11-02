#----------------------------------------------------------------------------#
# Imports
#----------------------------------------------------------------------------#

from dataclasses import dataclass
from email.policy import default
import json
import sys
from tokenize import String
import dateutil.parser
import babel
from flask import Flask, jsonify, render_template, request, Response, flash, redirect, url_for
from flask_moment import Moment
from flask_sqlalchemy import SQLAlchemy
import logging
from logging import Formatter, FileHandler
from flask_wtf import FlaskForm
from flask_migrate import Migrate
from forms import *
import sys
import datetime
from models import *

#----------------------------------------------------------------------------#
# App Config.
#----------------------------------------------------------------------------#

app = Flask(__name__)
moment = Moment(app)
app.config.from_object('config')
db = SQLAlchemy(app)

app.config['SQLALCHEMY_DATABASE_URI'] = 'postgresql://altx:altx@localhost:5432/fyuur2'

migrate = Migrate(app, db)

#----------------------------------------------------------------------------#
# Models.
#----------------------------------------------------------------------------#

#----------------------------------------------------------------------------#
# Filters.
#----------------------------------------------------------------------------#

def format_datetime(value, format='medium'):
  date = dateutil.parser.parse(value)
  if format == 'full':
      format="EEEE MMMM, d, y 'at' h:mma"
  elif format == 'medium':
      format="EE MM, dd, y h:mma"
  return babel.dates.format_datetime(date, format, locale='en')

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
  data = []

  venues_list = []
  test_venues_list = Venue.query.with_entities(Venue.city).all()
  for x in test_venues_list:
    if x in venues_list:
      pass
    else:
      venues_list.append(x)

  for i in venues_list:
    c = (str(i))[2:-3]
    venue = Venue.query.with_entities(Venue.id, Venue.name, Venue.state, Venue.city).filter(Venue.city==c).all()
    test_keys_list = ["city", "state", "venues"]
    main_formula = dict(zip(test_keys_list, [None]*len(test_keys_list)))
    v_list = []
    for i in venue:
      v_keys = ["id", "name", "num_upcoming_shows"]
      v_dict = dict(zip(v_keys, [None]*len(v_keys)))
      v_dict.update({"id": i[0]})
      v_dict.update({"name": i[1]})
      v_list.append(v_dict)
      all_shows = Show.query.with_entities(Show.id, Show.venue_id, Show.start_time).filter(Show.venue_id==i[0]).all()
      if not all_shows:
        v_dict.update({"num_upcoming_shows": 0})
      else:
        us = 0
        ps = 0
        for show in all_shows:
          if show[2] > datetime.datetime.now():
            us = us + 1
          else:
            ps = ps + 1
        v_dict.update({"num_upcoming_shows": us})
    state = (venue[0][2])
    if state == '{C,A}':
      state = (str(venue[0][2]))[1:4:2]
    else:
      pass
    main_formula.update({"city": venue[0][3], "state": state})
    main_formula.update({"venues": v_list})
    data.append(main_formula)
  
  return render_template('pages/venues.html', areas=data);

@app.route('/venues/search', methods=['POST'])
def search_venues():

  search_term = (request.form.get('search_term', '')).lower()\

  venues = []

  venues_from_table = Venue.query.with_entities(Venue.id, Venue.name).all()
  for venue in venues_from_table:
    formatted_venue = str(venue[1]).lower()
    if search_term in formatted_venue:
      venue_data = ["id", "name", "num_upcoming_shows"]
      found_venue_dict = dict(zip(venue_data, [None]*len(venue_data)))
      found_venue_dict.update({"id": venue[0]})
      found_venue_dict.update({"name": venue[1]})
      all_shows = Show.query.with_entities(Show.id, Show.venue_id, Show.start_time).filter(Show.venue_id==venue[0])
      if not all_shows:
        found_venue_dict.update({"num_upcoming_shows": 0})
      else:
        us = 0
        ps = 0
        for show in all_shows:
          if show[2] > datetime.datetime.now():
            us = us + 1
          else:
            ps = ps + 1
        found_venue_dict.update({"num_upcoming_shows": us})
      venues.append(found_venue_dict)

  response={
    "count": venues.__len__(),
    "data": venues,
  }

  return render_template('pages/search_venues.html', results=response, search_term=request.form.get('search_term', ''))

@app.route('/venues/<int:venue_id>')
def show_venue(venue_id):

  upcoming_shows = []
  past_shows = []
  
  all_upcoming_shows = db.session.query(Show).join(Artist).filter(Show.venue_id==venue_id).filter(Show.start_time>datetime.datetime.now())
  for show in all_upcoming_shows:
    artist = Artist.query.get(show.artist_id)
    upcoming_shows.append({"artist_id": show.artist_id, "artist_name": artist.name, "artist_image_link": artist.image_link, "start_time": str(show.start_time)})
  
  all_past_shows = db.session.query(Show).join(Artist).filter(Show.venue_id==venue_id).filter(Show.start_time<datetime.datetime.now())
  for show in all_past_shows:
    artist = Artist.query.get(show.artist_id)
    past_shows.append({"artist_id": show.artist_id, "artist_name": artist.name, "artist_image_link": artist.image_link, "start_time": str(show.start_time)})

  upcoming_shows_count = len(upcoming_shows)
  past_shows_count = len(past_shows)

  all_venues = Venue.query.filter(Venue.id==venue_id).all()
  for venue in all_venues:
    data = {
      "id": venue.id,
      "name": venue.name,
      "genres": venue.genres,
      "address": venue.address,
      "city": venue.city,
      "state": venue.state,
      "phone": venue.phone,
      "website": venue.website_link,
      "facebook_link": venue.facebook_link,
      "seeking_talent": venue.looking_for_talent,
      "seeking_description": venue.seeking_description,
      "image_link": venue.image_link,
      "past_shows": past_shows,
      "upcoming_shows": upcoming_shows,
      "past_shows_count": past_shows_count,
      "upcoming_shows_count": upcoming_shows_count,
      }
  return render_template('pages/show_venue.html', venue=data)

#  Create Venue
#  ----------------------------------------------------------------

@app.route('/venues/create', methods=['GET'])
def create_venue_form():
  form = VenueForm()
  return render_template('forms/new_venue.html', form=form)

@app.route('/venues/create', methods=['POST'])
def create_venue_submission():
  venue_data = VenueForm(request.form, meta={'csrf': False})
  if venue_data.validate_on_submit():
    try:
      new_venue = Venue(
        name=venue_data.name.data,
        city=venue_data.city.data,
        state=venue_data.state.data,
        address=venue_data.address.data,
        phone=venue_data.phone.data,
        genres=venue_data.genres.data,
        facebook_link=venue_data.facebook_link.data,
        image_link=venue_data.image_link.data,
        website_link=venue_data.website_link.data,
        looking_for_talent=venue_data.seeking_talent.data,
        seeking_description=venue_data.seeking_description.data
      )
      db.session.add(new_venue)
      db.session.commit()
      flash('Venue ' + request.form['name'] + ' was successfully listed!')
    except:
      db.session.rollback()
      flash(sys.exc_info())
      flash('Unsuccess 😢')
    finally:
      db.session.close()
  else:
    for field, message in venue_data.errors.items():
            flash(field + ' - ' + str(message))
  return render_template('pages/home.html')

@app.route('/venues/<delete_id>', methods=['POST'])
def delete_venue(delete_id):

  try:
    all_shows = Show.query.filter(Show.venue_id==int(delete_id)).all()
    if not all_shows:
      pass
    else:
      for show in all_shows:
        db.session.delete(show)
      db.session.commit()
    
    venue = Venue.query.get(int(delete_id))
    db.session.delete(venue)
    db.session.commit()
    flash('success!')
  except:
    db.session.rollback()
    flash('unsuccess')
    flash(sys.exc_info)
  finally:
    db.session.close()
  return render_template('pages/home.html')

#  Artists
#  ----------------------------------------------------------------
@app.route('/artists')
def artists():

  data = []

  all_artists = Artist.query.all()
  for artist in all_artists:
    artist_keys = ["id", "name"]
    artist_dict = dict(zip(artist_keys, [None]*len(artist_keys)))
    artist_dict.update({"id": artist.id, "name": artist.name})
    data.append(artist_dict)

  return render_template('pages/artists.html', artists=data)

@app.route('/artists/search', methods=['POST'])
def search_artists():

  data = []

  search_term = request.form.get('search_term', '')
  all_artists = Artist.query.all()
  artist_count = 0
  for artist in all_artists:
    if search_term.lower() in (artist.name).lower():
      artist_dict = {"id": artist.id, "name": artist.name, "num_upcoming_shows": 0}
      show_data = Show.query.filter(Show.artist_id==artist.id)
      if not show_data:
        pass
      else:
        upcoming_shows = 0
        for show in show_data:
          if show.start_time > datetime.datetime.now():
            upcoming_shows = upcoming_shows + 1
          else:
            pass
          artist_dict.update({"num_upcoming_shows": upcoming_shows})
      data.append(artist_dict)
      artist_count = artist_count + 1
    else:
      pass

  response={
    "count": artist_count,
    "data": data
  }

  return render_template('pages/search_artists.html', results=response, search_term=request.form.get('search_term', ''))

@app.route('/artists/<int:artist_id>')
def show_artist(artist_id):

  upcoming_shows = []
  past_shows = []
  
  all_upcoming_shows = db.session.query(Show).join(Venue).filter(Show.artist_id==artist_id).filter(Show.start_time>datetime.datetime.now())
  for show in all_upcoming_shows:
    venue = Venue.query.get(show.venue_id)
    upcoming_shows.append({"venue_id": show.venue_id, "venue_name": venue.name, "venue_image_link": venue.image_link, "start_time": str(show.start_time)})
  
  all_past_shows = db.session.query(Show).join(Venue).filter(Show.artist_id==artist_id).filter(Show.start_time<datetime.datetime.now())
  for show in all_past_shows:
    venue = Venue.query.get(show.venue_id)
    past_shows.append({"venue_id": show.venue_id, "venue_name": venue.name, "venue_image_link": venue.image_link, "start_time": str(show.start_time)})

  upcoming_shows_count = len(upcoming_shows)
  past_shows_count = len(past_shows)

  artist = Artist.query.get(artist_id)

  data = {
    "id": artist.id,
    "name": artist.name,
    "genres": artist.genres,
    "city": artist.city,
    "state": artist.state,
    "phone": artist.phone,
    "website": artist.website_link,
    "facebook_link": artist.facebook_link,
    "seeking_venue": artist.looking_for_venues,
    "seeking_description": artist.seeking_description,
    "image_link": artist.image_link,
    "past_shows": past_shows,
    "upcoming_shows": upcoming_shows,
    "past_shows_count": past_shows_count,
    "upcoming_shows_count": upcoming_shows_count,
  }

  return render_template('pages/show_artist.html', artist=data)

#  Update
#  ----------------------------------------------------------------
@app.route('/artists/<int:artist_id>/edit', methods=['GET'])
def edit_artist(artist_id):

  form = ArtistForm()

  existing_data = Artist.query.filter(Artist.id==artist_id).first()

  artist={
    "id": artist_id,
    "name": existing_data.name,
    "genres": existing_data.genres,
    "city": existing_data.city,
    "state": existing_data.state,
    "phone": existing_data.phone,
    "website": existing_data.website_link,
    "facebook_link": existing_data.facebook_link,
    "seeking_venue": existing_data.looking_for_venues,
    "seeking_description": existing_data.seeking_description,
    "image_link": existing_data.image_link
  }

  return render_template('forms/edit_artist.html', form=form, artist=artist)

@app.route('/artists/<int:artist_id>/edit', methods=['POST'])
def edit_artist_submission(artist_id):

  form = ArtistForm(request.form)

  artist = Artist.query.get(artist_id)
  artist.name = form.name.data
  artist.city = form.city.data
  artist.state = form.state.data
  artist.phone = form.phone.data
  artist.genres = form.genres.data
  artist.facebook_link = form.facebook_link.data
  artist.image_link = form.image_link.data
  artist.website_link = form.website_link.data
  artist.looking_for_venues = form.seeking_venue.data
  artist.seeking_description = form.seeking_description.data
  db.session.commit()

  return redirect(url_for('show_artist', artist_id=artist_id))

@app.route('/venues/<int:venue_id>/edit', methods=['GET'])
def edit_venue(venue_id):
  form = VenueForm()

  existing_data = Venue.query.filter(Venue.id==venue_id).first()

  venue={
    "id": venue_id,
    "name": existing_data.name,
    "genres": existing_data.genres,
    "address": existing_data.address,
    "city": existing_data.city,
    "state": existing_data.state,
    "phone": existing_data.phone,
    "website": existing_data.website_link,
    "facebook_link": existing_data.facebook_link,
    "seeking_talent": existing_data.looking_for_talent,
    "seeking_description": existing_data.seeking_description,
    "image_link": existing_data.image_link
  }

  return render_template('forms/edit_venue.html', form=form, venue=venue)

@app.route('/venues/<int:venue_id>/edit', methods=['POST'])
def edit_venue_submission(venue_id):

  form = VenueForm(request.form)

  venue = Venue.query.get(venue_id)
  venue.name = form.name.data
  venue.city = form.city.data
  venue.state = form.state.data
  venue.address = form.address.data
  venue.phone = form.phone.data
  venue.genres = form.genres.data
  venue.facebook_link = form.facebook_link.data
  venue.image_link = form.image_link.data
  venue.website_link = form.website_link.data
  venue.looking_for_talent = form.seeking_talent.data
  venue.seeking_description = form.seeking_description.data
  db.session.commit()
  
  return redirect(url_for('show_venue', venue_id=venue_id))

#  Create Artist
#  ----------------------------------------------------------------

@app.route('/artists/create', methods=['GET'])
def create_artist_form():
  form = ArtistForm()
  return render_template('forms/new_artist.html', form=form)

@app.route('/artists/create', methods=['GET', 'POST'])
def create_artist_submission():
  form = ArtistForm(request.form, meta={'csrf': False})
  if form.validate_on_submit():
    try:
      new_artist = Artist(
        name=form.name.data,
        city=form.city.data,
        state=form.state.data,
        phone=form.phone.data,
        genres=form.genres.data,
        facebook_link=form.facebook_link.data,
        image_link=form.image_link.data,
        website_link=form.website_link.data,
        looking_for_venues=form.seeking_venue.data,
        seeking_description=form.seeking_description.data
      )
      db.session.add(new_artist)
      db.session.commit()
      flash('Artist ' + request.form['name'] + ' was successfully listed!')
    except:
      db.session.rollback()
      flash(sys.exc_info())
      flash('unsuccess 😢')
    finally:
      db.session.close()
  else:
    for field, message in form.errors.items():
            flash(field + ' - ' + str(message))
  return render_template('pages/home.html')
  


#  Shows
#  ----------------------------------------------------------------

@app.route('/shows')
def shows():
  data=[]

  upcoming_shows = Show.query.all()
  for show in upcoming_shows:
    if show.start_time > datetime.datetime.now():
      venue = Venue.query.filter(Venue.id==show.venue_id).first()
      artist = Artist.query.filter(Artist.id==show.artist_id).first()
      start_time = str(show.start_time)
      show_data = {
        "venue_id": venue.id,
        "venue_name": venue.name,
        "artist_id": artist.id,
        "artist_name": artist.name,
        "artist_image_link": artist.image_link,
        "start_time": start_time
      }
      data.append(show_data)


  return render_template('pages/shows.html', shows=data)

@app.route('/shows/create')
def create_shows():
  # renders form. do not touch.
  form = ShowForm()
  return render_template('forms/new_show.html', form=form)

@app.route('/shows/create', methods=['POST'])
def create_show_submission():
  show_data = ShowForm(request.form)
  try:
    new_show = Show(
      artist_id=show_data.artist_id.data,
      venue_id=show_data.venue_id.data,
      start_time=show_data.start_time.data
    )
    db.session.add(new_show)
    db.session.commit()
    flash('Show was successfully listed!')
  except:
    db.session.rollback()
    flash(sys.exc_info())
    flash('unsuccess 😢')
  finally:
    db.session.close()
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
    app.run()

# Or specify port manually:
'''
if __name__ == '__main__':
    port = int(os.environ.get('PORT', 5000))
    app.run(host='0.0.0.0', port=port)
'''
