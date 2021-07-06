from PyQt5.QtWidgets import (QMainWindow, QApplication, QAction, QLabel, QPushButton, QTabBar,
                             QTabWidget, QToolBar, QMenu, QShortcut, QStyleOptionTab, QStyle)
from PyQt5.QtCore import Qt, QSize, pyqtSignal
from PyQt5.QtGui import QIcon, QColor, QKeySequence, QPainter


class Menu(QMenu):

    def __init__(self, parent=None):
        super(Menu, self).__init__(parent)
        self.setStyleSheet("""
                    QMenu{
                    font-size: 14px; font-weight: bold; color: #000000;
                    background-color: orange;
                    font: Helvetica Neue;
                    }
                    QMenu::item:selected {
                        background-color: rgb(52,73,94);
                        border-top: none;
                        border-left:none;
                        border-bottom:none;
                        border-left:3px solid  rgb(44,205,112);;
                    }""")


class MainEditableTabBar(QTabBar):
    tabBarRemoveSignal = pyqtSignal(int)

    def __init__(self, parent):
        QTabBar.__init__(self, parent)
        self.setMouseTracking(True)
        self.setStyleSheet('''
                        QTabBar{
                                width: 100px; height: 20px;
                                font-family: Helvetica Neue;
                                color: rgb(52, 39, 152);
                                font:16pt Arial, sans-serif;
                                background-color: rgb(00, 00, 00);
                                padding: 6px 6px;
                                }
                        QTabBar::tab {
                                width: 100px; height: 20px;
                                font-family: Helvetica Neue;
                                font-size: 16;
                                background: rgb(52, 39, 152);
                                color: rgb(255, 255, 255);
                                padding: 6px 6px;
                                border-top-left-radius: 12px;
                                border-bottom-left-radius: 12px;
                                border-top-right-radius: 12px;
                                border-bottom-right-radius: 12px;
                                margin-left:4px;
                                margin-right:4px;
                                margin-bottom:6px;
                                    }
                        QTabBar::tab:selected {
                                width: 100px; height: 20px;
                                font-family: Helvetica Neue;
                                font-size: 18px;font-weight: bold; color: #00ff00;
                                background-color: rgb(233, 83, 148);
                                padding: 6px 6px;
                                                }
                        QTabBar::tab:hover {
                                font-size: 18px;font-weight: bold; color: #00ff00;
                                padding: 6px 6px;
                                                }
                           ''')
    # Right-click menu on the tab bar
    def mousePressEvent(self, event):
        index = self.tabAt(event.pos())
        point = event.pos()
        if event.button() == Qt.RightButton:
            menu_right = Menu(self)
            del_act = QAction("Delete")
            del_act.triggered.connect(lambda state, x=index: self.del_item(x))
            menu_right.addAction(del_act)
            menu_right.exec_(self.mapToGlobal(point))

        super().mousePressEvent(event)

    # emit the tab index number to be deleted
    def del_item(self, index):
        self.tabBarRemoveSignal.emit(index)


class MainTabWidget(QTabWidget):
    tabWidgetRemoveSignal = pyqtSignal(int)

    def __init__(self):
        QTabWidget.__init__(self)
        self.editableTabBar = MainEditableTabBar(self)
        self.setTabBar(self.editableTabBar)
        self.setTabPosition(QTabWidget.South)

        self.editableTabBar.tabBarRemoveSignal.connect(self.del_item)

    # emit the tab index number to be deleted
    # the signal comes from the tab widget
    def del_item(self, index):
        self.tabWidgetRemoveSignal.emit(index)


class ToolBar(QToolBar):

    def __init__(self, parent=None):
        super(ToolBar, self).__init__(parent)
        stylesheet = '''
            QToolBar {
            background: #292C31;
            border: none;
            }
            QToolBar QToolButton{
            background-color: #292C31;
            }
            QToolBar QToolButton:hover {
            background-color: rgb(233, 83, 148);
            }
        '''
        self.setStyleSheet(stylesheet)


