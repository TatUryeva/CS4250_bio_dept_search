from urllib.request import urlopen
from urllib.error import HTTPError
from urllib.error import URLError
from bs4 import BeautifulSoup
from pymongo import MongoClient
import re


def crawlerThread (frontier):
    targets = 0
    while frontier:
        try:
            url = frontier.pop(0)
            url=url.replace('~', '')
            if 'https://www.cpp.edu' not in url and '@' not in url:
                url = 'https://www.cpp.edu'+url  
            #print('opening url:', url, end='\n')             
            html = urlopen(url)
            bs = BeautifulSoup(html.read(), 'html.parser')
            #db.pages.insert_one({'url':url, 'html':html.read()})
            #if bs.find('div', class_='fac-info') and bs.find('div', class_='fac-staff') and bs.find('div', class_='accolades') and bs.find('ul', class_='fac-nav'):
            if (bs.find('div', class_='fac-info') 
                and bs.find('div', class_='fac-info').find('p', class_='emailicon')
                and bs.find('div', class_='fac-info').find('p', class_='phoneicon') 
                and bs.find('div', class_='fac-info').find('p', class_='locationicon') 
                and bs.find('div', class_='fac-info').find('p', class_='hoursicon')):
                targets = targets + 1
                db.websites.insert_one({'url':url, 'html':html.read()})
            elif targets == 10:
                frontier.clear()
            else:
                #frontier.extend(a.get('href') for a in bs.findAll('a'))
                for link in bs.findAll('a'):
                    frontier.append(link.get('href'))
        except HTTPError as e:
            print(e)
        except URLError as e:
            print('server not found')

html = urlopen('https://www.cpp.edu/sci/biological-sciences/faculty/index.shtml')
bs = BeautifulSoup(html.read(), 'html.parser')

#frontier = [a.get('href') for a in bs.find('div', id = 'main').findAll('a', text = re.compile('Website'))]
#print(bs.find('div', id = 'main').findAll('a', string = re.compile('Website')))
#print([a for a in bs.find('div', id = 'main').findAll(text=re.compile('Website'))])
#print([a for a in bs.find('div', id = 'main').findAll('a')])

#print([a.parent for a in bs.findAll(string=re.compile('link'))])
#for a in bs.find('div', id = 'main').findAll('a'):
#    if 'Website' in a.getText():
#        frontier.append(a.get('href'))

frontier=[a.parent.get('href') for a in bs.findAll(string=re.compile('Website'))]
print(frontier)
db = MongoClient(host = "localhost", port = 27017).documents
db.websites.drop()
crawlerThread(frontier)
