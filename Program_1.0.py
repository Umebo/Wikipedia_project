import wikipedia
import pprint
from PIL import Image
import glob
import imgcompare
from pymongo import MongoClient

# Podlaczenie do lokalnej bazy danych
client = MongoClient()
db = client.countries


def SavingCountry(country_input):
    country = wikipedia.WikipediaPage(country_input).summary
    country_data = {'name': country_name, 'Summary': country}
    db.countries.insert_one(country_data)


country_input = input(' Select country: ')
country_name = wikipedia.WikipediaPage(country_input).title


if db.countries.find({'name': country_name}).count() == 0:
    SavingCountry(country_input)
else:
    print('You have that one already!')
    pprint.pprint(db.countries.find_one({'name': country_name}))


flag = Image.open('/home/igor/Documents/Python/GitKraken/Wikipedia_project/flag2.png').convert('RGB')

def FlagName(path):
    flag_name = ''
    for letter in path[len(path)-5::-1]:
        if letter != '/':
            flag_name = flag_name + letter
        else:
            break
    return flag_name[::-1]


for file in glob.glob('/home/igor/Documents/Python/GitKraken/Wikipedia_project/Flags/*.png'):
    test_flag = Image.open(file).resize(flag.size).convert('RGB')
    if imgcompare.is_equal(flag, test_flag, tolerance = 20.0):
        print(FlagName(file))
