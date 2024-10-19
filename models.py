from extensions import db  # Import db from extensions
from datetime import datetime

class Pokemon(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String(100))
    elo_rating = db.Column(db.Float, default=1000.0)
    image_url = db.Column(db.String(200))

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
        return f"<Match {self.winner_id} defeated {self.loser_id}>"
