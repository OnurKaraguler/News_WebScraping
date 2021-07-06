import pandas as pd
# ##################
# for making desktop application
import pandas._libs.tslibs.base
import pandas._libs.tslibs.conversion
import pandas._libs.missing
import pandas._libs.hashtable
import pandas._libs.interval
import pandas._libs.testing
import cmath
# ##################
from PyQt5.QtWidgets import QApplication
from PyQt5.QtCore import pyqtSignal, QThread, QTimer, QUrl
from PyQt5.QtGui import QDesktopServices
import time
from WebScrMainWindow import WebScrMainWindow
from NewsMainWin import NewsMainWindow
from CumhuriyetNews import CumhuriyetWebsite
from HaberturkNews import HaberturkWebsite
from Eksisozluk import EksiSozlukWebsite


class WorkThread(QThread):
    cumNewsSig = pyqtSignal(list)

    def __init__(self, new_links, website_name):
        super().__init__()

        self.new_links = new_links
        self.website_name = website_name
        if self.website_name == 'Cumhuriyet':
            self.website = CumhuriyetWebsite()
        elif self.website_name == 'Haberturk':
            self.website = HaberturkWebsite()
        elif self.website_name == 'Eksisozluk':
            self.website = EksiSozlukWebsite()

    def run(self):
        news_num = 0
        news = []
        for new_link in self.new_links:
            read_news = self.website.read_news_func(new_link)
            if read_news:
                news.append(read_news)
                news_num += 1
                downloaded_msg = "{} news has been downloaded from {}.".format(news_num, self.website_name)
                self.cumNewsSig.emit([downloaded_msg, news])
                time.sleep(0.1)


