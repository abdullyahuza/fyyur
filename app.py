# all the necessary imports needed for the app to run
from imports import *

#----------------------------------------------------------------------------#
# App Config.
#----------------------------------------------------------------------------#
app = Flask(__name__)
moment = Moment(app)
app.config.from_object('config')
app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = False
db.init_app(app)

# create tables if database exist
with app.app_context():
    db.create_all()

# initiate flask migrate
migrate = Migrate(app, db)


#----------------------------------------------------------------------------#
# Filters.
#----------------------------------------------------------------------------#
def format_datetime(value, format='medium'):
    date = dateutil.parser.parse(value)
    if format == 'full':
        format = "EEEE MMMM, d, y 'at' h:mma"
    elif format == 'medium':
        format = "EE MM, dd, y h:mma"
    return babel.dates.format_datetime(date, format, locale='en')


app.jinja_env.filters['datetime'] = format_datetime


#----------------------------------------------------------------------------#
# Controllers.
#----------------------------------------------------------------------------#

# Home route
@app.route('/')
def index():
    # query newly listed artist limit 10
    query_new_listed_artists = db.session.query(
        Artist.id,
        Artist.name,
        Artist.city,
        Artist.state).order_by(
        db.desc(
            Artist.id)).limit(10).all()
    new_listed_artists = []
    for nla in query_new_listed_artists:
        artist = {}
        artist['id'] = nla.id
        artist['name'] = nla.name
        artist['city_state'] = nla.city + " " + nla.state
        new_listed_artists.append(artist)

    # query newly listed venues limit 10
    query_new_listed_venues = db.session.query(
        Venue.id,
        Venue.name,
        Venue.city,
        Venue.state).order_by(
        db.desc(
            Venue.id)).limit(10).all()
    new_listed_venues = []
    for nlv in query_new_listed_venues:
        venue = {}
        venue['id'] = nlv.id
        venue['name'] = nlv.name
        venue['city_state'] = nlv.city + " " + nlv.state
        new_listed_venues.append(venue)

    return render_template(
        'pages/home.html',
        artists=new_listed_artists,
        venues=new_listed_venues)


# Venues route
@app.route('/venues')
def venues():
    venues = db.session.query(Venue.city, Venue.state).distinct()
    data = []  # A list to hold all venues according to cities
    venuesArr = []
    for v in venues:
        venuesArr.append(v)

    for city_state in venuesArr:
        city = city_state[0]
        state = city_state[1]
        venue = {}
        venue['city'] = city
        venue['state'] = state
        venue['venues'] = []
        _thisVenues = Venue.query.filter_by(city=city, state=state).all()
        for _thisVenue in _thisVenues:
            upcomming_shows_in_thisVenue = Show.query.filter_by(
                venueID=_thisVenue.id).filter(
                Show.startTime > datetime.now()).all()
            num_of_upcomming = len(upcomming_shows_in_thisVenue)
            venue['venues'].append(
                {
                    "id": _thisVenue.id,
                    "name": _thisVenue.name,
                    "num_upcoming_shows": num_of_upcomming
                }
            )
        data.append(venue)
    return render_template('pages/venues.html', areas=data)

# search venues endpoint


@app.route('/venues/search', methods=['POST'])
def search_venues():
    request_str = request.form.get('search_term', '')
    search_venue = '%{}%'.format(request_str)
    response = {}
    response['data'] = []
    venues = Venue.query.filter(Venue.name.ilike(search_venue)).all()
    if len(venues) > 0:
        for v in venues:
            shows = Show.query.filter_by(venueID=v.id).all()
            venue = {}
            venue['id'] = v.id
            venue['name'] = v.name
            venue['num_upcoming_shows'] = len(shows)
            response['data'].append(venue)
            response['count'] = len(response['data'])

    return render_template(
        'pages/search_venues.html',
        results=response,
        search_term=request.form.get(
            'search_term',
            ''))

# View a venue route


