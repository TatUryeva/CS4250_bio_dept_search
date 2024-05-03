from bs4 import BeautifulSoup
from pymongo import MongoClient
from sklearn.feature_extraction.text import CountVectorizer
import nltk
nltk.download('omw-1.4')
from nltk.stem import WordNetLemmatizer
from nltk import word_tokenize

""" 
1. Put url and html into a dict 'pages'
2. For each html in pages, retrieve and transform relevant text
    - get Text and Accolades text and put into string
    - stopping and stemming on html text data
    - store 
3. Store the terms as a list into a dictionary with the url as the key
"""

class LemmaTokenizer:
    def __init__(self):
        self.wnl = WordNetLemmatizer()
    def __call__(self, doc):
        return [self.wnl.lemmatize(t) for t in word_tokenize(doc)]

def connectDataBase():

    # Create a database connection object using pymongo
    DB_NAME = "documents"
    DB_HOST = "localhost"
    DB_PORT = 27017
    try:
        client = MongoClient(host=DB_HOST, port=DB_PORT)
        db = client[DB_NAME]
        return db
    except:
        print("Database not connected successfully...")

def text_transformation():
    # Connnect to DB
    db = connectDataBase()
    collection = db["websites"]

    # Retrieve documents only if they match format
    pages = collection.find({"parseable": True}, {"url": 1, "html": 1})
    pages_terms = []
    for page in pages:
        # Retrieve relevant text from html
        bs = BeautifulSoup(page["html"], "html.parser")
        text = bs.find('div', class_= 'col').text
        text += bs.find('div', class_= 'accolades').text
        text = [text]
        # Stopping and Stemming
        vectorizer = CountVectorizer(stop_words='english')
        vectorizer.fit(text)
        text = list(vectorizer.vocabulary_)
        # Dict for url: terms
        page["html"] = text
        pages_terms.append(page)
    return pages_terms
        
pages = text_transformation()
print('hi')







