from PyQt5.QtWidgets import QWidget
import requests
from bs4 import BeautifulSoup, element
import pandas as pd

class EksiSozlukWebsite:

    def __init__(self):
        super().__init__()

        self.website = 'https://eksisozluk.com/basliklar/gundem'

        self.header = {
            'User-Agent': 'Mozilla/5.0 (Macintosh; Intel Mac OS X 10_15_7) AppleWebKit/537.36 (KHTML, like Gecko) '
                          'Chrome/91.0.4472.77 Safari/537.36 '
        }

        # make HTTP requests. download the HTML contents from the given link
        # a more complex task that requires persistent cookies
        ses = requests.Session()
        r = ses.get(self.website, headers=self.header)
        # create a Beautiful Soup object and parse the contents
        self.soup = BeautifulSoup(r.content, features="html.parser")
        # self.ht_news = []
        # self.ht_news_num = 0

    def read_news_func(self, link):
        entry_list = []
        for page in range(1,2):
            # Sometimes an error may be encountered during the download
            try:
                # make HTTP requests. download the HTML contents from the given link
                req_link = requests.get(link+str(page), headers=self.header)
                # create a Beautiful Soup object and parse the contents
                soup_link = BeautifulSoup(req_link.content, features="html.parser")
                # find Elements by HTML Class Name and extract text
                instapaper_body = soup_link.find_all('div', {"class": "instapaper_body"})[0]
                entry_item_list = instapaper_body.find_all('ul', {"id": "entry-item-list"})[0]
                entries_list = entry_item_list.find_all('li')

                for entry_item in entries_list:
                    entry = entry_item.find('div', {'class': 'content'}).text
                    # remove spaces at the beginning and at the end of the string
                    entry_list.append(entry.strip())
            except:
                pass

        # take all items in an iterable and joins them into one string by adding new lines between them
        return '\n\n'.join(entry_list)

    def news_links_funk(self):
        # get the topic items links from the website
        topic_items = []
        main_left_frame = self.soup.find_all('ul', {"class": "topic-list"})[1]
        topic_list_items = main_left_frame.find_all("a")
        for topic_item in topic_list_items:
            topic_item_list = []
            # a NavigableString represents text found in the HTML document
            if isinstance(topic_item, element.NavigableString):
                continue
            # a Tag object contains nested tags
            if isinstance(topic_item, element.Tag):
                # find Elements and extract link
                topic_item_href = topic_item.get("href")
                topic_item_text = topic_item.find(text=True, recursive=False)
                topic_item_rating = topic_item.find('small').text
                # a topic with 2500 entries appears as 2,5b on the website.
                # convert the text to the numeric data (2,5b -> 2500)
                if 'b' in topic_item_rating:
                    split_num = topic_item_rating.split(',')
                    number = split_num[0]
                    decimal = split_num[1][:-1]
                    topic_item_rating = (int(number) + int(decimal)/10)*1000
                topic_item_link = 'https://eksisozluk.com' + topic_item_href + '&p='

                # append the fetched contents to the topic_items list
                topic_item_list.append(topic_item_link)
                topic_item_list.append('https://upload.wikimedia.org/wikipedia/commons/2/25/Ekşi_Sözlük_yeni_logo.svg')
                topic_item_list.append(topic_item_text)
                topic_item_list.append(int(topic_item_rating))
                topic_items.append(topic_item_list)

        # return the list
        return topic_items

