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
        input_data = eval('{' + (self.path.replace('%22', '"').replace('%20', ' ').replace('%7D', ',').replace('%7B', ': '))[8::] + '}')
        input_data_content = input_data['content']

        if input_data_content.find('country') != -1 and input_data_content.find('tag') != -1:
            country_name = re.search('country\((.*)\);', input_data_content)
            country_name = country_name.group(1)
            tag = re.search('tag\((.*)\)', input_data_content)
            tag = tag.group(1)
            if db.countries.find({'name': country_name}).count() == 0:
                saving_country_to_db(country_name)
                data = phrase_with_tag(country_name, tag)
                for phrase in data:
                    print(phrase)
            else:
                data = phrase_with_tag(country_name, tag)
                for phrase in data:
                    print(phrase)
        elif input_data_content.find('country') != -1 and input_data_content.find('getflag') != -1:
            country_name = re.search('country\((.*)\)', input_data_content)
            country_name = country_name.group(1)
            print('https://en.wikipedia.org/wiki/File:Flag_of_' + country_name + '.svg')
        elif input_data_content.find('country') != -1:
            country_name = re.search('country\((.*)\)', input_data_content)
            country_name = country_name.group(1)
            if db.countries.find({'name': country_name}).count() == 0:
                saving_country_to_db(country_name)
                pprint.pprint((db.countries.find_one({'name': country_name}))['Summary'])
            else:
                print('You have that one already!')
                pprint.pprint((db.countries.find_one({'name': country_name}))['Summary'])
        elif input_data_content.find('checkflag') != -1:
            link_to_flag = re.search('checkflag\((.*)\)', input_data_content)
            link_to_flag = link_to_flag.group(1)
            urllib.request.urlretrieve(link_to_flag, 'flag.png')
            flag = Image.open('flag.png').convert('RGB')
            print(comparing_flags(flag))


def run():
    server_address = ('localhost', 9901)
    httpd = HTTPServer(server_address, WikiHandler)
    try:
        httpd.serve_forever()
    except KeyboardInterrupt:
        pass
    httpd.server_close()


def saving_country_to_db(input_country):
    country_name = input_country
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


#################################################################

run()
