from app import app
from extensions import db
from models import Pokemon, Type
import requests
import os

def populate_pokemon():
    with app.app_context():
        db.create_all()

        # Fetch existing types
        existing_types = {t.name: t for t in Type.query.all()}

        # Create directory for sprites if it doesn't exist
        sprite_dir = os.path.join('static', 'sprites')
        if not os.path.exists(sprite_dir):
            os.makedirs(sprite_dir)

        # Fetch the list of Pokémon
        response = requests.get('https://pokeapi.co/api/v2/pokemon?limit=10000')
        if response.status_code != 200:
            print('Error fetching Pokémon list')
            return
        pokemon_list = response.json()['results']
        print(pokemon_list)
        for poke in pokemon_list:
            # Fetch detailed Pokémon data
            poke_data = requests.get(poke['url']).json()
            name = poke['name'].capitalize()
            image_url = poke_data['sprites']['front_default']
            types = [t['type']['name'].capitalize() for t in poke_data['types']]

            # Fetch generation information
            species_data = requests.get(poke_data['species']['url']).json()
            generation_url = species_data['generation']['url']
            generation_number = int(generation_url.strip('/').split('/')[-1])


            # Add types to the database if they don't exist
            type_objects = []
            for type_name in types:
                type_obj = existing_types.get(type_name)
                if not type_obj:
                    type_obj = Type(name=type_name)
                    db.session.add(type_obj)
                    db.session.flush()
                    existing_types[type_name] = type_obj
                type_objects.append(type_obj)

            # Download sprite and store it locally
            if image_url:
                sprite_response = requests.get(image_url)
                if sprite_response.status_code == 200:
                    sprite_filename = f"{poke_data['id']}.png"
                    sprite_path = os.path.join(sprite_dir, sprite_filename)
                    with open(sprite_path, 'wb') as f:
                        f.write(sprite_response.content)
                else:
                    sprite_filename = None
            else:
                sprite_filename = None

            # Create a new Pokémon instance
            pokemon = Pokemon(
                name=name,
                generation=generation_number,
                # image_url=image_url,
                sprite_filename=sprite_filename
            )
            pokemon.types.extend(type_objects)
            db.session.add(pokemon)

        db.session.commit()
        print('Database populated with Pokémon.')

if __name__ == '__main__':
    populate_pokemon()
