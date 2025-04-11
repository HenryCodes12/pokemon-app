import tkinter as tk
from tkinter import ttk
import requests
from PIL import Image, ImageTk
import io
import pyttsx3
import os

# Function to fetch Pokémon data
def fetch_pokemon(name):
    response = requests.get(f"https://pokeapi.co/api/v2/pokemon/{name}")
    if response.status_code == 200:
        data = response.json()
        pokemon_name = data['name'].capitalize()
        types = ", ".join(t['type']['name'].capitalize() for t in data['types'])
        height = data['height'] / 10  # Convert from decimeters to meters
        weight = data['weight'] / 10  # Convert from hectograms to kilograms
        description = fetch_pokemon_description(name)
        stats = [f"{stat['stat']['name'].capitalize()}: {stat['base_stat']}" for stat in data['stats']]
        sprite_url = data['sprites']['front_default']
        response = requests.get(sprite_url)
        image_data = Image.open(io.BytesIO(response.content))
        image_data = image_data.resize((150, 150))
        img = ImageTk.PhotoImage(image_data)
        img_label.config(image=img)
        img_label.image = img
        result_label.config(text=f"{pokemon_name}\nType: {types}\nHeight: {height} m\nWeight: {weight} kg\nDescription: {description}\nStats: {' | '.join(stats)}")
        
        # Enable text-to-speech button if the Pokémon is valid
        speak_button.config(state=tk.NORMAL)
    else:
        show_question_mark_image()
        result_label.config(text="Pokémon not found")
        
        # Disable text-to-speech button if the Pokémon is not valid
        speak_button.config(state=tk.DISABLED)

# Function to fetch Pokémon description, ensuring it's in English
def fetch_pokemon_description(name):
    response = requests.get(f"https://pokeapi.co/api/v2/pokemon-species/{name}")
    if response.status_code == 200:
        data = response.json()
        # Loop through available descriptions and find the English one
        for entry in data['flavor_text_entries']:
            if entry['language']['name'] == 'en':  # Check for English description
                description = entry['flavor_text']
                return description.replace('\n', ' ').replace('\f', ' ')
    return "No description available"

# Function to fetch and show question mark image when Pokémon is not found
def show_question_mark_image():
    # Get the absolute path of the question mark image
    image_path = os.path.join(os.path.dirname(__file__), "question_mark.png")
    try:
        img = Image.open(image_path)  # Open the image using its absolute path
        img = img.resize((150, 150))  # Resize the image to fit in the window
        img = ImageTk.PhotoImage(img)  # Convert image to Tkinter compatible format
        img_label.config(image=img)  # Update the image on the label
        img_label.image = img  # Keep a reference to the image
    except FileNotFoundError:
        print(f"Image not found at {image_path}")  # Print an error message if the image is not found

# Function to speak the Pokémon's name
def speak_pokemon():
    engine = pyttsx3.init()
    text = dropdown.get().capitalize()  # Use the dropdown to get the selected name
    engine.say(text)
    engine.runAndWait()

# Function to update background image on window resize
def update_background(event):
    bg_image = Image.open(os.path.join(os.path.dirname(__file__), "pokedex_background.png"))
    bg_image = bg_image.resize((event.width, event.height), Image.ANTIALIAS)
    bg_image_tk = ImageTk.PhotoImage(bg_image)
    bg_label.config(image=bg_image_tk)
    bg_label.image = bg_image_tk  # Keep a reference to the image

# Create the main window
root = tk.Tk()
root.title("Pokédex")
root.geometry("600x700")
root.configure(bg="#f0f0f0")  # Light background color for the main window

# Add a background image
bg_image = Image.open(os.path.join(os.path.dirname(__file__), "pokedex_background.png"))
bg_image = bg_image.resize((600, 700), Image.ANTIALIAS)
bg_image_tk = ImageTk.PhotoImage(bg_image)
bg_label = tk.Label(root, image=bg_image_tk)
bg_label.place(x=0, y=0, relwidth=1, relheight=1)

# Bind window resize event to update background
root.bind("<Configure>", update_background)

# Pokémon List (for directory)
pokemon_list = [
    "bulbasaur", "ivysaur", "venusaur", "charmander", "charmeleon", "charizard",
    "squirtle", "wartortle", "blastoise", "pikachu", "raichu", "sandshrew", "sandslash"
]

# Dropdown for Pokémon selection
tk.Label(root, text="Select Pokémon:", font=("Helvetica", 14, "bold"), bg="#f0f0f0").pack(pady=10)
dropdown = ttk.Combobox(root, values=pokemon_list, font=("Helvetica", 12), width=20)
dropdown.pack(pady=10)

# Search Button
search_button = tk.Button(root, text="Search Pokémon", command=lambda: fetch_pokemon(dropdown.get()), font=("Helvetica", 12), bg="#ffcc00", width=15, height=2, relief="raised")
search_button.pack(pady=10)

# Button for text-to-speech, initially disabled
speak_button = tk.Button(root, text="Speak Name", command=speak_pokemon, state=tk.DISABLED, font=("Helvetica", 12), bg="#4CAF50", width=15, height=2, relief="raised")
speak_button.pack(pady=10)

# Image and result labels
img_label = tk.Label(root)
img_label.pack(pady=20)

result_label = tk.Label(root, text="", font=("Helvetica", 12), bg="#f0f0f0", justify="left")
result_label.pack(pady=20)

# Run the application
root.mainloop()
