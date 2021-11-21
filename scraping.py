import requests
from bs4 import BeautifulSoup


def get_author(parser):
    try:
        author = (parser.find('a', {'class': 'hnuser'})).text
    except AttributeError:
        author = 'N/A'
    return author


def get_points(parser):
    try:
        points = int(parser.find("span", {"class": "score"}).text.split()[0])
    except AttributeError:
        points = 0
    return points


def get_comments(parser):
    if parser.text.split()[-1] == 'discuss':
        comments = 0
    elif parser.text.split()[-2] == '|':  # если нет discuss
        comments = 0
    else:
        int(parser.text.split()[-2])
        comments = int(parser.text.split()[-2])
    return comments


def get_url(parser):
    url = (parser.find('a', {'class': 'titlelink'}))['href']
    if len(url.split(".")) == 1:
        return "https://news.ycombinator.com/" + url
    return url


def extract_news(parser):
    """ Extracting useful info from html markup"""
    news_list = []

    news = parser.find_all('tr', {'class': 'athing'})
    news_stat = parser.find_all('td', {'class': 'subtext'})

    for i in range(len(news_stat)):
        title = (news[i].find('a', {'class': 'titlelink'})).text
        author = get_author(news_stat[i])
        comments = get_comments(news_stat[i])
        points = get_points(news_stat[i])
        url = get_url(news[i])

        news_list.append(
            {'title': title,
             'author': author,
             'points': points,
             'comments': comments,
             'url': url})

    return news_list


def extract_next_page(parser):
    """ Extract next page URL """
    next_page_beeline = parser.find('a', {'class': 'morelink'})['href']
    return next_page_beeline


def get_news(url, n_pages=10):
    """ Get news from few pages """
    news = []
    counter = 1
    while counter <= n_pages:
        print(f"Collecting data from page: {url}")
        print(f"Page number {counter}")
        response = requests.get(url)
        soup = BeautifulSoup(response.text, "html.parser")
        news_list = extract_news(soup)
        next_page = extract_next_page(soup)
        url = "https://news.ycombinator.com/" + next_page
        news.extend(news_list)

        counter += 1

    return news


if __name__ == "__main__":
    print(get_news('https://news.ycombinator.com/', 5))
