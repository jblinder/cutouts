#!/usr/bin/env python2

import requests
import unicodecsv
import hashlib
from curtsies import Input
from pymongo import MongoClient
from pymongo import InsertOne, DeleteOne, ReplaceOne
import logging

# setup mongo
client = MongoClient()
db = client.muckrock
print("original",db.collection_names())

if 'foia' not in db.collection_names():
    print("foia collection not found")
    db.create_collection("foia")
if 'communication' not in db.collection_names():
    print("communication collection not found")
    db.create_collection("communication")
if 'file' not in db.collection_names():
    print("file collection not found")
    db.create_collection("file")

foias           = db.get_collection('foia')
communications  = db.get_collection('communication')
files           = db.get_collection('file')

print("new",db.collection_names())

logger = logging.getLogger(__name__)
logger.setLevel(logging.INFO)

# create a file handler
handler = logging.FileHandler('hello.log')
handler.setLevel(logging.INFO)

# create a logging format
formatter = logging.Formatter('%(asctime)s - %(name)s - %(levelname)s - %(message)s')
handler.setFormatter(formatter)

# add the handlers to the logger
logger.addHandler(handler)

token = 'd0c2d39330ca78bdafae9c8d7f0dec284c3c8fc1'#get_api_key()
url = 'https://www.muckrock.com/api_v1/'

headers = {'Authorization': 'Token %s' % token, 'content-type': 'application/json'}


url = url + 'foia/?page='

fields = (
    'id',
    'user',
    'title',
    'slug',
    'status',
#    'jurisdiction',
    'agency',
    'date_submitted',
    'date_done',
    'date_due',
    'days_until_due',
    'date_followup',
    'embargo',
    'date_embargo',
    'price',
    'description',
    'tracking_id',
    'tags'
)
fields_root  = ['id_key', 'id', 'title', 'slug', 'status', 'embargo', 'permanent_embargo', 'user', 'username', 'agency', 'date_due', 'days_until_due', 'date_followup', 'datetime_done', 'date_embargo', 'tracking_id', 'price', 'disable_autofollowups', 'tags', 'absolute_url']
fields_comm  = ['id_key', 'foia', 'from_user', 'to_user', 'subject', 'datetime', 'response', 'autogenerated', 'thanks', 'full_html', 'communication', 'status', 'likely_foia', 'delivered']
fields_file =  ['id_key', 'id', 'ffile', 'title', 'datetime', 'source', 'description','access','doc_id','pages']

# set page to control end point
page = 1

csv_file = open('foia_root.csv', 'wb')
csv_file.seek(0)
csv_writer = unicodecsv.writer(csv_file)
csv_writer.writerow(fields_root)

csv_file_comm = open('foia_comm.csv', 'wb')
csv_file_comm.seek(0)
csv_writer_comm = unicodecsv.writer(csv_file_comm)
csv_writer_comm.writerow(fields_comm)

csv_file_file = open('foia_file.csv', 'wb')
csv_file_file.seek(0)
csv_writer_file = unicodecsv.writer(csv_file_file)
csv_writer_file.writerow(fields_file)

is_finished = False
while is_finished is False:

    req_url = url + str(page)

    try:
        r = requests.get(req_url, headers=headers) 
        json = r.json()
    except requests.exceptions.RequestException as e:  # This is the correct syntax
        print(e)
        print("exception")
        json = []

    if 'results' not in json:
        is_finished = True
        print("No results found")
        break

    for datum in json['results']:
        # clean commas
        for key, value in datum.items():
            if isinstance(value, str):
                datum[key] = value.replace(',',' ')

        # index across tables
        id_key = datum['id']
        datum['id_key'] = id_key
        foias.insert_one(datum)
        # main foia data
        csv_writer.writerow([datum[field] for field in fields_root])
        for comm in datum['communications']:
            # clean commas
            for key, value in comm.items():
                if isinstance(value, str):
                    comm[key] = value.replace(',',' ')

            comm['id_key'] = id_key
            # communication data
            communications.insert_one(comm)
            csv_writer_comm.writerow([comm[field] for field in fields_comm])
            for file in comm['files']:
                # clean commas
                for key, value in file.items():
                    if isinstance(value, str):
                        file[key] = value.replace(',',' ')

                # file data
                file['id_key'] = id_key
                files.insert_one(file)
                csv_writer_file.writerow([file[field] for field in fields_file])
    
    print('Page %d of %d' % (page, json['count'] / 20 + 1))
    total_pages = json['count'] // 20 + 1
    logger.info(f'Page: {page} / {total_pages} Url: {req_url}')
    page += 1
    if page >= total_pages:
        total_pages = True

print("Closing CSVs...")
csv_file.close()
csv_file_comm.close()
csv_file_file.close()
print("Exiting")
exit()

