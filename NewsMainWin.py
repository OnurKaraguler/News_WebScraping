import pandas as pd
from PyQt5.QtWidgets import (QApplication, QWidget, QListWidget, QLabel, QSplitter, QFrame, QSizePolicy, QScrollArea,
                             QHBoxLayout, QVBoxLayout, QAbstractItemView, QMenu, QAction)
from PyQt5.QtCore import Qt, QSize, pyqtSignal, QEvent, QRect
from PyQt5.QtGui import (QFont, QImage, QPixmap, QGradient, QColor, QBrush, QPen,
                         QFontMetrics, QPainter, QLinearGradient)
import requests, math


class ListWidget(QListWidget):
    news_clicked_signal = pyqtSignal(int)
    double_clicked_signal = pyqtSignal(int)
    news_deleted_signal = pyqtSignal(list)

    def __init__(self):
        super().__init__()

        self.setIconSize(QSize(124, 124))
        # Multiple items can be selected by pressing Ctrl or shift, or by dragging the mouse
        self.setSelectionMode(QAbstractItemView.ExtendedSelection)
        self.setFont(QFont('Arial', 16))
        # wrap lines along word boundaries
        self.setWordWrap(True)
        self.setStyleSheet("color : white; padding: 20px -10px 20px 0px")
        # all the events are first sent  to the eventFilter() function. 
        self.installEventFilter(self)
        self.itemClicked.connect(self.item_clicked)
        self.itemDoubleClicked.connect(self.item_double_clicked)

        # Right-click menu
        self.setContextMenuPolicy(Qt.CustomContextMenu)
        self.customContextMenuRequested.connect(self.context_menu)

    def context_menu(self, position):
        pop_menu = QMenu()
        del_act = QAction("Delete", self)
        pop_menu.addAction(del_act)
        if self.itemAt(position):
            pop_menu.addAction(del_act)

        del_act.triggered.connect(self.del_news)
        pop_menu.exec_(self.mapToGlobal(position))

    def eventFilter(self, source, event):
        total_items = self.count()
        if event.type() == QEvent.KeyPress:
            if event.key() == Qt.Key_Down:
                new_pos = self.currentRow() + 1
                self.item_rows = [new_pos]
                if (new_pos >= 0) and (new_pos < total_items):
                    self.setCurrentRow(self.currentRow())
                    self.news_clicked_signal.emit(new_pos)
                event.accept()
            elif event.key() == Qt.Key_Up:
                new_pos = self.currentRow() - 1
                self.item_rows = [new_pos]
                if (new_pos >= 0) and (new_pos < total_items):
                    self.setCurrentRow(self.currentRow())
                    self.news_clicked_signal.emit(new_pos)
                event.accept()
            elif event.key() == Qt.Key_Backspace:
                try:
                    self.news_deleted_signal.emit(self.item_rows)
                    self.setCurrentItem(self.item(0))
                except:
                    pass

        return super().eventFilter(source, event)

    # emit when an clicked item row number to display image, spot and text
    def item_clicked(self):
        items = self.selectedItems()
        self.item_rows = []
        for item in items:
            self.item_rows.append(self.row(item))
        self.news_clicked_signal.emit(self.item_rows[0])

    # emit one or more items' row number that will be deleted in the list widget
    def del_news(self):
        self.news_deleted_signal.emit(self.item_rows)

    # emit an item row number to open the web page
    def item_double_clicked(self):
        item = self.row(self.selectedItems()[0])
        self.double_clicked_signal.emit(item)


class LabelText(QLabel):
    def __init__(self, *args, **kwargs):
        QLabel.__init__(self, *args, **kwargs)
        # The sizeHint() is ignored. The widget will get as much space as possible.
        self.setSizePolicy(QSizePolicy.Ignored, QSizePolicy.Ignored)
        self.setAlignment(Qt.AlignTop)
        self.setAlignment(Qt.AlignLeft)
        self.setWordWrap(True)