class NewsFromWebApp(WebScrMainWindow):

    def __init__(self):
        super().__init__()
        self.statusBar().showMessage('Welcome', 1000)

        self.cum_cur_news = []
        self.cum_del_news = []
        self.ht_cur_news = []
        self.ht_del_news = []
        self.es_cur_news = []
        self.es_del_news = []

        self.df_cum = pd.DataFrame(columns=['Link', 'Image', 'Headline', 'Spot', 'News text'])
        self.cumMainWindow = NewsMainWindow(self.df_cum)
        self.df_ht = pd.DataFrame(columns=['Link', 'Image', 'Headline', 'Spot', 'News text'])
        self.htMainWindow = NewsMainWindow(self.df_ht)
        self.df_es = pd.DataFrame(columns=['Link', 'Image', 'Headline', 'Spot', 'News text'])
        self.esMainWindow = NewsMainWindow(self.df_es)

        # state of being connected or disconnected
        self.cum_connected = False
        self.ht_connected = False
        self.es_connected = False

        # connected
        self.ss_con = '''background-color: qlineargradient(x1:0.1 y1:0.1, x2:0.9 y2:0.9, stop: 0 rgb(84, 166, 71),
        stop: 1 rgb(00, 00, 00)); padding: 10px 0px 10px 00px; color : rgb(255,255,255)'''

        # disconnected
        self.ss_discon = '''background-color: qlineargradient(x1:0.1 y1:0.1, x2:0.9 y2:0.9, stop: 0 rgb(102, 40, 216), 
        stop: 1 rgb(00, 00, 00)); padding: 10px 0px 10px 00px; color : rgb(255,255,255)'''

        # get dollar / euro values from Cumhuriyet when the app starts
        cumhuriyet = CumhuriyetWebsite()
        currency_types, currency_values = cumhuriyet.currency_info_func()
        dollar_text = "{}: {}".format(currency_types[0], currency_values[0])
        euro_text = "{}: {}".format(currency_types[1], currency_values[1])
        # show them on the main window
        self.dolar_l.setText(dollar_text)
        self.euro_l.setText(euro_text)

        # call the button_toggled function when the triggered signal is emitted
        self.cumhuriyetAct.toggled.connect(self.button_toggled)
        self.haberturkAct.toggled.connect(self.button_toggled)
        self.eksisozlukAct.toggled.connect(self.button_toggled)

        # call the remove_tab function when the remove tab signal is emitted
        self.tabs.tabWidgetRemoveSignal.connect(self.remove_tab)

    # method to connect or disconnect from a news website when a button is triggered
    def button_toggled(self):
        # get the name of the triggered button. objectName() method can be called as well
        sender = self.sender().text()
        if sender == 'Cumhuriyet':
            if self.cumhuriyetAct.isChecked():
                self.connection(sender)
            else:
                self.disconnection(sender)
        elif sender == 'Haberturk':
            if self.haberturkAct.isChecked():
                self.connection(sender)
            else:
                self.disconnection(sender)
        elif sender == 'Eksisozluk':
            if self.eksisozlukAct.isChecked():
                self.connection(sender)
            else:
                self.disconnection(sender)

    def connection(self, website):
        if website == 'Cumhuriyet':
            # set the state to true to change the news list widget color to green since it is connected to the website
            self.cum_connected = True
            # call the method to connect the website
            self.open_cumhuriyet(website)
            # call the method periodically
            self.cumhuriyet_timer = QTimer()
            # The website will connect every minute.
            self.cumhuriyet_timer.start(60000)
            self.cumhuriyet_timer.timeout.connect(lambda x=website: self.open_cumhuriyet(x))
        elif website == 'Haberturk':
            self.ht_connected = True
            self.open_haberturk(website)
            self.haberturk_timer = QTimer()
            self.haberturk_timer.start(60000)
            self.haberturk_timer.timeout.connect(lambda x=website: self.open_haberturk(x))
        elif website == 'Eksisozluk':
            self.es_connected = True
            self.open_eksisozluk(website)
            self.eksisozluk_timer = QTimer()
            self.eksisozluk_timer.start(60000)
            self.eksisozluk_timer.timeout.connect(lambda x=website: self.open_eksisozluk(x))

    def disconnection(self, website):
        if website == 'Cumhuriyet':
            # set the state to false to change the news list widget color to purple since it is not connected to the website
            self.cum_connected = False
            # change the color of the news list widget
            self.tab_control(self.cumMainWindow, website)
            # stop the timer
            self.cumhuriyet_timer.stop()
        elif website == 'Haberturk':
            self.ht_connected = False
            self.tab_control(self.htMainWindow, website)
            self.haberturk_timer.stop()
        elif website == 'Eksisozluk':
            self.es_connected = False
            self.tab_control(self.esMainWindow, website)
            self.eksisozluk_timer.stop()
        self.statusBar().showMessage('{} disconnected....'.format(website), 3000)

    def open_cumhuriyet(self, website):
        cumhuriyet = CumhuriyetWebsite()

        # update dollar / euro values
        currency_types, currency_values = cumhuriyet.currency_info_func()
        dollar_text = "{}: {}".format(currency_types[0], currency_values[0])
        euro_text = "{}: {}".format(currency_types[1], currency_values[1])
        self.dolar_l.setText(dollar_text)
        self.euro_l.setText(euro_text)

        # news links of the website on the internet
        links = cumhuriyet.news_links_funk()
        # existing or deleted news links of the website
        current_links = self.cum_cur_news + self.cum_del_news
        # new news links
        new_links = []
        if len(current_links) > 0:
            for link in links:
                # only get new news links that are not in existing and deleted news links
                if link not in current_links:
                    new_links.append(link)
        else:
            new_links = links.copy()

        # set the news list background color to green when connected, even if there is no new news
        if len(new_links) == 0:
            self.tab_control(self.cumMainWindow, website)
            self.statusBar().showMessage('{} connected....'.format(website), 2000)
        elif len(new_links) > 0:
            # get data of new news from website
            self.cum_thread = WorkThread(new_links, website)
            self.cum_thread.start()
            self.cum_thread.cumNewsSig.connect(self.cum_news_funk)
            self.cum_thread.finished.connect(lambda x=website: self.cum_status_bar_msg(x))

    def cum_news_funk(self, data):
        # dataframe with new news
        self.df_cum_web = pd.DataFrame(data[1], columns=['Link', 'Image', 'Headline', 'Spot', 'News text'])
        self.statusBar().showMessage(data[0], 2000)

    def cum_status_bar_msg(self, website):
        if len(self.df_cum_web) > 0:
            # merging new and existing dataframes
            self.df_cum = pd.concat([self.df_cum, self.df_cum_web]).drop_duplicates().reset_index(drop=True)
            # delete the dataset data so that it does not mix with new news links on the next connection
            self.df_cum_web = pd.DataFrame(columns=['Link', 'Image', 'Headline', 'Spot', 'News text'])

            # send the dataframe to the News Main Window
            self.cumMainWindow = NewsMainWindow(self.df_cum)

            # Signal from the News Main Window window when an item in the news list is deleted or clicked
            self.cumMainWindow.news_deleted_signal.connect(self.deleted_news)
            # Signal from the News Main Window when an item in the news list is doubleclicked
            # to open the corresponding website page
            self.cumMainWindow.dbl_click_item_signal.connect(self.open_link)

            # show news on the main window
            self.tab_control(self.cumMainWindow, website)

            # append the new news into the current news list
            for link in self.df_cum['Link']:
                if link not in self.cum_cur_news:
                    self.cum_cur_news.append(link)

        self.statusBar().showMessage('{} connected....'.format(website), 2000)

    def open_haberturk(self, website):
        haberturk = HaberturkWebsite()
        links = haberturk.news_links_funk()
        current_links = self.ht_cur_news + self.ht_del_news
        new_links = []
        if len(current_links) > 0:
            for link in links:
                if link not in current_links:
                    new_links.append(link)
        else:
            new_links = links.copy()

        if len(new_links) == 0:
            self.tab_control(self.htMainWindow, website)
            self.statusBar().showMessage('{} connected....'.format(website), 2000)
        elif len(new_links) > 0:
            self.ht_thread = WorkThread(new_links, website)
            self.ht_thread.start()
            self.ht_thread.cumNewsSig.connect(self.ht_news_funk)
            self.ht_thread.finished.connect(lambda x=website: self.ht_status_bar_msg(x))

    def ht_news_funk(self, data):
        self.df_ht_web = pd.DataFrame(data[1], columns=['Link', 'Image', 'Headline', 'Spot', 'News text'])
        self.statusBar().showMessage(data[0], 2000)

    def ht_status_bar_msg(self, website):
        if len(self.df_ht_web) > 0:
            self.df_ht = pd.concat([self.df_ht, self.df_ht_web]).drop_duplicates().reset_index(drop=True)
            self.df_ht_web = pd.DataFrame(columns=['Link', 'Image', 'Headline', 'Spot', 'News text'])
            self.htMainWindow = NewsMainWindow(self.df_ht)
            self.htMainWindow.news_deleted_signal.connect(self.deleted_news)
            self.htMainWindow.dbl_click_item_signal.connect(self.open_link)

            self.tab_control(self.htMainWindow, website)

            for link in self.df_ht['Link']:
                if link not in self.ht_cur_news:
                    self.ht_cur_news.append(link)

        self.statusBar().showMessage('{} connected....'.format(website), 2000)

    def open_eksisozluk(self, website):
        eksisozluk = EksiSozlukWebsite()
        eksisozluk_data = eksisozluk.news_links_funk()
        self.df_es_web = pd.DataFrame(eksisozluk_data, columns=['Link', 'Image', 'Headline', 'Spot'])
        self.df_es_web = self.df_es_web.sort_values(by=['Spot'], ascending=False).reset_index(drop=True)[:30]
        current_links = self.es_cur_news + self.es_del_news

        if len(current_links) > 0:
            for link in self.df_es_web['Link']:
                if link in self.es_cur_news:
                    index_df_es = self.df_es[self.df_es['Link'] == link].index
                    index_df_es_web = self.df_es_web[self.df_es_web['Link'] == link].index
                    self.df_es.loc[index_df_es, 'Spot'] = int(self.df_es_web.loc[index_df_es_web, 'Spot'].values.copy())
                    self.df_es_web.drop(index_df_es_web, inplace=True)
                elif link in self.es_del_news:
                    index_df_es_web = self.df_es_web[self.df_es_web['Link'] == link].index
                    self.df_es_web.drop(index_df_es_web, inplace=True)

        if len(self.df_es_web['Link']) == 0:
            self.tab_control(self.esMainWindow, website)
            self.statusBar().showMessage('{} connected....'.format(website), 2000)
        elif len(self.df_es_web['Link']) > 0:
            self.es_thread = WorkThread(self.df_es_web['Link'], website)
            self.es_thread.start()
            self.es_thread.cumNewsSig.connect(self.es_news_funk)
            self.es_thread.finished.connect(lambda x=website: self.es_status_bar_msg(x))

    def es_news_funk(self, data):
        self.eksisozluk_entries = data[1]
        self.statusBar().showMessage(data[0], 2000)

    def es_status_bar_msg(self, website):
        if len(self.eksisozluk_entries) > 0:
            self.df_es_web['News text'] = self.eksisozluk_entries
            self.df_es = pd.concat([self.df_es, self.df_es_web]).drop_duplicates().reset_index(drop=True)
            self.df_es_web = pd.DataFrame(columns=['Link', 'Image', 'Headline', 'Spot', 'News text'])
            self.esMainWindow = NewsMainWindow(self.df_es)
            self.esMainWindow.news_deleted_signal.connect(self.deleted_news)
            self.esMainWindow.dbl_click_item_signal.connect(self.open_link)

            self.tab_control(self.esMainWindow, website)

            for link in self.df_es['Link']:
                if link not in self.es_cur_news:
                    self.es_cur_news.append(link)

        self.statusBar().showMessage('{} connected....'.format(website), 2000)

    def tab_control(self, mainwindow, website):
        # check which website is connected
        if mainwindow is self.cumMainWindow:
            if self.cum_connected:
                # change the color of the news list widget to green
                mainwindow.news_list_lw.setStyleSheet(self.ss_con)
            else:
                # change the color of the news list widget to purple
                mainwindow.news_list_lw.setStyleSheet(self.ss_discon)
        elif mainwindow is self.htMainWindow:
            if self.ht_connected:
                mainwindow.news_list_lw.setStyleSheet(self.ss_con)
            else:
                mainwindow.news_list_lw.setStyleSheet(self.ss_discon)
        elif mainwindow is self.esMainWindow:
            if self.es_connected:
                mainwindow.news_list_lw.setStyleSheet(self.ss_con)
            else:
                mainwindow.news_list_lw.setStyleSheet(self.ss_discon)

        # active tab
        current_tab = self.tabs.currentIndex()
        # total number of tabs
        tab_count = self.tabs.count()
        # list of the current tab names
        tab_list = []
        for i in range(tab_count):
            tab_list.append(self.tabs.tabText(i))

        if tab_count > 0:
            for i in range(tab_count):
                # get the index number of the website in the current tab names list
                if self.tabs.tabText(i) == website:
                    # remove the tab
                    self.tabs.removeTab(i)
                # add the tab againg
                self.tabs.addTab(mainwindow, website)

            for i in range(tab_count):
                tab_count = self.tabs.count()
                if self.tabs.tabText(i) == 'Cumhuriyet':
                    # move the added tab to 0 if it is Cumhuriyet
                    self.tabs.tabBar().moveTab(i, 0)

                if self.tabs.tabText(i) == 'Haberturk':
                    if tab_count > 1:
                        # move the added tab to 1 if it is Haberturk
                        self.tabs.tabBar().moveTab(i, 1)

                self.tabs.setCurrentIndex(current_tab)
        else:
            self.tabs.addTab(mainwindow, website)

    # delete news in the list widget
    def deleted_news(self, data):
        # sort the list from largest to smallest
        del_list = sorted(data, reverse=True)
        if self.sender() is self.esMainWindow:
            # set the news list background color to green if connected
            if self.es_connected:
                self.esMainWindow.news_list_lw.setStyleSheet(self.ss_con)
            # set the news list background color to purple if disconnected
            else:
                self.esMainWindow.news_list_lw.setStyleSheet(self.ss_discon)

            for item in del_list:
                try:
                    # get the link to be deleted
                    del_link = self.df_es['Link'][item]
                    # append the link to the deleted news link list
                    self.es_del_news.append(del_link)
                    # remove the link from the existing news link list
                    self.es_cur_news.remove(del_link)
                    # drop the link from the current dataframe
                    self.df_es = self.df_es.drop(labels=item, axis=0).reset_index(drop=True)
                except:
                    pass

            self.esMainWindow = NewsMainWindow(self.df_es)
            self.esMainWindow.news_deleted_signal.connect(self.deleted_news)
            self.esMainWindow.dbl_click_item_signal.connect(self.open_link)
            self.tab_control(self.esMainWindow, 'Eksisozluk')
        elif self.sender() is self.cumMainWindow:
            # set the news list background color to green when connected, even if there is no new news
            if self.cum_connected:
                self.cumMainWindow.news_list_lw.setStyleSheet(self.ss_con)
            else:
                self.cumMainWindow.news_list_lw.setStyleSheet(self.ss_discon)

            for item in del_list:
                try:
                    del_link = self.df_cum['Link'][item]
                    self.cum_del_news.append(del_link)
                    self.cum_cur_news.remove(del_link)
                    self.df_cum = self.df_cum.drop(labels=item, axis=0).reset_index(drop=True)
                except:
                    pass

            self.cumMainWindow = NewsMainWindow(self.df_cum)
            self.cumMainWindow.news_deleted_signal.connect(self.deleted_news)
            self.cumMainWindow.dbl_click_item_signal.connect(self.open_link)
            self.tab_control(self.cumMainWindow, 'Cumhuriyet')
        elif self.sender() is self.htMainWindow:
            for item in del_list:
                try:
                    del_link = self.df_ht['Link'][item]
                    self.ht_del_news.append(del_link)
                    self.ht_cur_news.remove(del_link)
                    self.df_ht = self.df_ht.drop(labels=item, axis=0).reset_index(drop=True)
                except:
                    pass

            self.htMainWindow = NewsMainWindow(self.df_ht)
            self.htMainWindow.news_deleted_signal.connect(self.deleted_news)
            self.htMainWindow.dbl_click_item_signal.connect(self.open_link)
            self.tab_control(self.htMainWindow, 'Haberturk')

    # open a web page when doubleclicking an item in the list widget
    def open_link(self, data):
        link = False
        if self.sender() is self.esMainWindow:
            link = self.df_es['Link'][data] + '1'
        elif self.sender() is self.cumMainWindow:
            link = self.df_cum['Link'][data]
        elif self.sender() is self.htMainWindow:
            link = self.df_ht['Link'][data]

        QDesktopServices.openUrl(QUrl(link))

    def remove_tab(self, index):
        if self.tabs.tabText(index) == 'Cumhuriyet':
            self.cumhuriyetAct.setChecked(False)
            self.cum_connected = False
            self.cumhuriyet_timer.stop()
            self.df_cum = pd.DataFrame(columns=['Link', 'Image', 'Headline', 'Spot', 'News text'])
            self.cum_cur_news = []
            self.cum_del_news = []
        elif self.tabs.tabText(index) == 'Haberturk':
            self.haberturkAct.setChecked(False)
            self.ht_connected = False
            self.haberturk_timer.stop()
            self.df_ht = pd.DataFrame(columns=['Link', 'Image', 'Headline', 'Spot', 'News text'])
            self.ht_cur_news = []
            self.ht_del_news = []
        elif self.tabs.tabText(index) == 'Eksisozluk':
            self.eksisozlukAct.setChecked(False)
            self.es_connected = False
            self.eksisozluk_timer.stop()
            self.df_es = pd.DataFrame(columns=['Link', 'Image', 'Headline', 'Spot', 'News text'])
            self.es_cur_news = []
            self.es_del_news = []

        self.tabs.removeTab(index)


if __name__ == '__main__':
    app = QApplication([])
    window = NewsFromWebApp()
    window.showFullScreen()
    app.exit(app.exec_())
