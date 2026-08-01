from datetime import datetime
from . API import Hallsel, fetch_menu, get_today
import json

now = datetime.now()
date = now.strftime('%Y-%m-%d')
hour = int(now.strftime('%H'))

def menu_slug(hour):
    if 6 <= hour < 12:
        return 'breakfast'
    elif 12 <= hour <18:
        return 'lunch'
    else:
        return 'dinner'

slug = menu_slug(hour)
hall = Hallsel()
print(f'hall: {hall}')

data = fetch_menu(hall, slug, now.strftime('%Y'), now.strftime('%m'), now.strftime('%d'))
test_date = now.strftime('2026-07-30')

today = get_today(data, test_date)
print(f'Todays date: {date}')
print(f'Today found: {today is not None}')

MenuVer = True

if today:
    for item in today.get('menu_items', []):
        if item.get('food'):
            print(item['food']['name'])
else:
    print('No menu found for today')
    MenuVer = False





if MenuVer:
    
    todays_food_names = {
            item['food']['name'].title()
            for item in today.get('menu_items', [])
            if item.get('food')
    }

    name_to_info = {
            item['food']['name'].title() : item['food']['rounded_nutrition_info']
            for item in today.get('menu_items', [])
            if item.get('food')
    }

    foods = input('Type which item/s you ate, for multiple items seperate them with a comma: ')
    FoodInfo = {}
    if foods:
        food_list = [item.strip().title() for item in foods.split(',')]

        for food in food_list:
            if food in todays_food_names:
                FoodInfo[food] = name_to_info[food]
                

api_to_page_label = {
    'calories': 'Calories',
    'g_fat': 'Total Fat: g',
    'g_saturated_fat': 'Saturated Fat: g',
    'g_trans_fat': 'Trans Fat: g',
    'mg_cholesterol': 'Cholesterol: g',
    'g_carbs': 'Total Carbohydrate: g',
    'g_added_sugar': 'Added Sugars: g',
    'g_sugar': 'Total Sugars: g',
    'mg_potassium': 'Potassium: g',
    'mg_sodium': 'Sodium: g',
    'g_fiber': 'Dietary Fiber: g',
    'g_protein': 'Protein: g',
    'mg_iron': 'Iron: g',
    'mg_calcium': 'Calcium: g',
    'mcg_vitamin_d': 'Vitamin D: g',
}

page_order = [
    'Calories',
    'Total Fat: g', 'Total Fat: dv',
    'Saturated Fat: g', 'Saturated Fat: dv',
    'Trans Fat: g',
    'Cholesterol: g', 'Cholesterol: dv',
    'Sodium: g', 'Sodium: dv',
    'Total Carbohydrate: g', 'Total Carbohydrate: dv',
    'Dietary Fiber: g', 'Dietary Fiber: dv',
    'Total Sugars: g',
    'Added Sugars: g', 'Added Sugars: dv',
    'Protein: g',
    'Vitamin D: g', 'Vitamin D: dv',
    'Calcium: g', 'Calcium: dv',
    'Iron: g', 'Iron: dv',
    'Potassium: g', 'Potassium: dv'
]

AllNumberedFoodInfo = {}
for food_name, nutrition in FoodInfo.items():
    numbered = {}
    for api_key, page_label in api_to_page_label.items():
        if api_key in nutrition and page_label in page_order:
            page_index = page_order.index(page_label)
            numbered[page_index] = str(nutrition[api_key])
    AllNumberedFoodInfo[food_name] = numbered