class LabelHeadline(QLabel):
    def __init__(self, *args, **kwargs):
        QLabel.__init__(self, *args, **kwargs)
        self.setSizePolicy(QSizePolicy.Ignored, QSizePolicy.Ignored)
        self.setAlignment(Qt.AlignTop)
        self.setAlignment(Qt.AlignLeft)
        self.setWordWrap(True)

        self.set_brush(Qt.white)
        self.set_pen(Qt.black)

    def set_brush(self, brush):
        if not isinstance(brush, QBrush):
            brush = QBrush(brush)
        self.brush = brush

    def set_pen(self, pen):
        if not isinstance(pen, QPen):
            pen = QPen(pen)
        pen.setJoinStyle(Qt.RoundJoin)
        self.pen = pen

    def paintEvent(self, event):
        radial_grad = QLinearGradient(0.3, 0.3, 0.8, 0.8)
        radial_grad.setCoordinateMode(QGradient.ObjectBoundingMode)
        radial_grad.setSpread(QGradient.ReflectSpread)
        radial_grad.setColorAt(0, QColor(218, 55, 44))
        radial_grad.setColorAt(1, QColor(236, 139, 71))

        metrics = QFontMetrics(self.font())
        border = max(4, metrics.leading())
        rect = metrics.boundingRect(0, 0, self.width() - 2 * border,
                                    int(self.height() * 0.125),
                                    Qt.AlignCenter | Qt.TextWordWrap, self.text())
        painter = QPainter(self)
        painter.setRenderHint(QPainter.TextAntialiasing)

        painter.setPen(QPen(radial_grad, 5))
        painter.drawText((self.width() - rect.width()) / 2, border, rect.width(),
                         rect.height(), Qt.AlignCenter | Qt.TextWordWrap,
                         self.text())