@app.route('/venues/<int:venue_id>')
def show_venue(venue_id):

    data = {}
    venueData = Venue.query.get(venue_id)
    if venueData.id == venue_id:
        data['id'] = venueData.id
        data['name'] = venueData.name
        data['genres'] = venueData.genres.split(',')
        data['address'] = venueData.address
        data['city'] = venueData.city
        data['state'] = venueData.state
        data['phone'] = venueData.phone
        data['website'] = venueData.website_link
        data['facebook_link'] = venueData.facebook_link
        data['seeking_talent'] = venueData.looking_for_talent
        if venueData.looking_for_talent:
            data['seeking_description'] = venueData.seeking_description
        data['image_link'] = venueData.image_link

        # A joined query to return upcomming shows base on the current venue id
        upcoming_shows_query = db.session.query(Show).join(Venue).filter(
            Show.venueID == venue_id).filter(Show.startTime > datetime.now()).all()
        data['upcoming_shows'] = []
        for us in upcoming_shows_query:
            show = {}
            show['artist_id'] = us.artistID
            show['venue_id'] = us.venueID
            show['start_time'] = us.startTime.isoformat()
            show['artist_name'] = Artist.query.filter_by(
                id=us.artistID).first().name
            show['artist_image_link'] = Artist.query.filter_by(
                id=us.artistID).first().image_link
            data['upcoming_shows'].append(show)
        data['upcoming_shows_count'] = len(data['upcoming_shows'])

        # A joined query to return past shows base on the current venue id
        past_shows_query = db.session.query(Show).join(Venue).filter(
            Show.venueID == venue_id).filter(
            Show.startTime < datetime.now()).all()
        data['past_shows'] = []
        for ps in past_shows_query:
            show = {}
            show['artist_id'] = ps.artistID
            show['venue_id'] = ps.venueID
            show['start_time'] = ps.startTime.isoformat()
            show['artist_name'] = Artist.query.filter_by(
                id=ps.artistID).first().name
            show['artist_image_link'] = Artist.query.filter_by(
                id=ps.artistID).first().image_link
            data['past_shows'].append(show)
        data['past_shows_count'] = len(data['past_shows'])

        return render_template('pages/show_venue.html', venue=data)
    else:
        flash({'type': 'error', 'msg': 'A venue with that ID could not be found.'})
        return redirect(url_for('index'))


#  Create Venue route
@app.route('/venues/create', methods=['GET'])
def create_venue_form():
    form = VenueForm()
    return render_template('forms/new_venue.html', form=form)

# Create a venue endpoint


@app.route('/venues/create', methods=['GET', 'POST'])
def create_venue_submission():
    error = False
    if request.method == "POST":
        try:
            v_name = request.form.get('name', default='')
            v_city = request.form.get('city', default='')
            v_state = request.form.get('state', default='')
            v_address = request.form.get('address', default='')
            v_phone = request.form.get('phone', default='')
            v_genres = request.form.getlist('genres')
            v_genres_toStr = ','.join(map(str, v_genres))
            v_imglink = request.form.get('image_link', default='')
            v_fblink = request.form.get('facebook_link', default='')
            v_sitelink = request.form.get('website_link', default='')
            v_seeking_talent = request.form.get(
                'seeking_talent') == 'y' if True else False
            v_seeking_description = request.form.get(
                'seeking_description', default='')

            # initialize the venue
            new_venue = Venue(
                name=v_name,
                city=v_city,
                state=v_state,
                address=v_address,
                phone=v_phone,
                image_link=v_imglink,
                facebook_link=v_fblink,
                genres=v_genres_toStr,
                website_link=v_sitelink,
                looking_for_talent=v_seeking_talent,
                seeking_description=v_seeking_description
            )
            db.session.add(new_venue)
            db.session.commit()
            venue_success = new_venue.name
        except():
            db.session.rollback()
            error = True
            print(sys.exc_info())
        finally:
            db.session.close()
        if error:
            abort(500)
        else:
            # on successful db insert, flash success
            if not error:
                flash({'type': 'success', 'msg': 'Venue ' +
                      venue_success + ' was successfully listed!'})
            else:
                flash({'type': 'error', 'msg': 'An error occurred. Venue ' +
                      v_name + ' could not be listed.'})
            return redirect(url_for('index'))
    else:
        return render_template('forms/new_venue.html')

# delete a venue endpoint


@app.route('/venues/<venue_id>/delete', methods=['DELETE'])
def delete_venue(venue_id):

    error = False
    try:
        venue = Venue.query.get(venue_id)
        venue_name = venue.name
        db.session.delete(venue)
        db.session.commit()
    except():
        db.session.rollback()
        error = True
    finally:
        db.session.close()
    if error:
        abort(500)
    else:
        flash({'type': 'success', 'msg': 'Venue ' +
              venue_name + ' deleted successfully!'})
        return redirect(url_for('index'))

    flash({'type': 'error', 'msg': 'Venue ' +
          venue_name + ' could not be deleted!'})
    return redirect(url_for('venues'))


