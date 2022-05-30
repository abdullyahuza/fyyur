from flask_sqlalchemy import SQLAlchemy

db = SQLAlchemy()

#----------------------------------------------------------------------------#
# App Models.
#----------------------------------------------------------------------------#
# Venue model
class Venue(db.Model):
  __tablename__= 'venues'

  id = db.Column(db.Integer, primary_key=True)
  name = db.Column(db.String, unique=True, nullable=False)
  city = db.Column(db.String(120), nullable=False)
  state = db.Column(db.String(120), nullable=False)
  address = db.Column(db.String(120), nullable=False)
  phone = db.Column(db.String(120), nullable=False)
  genres = db.Column(db.String(500), nullable=False)
  image_link = db.Column(db.String(500), nullable=False)
  facebook_link = db.Column(db.String(120))
  website_link = db.Column(db.String(120))
  looking_for_talent = db.Column(db.Boolean(), default=False)
  seeking_description = db.Column(db.String(200))

  # A venue has shows
  shows = db.relationship('Show', backref='venues', lazy=True)

  def __repr__(self):
    return f'<Venue {self.id} {self.name}>'

# Artist Model
class Artist(db.Model):
  __tablename__= 'artists'

  id = db.Column(db.Integer, primary_key=True)
  name = db.Column(db.String, nullable=False)
  city = db.Column(db.String(120), nullable=False)
  state = db.Column(db.String(120), nullable=False)
  phone = db.Column(db.String(120), nullable=False)
  genres = db.Column(db.String(500), nullable=False)
  image_link = db.Column(db.String(500))
  facebook_link = db.Column(db.String(120))
  website_link = db.Column(db.String(120))
  looking_for_venues = db.Column(db.Boolean, default=False)
  seeking_description = db.Column(db.String(200))

  # artist have venues
  shows = db.relationship('Show', backref='artists', lazy=True)
  # artist available times
  # times = db.relationship('Availability', backref='artists', lazy=True)

  def __repr__(self):
    return f'<Artist {self.id} {self.name}>'


# class Availability(db.Model):
#   __tablename__= 'availability_list'

#   id = db.Column(db.Integer, primary_key=True)
#   artistID = db.Column(db.Integer, db.ForeignKey('artists.id'))
#   startTime = db.Column(db.DateTime, nullable=False, unique=True)
#   endTime = db.Column(db.DateTime, nullable=False, unique=True)
#   db.CheckConstraint('endTime>startTime')


# Show Model 
class Show(db.Model):
  __tablename__= 'shows'
  id = db.Column(db.Integer, primary_key=True)
  artistID = db.Column(db.Integer, db.ForeignKey('artists.id'), nullable=False)
  venueID = db.Column(db.Integer, db.ForeignKey('venues.id'), nullable=False)

  startTime = db.Column(db.DateTime, nullable=False)
  # def __repr__(self):
  #   return f'<Show {self.id} {self.startTime} artistID={artistID} venueID={venueID}>'