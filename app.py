import json
import os
from datetime import datetime, timedelta
from flask import Flask, jsonify, render_template, request, flash, redirect, url_for, session
import requests
from bs4 import BeautifulSoup
import logging
from calorie import calculate
from datetime import datetime
from project import get_recipe_data, extract_nutrition_info_from_html
from open import advise

app = Flask(__name__)
app.secret_key = os.urandom(24)  # Replace with a real secret key

logging.basicConfig(level=logging.INFO)

FILENAME = 'menu_data.json'
TIME_RANGE_FOR_SCRAPING = timedelta(days=1)

def calculate_calories(nutrition_info):
    return int(nutrition_info.get('Calories', '0'))

def should_scrape_again():
    if os.path.exists(FILENAME):
        with open(FILENAME, 'r') as file:
            data = json.load(file)
            file_time = datetime.fromisoformat(data['timestamp'])
            if datetime.now() - file_time < TIME_RANGE_FOR_SCRAPING:
                return False
    return True

def scrape_and_save():
    try:
        # Format today's date as YYYY-MM-DD for the URL
        today_date = datetime.now().strftime('%Y-%m-%d')
        url = f'https://dining.rochester.edu/locations/douglass-dining/?date={today_date}'
        response = requests.get(url)
        if response.status_code != 200:
            logging.error(f"Failed to retrieve data, status code {response.status_code}")
            return False

        soup = BeautifulSoup(response.text, 'html.parser')
        menu_items = soup.find_all('li', class_='menu-item-li')
        dish_data = {}
        for item in menu_items:
            dish_name = item.find('a').text.strip()
            ingredients = item['data-searchable']
            recipe_identifier = item.find('a')['data-recipe']
            recipe_data = get_recipe_data(recipe_identifier)
            if recipe_data:
                nutrition_info = extract_nutrition_info_from_html(recipe_data['html'])
                dish_data[dish_name] = {
                    'Ingredients': ingredients,
                    'Nutrition Info': nutrition_info
                }
        with open(FILENAME, 'w') as file:
            json.dump({'timestamp': datetime.now().isoformat(), 'data': dish_data}, file)
        logging.info("Data scraped and saved successfully.")
        return True
    except Exception as e:
        logging.error(f"An error occurred during scraping: {e}")
        return False

height = 0
weight = 0
gender = ""
goal = ""
exercise = ""
Age = 0
calories = 0
goal_calorie = 0
food = ""
Advise = ""

@app.route('/', methods=['GET', 'POST'])
def index():
    global height, weight, gender, goal, age, exercise
    if request.method == 'POST':
        age = request.form.get('age', 0)
        height = request.form.get('height', 0)
        weight = request.form.get('weight', 0)
        gender = request.form.get('gender', '')
        goal = request.form.get('goal', '')
        exercise = request.form.get('exercise', '')
        return redirect(url_for('view_menu'))
    return render_template('index.html')

@app.route('/menu')
def menu():
    if should_scrape_again():
        if not scrape_and_save():
            return jsonify({'error': 'Failed to scrape data'}), 500
    try:
        with open(FILENAME, 'r') as file:
            data = json.load(file)
        dish_names = list(data['data'].keys())
        return jsonify(dish_names)
    except FileNotFoundError:
        logging.error("Data file not found.")
        return jsonify({'error': 'Data not found'}), 404

@app.route('/view-menu', methods=['GET', 'POST'])
def view_menu():
    # Scrape and save if needed, then read the file and render the menu.html template.
    global goal_calorie, calories, food, Advise
    if should_scrape_again():
        scrape_and_save()
        
    if request.method == 'POST':
        if 'clear_button' in request.form:
            food = ""
            calories = 0
        if 'get_advise' in request.form:
            Advise = advise(food, goal_calorie, goal)
            
    try:
        goal_calorie = calculate(float(age), float(height), float(weight), gender, goal, exercise)
        with open(FILENAME, 'r') as file:
            data = json.load(file)
        dish_names = list(data['data'].keys())

        return render_template('menu.html', dish_names=dish_names, session=session,
        a=age, h=height, w=weight, ge=gender, go=goal, e=exercise, c=calories, gc=goal_calorie, f=food, ad=Advise)
    except FileNotFoundError:
        logging.error("Data file not found.")
        return jsonify({'error': 'Data file not found'}), 404

@app.route('/menu/<dish_name>')
def dish_details(dish_name):
    try:
        with open(FILENAME, 'r') as file:
            data = json.load(file)
        dish_info = data['data'].get(dish_name)
        if dish_info:
            calories = calculate_calories(dish_info['Nutrition Info'])
            ingredients = dish_info['Ingredients'].split(', ')
            # Additional nutrition details can be added here if available
            protein = dish_info['Nutrition Info'].get('Protein', 'N/A')
            return render_template('dish_details.html', dish_name=dish_name, ingredients=ingredients, calories=calories, protein=protein)
        else:
            return jsonify({'error': 'Dish not found'}), 404
    except FileNotFoundError:
        return jsonify({'error': 'Data file not found'}), 404


@app.route('/add-dish', methods=['POST'])
def add_dish():
    global calories, food  # Declare that you'll use the global calories variable
    dish_name = request.form['dish_name']
    dish_calories = request.form['calories']  # Get the calories from the form

    # Now update the global calories variable
    calories += int(dish_calories)
    food += f"Dish: {dish_name}, calories: {calories}\n"

    if 'selected_dishes' not in session:
        session['selected_dishes'] = []
    
    # Append the dish to the session
    session['selected_dishes'].append({
        'dish_name': dish_name,
        'calories': int(dish_calories),
    })

    flash('Dish added successfully!')
    return redirect(url_for('view_menu'))


@app.route('/advice', methods=['POST'])
def get_advise():
    # You don't need to get dish_name or dish_calories if you're just giving advice
    # based on the current session state.

    # Get advice using the accumulated food list, the goal calories, and the diet goal
    if 'selected_dishes' in session:
        advice_text = advise(session['selected_dishes'], goal_calorie, goal, age, height, weight, gender, exercise)
    else:
        advice_text = "Please select some dishes first."

    # Flash a message to the user
    flash('Advised successfully!')

    # Store the advice in the session and redirect to the advice display page
    session['advice'] = advice_text
    return redirect(url_for('show_advice'))


@app.route('/show-advice')
def show_advice():
    # Retrieve the advice from the session
    advice_text = session.get('advice', 'No advice to show.')
    # Render the advise.html template with the advice data
    return render_template('advise.html', advice=advice_text)


if __name__ == '__main__':
    app.run(debug=True)





