import wikipedia
import pprint
import requests
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
    most_similar_flag = ''
    for file in glob.glob('Flags/*.png'):
        test_flag = Image.open(file).resize(input_flag.size).convert('RGB')
        percentage = imgcompare.image_diff_percent(test_flag, input_flag)
        if percentage < difference:
            most_similar_flag = (flag_name_from_path(file))
            difference = percentage
    return most_similar_flag


def phrase_with_tag(country, tagged_word):
    whole_country_summary = TextBlob(db.countries.find_one({'name': country})['Summary']).sentences
    tagged_phrases = []
    for sentence in whole_country_summary:
        if sentence.find(tagged_word) != -1:
            sentence = str(sentence)
            tagged_phrases.append(sentence)
    return tagged_phrases


##################################################################

while True:
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
    elif country_name != '' and tag == 'getflag':
        print('https://en.wikipedia.org/wiki/File:Flag_of_' + country_name + '.svg')
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
