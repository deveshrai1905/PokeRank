from extensions import db
from datetime import datetime

class Pokemon(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String(100))
    generation = db.Column(db.Integer)  # New field for generation
    elo_rating = db.Column(db.Float, default=1000.0)
    # image_url = db.Column(db.String(200))  # Original image URL (optional)
    sprite_filename = db.Column(db.String(200))  # Filename for local sprite

    def __repr__(self):
        return f"<Pokemon {self.name}>"

class Match(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    winner_id = db.Column(db.Integer, db.ForeignKey('pokemon.id'))
    loser_id = db.Column(db.Integer, db.ForeignKey('pokemon.id'))
    timestamp = db.Column(db.DateTime, default=datetime.utcnow)

    winner = db.relationship('Pokemon', foreign_keys=[winner_id], backref='wins')
    loser = db.relationship('Pokemon', foreign_keys=[loser_id], backref='losses')

    def __repr__(self):
        return f"<Match {self.winner.name} defeated {self.loser.name}>"

class GlobalStats(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    total_votes = db.Column(db.Integer, default=0)