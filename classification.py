from sklearn.naive_bayes import MultinomialNB
from sklearn.feature_extraction.text import CountVectorizer
from db import News, session
from nltk.corpus import stopwords
from nltk.tokenize import word_tokenize
from nltk.stem import WordNetLemmatizer
import string
import re


def title_from_db(s):
    translator = str.maketrans("", "", string.punctuation)
    return s.translate(translator).lower()


def clean_one_doc(doc):
    """ Preparing a news title for classification """
    stops = stopwords.words("english")
    punct_marks = string.punctuation + "—" + "«" + "»" + "`" + "``" + "..." + "“" \
                  + "''" + "”" + '’' + '…'
    wordnet_lemmatizer = WordNetLemmatizer()

    doc = re.sub(r'@', '', doc)  # удаление @
    doc = re.sub('http://\S+|https://\S+', '', doc)  # удаление ссылок
    doc = re.sub('http[s]?://\S+', '', doc)
    doc = word_tokenize(doc)  # токенизация
    doc = [word for word in doc if word not in punct_marks and word not in stops and word.isalpha()]
    doc = [wordnet_lemmatizer.lemmatize(word, pos="v") for word in doc]  # лемматизация
    doc = ' '.join(doc)
    return doc


def clean_docs(docs):
    for i in range(len(docs)):
        docs[i] = clean_one_doc(docs[i])
    return docs


def clean_titles(titles):
    X = [title_from_db(news.title) for news in titles]
    X = clean_docs(X)
    return X


class NaiveBayesClassifier:
    """ Our classifier based on n-gram vectorizer put into MultinomialNB from sklearn"""
    def __init__(self):
        self.clf = MultinomialNB()
        self.vectorizer = CountVectorizer(ngram_range=(1, 2))

    def fit(self, X, y):
        X_train_vectorized = self.vectorizer.fit_transform(X)
        self.clf.fit(X_train_vectorized, y)

    def predict(self, X):
        X_test_vectorized = self.vectorizer.transform(X)
        predictions = self.clf.predict(X_test_vectorized)
        return predictions


if __name__ == "__main__":
    s = session()
    labeled_news = s.query(News).filter(News.label != None).all()
    unlabeled_news = s.query(News).filter(News.label == None).all()
    X = clean_titles(labeled_news)
    X_test = clean_titles(unlabeled_news)

    y = [news.label for news in labeled_news]
    y_test = [news.label for news in unlabeled_news]

    bayes = NaiveBayesClassifier()
    bayes.fit(X, y)
    preddds = bayes.predict(X_test)
    print(preddds)
