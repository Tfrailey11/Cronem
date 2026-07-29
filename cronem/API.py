import requests
import json

HALLS = {
        '1': 'garnet-station',
        '2': 'fresh-greenes',
        '3': 'gibbes-court-bistro',
        '4': 'honeycomb-cafe',
        '5': 'the-community-table',
        '6': 'the-pavillion'
}

def Hallsel():
    print('USC Dining Halls: ')
    print('1: Garnet Station')
    print('2: Fresh Greenes')
    print('3: Gibbes Court Bistro')
    print('4: Honeycomb Cafe')
    print('5: The Community Table')
    print('6: The Pavilion')
    choice = input('Enter the number of the dining hall you ate at: ')
    return HALLS.get(choice)


def fetch_menu(hall, menu_slug, year, month, day):
    url = (
            f"https://sc.api.nutrislice.com/menu/api/weeks/school/{hall}/"
            f"menu-type/{menu_slug}/{year}/{month}/{day}/?format=json"
        )


    response = requests.get(url)

    return response.json()

def get_today(data, date):
    for day in data.get('days', []):
        day_date = day.get('date')
        #print(f'Comparing: {repr(day_date)} == {repr(date)} = {day_date == date}')
        if day_date == date:
            print(f'Today returned date: {day_date}')
            return day
    return None



