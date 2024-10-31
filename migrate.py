# from sqlalchemy import create_engine, MetaData, Table
# from sqlalchemy.orm import sessionmaker
# import os
# from dotenv import load_dotenv
# from flask import Flask
# from extensions import db
# from models import Pokemon, GlobalStats

# load_dotenv()

# # Set up Flask app
# app = Flask(__name__)
# app.secret_key = 'great_key_no?'

# # Configure the database URI for PostgreSQL
# app.config['SQLALCHEMY_DATABASE_URI'] = os.getenv('DATABASE_URI')
# if not app.config['SQLALCHEMY_DATABASE_URI']:
#     raise ValueError("DATABASE_URI environment variable is not set.")
# app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = False

# # Initialize the database
# db.init_app(app)

# # Set up SQLite connection
# sqlite_uri = 'sqlite:///instance/pokemon.db'
# sqlite_engine = create_engine(sqlite_uri)
# sqlite_connection = sqlite_engine.connect()

# # Set up PostgreSQL connection
# postgres_uri = os.getenv('DATABASE_URI')
# if not postgres_uri:
#     raise ValueError("DATABASE_URI environment variable is not set.")
# postgres_engine = create_engine(postgres_uri)
# Session = sessionmaker(bind=postgres_engine)
# postgres_session = Session()

# # Load metadata for SQLite
# metadata = MetaData()
# metadata.reflect(bind=sqlite_engine)

# # Define SQLite tables
# pokemon_table = Table('pokemon', metadata, autoload_with=sqlite_engine)
# global_stats_table = Table('global_stats', metadata, autoload_with=sqlite_engine)

# # Data Migration Function
# def migrate_data():
#     # Migrate Pokemon
#     sqlite_pokemon = sqlite_connection.execute(pokemon_table.select()).fetchall()
#     for pokemon_row in sqlite_pokemon:
#         # Check if the Pokemon already exists in PostgreSQL
#         existing_pokemon = postgres_session.query(Pokemon).filter_by(id=pokemon_row.id).first()
#         if existing_pokemon:
#             # Update existing record
#             existing_pokemon.name = pokemon_row.name
#             existing_pokemon.generation = pokemon_row.generation
#             existing_pokemon.elo_rating = pokemon_row.elo_rating
#             existing_pokemon.sprite_filename = pokemon_row.sprite_filename
#         else:
#             # Add new Pokemon
#             pokemon_obj = Pokemon(
#                 id=pokemon_row.id,
#                 name=pokemon_row.name,
#                 generation=pokemon_row.generation,
#                 elo_rating=pokemon_row.elo_rating,
#                 sprite_filename=pokemon_row.sprite_filename,
#             )
#             postgres_session.add(pokemon_obj)
    
#     # Migrate GlobalStats
#     sqlite_global_stats = sqlite_connection.execute(global_stats_table.select()).fetchall()
#     for stats_row in sqlite_global_stats:
#         global_stats_obj = GlobalStats(
#             id=stats_row.id,
#             total_votes=stats_row.total_votes
#         )
#         postgres_session.merge(global_stats_obj)  # Use merge to append or update
    
#     # Commit all changes
#     postgres_session.commit()
#     print("Data migration completed successfully.")

# if __name__ == '__main__':
#     with app.app_context():
#         db.create_all()  # Ensure PostgreSQL tables are created
#         migrate_data()