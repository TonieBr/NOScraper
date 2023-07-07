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

conn = sqlite3.connect(os.path.join(cwd, 'liveblogDBCovid.sqlite'))
cur = conn.cursor()

cur.execute('CREATE TABLE IF NOT EXISTS Covid(id INTEGER NOT NULL PRIMARY KEY AUTOINCREMENT UNIQUE, datum DATE, url TEXT)')
cur.execute('CREATE TABLE IF NOT EXISTS CovidMsg(url_id INTEGER, title TEXT, time TIME, message TEXT)')

links = list()
article = 2417536

baseURL = os.path.join('http://nos.nl/liveblog/', str(article))
handle = urllib.request.urlopen(baseURL).read()
soup = BeautifulSoup(handle, 'html.parser')

#while article > 2418365:

requests_session = requests.Session()
r = requests_session.get('http://nos.nl/')

while article > 2320480:
     baseURL = os.path.join('http://nos.nl/liveblog/', str(article))
     print('Reading:', baseURL)
     Covid = False
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
         elif 'corona' in str(liveUkr) or 'covid' in str(liveUkr):
            Covid = True
         elif 'liveblog' in str(liveUkr):
            Liveblog = True

         if Covid and Liveblog and Datum:
            cur.execute('INSERT INTO Covid(datum, url) VALUES(?, ?)', (date, baseURL))
            cur.execute('SELECT id FROM Covid WHERE url=?', (baseURL,))
            Cov_id = cur.fetchone()[0]

            for container in soup.find_all('div', id=re.compile('^UPDATE-container')):
                title = container.find('h2').text
                arr = container.find_all('p')
                time = arr[0].text
                msg = ''
                for x in arr[1:]:
                    msg = msg + x.text

                cur.execute('INSERT INTO CovidMsg(url_id, title, time, message) VALUES(?, ?, ?, ?)', (Cov_id, title, time, msg,))

            conn.commit()
            break

     article = article - 1
