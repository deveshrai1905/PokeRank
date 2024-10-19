from flask import Flask, render_template, request, jsonify
import random
from utils import update_elo_rating
from extensions import db  # Import db from extensions

app = Flask(__name__)

# Configure the database URI
app.config['SQLALCHEMY_DATABASE_URI'] = 'sqlite:///pokemon.db'
app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = False

db.init_app(app)  # Initialize db with app

# Import models after db is initialized
from models import Pokemon, Match

@app.route('/')
def index():
    pokemon_ids = [pokemon.id for pokemon in Pokemon.query.all()]
    pokemon1_id = random.choice(pokemon_ids)
    pokemon2_id = random.choice(pokemon_ids)
    while pokemon2_id == pokemon1_id:
        pokemon2_id = random.choice(pokemon_ids)

    pokemon1 = Pokemon.query.get(pokemon1_id)
    pokemon2 = Pokemon.query.get(pokemon2_id)

    return render_template('index.html', pokemon1=pokemon1, pokemon2=pokemon2)

@app.route('/choose', methods=['POST'])
def choose():
    data = request.get_json()
    winner_id = data.get('winner_id')
    loser_id = data.get('loser_id')

    winner = Pokemon.query.get(winner_id)
    loser = Pokemon.query.get(loser_id)

    if not winner or not loser:
        return jsonify({'status': 'error', 'message': 'Invalid Pokémon selected.'})

    winner_new_rating, loser_new_rating = update_elo_rating(winner.elo_rating, loser.elo_rating)

    winner.elo_rating = winner_new_rating
    loser.elo_rating = loser_new_rating

    db.session.add(Match(winner_id=winner.id, loser_id=loser.id))
    db.session.commit()

    return jsonify({'status': 'success'})

@app.route('/leaderboard')
def leaderboard():
    # Get the page number from the query parameters, default to 1
    page = request.args.get('page', 1, type=int)
    per_page = 50  # Number of Pokémon to display per page

    # Query the total number of Pokémon
    total_pokemon = Pokemon.query.count()

    # Calculate the total number of pages
    total_pages = (total_pokemon + per_page - 1) // per_page  # Ceiling division

    # Ensure the page number is within valid range
    if page < 1:
        page = 1
    elif page > total_pages:
        page = total_pages

    # Fetch the Pokémon for the current page
    pokemon_list = (
        Pokemon.query
        .order_by(Pokemon.elo_rating.desc())
        .limit(per_page)
        .offset((page - 1) * per_page)
        .all()
    )

    # Pass pagination info to the template
    return render_template(
        'leaderboard.html',
        pokemon_list=pokemon_list,
        page=page,
        total_pages=total_pages,
        per_page=per_page
    )

if __name__ == '__main__':
    with app.app_context():
        db.create_all()
    app.run(debug=True)
