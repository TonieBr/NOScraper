import os
import sys
from bs4 import BeautifulSoup
import sqlite3 
import urllib.request, urllib.parse, urllib.error
import re
import cchardet as chardet
import lxml
import http.client
import requests

cwd = sys.path[0]

conn = sqlite3.connect(os.path.join(cwd, 'liveblogDBOekraine.sqlite'))
cur = conn.cursor()

cur.execute('CREATE TABLE IF NOT EXISTS Oekraine(id INTEGER NOT NULL PRIMARY KEY AUTOINCREMENT UNIQUE, datum DATE, url TEXT)')
cur.execute('CREATE TABLE IF NOT EXISTS OekraineMsg(url_id INTEGER, title TEXT, time TIME, message TEXT)')

links = list()

# Continue or Begin Reading
cur.execute('SELECT MIN(url) FROM Oekraine')
tmp = cur.fetchone()[0]

if tmp is None:
    article = 2481670
else:
    arr = tmp.split('/')
    article = int(arr[len(arr) - 1])

baseURL = os.path.join('http://nos.nl/liveblog/', str(article))
handle = urllib.request.urlopen(baseURL).read()
soup = BeautifulSoup(handle, 'html.parser')

requests_session = requests.Session()
r = requests_session.get('http://nos.nl/')

# While True Loop with manual Date (i.e. 20 Feb 2022) instead of art number 
while article > 2418365:
     baseURL = os.path.join('http://nos.nl/liveblog/', str(article))
     print('Reading:', baseURL)
     Oekraine = False
     Datum = False
     Liveblog = False

     try:
         handle = urllib.request.urlopen(baseURL).read()
     except urllib.error.HTTPError:
         article = article - 1
         continue

     soup = BeautifulSoup(handle, 'lxml')

     for liveUkr in soup.find_all('meta'):
         if 'published_time' in str(liveUkr):
            date = str(liveUkr).split('T')[0].split('"')[1]
            Datum = True
         elif 'Oekraine' in str(liveUkr) or 'Oekraïne' in str(liveUkr):
            Oekraine = True
         elif 'liveblog' in str(liveUkr):
            Liveblog = True

         if Oekraine and Liveblog and Datum:
            print('Found')
            cur.execute('INSERT INTO Oekraine(datum, url) VALUES(?, ?)', (date, baseURL))
            cur.execute('SELECT id FROM Oekraine WHERE url=?', (baseURL,))
            Ukr_id = cur.fetchone()[0]

            for container in soup.find_all('div', id=re.compile('^UPDATE-container')):
                title = container.find('h2').text
                arr = container.find_all('p')
                time = arr[0].text
                msg = ''
                for x in arr[1:]:
                    msg = msg + x.text

                cur.execute('INSERT INTO OekraineMsg(url_id, title, time, message) VALUES(?, ?, ?, ?)', (Ukr_id, title, time, msg,))

            conn.commit()
            break

     article = article - 1

