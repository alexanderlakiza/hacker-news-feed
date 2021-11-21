from bottle import (
    route, run, template, request, redirect
)
from scraping import get_news
from db import News, session
from classification import NaiveBayesClassifier, clean_titles, clean_one_doc
import string


def title_from_db(s):
    """ Get a title of a news from db"""
    translator = str.maketrans("", "", string.punctuation)
    return s.translate(translator)


@route("/news")
def news_list():
    s = session()
    rows = s.query(News).filter(News.label == None).all()
    return template('news_template', rows=rows)


@route("/add_label/")
def add_label():
    s = session()

    news_id = request.query['id']
    label = request.query['label']

    news = s.query(News).filter(News.id == news_id).one()
    news.label = label

    s.commit()
    redirect("/news")


@route("/update")
def update_news():
    s = session()
    news = get_news("https://news.ycombinator.com/newest", 10)
    top_news = get_news("https://news.ycombinator.com/", 11)
    news.extend(top_news)

    for n in range(len(news)):
        row = News(title=news[n]["title"],
                   author=news[n]["author"],
                   url=news[n]["url"],
                   comments=news[n]["comments"],
                   points=news[n]["points"])
        if s.query(News).filter(News.title == row.title and News.author == row.author).all():
            continue
        s.add(row)
        s.commit()
    redirect("/news")


@route("/classify")
def classify_news():
    s = session()
    labeled_news = s.query(News).filter(News.label != None).all()
    X = clean_titles(labeled_news)
    y = [news.label for news in labeled_news]

    clf = NaiveBayesClassifier()
    clf.fit(X, y)

    unlabeled_news = s.query(News).filter(News.label == None).all()
    good, never = [], []
    for row in unlabeled_news:
        row.title = title_from_db(row.title)
        print(row.title)
        title_for_clf = clean_one_doc(row.title)

        prediction = clf.predict([title_for_clf])
        print(prediction)

        if prediction == ['good']:
            good.append(row)
        else:
            never.append(row)

    return template('news_recs', good=good, never=never)


@route("/update_recs")
def update_recs():
    s = session()
    news = get_news("https://news.ycombinator.com/newest", 4)
    top_news = get_news("https://news.ycombinator.com/", 2)
    news.extend(top_news)

    for n in range(len(news)):
        row = News(title=news[n]["title"],
                   author=news[n]["author"],
                   url=news[n]["url"],
                   comments=news[n]["comments"],
                   points=news[n]["points"])
        if s.query(News).filter(News.title == row.title and News.author == row.author).all():
            continue
        s.add(row)
        s.commit()
    redirect("/classify")


if __name__ == "__main__":
    run(host="localhost", port=8080)