# view all Artists route
@app.route('/artists')
def artists():
    data = []
    artists = db.session.query(Artist.id, Artist.name).all()
    for a in artists:
        artist = {}
        artist['id'] = a.id
        artist['name'] = a.name
        data.append(artist)
    return render_template('pages/artists.html', artists=data)

# Search an artist route


@app.route('/artists/search', methods=['POST'])
def search_artists():
    request_str = request.form.get('search_term', '')
    search_artist = '%{}%'.format(request_str)
    response = {}
    response['data'] = []
    artists = Artist.query.filter(Artist.name.ilike(search_artist)).all()
    if len(artists) > 0:
        for a in artists:
            shows = Show.query.filter_by(artistID=a.id).all()
            artist = {}
            artist['id'] = a.id
            artist['name'] = a.name
            artist['num_upcoming_shows'] = len(shows)
            response['data'].append(artist)
            response['count'] = len(response['data'])
    return render_template(
        'pages/search_artists.html',
        results=response,
        search_term=request.form.get(
            'search_term',
            ''))

# view an artist route

@app.route('/artists/<int:artist_id>')
def show_artist(artist_id):
    data = {}
    ArtistData = Artist.query.get(artist_id)
    data['id'] = ArtistData.id
    data['name'] = ArtistData.name
    data['genres'] = ArtistData.genres.split(',')
    data['city'] = ArtistData.city
    data['state'] = ArtistData.state
    data['phone'] = ArtistData.phone
    data['seeking_venue'] = ArtistData.looking_for_venues
    if ArtistData.looking_for_venues:
        data['seeking_description'] = ArtistData.seeking_description
    data['image_link'] = ArtistData.image_link
    data['facebook_link'] = ArtistData.facebook_link
    data['website_link'] = ArtistData.website_link

    # A joined query to return upcoming shows base on the current artist id
    upcoming_shows_query = db.session.query(Show).join(Artist).filter(
        Show.artistID == artist_id).filter(
        Show.startTime > datetime.now()).all()
    data['upcoming_shows'] = []
    for us in upcoming_shows_query:
        show = {}
        show['artist_id'] = us.artistID
        show['venue_id'] = us.venueID
        show['start_time'] = us.startTime.isoformat()
        show['venue_name'] = Venue.query.filter_by(id=us.venueID).first().name
        show['venue_image_link'] = Venue.query.filter_by(
            id=us.venueID).first().image_link
        data['upcoming_shows'].append(show)
    data['upcoming_shows_count'] = len(data['upcoming_shows'])

    # A joined query to return past shows base on the current artist id
    past_shows_query = db.session.query(Show).join(Artist).filter(
        Show.artistID == artist_id).filter(
        Show.startTime < datetime.now()).all()
    data['past_shows'] = []
    for ps in past_shows_query:
        show = {}
        show['artist_id'] = ps.artistID
        show['venue_id'] = ps.venueID
        show['start_time'] = ps.startTime.isoformat()
        show['venue_name'] = Venue.query.filter_by(id=ps.venueID).first().name
        show['venue_image_link'] = Venue.query.filter_by(
            id=ps.venueID).first().image_link
        data['past_shows'].append(show)
    data['past_shows_count'] = len(data['past_shows'])

    return render_template('pages/show_artist.html', artist=data)

#  Update and artist route


@app.route('/artists/<int:artist_id>/edit', methods=['GET'])
def edit_artist(artist_id):
    form = ArtistForm()
    artist = Artist.query.get(artist_id)
    # TODO: populate form with fields from artist with ID <artist_id>
    return render_template('forms/edit_artist.html', form=form, artist=artist)

# update an artist endpoint


