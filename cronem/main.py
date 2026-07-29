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

data = fetch_menu(hall, slug , now.strftime('%Y'), now.strftime('%m'), now.strftime('%d'))

today = get_today(data, date)
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

FoodInfo = None

FoodName = None


if MenuVer:
    food = input('Type which item you ate: ')
    if food:
        for item in today.get('menu_items', []):
            if item.get('food') and item['food']['name'] == food.title():
                FoodName = (hall.title() + '-' + food)
                FoodInfo = item['food']['rounded_nutrition_info']
                print(FoodInfo)
                break
        else:
            print("Could not find food item. Please run again and double check spelling!")

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

NumberedFoodInfo = {}
for api_key, page_label in api_to_page_label.items():
    if api_key in FoodInfo and page_label in page_order:
        page_index = page_order.index(page_label)
        NumberedFoodInfo[page_index] = str(FoodInfo[api_key])






