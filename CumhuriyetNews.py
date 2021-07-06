from PyQt5.QtWidgets import QWidget
import requests
from bs4 import BeautifulSoup, element
import pandas as pd


class CumhuriyetWebsite:

    def __init__(self):
        super().__init__()

        self.website = 'http://www.cumhuriyet.com.tr'
        self.header = {
            'User-Agent': 'Mozilla/5.0 (Macintosh; Intel Mac OS X 10_15_7) AppleWebKit/537.36 (KHTML, like Gecko) '
                          'Chrome/91.0.4472.77 Safari/537.36 '
        }
        # make HTTP requests. download the HTML contents from the given link
        req = requests.get(self.website, headers=self.header)
        # create a Beautiful Soup object and parse the contents
        self.soup = BeautifulSoup(req.content, features="html.parser")

    # method to download news from the website using links
    def read_news_func(self, news_link):
        read_news = []

        r_news_box_link = requests.get(news_link, headers=self.header)
        soup_news_box_link = BeautifulSoup(r_news_box_link.content, features="html.parser")
        # find Elements by HTML Class Name and extract text
        news_box_headline = soup_news_box_link.find_all('h1', {"class": "baslik"})[0].text
        news_box_spot = soup_news_box_link.find_all('h2', {"class": "spot"})[0].text
        news_box_news_texts = soup_news_box_link.find_all('div', {"class": "haberMetni"})[0]
        # get the image of the news if exists. If not, use the link for displaying the website main image
        try:
            news_box_img = soup_news_box_link.find('img', {"class": "img-responsive mb20"}).get('src')
            news_box_img_link = self.website + news_box_img
        except:
            news_box_img_link = 'https://www.cumhuriyet.com.tr/Archive/2015/10/30/400287_resource/55555.jpg'

        # append the fetched contents to the read_news list
        read_news.append(news_link)
        read_news.append(news_box_img_link)
        read_news.append(news_box_headline)
        read_news.append(news_box_spot)
        read_news.append(news_box_news_texts)

        # return the list
        return read_news

    def news_links_funk(self):
        # get the top box news links from the website
        news_box_link_list = []
        news_boxes = self.soup.find_all('div', {"class": "row hidden-xs"})[1].contents
        for news_box in news_boxes:
            # a NavigableString represents text found in the HTML document
            if isinstance(news_box, element.NavigableString):
                continue
            # a Tag object contains nested tags
            if isinstance(news_box, element.Tag):
                # find Elements by HTML Class Name and extract link
                news_box_href = news_box.find_all("div", {"class": "haber-kutu"})[0].find("a").get("href")
                news_kind = news_box_href.split('/')[1]
                # eliminate non-news links
                if news_kind == 'haber' or news_kind == 'video':
                    news_box_link = self.website + news_box_href
                    news_box_link_list.append(news_box_link)

        # get the slider news links from the website
        container_headlines = self.soup.find_all('div', {"class": "row container-manset"})[0]
        slider_headlines = container_headlines.find_all('div', {"class": "slider-manset"})[0].contents[1].find_all("a")
        for slider_headline in slider_headlines:
            if isinstance(slider_headline, element.NavigableString):
                continue
            if isinstance(slider_headline, element.Tag):
                slider_headline_href = slider_headline.get("href")
                news_kind = slider_headline_href.split('/')[1]
                if news_kind == 'haber' or news_kind == 'video':
                    slider_headline_link = self.website + slider_headline_href
                    news_box_link_list.append(slider_headline_link)

        # get the double news links from the website
        double_news = self.soup.find_all('div', {"class": "haber ikili haber-ikili-box"})
        for double_new in double_news:
            double_news_href = double_new.find('div', {"class": "haber-galerisi kucuk"}).contents[1].get("href")
            double_news_kind = double_news_href.split('/')[1]
            if double_news_kind == 'haber' or double_news_kind == 'video':
                double_news_link = self.website + double_news_href
                news_box_link_list.append(double_news_link)

        return news_box_link_list

    # method to get the current dollar/euro currency info from the website
    def currency_info_func(self):
        currency_soup = self.soup.find('div', {"class": "doviz-bilgileri"})
        currency_types_soup = currency_soup.find_all('span', {"class": "tipi"})
        currency_values_soup = currency_soup.find_all('span', {"class": "deger"})

        currency_types = []
        for currency_type in currency_types_soup:
            currency_types.append(currency_type.text)

        currency_values = []
        for currency_value in currency_values_soup:
            currency_values.append(currency_value.text.strip())

        return currency_types, currency_values