@app.route('/artists/<int:artist_id>/edit', methods=['POST'])
def edit_artist_submission(artist_id):
    form = ArtistForm()
    artist = Artist.query.get(artist_id)
    error = False
    if artist.id == artist_id:
        try:
            artist.name = request.form.get('name')
            artist.city = request.form.get('city')
            artist.state = request.form.get('state')
            artist.phone = request.form.get('phone')
            genres = request.form.getlist('genres')
            genres_toStr = ','.join(map(str, genres))
            artist.genres = genres_toStr
            artist.facebook_link = request.form.get('facebook_link')
            artist.image_link = request.form.get('image_link')
            artist.website_link = request.form.get('website_link')
            artist.looking_for_venues = request.form.get(
                'seeking_venue') == 'y' if True else False
            if artist.looking_for_venues:
                artist.seeking_description = request.form.get(
                    'seeking_description')
            else:
                artist.seeking_description = ''

            artist_name = artist.name
            db.session.commit()
        except():
            db.session.rollback()
            error = True
            print(sys.exc_info())
        finally:
            db.session.close()
        if error:
            abort(500)
        else:
            if not error:
                flash({'type': 'success', 'msg': 'Artist ' +
                      artist_name + ' updated successfully!'})
            else:
                flash({'type': 'error', 'msg': 'An error occurred. Artist ' +
                      artist_name + ' could not be updated.'})
            return redirect(url_for('show_artist', artist_id=artist_id))
            # venue record with ID <venue_id> using the new attributes
            # return redirect(url_for('index'))
    else:
        flash({'type': 'error', 'msg': 'Unknown Artist ID...'})
        return redirect(url_for('index'))

# edit a venue route


@app.route('/venues/<int:venue_id>/edit', methods=['GET'])
def edit_venue(venue_id):
    form = VenueForm()
    venue = Venue.query.get(venue_id)
    return render_template('forms/edit_venue.html', form=form, venue=venue)

# edit a venue endpoint


@app.route('/venues/<int:venue_id>/edit', methods=['POST'])
def edit_venue_submission(venue_id):
    # TODO: take values from the form submitted, and update existing
    venue = Venue.query.get(venue_id)
    error = False
    if venue.id == venue_id:
        try:
            venue.name = request.form.get('name')
            venue.city = request.form.get('city')
            venue.state = request.form.get('state')
            venue.address = request.form.get('address')
            venue.phone = request.form.get('phone')
            genres = request.form.getlist('genres')
            genres_toStr = ','.join(map(str, genres))
            venue.genres = genres_toStr
            venue.image_link = request.form.get('image_link')
            venue.facebook_link = request.form.get('facebook_link')
            venue.website_link = request.form.get('website_link')
            venue.looking_for_talent = request.form.get(
                'seeking_talent') == 'y' if True else False
            if venue.looking_for_talent:
                venue.seeking_description = request.form.get(
                    'seeking_description')
            else:
                venue.seeking_description = ''

            venue_name = venue.name
            db.session.commit()
        except():
            db.session.rollback()
            error = True
            print(sys.exc_info())
        finally:
            db.session.close()
        if error:
            abort(500)
        else:
            if not error:
                flash({'type': 'success', 'msg': 'Venue ' +
                      venue_name + ' updated successfully!'})
            else:
                flash({'type': 'error', 'msg': 'An error occurred. Venue ' +
                      venue_name + ' could not be updated.'})
            return redirect(url_for('show_venue', venue_id=venue_id))
            # venue record with ID <venue_id> using the new attributes
            # return redirect(url_for('index'))
    else:
        flash({'type': 'error', 'msg': 'Unknown Venue ID...'})
        return redirect(url_for('index'))


#  Create Artist route
@app.route('/artists/create', methods=['GET'])
def create_artist_form():
    form = ArtistForm()
    return render_template('forms/new_artist.html', form=form)

# Create artist enpoint


@app.route('/artists/create', methods=['POST'])
def create_artist_submission():
    # called upon submitting the new artist listing form
    error = False
    if request.method == 'POST':
        try:
            a_name = request.form.get('name', default='')
            a_city = request.form.get('city', default='')
            a_state = request.form.get('state', default='')
            a_phone = request.form.get('phone', default='')
            a_genres = request.form.getlist('genres')
            a_genres_toStr = ','.join(map(str, a_genres))
            a_imglink = request.form.get('image_link', default='')
            a_fblink = request.form.get('facebook_link', default='')
            a_sitelink = request.form.get('website_link', default='')
            a_seeking_venue = request.form.get(
                'seeking_venue') == 'y' if True else False
            a_seeking_description = request.form.get(
                'seeking_description', default='')

            # initialize the venue
            new_artist = Artist(
                name=a_name,
                city=a_city,
                state=a_state,
                phone=a_phone,
                image_link=a_imglink,
                facebook_link=a_fblink,
                genres=a_genres_toStr,
                website_link=a_sitelink,
                looking_for_venues=a_seeking_venue,
                seeking_description=a_seeking_description
            )
            db.session.add(new_artist)
            db.session.commit()
            artist_success = new_artist.name
        except():
            db.session.rollback()
            error = True
            print(sys.exc_info())
        finally:
            db.session.close()
        if error:
            abort(500)
        else:
            if not error:
                flash({'type': 'success', 'msg': 'Artist ' +
                      artist_success + ' was successfully listed!'})
            else:
                flash({'type': 'error', 'msg': 'An error occurred. Artist ' +
                      a_name + ' could not be listed.'})

            return redirect(url_for('artists'))
    else:
        return render_template('forms/new_artist.html')


