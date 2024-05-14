from bs4 import BeautifulSoup
from pymongo import MongoClient
from sklearn.feature_extraction.text import TfidfVectorizer
import nltk
from nltk.stem import WordNetLemmatizer
from nltk import word_tokenize
from bs4 import BeautifulSoup
from pymongo import MongoClient
from sklearn.feature_extraction.text import CountVectorizer
import nltk
nltk.download('omw-1.4')
from nltk.stem import WordNetLemmatizer
from nltk import word_tokenize
nltk.download('punkt')
nltk.download('wordnet')
import pickle

# for index_of_document, tfidf_scores_of_document in enumerate(tfidf_scores_of_documents.toarray()):
    #     print(tfidf_scores_of_document)
    #     for index_of_term, tfidf_score_of_document in enumerate(tfidf_scores_of_document):
    #             if tfidf_score_of_document != 0:
    #                 term = terms[index_of_term]
    #                 if terms[index_of_term] in inverted_index:
    #                     inverted_index[term].append((urls[index_of_document], tfidf_scores_of_document))
    #                 else:
    #                     inverted_index[term] = [(page["url"],  tfidf_score_of_document)]

class LemmaTokenizer:
    def __init__(self):
        self.wnl = WordNetLemmatizer()
    def __call__(self, doc):
        # Tokenize the document
        tokens = word_tokenize(doc)
        # Lemmatize and filter out non-alphanumeric tokens
        filtered_tokens = []
        for t in tokens:
            # Include $ symbol and alphanumeric characters
            if t.isalnum() or t == '$':
                filtered_tokens.append(self.wnl.lemmatize(t))
        return filtered_tokens


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
    # Connect to DB
    db = connectDataBase()
    website_collection = db["websites"]
    inverted_index_collection = db["inverted_index"]
    inverted_index_collection.drop()
    documents_collection = db["documents"]
    documents_collection.drop()

    # Initialize inverted index
    inverted_index = {}

    # Initialize TF-IDF vectorizer
    vectorizer = TfidfVectorizer(tokenizer=LemmaTokenizer(), stop_words='english')

    # Retrieve documents only if they match format
    pages = website_collection.find({"parseable": True}, {"url": 1, "html": 1})
    
    #Relevant text of documents array
    relevant_text_of_documents = []
    
    #Urls
    urls = []
    
    # Retrieve relevant/Area of Search text from html
    for page in pages:
        bs = BeautifulSoup(page["html"], "html.parser")
        text = bs.find('div', class_='col').text + bs.find('div', class_='accolades').text
        relevant_text_of_documents.append(text)
        urls.append(page["url"])
    
    # Training  
    vectorizer.fit(relevant_text_of_documents)

    # Calculate TF-IDF scores
    tfidf_scores_of_documents = vectorizer.transform(relevant_text_of_documents)

    # Get feature names (terms)
    terms = vectorizer.get_feature_names_out()
    
    for index_of_document, tfidf_scores_of_document in enumerate(tfidf_scores_of_documents.toarray()):
        #Insert the document into the doucment collection (the documents in the collection will be referenced by the terms in the inverted_index)
        new_document_id = documents_collection.insert_one({"url": urls[index_of_document], "tfidf_scores_of_document": tfidf_scores_of_document.tolist()}).inserted_id
        for index_of_term, tfidf_score_of_document in enumerate(tfidf_scores_of_document):
            if tfidf_score_of_document != 0:
                term = terms[index_of_term]
                #Checking if term exists in the inverted index
                if term in inverted_index: 
                    inverted_index[term][1].append(new_document_id)
                    inverted_index_collection.update_one({"_id": inverted_index[term][0]},{"$push":{ "document_ids": new_document_id}})
                    
                else:
                    inverted_index_id = inverted_index_collection.insert_one({"term": term, "document_ids": [new_document_id]}).inserted_id
                    inverted_index[term] = (inverted_index_id, [new_document_id])
                #Insert each relevant term into the inverted index collection along with the reference to document             
            
    # Insert inverted index into MongoDB collection
    # for term, documents in inverted_index.items():
    #     inverted_index_collection.insert_one({"term": term, "documents": documents})
    
    with open('tfidf_vectorizer.pkl', 'wb') as f:
        pickle.dump(vectorizer, f)


    return inverted_index


inverted_index = text_transformation()



# Print the inverted index
for term, documents in inverted_index.items():
    print(f"{term}: {documents}")
    
