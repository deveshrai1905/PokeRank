from flask import Flask, render_template, request, jsonify, flash, redirect, url_for
import random
from utils import update_elo_rating
from sqlalchemy import func, desc, over
# from flask_migrate import Migrate
from extensions import db  # Import db from extensions

app = Flask(__name__)
app.secret_key = 'great_key_no?'

# Configure the database URI
app.config['SQLALCHEMY_DATABASE_URI'] = 'sqlite:///pokemon.db'
app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = False

db.init_app(app)  # Initialize db with app
# migrate = Migrate(app, db)

# Import models after db is initialized
from models import Pokemon, Match, GlobalStats

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

    global_stats = GlobalStats.query.first()
    global_stats.total_votes += 1

    db.session.commit()

    return jsonify({'status': 'success'})

@app.route('/skip', methods=['POST'])
def skip():
    selected_generation = request.args.get('generation', type=int)
    return redirect(url_for('index', generation=selected_generation))

def get_page_numbers(current_page, total_pages):
    pages = []
    if total_pages <= 10:
        # If there are 10 or fewer pages, display all page numbers
        pages = list(range(1, total_pages + 1))
    else:
        # Always include the first two pages
        pages.extend([1, 2])

        # Add an ellipsis if the current page is beyond page 5
        if current_page > 5:
            pages.append('...')

        # Determine the range of central pages around the current page
        start = max(3, current_page - 1)
        end = min(total_pages - 2, current_page + 1)
        pages.extend(range(start, end + 1))

        # Add an ellipsis if the current page is at least 4 pages away from the end
        if current_page < total_pages - 4:
            pages.append('...')

        # Always include the last two pages
        pages.extend([total_pages - 1, total_pages])

    # Remove any duplicate page numbers while preserving order
    seen = set()
    unique_pages = []
    for p in pages:
        if p not in seen:
            unique_pages.append(p)
            seen.add(p)
    return unique_pages

@app.route('/leaderboard')
def leaderboard():
    # Get query parameters
    page = request.args.get('page', 1, type=int)
    per_page = 50  # Number of Pokémon per page
    selected_generation = request.args.get('generation', type=int)
    search_query = request.args.get('search', type=str)

    # Base query
    query = Pokemon.query

    if selected_generation:
        query = query.filter(Pokemon.generation == selected_generation)

    found_pokemon_id = request.args.get('found_pokemon_id', type=int)

    if search_query:
        # Find the Pokémon by name (case-insensitive)
        found_pokemon = query.filter(Pokemon.name.ilike(f'{search_query}%')).first()

        if found_pokemon:
            # Build the same ordering as in the leaderboard
            ordered_pokemon = (
                query
                .order_by(Pokemon.elo_rating.desc(), Pokemon.name.asc())
                .with_entities(Pokemon.id)
                .all()
            )

            # Convert list of tuples to list of IDs
            ordered_pokemon_ids = [p.id for p in ordered_pokemon]

            # Find the index of the found Pokémon
            try:
                index = ordered_pokemon_ids.index(found_pokemon.id)
            except ValueError:
                index = None  # This should not happen, but handle it just in case

            if index is not None:
                # Calculate the page number
                page = (index) // per_page + 1
                found_pokemon_id = found_pokemon.id

                # Redirect to the leaderboard without the 'search' parameter
                flash(f'Redirected to page with {search_query.upper()}. Highlighted in yellow.', 'success')
                return redirect(url_for('leaderboard', page=page, generation=selected_generation, found_pokemon_id=found_pokemon_id))
        else:
            # Pokémon not found
            flash(f'{search_query.upper()} not found, back on Page 1.', 'warning')
            return redirect(url_for('leaderboard', generation=selected_generation))

    # Proceed to fetch the Pokémon list
    total_pokemon = query.count()
    total_pages = (total_pokemon + per_page - 1) // per_page  # Ceiling division

    # Ensure the page number is within valid range
    page = max(1, min(page, total_pages))

    # Fetch the Pokémon for the current page, using the same ordering
    pokemon_list = (
        query
        .order_by(Pokemon.elo_rating.desc(), Pokemon.name.asc())
        .limit(per_page)
        .offset((page - 1) * per_page)
        .all()
    )

    # total_votes = Match.query.count()
    global_stats = GlobalStats.query.first()
    total_votes = global_stats.total_votes if global_stats else 0

    # Generate page numbers for pagination
    page_numbers = get_page_numbers(page, total_pages)

    # Render the template with an empty search query
    return render_template(
        'leaderboard.html',
        pokemon_list=pokemon_list,
        page=page,
        total_pages=total_pages,
        per_page=per_page,
        total_votes=total_votes,
        selected_generation=selected_generation,
        available_generations=available_generations,
        total_pokemon=total_pokemon,
        search_query='',  # Clear the search bar
        found_pokemon_id=found_pokemon_id,
        page_numbers=page_numbers
    )

@app.route('/about')
def about():
    return render_template('about.html')

if __name__ == '__main__':
    with app.app_context():
        db.create_all()
        if not GlobalStats.query.first():
            db.session.add(GlobalStats(total_votes=0))
            db.session.commit()
    app.run(debug=True)