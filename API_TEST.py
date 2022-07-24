import requests
import re

id = 52878
url = f"https://www.themealdb.com/api/json/v1/1/lookup.php?i={id}"
response = requests.get(url)
response.raise_for_status()

meals = response.json()['meals']

print(len(meals))
for meal in meals:
    print(meal['strInstructions'].replace('. ', '.\n'))
    print()
    for i in range(1,21):
        if meal['strIngredient'+str(i)] != '' and meal['strIngredient'+str(i)] != None:
            print(meal['strIngredient'+str(i)] +' - '+ meal['strMeasure'+str(i)])
    print()
