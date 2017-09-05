import wikipedia
import pprint
from PIL import Image
import glob
import imgcompare
from pymongo import MongoClient

# Podlaczenie do lokalnej bazy danych
client = MongoClient()
db = client.countries


def saving_country_to_db(country_input):
    country = wikipedia.WikipediaPage(country_input).summary
    country_data = {'name': country_name, 'Summary': country}
    db.countries.insert_one(country_data)


country_input = input(' Select country: ')
country_name = wikipedia.WikipediaPage(country_input).title


if db.countries.find({'name': country_name}).count() == 0:
    saving_country_to_db(country_input)
else:
    print('You have that one already!')
    pprint.pprint(db.countries.find_one({'name': country_name}))

###################################################

flag = Image.open('flag.png').convert('RGB')

def flag_name(path):
    flag_name = ''
    for letter in path[len(path)-5::-1]:
        if letter != '/':
            flag_name = flag_name + letter
        else:
            return flag_name[::-1]

def comparing_flags(input_flag):
    difference = 30.0
    for file in glob.glob('Flags/*.png'):
        test_flag = Image.open(file).resize(input_flag.size).convert('RGB')
        percentage = imgcompare.image_diff_percent(test_flag, input_flag)
        if percentage < difference:
            result = (flag_name(file))
    return result

print(comparing_flags(flag))