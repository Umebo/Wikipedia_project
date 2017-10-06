import wikipedia
import pprint
import requests
import json
import re
import urllib.request
from http.server import BaseHTTPRequestHandler, HTTPServer
from PIL import Image
from textblob import TextBlob
import glob
import imgcompare
from pymongo import MongoClient

# Podlaczenie do lokalnej bazy danych
client = MongoClient()
db = client.countries

host_name = 'localhost'
post_number = 9901


class WikiHandler(BaseHTTPRequestHandler):
    def do_POST(self):
        self.send_response(200)
        self.end_headers()
        input_data = eval('{' + (self.path.replace('%22', '"').replace('%20', ' ')
                                 .replace('%7D', ',').replace('%7B', ': '))[8::] + '}')
        input_data_content = input_data['content']
        pprint.pprint(downloading_content(input_data_content))


def run():
    server_address = ('localhost', 9901)
    httpd = HTTPServer(server_address, WikiHandler)
    try:
        httpd.serve_forever()
    except KeyboardInterrupt:
        pass
    httpd.server_close()


def country_name_from_content(content):
    if content.find('tag') != -1:
        return re.search('country\((.*)\);', content).group(1)
    elif content.find('checkflag') != -1:
        return re.search('checkflag\((.*)\)', content).group(1)
    else:
        return re.search('country\((.*)\)', content).group(1)


def saving_country_to_db(input_country):
    country = wikipedia.WikipediaPage(input_country).summary
    country_data = {'name': input_country, 'Summary': country}
    db.countries.insert_one(country_data)


def whole_country_summary(input_country):
    if db.countries.find({'name': input_country}).count() == 0:
        saving_country_to_db(input_country)
    else:
        print('You have that one already!')
    return (db.countries.find_one({'name': input_country}))['Summary']


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
    if db.countries.find({'name': country}).count() == 0:
        saving_country_to_db(country)
    tagged_phrases = []
    for sentence in TextBlob(db.countries.find_one({'name': country})['Summary']).sentences:
        if sentence.find(tagged_word) != -1:
            tagged_phrases.append(str(sentence))
    return tagged_phrases


def downloading_content(chosen_data):
    country_name = country_name_from_content(chosen_data)
    if chosen_data.find('tag') != -1:
        tag = re.search('tag\((.*)\)', chosen_data).group(1)
        return phrase_with_tag(country_name, tag)
    elif chosen_data.find('getflag') != -1:
        return 'https://en.wikipedia.org/wiki/File:Flag_of_' + country_name + '.svg'
    elif chosen_data.find('country') != -1:
        return whole_country_summary(country_name)
    elif chosen_data.find('checkflag') != -1:
        urllib.request.urlretrieve(country_name, 'flag.png')
        flag = Image.open('flag.png').convert('RGB')
        return comparing_flags(flag)
    else:
        print('Something went wrong.')


#################################################################

run()