class NewsMainWindow(QWidget):
    news_deleted_signal = pyqtSignal(list)
    dbl_click_item_signal = pyqtSignal(int)

    def __init__(self, df_web=pd.DataFrame(columns=['Link', 'Image', 'Headline', 'Spot', 'News text']), row=0):
        super().__init__()
        self.setGeometry(200, 100, 1200, 800)
        self.setStyleSheet("background-color : rgb(0,0,0);")
        self.df = df_web
        self.row = row

        self.ui()

    def ui(self):
        self.widgets()
        self.layout()

        # signals emitted from the list widget
        self.news_list_lw.news_clicked_signal.connect(self.sel_item)
        self.news_list_lw.news_deleted_signal.connect(self.del_item)
        self.news_list_lw.double_clicked_signal.connect(self.dbl_click_item)

    def widgets(self):
        # ---> left frame
        self.news_list_lw = ListWidget()
        stylesheet = '''background-color: qlineargradient(x1:0.1 y1:0.1, x2:0.9 y2:0.9, stop: 0 rgb(84, 166, 71), 
        stop: 1 rgb(00, 00, 00)); padding: 10px 0px 10px 00px; color : rgb(255,255,255)'''
        self.news_list_lw.setStyleSheet(stylesheet)

        self.left_frame_lay = QVBoxLayout()
        self.left_frame_lay.addWidget(self.news_list_lw)

        # ---> right frame
        # image
        self.image_l = QLabel()
        self.image_l.setFixedSize(300, 150)

        # headline
        self.headline_l = LabelHeadline()
        self.headline_l.setFont(QFont('Arial', 25))

        self.scrollArea_headline = QScrollArea()
        self.scrollArea_headline.setWidgetResizable(True)
        self.scrollArea_headline.setWidget(self.headline_l)

        # spot
        self.spot_l = LabelText()
        self.spot_l.setStyleSheet("color : rgb(127,237,120); background-color : rgb(0,0,0); padding: 10px 0px 10px 00px")
        self.spot_l.setFont(QFont('Helvetica Neue', 20))
        self.scrollArea_spot = QScrollArea()
        self.scrollArea_spot.setWidgetResizable(True)
        self.scrollArea_spot.setWidget(self.spot_l)

        # ---> right bottom frame
        self.news_texts_l = LabelText()
        self.news_texts_l.setStyleSheet("color : rgb(161,161,166); background-color : rgb(0,0,0); padding: 10px 0px 10px 00px")
        self.news_texts_l.setFont(QFont('Helvetica Neue', 24))
        self.scrollArea = QScrollArea()
        self.scrollArea.setWidgetResizable(True)
        self.scrollArea.setWidget(self.news_texts_l)

        self.right_frame_image = QVBoxLayout()
        self.right_frame_image.addWidget(self.image_l)

        self.right_frame_headline_and_spot = QVBoxLayout()
        self.right_frame_headline_and_spot.addWidget(self.scrollArea_headline)
        self.right_frame_headline_and_spot.addWidget(self.scrollArea_spot)

        self.right_top_frame_lay = QHBoxLayout()
        self.right_top_frame_lay.addLayout(self.right_frame_image)
        self.right_top_frame_lay.addLayout(self.right_frame_headline_and_spot)
        self.right_bot_frame_lay = QHBoxLayout()
        self.right_bot_frame_lay.addWidget(self.scrollArea)

        # --> downloaded data
        try:
            # add news headlines to the list widget
            news_list = self.df['Headline']
            self.news_list_lw.addItems(news_list)

            # display the first news' image
            url_image = self.df['Image'][0]
            image = QImage()
            image.loadFromData(requests.get(url_image).content)
            pixmap = QPixmap(image)
            scaled = pixmap.scaled(self.image_l.size(), Qt.KeepAspectRatio)
            self.image_l.setPixmap(scaled)

            # display the first news' headline
            text_headline = self.df['Headline'][0]
            self.headline_l.setText(str(text_headline))

            # display the first news' spot
            text_spot = self.df['Spot'][0]
            self.spot_l.setText(str(text_spot))

            # display the first news' text
            news_texts = self.df['News text'][0]
            self.news_texts_l.setText(str(news_texts))
            self.news_list_lw.setEnabled(True)
        except:
            pass

    def layout(self):
        self.mainLayout = QHBoxLayout()

        split_1 = QSplitter()
        split_1.setOrientation(Qt.Horizontal)
        left_frame = QFrame(split_1)
        left_frame.setFrameShape(QFrame.StyledPanel)
        left_frame.setMaximumWidth(300)
        left_frame.setLayout(self.left_frame_lay)

        split_2 = QSplitter(split_1)
        split_2.setOrientation(Qt.Vertical)
        right_top_frame = QFrame(split_2)
        right_top_frame.setFrameShape(QFrame.StyledPanel)
        right_top_frame.setMaximumHeight(180)
        right_top_frame.setLayout(self.right_top_frame_lay)

        split_3 = QSplitter(split_2)
        split_3.setOrientation(Qt.Vertical)
        right_bot_frame = QFrame(split_3)
        right_bot_frame.setFrameShape(QFrame.StyledPanel)
        right_bot_frame.setLayout(self.right_bot_frame_lay)

        self.mainLayout.addWidget(split_1)
        self.setLayout(self.mainLayout)

    # method to display image, spot and text when an item is clicked in the list widget
    # the signal comes from the list widget
    def sel_item(self, data):
        if data >= 0:
            try:
                url_image = self.df['Image'][data]
                image = QImage()
                image.loadFromData(requests.get(url_image).content)
                pixmap = QPixmap(image)
                scaled = pixmap.scaled(self.image_l.size(), Qt.KeepAspectRatio)
                self.image_l.setPixmap(scaled)

                text_headline = self.df['Headline'][data]
                self.headline_l.setText(str(text_headline))
                text_spot = self.df['Spot'][data]
                self.spot_l.setText(str(text_spot))
                news_texts = self.df['News text'][data]
                self.news_texts_l.setText(str(news_texts))
            except:
                pass

    # emit one or more items' row number that will be deleted in the list widget
    # the signal comes from the list widget
    def del_item(self, data):
        self.news_deleted_signal.emit(data)

    # emit an item row number to open the web page
    # the signal comes from the list widget
    def dbl_click_item(self, data):
        self.dbl_click_item_signal.emit(data)

