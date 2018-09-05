#!/usr/bin/env python
"""
This module will allow us to reuse the same functions across all of the code to make it more centralized
It will provide the connector to mongodb and the an easy way to loadeggs of python packages
"""

import os, sys, json, cgi, cgitb
import jinja2, datetime
import pymongo, bson.json_util
from bson.objectid import ObjectId

def connectDB():
    #serverName = '10.28.13.25'
    serverName = 'itsusralsp06447.jnj.com'
    uri = "mongodb://networkInvAdmin:supp0rtM3@%s:27017/networkInv" % serverName
    try:
        # Connect to Server and DB named 'networkInv'
        m = pymongo.MongoClient(uri)
        db = m.networkInv
    except pymongo.errors.ConnectionFailure, e:
        sys.stderr.write("save(): Could not connect to MongoDB: %s" % e)
        sys.exit(2)
        # we will update the collection named 'ansInventory'
    return db

def loadeggs(dir):
    """
    Add 3rd party modules packed as eggs to sys.path.
    Parameter d is either a directory or list of directories.
    """
    directories = dir.split(":")
    for d in directories:
        for root, dirs, files in os.walk(d):
            for file in files:
                if file.endswith(".egg"):
                    sys.path.insert(1, os.path.join(root, file))

# Used to search the webdirectory and from there create the correct file rendering from the Jinja2 templates
def render(dev, renderFile):
    try:
        up1 = os.path.dirname(os.getcwd())
        sp = up1 + '/htdocs/j2'
        fsl = jinja2.FileSystemLoader(searchpath=sp)
        env = jinja2.Environment(trim_blocks=True, lstrip_blocks=True, loader=fsl)
        tmpl = env.get_template(renderFile)
        print tmpl.render(dev).encode('utf-8')
    except jinja2.exceptions.TemplateNotFound as e:
        msg = "I'm sorry.  I couldn't finish the job because I can't find %s\n" % e
        sys.stderr.write(msg)
        sys.exit(2)

def getWebAndEnvVars():
    # Here we get the environment variables and any web variables that have been called and retunr them in a data Structure
    # This data structure has 2 keys 'webParams' and 'environOS'
    dataStruct = {}
    fs = cgi.FieldStorage()
    dataStruct['keys'] = ",".join(fs.keys())
    # Get os Environment Variables
    d = {}
    for k in os.environ.keys():
        d[k] = os.environ[k]
    dataStruct['environOS'] = d
    del d
    # Get Form Variables Only if they are defined
    d = {}
    for k in fs.keys():
        d[k] = fs.getvalue(k)
    if (len(d) > 0):
        dataStruct['webParams'] = d
        del d
    else:
        dataStruct['webParams'] = {}
    return dataStruct

def combineDicts(dictionary1, dictionary2):
    # Code will take dictionary2 and then overwrite the values in dictionary1
    output = {}
    for item, value in dictionary1.iteritems():
        if dictionary2.has_key(item):
            if isinstance(dictionary2[item], dict):
                output[item] = combineDicts(value, dictionary2.pop(item))
        else:
            output[item] = value
    for item, value in dictionary2.iteritems():
        output[item] = value
    return output

def jsonToDict(jsonFile):
    dictToReturn = {}
    try:
        j = open(jsonFile)
        dictToReturn = json.load(j)
    except Exception as e:
        print "Error occurred : %s %s" % (str(e), jsonFile)
        sys.exit(2)
    else:
        j.close()
    return dictToReturn
