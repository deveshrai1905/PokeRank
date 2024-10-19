from flask import Flask, render_template, request, jsonify
import random
from utils import update_elo_rating
# from flask_migrate import Migrate
from extensions import db  # Import db from extensions

app = Flask(__name__)

# Configure the database URI
app.config['SQLALCHEMY_DATABASE_URI'] = 'sqlite:///pokemon.db'
app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = False

db.init_app(app)  # Initialize db with app
# migrate = Migrate(app, db)

# Import models after db is initialized
from models import Pokemon, Match

available_generations = [1,2,3,4,5,6,7,8,9]

@app.route('/')
def index(generation=None):


    selected_generation = request.args.get('generation', type=int)
    if selected_generation:
        pokemon_list = Pokemon.query.filter_by(generation=selected_generation).all()
    else:
        pokemon_list = Pokemon.query.all()

    pokemon_ids = [pokemon.id for pokemon in pokemon_list]
    pokemon1_id = random.choice(pokemon_ids)
    pokemon2_id = random.choice(pokemon_ids)
    while pokemon2_id == pokemon1_id:
        pokemon2_id = random.choice(pokemon_ids)

    pokemon1 = Pokemon.query.get(pokemon1_id)
    pokemon2 = Pokemon.query.get(pokemon2_id)

    return render_template('index.html', 
                           pokemon1=pokemon1, 
                           pokemon2=pokemon2,
                           available_generations=available_generations,
                           selected_generation=selected_generation)

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

    selected_generation = request.args.get('generation', type=int)

    query = Pokemon.query

    if selected_generation:
        query = query.filter(Pokemon.generation == selected_generation)
        

    # Query the total number of Pokémon
    total_pokemon = query.count()

    # Calculate the total number of pages
    total_pages = (total_pokemon + per_page - 1) // per_page  # Ceiling division

    # Ensure the page number is within valid range
    if page < 1:
        page = 1
    elif page > total_pages:
        page = total_pages

    # Fetch the Pokémon for the current page
    pokemon_list = (
        query
        .order_by(Pokemon.elo_rating.desc())
        .limit(per_page)
        .offset((page - 1) * per_page)
        .all()
    )

    total_votes = Match.query.count()

    # Pass pagination info to the template
    return render_template(
        'leaderboard.html',
        pokemon_list=pokemon_list,
        page=page,
        total_pages=total_pages,
        per_page=per_page,
        total_votes=total_votes,
        selected_generation=selected_generation,
        available_generations=available_generations,
        total_pokemon=total_pokemon
    )

if __name__ == '__main__':
    with app.app_context():
        db.create_all()
    app.run(debug=True)
