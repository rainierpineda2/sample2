#!/usr/bin/python
import requests
import json

state = raw_input('Enter state initials: ')
city = raw_input('Enter city: ')
r = requests.get('http://api.zippopotam.us/us/'+state.lower()+'/'+city.lower())
j = r.json()

print json.dumps(j, indent=4)

print j['state']
for each in j['places']:
    print each['latitude']
