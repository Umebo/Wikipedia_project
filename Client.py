import requests
import json

host_name = 'localhost'
post_number = 9901

#
data = {'address':    host_name,
        'port':       post_number,
        'type':       'text',
        'content':    'country(Peru);tag(rainforest)'}

dest = 'http://localhost:9901'
headers = {'content-type': 'application/json'}

r = requests.post('http://localhost:9901/post', params=json.dumps(data), headers=headers)
