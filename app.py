from flask import Flask, render_template, request, jsonify, url_for, redirect
import requests
from PIL import Image
import io
import pyttsx3
import os
import json
import random


app = Flask(__name__)

POKEMON_API_URL = "https://pokeapi.co/api/v2/pokemon/"

# Function to fetch all Pokémon and organize by type
def fetch_pokemon_glossary():
    url = "https://pokeapi.co/api/v2/type/"
    response = requests.get(url)
    if response.status_code == 200:
        types_data = response.json()["results"]
        glossary = {}

        for type_info in types_data:
            type_name = type_info["name"].capitalize()
            type_url = type_info["url"]

            type_response = requests.get(type_url)
            if type_response.status_code == 200:
                pokemon_list = type_response.json()["pokemon"]
                glossary[type_name] = sorted(
                    [entry["pokemon"]["name"].capitalize() for entry in pokemon_list]
                )

        return glossary
    return {}

@app.route("/quiz")
def quiz():
    return render_template("quiz.html")

@app.route("/get_quiz_questions")
def get_quiz_questions():
    # Fetch the list of Pokémon from your API
    response = requests.get("https://pokeapi.co/api/v2/pokemon?limit=1000")
    
    if response.status_code != 200:
        return jsonify({"error": "Failed to fetch Pokémon data"}), 500
    
    all_pokemon = response.json()["results"]
    pokemon_list = [p["name"] for p in all_pokemon]

    questions = []
    for _ in range(10):
        correct_pokemon = random.choice(pokemon_list)
        wrong_choices = random.sample([p for p in pokemon_list if p != correct_pokemon], 3)

        # Fetch correct Pokémon data
        correct_pokemon_data = requests.get(f"https://pokeapi.co/api/v2/pokemon/{correct_pokemon}").json()
        correct_image = correct_pokemon_data["sprites"]["other"]["official-artwork"]["front_default"]

        choices = [{"name": correct_pokemon, "image": correct_image}]

        for wrong in wrong_choices:
            wrong_pokemon_data = requests.get(f"https://pokeapi.co/api/v2/pokemon/{wrong}").json()
            wrong_image = wrong_pokemon_data["sprites"]["other"]["official-artwork"]["front_default"]
            choices.append({"name": wrong, "image": wrong_image})

        random.shuffle(choices)

        questions.append({
            "name": correct_pokemon,
            "correct_image": correct_image,
            "choices": choices
        })

    return jsonify(questions)

@app.route("/")
def homepage():
    return render_template("home.html")

@app.route("/random")
def random_pokemon():
    random_id = random.randint(1, 898)  # Get a random Pokémon ID
    response = requests.get(f"{POKEMON_API_URL}{random_id}")  # Fetch Pokémon details

    if response.status_code == 200:
        pokemon = response.json()
        pokemon_name = pokemon["name"]  # Extract Pokémon name
        return redirect(url_for("pokemon_details", name=pokemon_name))

    return "Pokémon not found", 404  # Handle errors just in case


@app.route("/pokemon/<name>")
def pokemon_details(name):
    response = requests.get(f"{POKEMON_API_URL}{name.lower()}")
    if response.status_code == 200:
        pokemon = response.json()
        return render_template("pokemon_details.html", pokemon=pokemon)
    return "Pokémon not found", 404

@app.route("/pokedex")
def pokedex():
    return render_template("index.html")

@app.route("/glossary")
def glossary():
    glossary_data = fetch_pokemon_glossary()  # Fetch glossary data
    types = list(glossary_data.keys())  # Extract all Pokémon types
    return render_template("glossary.html", types=types)

@app.route("/glossary/<type>")
def glossary_type(type):
    glossary_data = fetch_pokemon_glossary()
    pokemons = glossary_data.get(type, [])  # Get Pokémon of selected type
    return render_template("glossary_type.html", type=type, pokemons=pokemons)

@app.route("/pokedex/<name>")
def pokedex_pokemon(name):

    response = requests.get(f"https://pokeapi.co/api/v2/pokemon/{name.lower()}")
    if response.status_code == 200:
        data = response.json()
        pokemon_name = data['name'].capitalize()
        types = ", ".join(t['type']['name'].capitalize() for t in data['types'])
        height = f"{data['height'] / 10}"  # Convert to string without adding "m"
        weight = f"{data['weight'] / 10}"  # Convert to string without adding "kg"


        description = fetch_pokemon_description(name)
        stats = "<br>".join(f"{stat['stat']['name'].capitalize()}: {stat['base_stat']}" for stat in data['stats'])

        sprite_url = data['sprites']['front_default'] if data['sprites']['front_default'] else "/static/question_mark.png"


        return {
            "name": pokemon_name,
            "types": types,
            "height": f"{height}",
            "weight": f"{weight}",
            "description": description,
            "stats": stats,
            "image": sprite_url
        }
    else:
        return {
            "name": "Pokémon Not Found",
            "types": "Unknown",
            "height": "-",
            "weight": "-",
            "description": "No description available.",
            "stats": "No stats available.",
            "image": url_for('static', filename='question_mark.png')
        }

# Function to fetch Pokémon data
def fetch_pokemon(name):
    response = requests.get(f"https://pokeapi.co/api/v2/pokemon/{name.lower()}")
    if response.status_code == 200:
        data = response.json()
        pokemon_name = data['name'].capitalize()
        types = ", ".join(t['type']['name'].capitalize() for t in data['types'])
        height = f"{data['height'] / 10}"  # Convert to string without adding "m"
        weight = f"{data['weight'] / 10}"  # Convert to string without adding "kg"


        description = fetch_pokemon_description(name)
        stats = "<br>".join(f"{stat['stat']['name'].capitalize()}: {stat['base_stat']}" for stat in data['stats'])

        sprite_url = data['sprites']['front_default'] if data['sprites']['front_default'] else "/static/question_mark.png"


        return {
            "name": pokemon_name,
            "types": types,
            "height": f"{height}",
            "weight": f"{weight}",
            "description": description,
            "stats": stats,
            "image": sprite_url
        }
    else:
        return {
            "name": "Pokémon Not Found",
            "types": "Unknown",
            "height": "-",
            "weight": "-",
            "description": "No description available.",
            "stats": "No stats available.",
            "image": url_for('static', filename='question_mark.png')
        }


# Function to fetch Pokémon description
def fetch_pokemon_description(name):
    response = requests.get(f"https://pokeapi.co/api/v2/pokemon-species/{name.lower()}")
    if response.status_code == 200:
        data = response.json()
        for entry in data['flavor_text_entries']:
            if entry['language']['name'] == 'en':
                return entry['flavor_text'].replace("\n", " ").replace("\f", " ")
    return "No description available"

# Text-to-speech function
def speak_pokemon(name):
    engine = pyttsx3.init()
    engine.say(name.capitalize())
    engine.runAndWait()

@app.route("/")
def home():
    return render_template("index.html")

@app.route("/search", methods=["POST"])
def search():
    data = request.get_json()
    pokemon_name = data.get("name", "").strip().lower()

    if not pokemon_name:
        return jsonify({"error": "No Pokémon name provided"}), 400

    pokemon_data = fetch_pokemon(pokemon_name)
    
    if not pokemon_data:
        return jsonify({"error": "Pokémon not found"}), 404

    return jsonify(pokemon_data)


@app.route("/speak", methods=["POST"])
def speak():
    pokemon_name = request.form.get("pokemon_name")
    speak_pokemon(pokemon_name)
    return jsonify({"message": "Speaking"}), 200


if __name__ == "__main__":
    app.run(debug=True)
