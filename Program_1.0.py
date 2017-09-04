import wikipedia
import pprint
import imgcompare
from pymongo import MongoClient

# Podlaczenie do lokalnej bazy danych
client = MongoClient()
db = client.countries

def saving_country(country_input):
    country = wikipedia.WikipediaPage(country_input).summary
    country_data = {'name': country_name, 'Summary': country}
    db.countries.insert_one(country_data)


country_input = input(' Select country: ')
country_name = wikipedia.WikipediaPage(country_input).title


if db.countries.find({'name': country_name}).count() == 0:
    saving_country(country_input)
else:
    print('You have that one already!')
    pprint.pprint(db.countries.find_one({'name': country_name}))


same = imgcompare.is_equal('/home/igor/Documents/Python/GitKraken/Wikipedia_project/flag.png',
                          ('/home/igor/Documents/Python/GitKraken/Wikipedia_project/Flags/' + country_name + '.png'),
                           tolerance = 2.5)