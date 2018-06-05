import requests
import csv
import time
import unicodecsv
import hashlib
from pymongo import MongoClient
from pymongo import InsertOne, DeleteOne, ReplaceOne
import logging
import re

logger = logging.getLogger(__name__)
logger.setLevel(logging.INFO)

# create a file handler
handler = logging.FileHandler('file_scraper_2.log')
handler.setLevel(logging.INFO)

# create a logging format
formatter = logging.Formatter('%(asctime)s - %(name)s - %(levelname)s - %(message)s')
handler.setFormatter(formatter)

# add the handlers to the logger
logger.addHandler(handler)

client = MongoClient()
db = client.muckrock
print("original",db.collection_names())

if 'file_data' not in db.collection_names():
    print("foia collection not found")
    db.create_collection("file_data")

file_data = db.get_collection('file_data')

url_base = 'https://www.documentcloud.org/documents/'
#url = 
files_filepath = '../data/foia_file.csv'

with open(files_filepath) as f:
    reader = csv.reader(f)
    next(reader) # skip header
    data = [r for r in reader]

urls = []
file_urls = {}
for entry in data:
  #  print(entry)
    id_key = entry[0]
    #entry = entry[3]
    doc_id = entry[len(entry)-2]
    pages  = entry[len(entry)-1]

    path = doc_id.split('-') # parse params
    file_id = path.pop(0)    # get file id
    path = '-'.join(path)
    #print(f'length: {len(entry)} doc_id: {doc_id} pages: {pages} file_id: {file_id}')
    if doc_id == "":
        print("NONE")
    else:
        file_urls[id_key] = []
        for page in range(int(pages)):
            file_urls[id_key].append(f'https://www.documentcloud.org/documents/{file_id}/pages/{path}-p{page+1}.txt')
log_file = open("file_scraper.log","r") 
#print(log_file)
li = re.findall('id: (.*) url:', log_file.read());
pids = list(set(li))

fields = ['id_key','file','url']
csv_file_file = open('foia_file_data.csv', 'wb')
csv_file_file.seek(0)
csv_writer_file = unicodecsv.writer(csv_file_file)
csv_writer_file.writerow(fields)

for key,value in file_urls.items():
    if key in pids:
        print("next")
        continue
    for url in value:
        data = {}
        r = requests.get(url)
        text = r.text
        print(key,url)
        text = text.replace(',',' ')

        data['id_key'] = key
        data['file'] = text
        data['url'] = url
        file_data.insert_one(data)
        csv_writer_file.writerow([data[field] for field in fields])
        logger.info(f'id: {key} url:{url}')
        #time.sleep(.5)

csv_writer_file.close()