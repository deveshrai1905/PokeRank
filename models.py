from extensions import db
from datetime import datetime

# Association table for the many-to-many relationship between Pokemon and Type
pokemon_types = db.Table('pokemon_types',
    db.Column('pokemon_id', db.Integer, db.ForeignKey('pokemon.id'), primary_key=True),
    db.Column('type_id', db.Integer, db.ForeignKey('type.id'), primary_key=True)
)

class Pokemon(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String(100))
    generation = db.Column(db.Integer)  # New field for generation
    elo_rating = db.Column(db.Float, default=1000.0)
    # image_url = db.Column(db.String(200))  # Original image URL (optional)
    sprite_filename = db.Column(db.String(200))  # Filename for local sprite
    types = db.relationship('Type', secondary=pokemon_types, backref=db.backref('pokemon', lazy='dynamic'))

    def __repr__(self):
        return f"<Pokemon {self.name}>"

class Type(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String(50))

    def __repr__(self):
        return f"<Type {self.name}>"

class Match(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    winner_id = db.Column(db.Integer, db.ForeignKey('pokemon.id'))
    loser_id = db.Column(db.Integer, db.ForeignKey('pokemon.id'))
    timestamp = db.Column(db.DateTime, default=datetime.utcnow)

    winner = db.relationship('Pokemon', foreign_keys=[winner_id], backref='wins')
    loser = db.relationship('Pokemon', foreign_keys=[loser_id], backref='losses')

    def __repr__(self):
        return f"<Match {self.winner.name} defeated {self.loser.name}>"
