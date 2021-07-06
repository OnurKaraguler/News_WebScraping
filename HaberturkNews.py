from PyQt5.QtWidgets import QWidget
import requests
from bs4 import BeautifulSoup, element
import pandas as pd


class HaberturkWebsite:

    def __init__(self):
        super().__init__()

        self.website = 'https://www.haberturk.com'
        self.header = {
            'User-Agent': 'Mozilla/5.0 (Macintosh; Intel Mac OS X 10_15_7) AppleWebKit/537.36 (KHTML, like Gecko) '
                          'Chrome/91.0.4472.77 Safari/537.36 '
        }

        # make HTTP requests. download the HTML contents from the given link
        # a more complex task that requires persistent cookies
        ses = requests.Session()
        req = ses.get(self.website, headers=self.header)
        # create a Beautiful Soup object and parse the contents
        self.soup = BeautifulSoup(req.content, features="html.parser")

    def read_news_func(self, news_link):
        read_news = []
        # Sometimes an error may be encountered during the download.
        try:
            # download the HTML contents from the given link
            ses = requests.Session()
            r_news_box_link = ses.get(news_link, headers=self.header)
        except:
            return None
        # create a Beautiful Soup object and parse the contents
        soup_news_box_link = BeautifulSoup(r_news_box_link.content, features="html.parser")
        # if the news is a standard article news
        try:
            # find Elements by HTML Class Name and extract text and image
            news_box_article = soup_news_box_link.find_all('section', {"class": "newsArticle featured"})[0]
            news_box_img_link = news_box_article.find_all('div', {"class": "img"})[0].find('img').get('src')
            news_box_title = news_box_article.find_all('h1', {"class": "title"})[0].text
            news_box_spot = news_box_article.find_all('h2', {"class": "spot-title"})[0].text
            news_box_tag = soup_news_box_link.find_all('article', {"class": "content type1"})[0].find_all('p')
            combined = [str(ul) for ul in news_box_tag]
            news_box_text = '\n'.join(combined)
        # if photos are used for the news
        except:
            news_box_article = soup_news_box_link.find_all('section', {"class": "featured"})[0]
            try:
                news_box_img = soup_news_box_link.find_all('article', {"class": "content type1 photo-section"})[0]
                news_box_img_link = news_box_img.find('li').find('img').get('src')
                news_box_title = news_box_article.find_all('h1', {"class": "title"})[0].text
                news_box_spot = news_box_article.find_all('h2', {"class": "spot-title"})[0].text
                news_box_text = 'Haberturk Photo News'
            except:
                return None

        # append the fetched contents to the read_news list
        read_news.append(news_link)
        read_news.append(news_box_img_link)
        read_news.append(news_box_title)
        read_news.append(news_box_spot)
        read_news.append(news_box_text)

        # return the list
        return read_news

    def news_links_funk(self):
        # get the top box news links from the website
        news_box_link_list = []
        news_boxes_row = self.soup.find_all('div', {"class": "box-row"})[0]
        news_boxes = news_boxes_row.find_all('div', {"class": "box column-3 type-2 color-white"})
        for news_box in news_boxes:
            # a NavigableString represents text found in the HTML document
            if isinstance(news_box, element.NavigableString):
                continue
            # a Tag object contains nested tags
            if isinstance(news_box, element.Tag):
                # find Elements by HTML Tag Name and extract link
                news_box_href = news_box.find("a").get("href")
                news_box_link = self.website + news_box_href
                news_box_link_list.append(news_box_link)

        # get the slider news links from the website
        slider_container_items = self.soup.find_all('div', {"class": "swiper-container slider"})
        for slider_news_item in slider_container_items:
            try:
                slider_news_items = slider_news_item.find_all('a', {"class": "gtm-tracker MainSliderLink"})
                for slider_news_item in slider_news_items:
                    if isinstance(slider_news_item, element.NavigableString):
                        continue
                    if isinstance(slider_news_item, element.Tag):
                        slider_news_href = slider_news_item.get("href")
                        # eliminate non-news links
                        news_kind = slider_news_href.split('/')
                        if news_kind[1] != 'video' and news_kind[0] == '':
                            slider_news_link = self.website + slider_news_href
                            news_box_link_list.append(slider_news_link)
            except:
                pass

        return news_box_link_list


