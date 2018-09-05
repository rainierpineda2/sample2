#!/usr/bin/python
import requests
import json

r = requests.get('http://api.zippopotam.us/us/ma/belmont')
j = r.json()

print json.dumps(j, indent=4)

print j['state']
for each in j['places']:
    print each['latitude']
