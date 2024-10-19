from app import app
from extensions import db
from models import Pokemon
import requests

def populate_pokemon():
    with app.app_context():
        db.create_all()
        response = requests.get('https://pokeapi.co/api/v2/pokemon?limit=151')
        pokemon_list = response.json()['results']

        for poke in pokemon_list:
            name = poke['name'].capitalize()
            poke_data = requests.get(poke['url']).json()
            image_url = poke_data['sprites']['front_default']

            pokemon = Pokemon(name=name, image_url=image_url)
            db.session.add(pokemon)

        db.session.commit()
        print('Database populated with Pokémon.')

if __name__ == '__main__':
    populate_pokemon()
