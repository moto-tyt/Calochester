import requests
from bs4 import BeautifulSoup
import re

# Function to retrieve recipe data using the identifier
def get_recipe_data(identifier):
    api_url = f"https://dining.rochester.edu/wp-content/themes/nmc_dining/ajax-content/recipe.php?recipe={identifier}"
    response = requests.get(api_url)
    if response.status_code == 200:
        try:
            data = response.json()
            return data
        except ValueError:
            print("Error: Unable to parse JSON response")
            return None
    else:
        print(f"Error: Failed to retrieve data, status code {response.status_code}")
        return None

# Function to extract nutrition information from HTML content
def extract_nutrition_info_from_html(html_content):
    soup = BeautifulSoup(html_content, 'html.parser')
    nutrition_info = {}

    # Find allergens
    allergens_header = soup.find('h6', string='Allergens')
    if allergens_header and allergens_header.find_next_sibling('p'):
        allergens = allergens_header.find_next_sibling('p').text.strip()
    else:
        allergens = 'No allergens listed'
    nutrition_info['Allergens'] = allergens

    # Find calories
    calories_info = soup.find('b', string='Calories')
    if calories_info and calories_info.parent:
        calories_text = calories_info.parent.get_text(strip=True)
        calories_match = re.search(r'\d+', calories_text)
        calories = calories_match.group(0) if calories_match else 'Calories not listed'
    else:
        calories = 'Calories not listed'
    nutrition_info['Calories'] = calories

    # Find protein
    protein_info = soup.find('b', string='Protein')
    if protein_info and protein_info.parent:
        protein_text = protein_info.parent.get_text(strip=True)
        protein_match = re.search(r'\d+', protein_text)
        protein = protein_match.group(0) if protein_match else 'Protein not listed'
    else:
        protein = 'Protein not listed'
    nutrition_info['Protein'] = protein

    return nutrition_info

# URL of the page to scrape
url = 'https://dining.rochester.edu/locations/douglass-dining/?date=2023-11-04'
response = requests.get(url)
soup = BeautifulSoup(response.text, 'html.parser')
menu_items = soup.find_all('li', class_='menu-item-li')

# Dictionary to store all the dish data
dish_data = {}

# Loop over each item and extract data
for item in menu_items:
    dish_name = item.find('a').text.strip()
    ingredients = item['data-searchable']
    recipe_identifier = item.find('a')['data-recipe']

    # Retrieve the recipe data using the identifier
    recipe_data = get_recipe_data(recipe_identifier)
    
    if recipe_data:
        # Extract the nutrition information
        nutrition_info = extract_nutrition_info_from_html(recipe_data['html'])
        
        # Store the data in the dish_data dictionary
        dish_data[dish_name] = {
            'Ingredients': ingredients,
            'Nutrition Info': nutrition_info
        }