#  Shows route
@app.route('/shows')
def shows():
    # displays list of shows at /shows
    # TODO: replace with real venues data.
    shows = Show.query.order_by(Show.startTime).all()
    data = []
    for s in shows:
        show = {}
        show['venue_id'] = s.venueID
        show['venue_name'] = db.session.query(
            Venue.name).filter(
            Venue.id == s.venueID).first()[0]
        show['artist_id'] = s.artistID
        show['artist_name'] = db.session.query(
            Artist.name).filter(
            Artist.id == s.artistID).first()[0]
        show['artist_image_link'] = db.session.query(
            Artist.image_link).filter(
            Artist.id == s.artistID).first()[0]
        show['start_time'] = s.startTime.isoformat()
        data.append(show)
    return render_template('pages/shows.html', shows=data)


# create show route
@app.route('/shows/create')
def create_shows():
    # renders form. do not touch.
    form = ShowForm()

    return render_template('forms/new_show.html', form=form)


# create show endpoint
@app.route('/shows/create', methods=['POST'])
def create_show_submission():
    error = False
    if request.method == 'POST':
        try:
            artist_id = request.form.get('artist_id')
            venue_id = request.form .get('venue_id')
            start_time = request.form.get('start_time')

            # initialize the venue
            new_show = Show(
                artistID=artist_id,
                venueID=venue_id,
                startTime=start_time
            )
            db.session.add(new_show)
            db.session.commit()
        except():
            db.session.rollback()
            error = True
            print(sys.exc_info())
        finally:
            db.session.close()
        if error:
            flash({'type': 'error',
                   'msg': 'An error occurred. Show could not be listed.'})
        else:
            if not error:
                flash({'type': 'success', 'msg': 'Show was successfully listed!'})
            else:
                flash({'type': 'error',
                       'msg': 'An error occurred. Show could not be listed.'})

            return redirect(url_for('create_show_submission'))
    else:
        return render_template('forms/new_show.html')


@app.route('/artists/<int:artist_id>/availability', methods=['GET', 'POST'])
def add_availabilty(artist_id):
    if request.method == 'GET':
        form = AvailabilityForm()
        artist = Artist.query.get(artist_id)
        if artist:
            artistName = artist.name
            return render_template(
                'forms/set_availability.html',
                form=form,
                name=artistName,
                artist_id=artist_id)
        flash({'type': 'error', 'msg': 'Invalid Artist ID'})
        return redirect(url_for('artists'))

    elif request.method == 'POST':
        error = False
        try:
            start_time = request.form.get('start_time')
            end_time = request.form.get('end_time')

            # initialize the venue
            new_availability = Availability(
                artistID=artist_id,
                startTime=start_time,
                endTime=end_time
            )
            db.session.add(new_availability)
            db.session.commit()
        except():
            db.session.rollback()
            error = True
            print(sys.exc_info())
        finally:
            db.session.close()
        if error:
            flash({'type': 'error',
                   'msg': 'An error occurred. Availability could not be added.'})
        else:
            if not error:
                flash({'type': 'success',
                       'msg': 'Availability added successfully!'})
            else:
                flash(
                    {'type': 'error', 'msg': 'An error occurred. Availability could not be added.'})

            return redirect(url_for('artists'))


@app.errorhandler(404)
def not_found_error(error):
    return render_template('errors/404.html'), 404
# add availability endpoint


@app.errorhandler(500)
def server_error(error):
    return render_template('errors/500.html'), 500


if not app.debug:
    file_handler = FileHandler('error.log')
    file_handler.setFormatter(Formatter(
        '%(asctime)s %(levelname)s: %(message)s [in %(pathname)s:%(lineno)d]'))
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
