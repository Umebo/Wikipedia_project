import wikipedia
import pprint
from PIL import Image
from textblob import TextBlob
import glob
import imgcompare
from pymongo import MongoClient

# Podlaczenie do lokalnej bazy danych
client = MongoClient()
db = client.countries


def saving_country_to_db(input_country):
    country = wikipedia.WikipediaPage(input_country).summary
    country_data = {'name': country_name, 'Summary': country}
    db.countries.insert_one(country_data)


def flag_name_from_path(path):
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
            result = (flag_name_from_path(file))
    return result


def phrase_with_tag(country_name, tag):
    whole_text = TextBlob(db.countries.find_one({'name': country_name})['Summary']).sentences
    tagged_phrases = []
    for phrase in whole_text:
        if phrase.find(tag) != -1:
            phrase = str(phrase)
            tagged_phrases.append(phrase)
    return tagged_phrases


##################################################################

flag = Image.open('flag.png').convert('RGB')

country_input = input(' Select country: ')
country_name = wikipedia.WikipediaPage(country_input).title
tag = input(' Lookin\' for sth specific? ')


if country_name != '' and tag == '':
    if db.countries.find({'name': country_name}).count() == 0:
        saving_country_to_db(country_input)
        pprint.pprint((db.countries.find_one({'name': country_name}))['Summary'])
    else:
        print('You have that one already!')
        pprint.pprint((db.countries.find_one({'name': country_name}))['Summary'])
elif country_name != '' and tag != '':
    if db.countries.find({'name': country_name}).count() == 0:
        saving_country_to_db(country_input)
        data = phrase_with_tag(country_name, tag)
        for phrase in data:
            print(phrase)
    else:
        data = phrase_with_tag(country_name, tag)
        for phrase in data:
            print(phrase)
