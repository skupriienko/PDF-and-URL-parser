# -*- coding: utf-8 -*-

# Install packages
# !pip install tika
# !pip install newspaper3k
# !curl https://raw.githubusercontent.com/codelucas/newspaper/master/download_corpora.py | python3

# Import tika parser, pandas and modules for files
import pandas as pd
import os
import re
from os import listdir
from os.path import isfile, join
from newspaper import Article, Config

from func import cleaning_raw_text, read_pdf, create_csv, create_timestamp


# Current directory path
path = os.path.abspath(os.curdir)

all_files = [f for f in listdir(path) if isfile(join(path, f)) and f.endswith(".pdf")]
print(all_files)

# File sizes
file_sizes = [os.path.getsize(os.path.join(path, f)) for f in listdir(path) if f.endswith(".pdf")]
print(file_sizes)

# For parsing long list of urls
# my_urls = pd.read_csv('data/Awesome_Python_Learning.csv', index_col=None)
# my_url_list = list(my_urls['URL'])

# For parsing sort list of urls
raw_urls = """
https://proglib.io/p/best-format-on-cv/
https://blog.bitsrc.io/15-app-ideas-to-build-and-level-up-your-coding-skills-28612c72a3b1
https://proglib.io/p/python-interview/
https://proglib.io/p/15-questions-for-programmers/
https://dou.ua/lenta/interviews/first-job-in-sixteen/?from=comment-digest_bc&utm_source=transactional&utm_medium=email&utm_campaign=digest-comments#1829186
https://medium.com/better-programming/50-python-interview-questions-and-answers-f8e80d031bd3
https://dev.to/javinpaul/50-data-structure-and-algorithms-problems-from-coding-interviews-4lh2
https://towardsdatascience.com/53-python-interview-questions-and-answers-91fa311eec3f
https://interviewing.io/
https://www.datasciencecentral.com/profiles/blogs/answers-to-dozens-of-data-science-job-interview-questions
"""
my_url_list = raw_urls.split()
print(my_url_list)

user_agent = 'Mozilla/5.0 (Macintosh; Intel Mac OS X 10_11_5) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/50.0.2661.102 Safari/537.36'
config = Config()
config.browser_user_agent = user_agent
config.memoize_articles = False

pdf_text_list = []
pdf_text_list_url = []
pagenumbers = []
articles_info_list = []


def read_html_or_pdf(path=None, url=None):
    global url_of_article
    if path or url is not None:
        for i, file in enumerate(path):
            # creating an object
            try:
                text = read_pdf(file)
                pagenumbers.append(text['metadata']['xmpTPg:NPages'])
                t = [[k, v] for k, v in text.items()]

                text_strings = str(t[1][1])

            except Exception:
                print(f"Something is wrong with reading PDF file #{i}")
                continue
            pdf_text_list.append(cleaning_raw_text(text_strings))

        for index, article_url in enumerate(url):
            # creating an object
            try:
                article = Article(article_url, config=config)
                article.download()
                article.parse()
                article.nlp()
                article_authors = article.authors
                article_title = article.title
                article_text = article.text
                article_keywords = article.keywords
                article_movies = article.movies
                article_publish_date = article.publish_date
                article_source_url = article.source_url
                url_of_article = article.url
                print(index, url_of_article, article_title)
                tmp = [article_authors, article_title, article_source_url, url_of_article, article_keywords,
                       article_movies, article_publish_date]
                text_strings = str(article_text)
            except Exception:
                print('***FAILED TO DOWNLOAD***', url_of_article)
                continue
            pdf_text_list_url.append(cleaning_raw_text(text_strings))
            articles_info_list.append(tmp)

read_html_or_pdf(path=all_files, url=my_url_list)

parsedData = pdf_text_list + pdf_text_list_url

# FOR PDF PARSER
# data = pd.DataFrame({'body_text': textList, 'file_size': file_sizes, 'pagenumbers': pagenumbers}, index=labelList)

# FOR HTML PARSER
# data = pd.DataFrame({'body_text': textList, 'file_size': file_sizes}, index=labelList)

# FOR PDF_OR_HTML PARSER
data = pd.DataFrame({'body_text': parsedData, 'timestamp': create_timestamp()})

print("Number of null in label: {}".format(data.index.isnull().sum()))
print("Number of null in text: {}".format(data['body_text'].isnull().sum()))

# Regexp and replace and substitute words and symbols
# Replace text with regexp

cleaned_text_list = []

def clean_with_regex(text):
    for article in text:
        try:
            clean_endlines = re.sub("\.\n", '.+++', article)
            clean_endlines = re.sub("!\n", '!+++', clean_endlines)
            clean_endlines = re.sub(":\n", '+++', clean_endlines)
            clean_endlines = re.sub("\n", ' ', clean_endlines)
            enter_endlines = re.sub("\+{3}", "\n", clean_endlines)
            # Replace more then two links one after the other
            pattern = "[http]\S+\s[http]\S+\s[http]\S+"
            clean_two_http_links = re.sub(pattern, '', enter_endlines)
            # Clean dates in headers
            pattern = "(\d{1,2}\.\d{2}\.\d{4})(.)+(\d{1,2}\/\d{1,2})"
            clean_http_and_pagenumbers = re.sub(pattern, '', clean_two_http_links)
            cleaned_text_list.append(clean_http_and_pagenumbers)
        except Exception:
            cleaned_text_list.append(float('nan'))
    return cleaned_text_list

data["cleaned_body_text"] = clean_with_regex(data['body_text'])
print(data)

create_csv(data, 'data')
