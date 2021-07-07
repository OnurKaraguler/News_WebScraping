## News_WebScraping

The application is used to scrape articles from news websites. It will be possible to read the current news quickly without visiting the websites. Thus, the time spent to follow the agenda will decrease.<br>

The websites to be scraped are well-known news websites and a popular forum website in Turkey.<br>
https://www.cumhuriyet.com.tr <br>
https://www.haberturk.com<br>
https://eksisozluk.com<br>

The main window shown below has been created by using PyQt5. Requests and BeautifulSoup are used for extracting news data from the websites. The news are stored and filtered in a dataframe by using Pandas.

<img height="200" src="https://user-images.githubusercontent.com/58983814/124748582-f875f580-df2b-11eb-8893-953aeadebdb8.png">

### How does it work?
We start to receive news by pressing the buttons in the menu or by pressing the shortcuts(C, H and E) on the keyboard. Nearly 70 news are downloaded in about 30 seconds by pressing the buttons one by one without waiting. Each news in the current news list contains its own image, headline, spot and text.

<img height="200" src="https://user-images.githubusercontent.com/58983814/124751376-3a546b00-df2f-11eb-99c7-d0598791fa9e.png">  <img height="200" src="https://user-images.githubusercontent.com/58983814/124755116-a33de200-df33-11eb-8bd8-3a485e175307.png"> 

Initially, the current news list color is green, meaning the application checks for new news every minute. If a new news is published on the website, it is added to the end of the list. When desired, the connection can be closed or reconnected by pressing the button or the related shortcut again. The list color turns purple when the connection is closed.

<img height="200" src="https://user-images.githubusercontent.com/58983814/124772664-e81e4480-df44-11eb-97aa-c50ba11ab5ba.png">

It is possible to scroll through the news by pressing the news in the list or by pressing the up/down arrow keys on the keyboard. Selected news can be deleted by pressing the Backspace key of the keyboard or by pressing the delete key from the right-click menu. Multiple selections can be made and deleted from the list by pressing the control key or the shift key. Since the deleted news will be in the memory of the application, it will not be added to the list again in the next connection.

<img height="200" src="https://user-images.githubusercontent.com/58983814/124773383-9629ee80-df45-11eb-9546-bcb752a9f93c.png"> <img height="200" src="https://user-images.githubusercontent.com/58983814/124774635-a2fb1200-df46-11eb-94f2-9a752564ceba.png"> <img height="200" src="https://user-images.githubusercontent.com/58983814/124774898-d50c7400-df46-11eb-8379-cb4deed88942.png"> <img height="200" src="https://user-images.githubusercontent.com/58983814/124775072-fc634100-df46-11eb-9726-fcc3b800f129.png">

The dollar and euro values will be updated with each new connection. <br>
<img height="50" src="https://user-images.githubusercontent.com/58983814/124776644-47ca1f00-df48-11eb-9f21-f7f6adaf92eb.png">

Tabs can be switched forwards by pressing tab key and backwards by pressing shift+tab key on the keyboard. A news tab can be deleted by right-clicking on it and clicking the delete button.

<img height="50" src="https://user-images.githubusercontent.com/58983814/124777243-bc04c280-df48-11eb-9e4f-b6b16f1cd443.png"> <img height="50" src="https://user-images.githubusercontent.com/58983814/124780316-2b7bb180-df4b-11eb-87bb-7ed3ce081999.png">