class WebScrMainWindow(QMainWindow):

    def __init__(self):
        super().__init__()
        self.setWindowTitle('Applications')
        self.setGeometry(0, 0, 1600, 800)
        self.setStyleSheet("background-color : rgb(0,0,0);")

        # switch tab forwards by pressing tab key
        shortcut_tab = QShortcut(QKeySequence(Qt.Key_Tab), self)
        shortcut_tab.activated.connect(self.tab_change)
        # switch tab backwards by pressing tab key
        shortcut_shifttab = QShortcut(QKeySequence('shift+tab'), self)
        shortcut_shifttab.activated.connect(self.tab_back_change)

        self.ui()
        self.show()

    def ui(self):
        self.main_menu()
        self.applications()
        self.toolbar_menu()

    def main_menu(self):
        self.menuBar = self.menuBar()
        self.menuBar.setStyleSheet("background: #292C31; color: #CFCFCF")

        self.statusBar()
        self.status_bar_samples()

        self.tabs = MainTabWidget()
        self.setCentralWidget(self.tabs)

    def applications(self):
        self.apps = self.menuBar.addMenu('Apps')
        ########################################
        self.cumhuriyetAct = QAction(QIcon('icons/cumhuriyet.icns'), 'Cumhuriyet', self)
        # set the action checkable
        self.cumhuriyetAct.setCheckable(True)
        self.cumhuriyetAct.setShortcut('c')
        self.cumhuriyetAct.setStatusTip('News from cumhuriyet.com')
        self.apps.addAction(self.cumhuriyetAct)

        self.haberturkAct = QAction(QIcon('icons/haberturk.icns'), 'Haberturk', self)
        # set the action checkable
        self.haberturkAct.setCheckable(True)
        self.haberturkAct.setShortcut('h')
        self.haberturkAct.setStatusTip('News from haberturk.com')
        self.apps.addAction(self.haberturkAct)

        self.eksisozlukAct = QAction(QIcon('icons/eksisozluk.icns'), 'Eksisozluk', self)
        # set the action checkable
        self.eksisozlukAct.setCheckable(True)
        self.eksisozlukAct.setShortcut('e')
        self.eksisozlukAct.setStatusTip('News from eksisozluk.com')
        self.apps.addAction(self.eksisozlukAct)

    def toolbar_menu(self):
        tb_width = 50
        # tb_height = 50
        icon_width = 26
        icon_height = 30

        self.tb_apps = ToolBar("Applications")
        self.addToolBar(self.tb_apps)
        self.tb_apps.setIconSize(QSize(icon_width, icon_height))
        self.tb_apps.setFixedWidth(tb_width)
        # move the toolbar within the toolbar area
        self.tb_apps.setMovable(False)
        # self.tb_apps.setToolButtonStyle(Qt.ToolButtonTextUnderIcon)
        # self.toolbar.setFixedSize(640, 64)
        self.tb_apps.setIconSize(QSize(100, 50))
        # add the toolbar to the left side of the main window
        self.addToolBar(Qt.LeftToolBarArea, self.tb_apps)

        # #####################Toolbar Buttons###################
        self.tb_apps.addAction(self.cumhuriyetAct)
        self.tb_apps.addAction(self.haberturkAct)
        self.tb_apps.addAction(self.eksisozlukAct)

    def status_bar_samples(self):
        self.dolar_l = QLabel("Label: ")
        self.dolar_l.setStyleSheet('border: 0; color:  red; font:14pt Arial, sans-serif;')
        self.euro_l = QLabel("Data : ")
        self.euro_l.setStyleSheet('border: 0; color:  yellow; font:14pt Arial, sans-serif;')

        self.statusBar().setStyleSheet(
            'border: 0; '
            'background-color: #171719;'
            'color: #A9AAAC;'
            'font:18pt Arial, sans-serif;'
            'height: 30;')

        # permanently display messages permanently on the status bar 
        self.statusBar().addPermanentWidget(self.dolar_l)
        self.statusBar().addPermanentWidget(self.euro_l)

        self.dolar_l.setText("DOLAR: 0,0000")
        self.euro_l.setText("EURO : 0,0000")

    def tab_change(self):
        tab_count = self.tabs.count()
        cur_ind = self.tabs.currentIndex()
        next_ind = cur_ind + 1
        if next_ind < tab_count:
            self.tabs.setCurrentIndex(next_ind)
        else:
            self.tabs.setCurrentIndex(0)

    def tab_back_change(self):
        tab_count = self.tabs.count()
        cur_ind = self.tabs.currentIndex()
        pre_ind = cur_ind - 1
        if pre_ind >= 0:
            self.tabs.setCurrentIndex(pre_ind)
        else:
            self.tabs.setCurrentIndex(tab_count - 1)


if __name__ == '__main__':
    app = QApplication([])
    app.setApplicationName("Internet News Channels")
    window = WebScrMainWindow()
    window.showFullScreen()
    app.exit(app.exec_())
