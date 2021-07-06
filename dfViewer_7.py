import sys
import pandas as pd

import numpy as np
from IPython.external.qt_for_kernel import QtCore
from PyQt5.QtWidgets import (QApplication, QGridLayout, QTableView, QSizePolicy, QAbstractItemView, QSpacerItem,
                             QStyledItemDelegate, QStyleOptionViewItem, QStyle, QFrame, QMenu, QAction, QWidget)
from PyQt5.QtCore import (pyqtSignal, QAbstractTableModel, Qt, QVariant, QSize, QRect, QModelIndex, QObject, QEvent,
                          QItemSelection,
                          QItemSelectionModel)
from PyQt5.QtGui import QColor, QFont, QShowEvent, QPainter, QCursor

import sys

sys.path.append('')
from standardWidgets import (GraphTableView, Widget, Splitter, Frame)
import style

total_column_width = 0
total_row_height = 0


class DataFrameViewer(Widget):
    sel_colsRowsSignal = pyqtSignal(list)
    sort_colsRowsSignal = pyqtSignal(str)

    def __init__(self, df=pd.DataFrame(), parent=None):
        super().__init__()
        self.df = df
        # Indicates whether the widget has been shown yet. Set to True in
        self._loaded = False

        # Set up DataFrame TableView and Model
        self.dataView = DataTableView(self.df)

        # Create headers
        self.columnHeader = HeaderView(self.df, orientation=Qt.Horizontal)
        self.indexHeader = HeaderView(self.df, orientation=Qt.Vertical)

        self.columnHeaderNames = HeaderNamesView(
            self.df, orientation=Qt.Horizontal)
        self.indexHeaderNames = HeaderNamesView(
            self.df, orientation=Qt.Vertical)

        # Set up layout
        self.gridLayout = QGridLayout()
        self.gridLayout.setContentsMargins(0, 0, 0, 0)
        self.gridLayout.setSpacing(0)
        self.setLayout(self.gridLayout)

        # Linking scrollbars
        # Scrolling in data table also scrolls the headers
        self.dataView.horizontalScrollBar().valueChanged.connect(
            self.columnHeader.horizontalScrollBar().setValue)
        self.dataView.verticalScrollBar().valueChanged.connect(
            self.indexHeader.verticalScrollBar().setValue)
        # Scrolling in headers also scrolls the data table
        self.columnHeader.horizontalScrollBar().valueChanged.connect(
            self.dataView.horizontalScrollBar().setValue)
        self.indexHeader.verticalScrollBar().valueChanged.connect(
            self.dataView.verticalScrollBar().setValue)
        # Turn off default scrollbars
        self.dataView.setHorizontalScrollBarPolicy(Qt.ScrollBarAlwaysOff)
        self.dataView.setVerticalScrollBarPolicy(Qt.ScrollBarAlwaysOff)
        # Disable scrolling on the headers. Even though the scrollbars are hidden, scrolling by dragging desyncs them
        self.indexHeader.horizontalScrollBar().valueChanged.connect(lambda: None)

        self.columnHeader.selColsRowsSignal.connect(self.selColsRows)
        self.indexHeader.selColsRowsSignal.connect(self.selColsRows)

        self.columnHeader.sortColsRowsSignal.connect(self.sortColsRows)
        self.indexHeader.sortColsRowsSignal.connect(self.sortColsRows)

        class CornerWidget(QWidget):
            def __init__(self):
                super().__init__()
                # https://stackoverflow.com/questions/32313469/stylesheet-in-pyside-not-working
                self.setAttribute(Qt.WA_StyledBackground)
                self.setStyleSheet('''
                    QWidget  {
                    font:10pt Arial, sans-serif;
                    background-color: #25282C;
                    color: #A9AAAC;
                    selection-background-color: #043E4B;
                    selection-color: #A9AAAC;
                    }''')

        self.corner_widget = CornerWidget()
        self.corner_widget.setSizePolicy(QSizePolicy(
            QSizePolicy.Expanding, QSizePolicy.Expanding))

        # Add items to grid layout
        self.gridLayout.addWidget(self.corner_widget, 0, 0)
        self.gridLayout.addWidget(self.columnHeader, 0, 1, 2, 2)
        self.gridLayout.addWidget(self.columnHeaderNames, 0, 3, 2, 1)
        self.gridLayout.addWidget(self.indexHeader, 2, 0, 2, 2)
        self.gridLayout.addWidget(
            self.indexHeaderNames, 1, 0, 1, 1, Qt.AlignBottom)
        self.gridLayout.addWidget(self.dataView, 3, 2, 1, 1)
        self.gridLayout.addWidget(
            self.dataView.horizontalScrollBar(), 4, 2, 1, 1)
        # self.gridLayout.addWidget(self.dataView.verticalScrollBar(), 3, 3, 1, 1)

        # These expand when the window is enlarged instead of having the grid squares spread out
        self.gridLayout.setColumnStretch(4, 1)
        self.gridLayout.setRowStretch(5, 1)

        # self.gridLayout.addItem(QSpacerItem(0, 0, QSizePolicy.Expanding, QSizePolicy.Expanding), 0, 0, 1, 1, )

        self.set_styles()
        self.indexHeader.setSizePolicy(
            QSizePolicy.MinimumExpanding, QSizePolicy.Maximum)
        self.columnHeader.setSizePolicy(
            QSizePolicy.Maximum, QSizePolicy.MinimumExpanding)

    def selColsRows(self, data):
        selRows = data[0]
        selCols = data[1]
        colRowList = [selRows, selCols]
        self.sel_colsRowsSignal.emit(colRowList)

    def sortColsRows(self, data):
        # col_or_row = data
        # # selCols = data[1]
        # # colRowList = [selRows, selCols]
        self.sort_colsRowsSignal.emit(data)

    def set_styles(self):

        for item in [self.dataView, self.columnHeader, self.indexHeader, self.indexHeaderNames, self.columnHeaderNames]:
            item.setContentsMargins(0, 0, 0, 0)
            # item.setItemDelegate(NoFocusDelegate())

        # Style table data cells
        # self.dataView.setStyleSheet(self.dataView.styleSheet() + "")

        # # Style header cells
        # for header in [self.columnHeader, self.indexHeader]:
        #     header.setStyleSheet(header.styleSheet() + ";")

        # # Style header level name labels
        # for header_label in [self.indexHeaderNames, self.columnHeaderNames]:
        #     header_label.setStyleSheet(header_label.styleSheet() + "")

    def __reduce__(self):
        # This is so dataclasses.asdict doesn't complain about this being unpicklable
        return "DataFrameViewer"

    def showEvent(self, event: QShowEvent):
        global total_column_width
        global total_row_height

        if not self._loaded:
            # Set column widths
            total_column_width = 0
            for column_index in range(len(self.df.columns)):
                width = self.auto_size_column(column_index)
                # print(width)
                total_column_width += width

            total_row_height = 0
            for row_index in range(len(self.df.index)):
                height = self.auto_size_row(row_index)
                total_row_height += height

        self._loaded = True
        event.accept()

    def auto_size_column(self, column_index):
        padding = 5
        self.columnHeader.resizeColumnToContents(column_index)
        width = self.columnHeader.columnWidth(column_index)
        for i in range(len(self.df.index)):
            mi = self.dataView.model().index(i, column_index)
            text = self.dataView.model().data(mi)
            w = self.dataView.fontMetrics().boundingRect(text).width()
            width = max(width, w)
        width += padding

        # add maximum allowable column width so column is never too big.
        max_allowable_width = 200
        width = min(width, max_allowable_width)

        self.columnHeader.setColumnWidth(column_index, width)
        self.dataView.setColumnWidth(column_index, width)

        self.dataView.updateGeometry()
        self.columnHeader.updateGeometry()
        return width

    def auto_size_row(self, row_index):
        padding = 5
        self.indexHeader.resizeRowToContents(row_index)
        height = self.indexHeader.rowHeight(row_index)
        for i in range(len(self.df.columns)):
            mi = self.dataView.model().index(row_index, i)
            text = self.dataView.model().data(mi)
            h = self.dataView.fontMetrics().boundingRect(text).height()
            height = max(height, h)
        height += padding

        # # add maximum allowable column width so column is never too big.
        max_allowable_height = 100
        height = min(height, max_allowable_height)

        self.indexHeader.setRowHeight(row_index, height)
        self.dataView.setRowHeight(row_index, height)
        return height

        self.dataView.updateGeometry()
        self.columnHeader.updateGeometry()


# Remove dotted border on cell focus.  https://stackoverflow.com/a/55252650/3620725
class NoFocusDelegate(QStyledItemDelegate):
    def paint(
            self,
            painter: QPainter,
            item: QStyleOptionViewItem,
            ix: QModelIndex,
    ):
        if item.state & QStyle.State_HasFocus:
            item.state = item.state ^ QStyle.State_HasFocus
        super().paint(painter, item, ix)


class DataTableView(QTableView):
    def __init__(self, df=pd.DataFrame()):
        super().__init__()
        self.setStyleSheet(style.tableViewStyle())

        self.df = df

        # Create and set model
        model = DataTableModel(self.df)
        self.setModel(model)

        # Hide the headers. The DataFrame headers (index & columns) will be displayed in the DataFrameHeaderViews
        self.horizontalHeader().hide()
        self.verticalHeader().hide()

        # # Link selection to headers
        # self.selectionModel().selectionChanged.connect(self.on_selectionChanged)

        # Settings
        # self.setWordWrap(True)
        # self.resizeRowsToContents()
        self.setHorizontalScrollMode(QAbstractItemView.ScrollPerPixel)
        self.setVerticalScrollMode(QAbstractItemView.ScrollPerPixel)

    def sizeHint(self):
        # Set width and height based on number of columns in model
        # Width
        width = 2 * self.frameWidth()  # Account for border & padding
        # width += self.verticalScrollBar().width()  # Dark theme has scrollbars always shown
        for i in range(len(self.df.columns)):
            width += self.columnWidth(i)

        # Height
        height = 2 * self.frameWidth()  # Account for border & padding
        # height += self.horizontalScrollBar().height()  # Dark theme has scrollbars always shown
        for i in range(len(self.df.index)):
            height += self.rowHeight(i)

        return QSize(width, height)

    # def sizeHint(self):
    #     global total_column_width
    #     width = total_column_width
    #     # Set width and height based on number of columns in model
    #     # Width
    #     # width = 2 * self.frameWidth()  # Account for border & padding
    #     # width += self.verticalScrollBar().width()  # Dark theme has scrollbars always shown
    #     # for i in range(len(self.df.columns)):
    #     # # for i in range(self.model().columnCount()):
    #     #     width += self.columnWidth(i)

    #     # Height
    #     height = 2 * self.frameWidth()  # Account for border & padding
    #     # height += self.horizontalScrollBar().height()  # Dark theme has scrollbars always shown
    #     for i in range(len(self.df.index)):
    #         height += self.rowHeight(i)

    #     return QSize(width, height)


class DataTableModel(QAbstractTableModel):
    """
    Model for DataTableView to connect for DataFrame data
    """

    def __init__(self, df):
        super().__init__()

        self.df = df
        self.colors = dict()

    # ------------- table display functions -----------------

    def rowCount(self, index):
        return self.df.shape[0]

    def columnCount(self, index):
        return self.df.shape[1]

    # Returns the data from the DataFrame
    def data(self, index, role=Qt.DisplayRole):
        row = index.row()
        col = index.column()
        cell = self.df.iloc[row, col]
        if index.isValid():
            if (role == Qt.DisplayRole
                    or role == Qt.EditRole
                    or role == Qt.ToolTipRole):
                # Need to check type since a cell might contain a list or Series, then .isna returns a Series not a bool
                cell_is_na = pd.isna(cell)
                if type(cell_is_na) == bool and cell_is_na:
                    return ""

                # Float formatting
                if isinstance(cell, float):
                    if not role == Qt.ToolTipRole:
                        return "{:.2f}".format(cell)

                if isinstance(cell, float):
                    return Qt.AlignVCenter + Qt.AlignRight

                # if isinstance(cell, int) or isinstance(cell, float):
                #     # Align right, vertical middle.
                #     return Qt.AlignVCenter + Qt.AlignRight

                return str(cell)

            if role == Qt.BackgroundRole:
                color = self.colors.get((row, cell))
                if color is not None:
                    return color
            if role == Qt.TextColorRole:
                return QVariant(QColor(169, 170, 172))

            if role == Qt.BackgroundRole:
                if row % 2:
                    return QVariant(QColor(41, 44, 49))
                else:
                    return QVariant(QColor(23, 23, 25))

            if role == Qt.TextAlignmentRole:
                value = self.df.iloc[row, col]

        elif role == Qt.ToolTipRole:
            return str(cell)

    def flags(self, index):
        flags = super(self.__class__, self).flags(index)
        flags |= Qt.ItemIsEditable
        flags |= Qt.ItemIsSelectable
        flags |= Qt.ItemIsEnabled
        # flags |= Qt.ItemIsDragEnabled
        # flags |= Qt.ItemIsDropEnabled
        return flags


class HeaderView(QTableView):
    selColsRowsSignal = pyqtSignal(list)
    sortColsRowsSignal = pyqtSignal(str)
    """
    Displays the DataFrame index or columns depending on orientation
    """

    def __init__(self, df=pd.DataFrame(), orientation=None):
        super().__init__()

        # self.setStyleSheet(style.tableViewStyle())

        self.df = df
        self.setProperty('orientation', 'horizontal' if orientation ==
                                                        1 else 'vertical')  # Used in stylesheet

        # Setup
        self.orientation = orientation
        self.table = DataTableView(self.df)
        # self.table = parent.dataView
        self.setModel(HeaderModel(self.df, orientation))
        # These are used during column resizing
        self.drag_size = 0
        self.header_being_resized = None
        self.resize_start_position = None
        self.initial_header_size = None

        # Handled by self.eventFilter()
        self.setMouseTracking(True)
        self.viewport().setMouseTracking(True)
        self.viewport().installEventFilter(self)

        # Settings
        self.setSizePolicy(QSizePolicy(
            QSizePolicy.Maximum, QSizePolicy.Maximum))
        self.setWordWrap(False)
        self.horizontalHeader().hide()
        self.setHorizontalScrollBarPolicy(Qt.ScrollBarAlwaysOff)
        self.setHorizontalScrollMode(QAbstractItemView.ScrollPerPixel)
        self.verticalHeader().hide()
        self.setVerticalScrollBarPolicy(Qt.ScrollBarAlwaysOff)
        self.setVerticalScrollMode(QAbstractItemView.ScrollPerPixel)

        font = QFont()
        font.setBold(True)
        self.setFont(font)

        cor = """QTableView  {
            font: 14pt Arial, sans-serif;
            color: #A9AAAC;
            selection-background-color: #043E4B;
            selection-color: #A9AAAC;
            }
            QToolTip {font:14pt Arial;background-color: orange;
            color: #171719;border: black solid 1px}
            """

        self.setStyleSheet(cor)

        # Link selection to DataTable
        self.selectionModel().selectionChanged.connect(self.on_selectionChanged)
        self.set_spans()
        self.init_column_sizes()

        # Set initial size
        self.resize(self.sizeHint())

        # self.on_selectionChanged()

    def mousePressEvent(self, event):
        point = event.pos()
        ix = self.indexAt(point)

        if event.button() == Qt.LeftButton:
            self.on_selectionChanged()

        elif event.button() == Qt.RightButton:
            if self.orientation == Qt.Horizontal:
                menuHor = QMenu(self)
                editCol_act = QAction("Edit Column")
                editCol_act.triggered.connect(self.rowCol_sorting)
                orderCol_act = QAction("Order Columns")
                orderCol_act.triggered.connect(self.rowCol_sorting)
                ascCol_act = QAction("Columns ascending")
                ascCol_act.triggered.connect(self.rowCol_sorting)
                desCol_act = QAction("Columns descending")
                desCol_act.triggered.connect(self.rowCol_sorting)
                menuHor.addAction(editCol_act)
                menuHor.addAction(orderCol_act)
                menuHor.addAction(ascCol_act)
                menuHor.addAction(desCol_act)
                menuHor.exec_(self.mapToGlobal(point))
            else:
                menuVer = QMenu(self)
                editRow_act = QAction("Edit Row")
                editRow_act.triggered.connect(self.rowCol_sorting)
                orderRow_act = QAction("Order Rows")
                orderRow_act.triggered.connect(self.rowCol_sorting)
                resetIndex_act = QAction("Reset Index")
                resetIndex_act.triggered.connect(self.rowCol_sorting)
                ascRow_act = QAction("Index ascending")
                ascRow_act.triggered.connect(self.rowCol_sorting)
                desRow_act = QAction("Index descending")
                desRow_act.triggered.connect(self.rowCol_sorting)
                menuVer.addAction(editRow_act)
                menuVer.addAction(orderRow_act)
                menuVer.addAction(resetIndex_act)
                menuVer.addAction(ascRow_act)
                menuVer.addAction(desRow_act)
                menuVer.exec_(self.mapToGlobal(point))

        super().mousePressEvent(event)

    def rowCol_sorting(self):
        sender = self.sender().text()
        self.sortColsRowsSignal.emit(sender)

    # Header
    def on_selectionChanged(self):
        selected_columns = [column.column()
                            for column in self.selectionModel().selectedColumns()]
        selected_rows = [row.row()
                         for row in self.selectionModel().selectedRows()]
        selColsRowsList = [selected_rows, selected_columns]
        self.selColsRowsSignal.emit(selColsRowsList)

        """
        Runs when cells are selected in the Header. This selects columns in the data table when the header is clicked,
        and then calls selectAbove()
        """
        # Check focus so we don't get recursive loop, since headers trigger selection of data cells and vice versa
        if self.hasFocus():
            dataView = self.parent().dataView

            # Set selection mode so selecting one row or column at a time adds to selection each time
            if (
                    self.orientation == Qt.Horizontal
            ):  # This case is for the horizontal header
                # Get the header's selected columns
                selection = self.selectionModel().selection()

                self.selected_columns = [
                    column.column() for column in self.selectionModel().selectedColumns()]

                # Removes the higher levels so that only the lowest level of the header affects the data table selection
                last_row_ix = self.df.columns.nlevels - 1
                last_col_ix = self.model().columnCount() - 1
                higher_levels = QItemSelection(
                    self.model().index(0, 0),
                    self.model().index(last_row_ix - 1, last_col_ix),
                )
                selection.merge(higher_levels, QItemSelectionModel.Deselect)

                # Select the cells in the data view
                dataView.selectionModel().select(
                    selection,
                    QItemSelectionModel.Columns
                    | QItemSelectionModel.ClearAndSelect,
                )
            if self.orientation == Qt.Vertical:
                selection = self.selectionModel().selection()

                last_row_ix = self.model().rowCount() - 1
                last_col_ix = self.df.index.nlevels - 1
                higher_levels = QItemSelection(
                    self.model().index(0, 0),
                    self.model().index(last_row_ix, last_col_ix - 1),
                )
                selection.merge(higher_levels, QItemSelectionModel.Deselect)

                dataView.selectionModel().select(selection, QItemSelectionModel.Rows |
                                                 QItemSelectionModel.ClearAndSelect, )

        self.selectAbove()

    # Take the current set of selected cells and make it so that any spanning cell above a selected cell is selected too
    # This should happen after every selection change
    def selectAbove(self):
        if self.orientation == Qt.Horizontal:
            if self.df.columns.nlevels == 1:
                return
        else:
            if self.df.index.nlevels == 1:
                return

        for ix in self.selectedIndexes():
            if self.orientation == Qt.Horizontal:
                # Loop over the rows above this one
                for row in range(ix.row()):
                    ix2 = self.model().index(row, ix.column())
                    self.setSelection(self.visualRect(
                        ix2), QtCore.QItemSelectionModel.Select)
            else:
                # Loop over the columns left of this one
                for col in range(ix.column()):
                    ix2 = self.model().index(ix.row(), col)
                    self.setSelection(self.visualRect(
                        ix2), QtCore.QItemSelectionModel.Select)

    # Fits columns to contents but with a minimum width and added padding
    def init_column_sizes(self):
        padding = 30

        if self.orientation == Qt.Horizontal:
            min_size = 100

            self.resizeColumnsToContents()

            # for col in range(len(self.df.columns)):
            for col in range(self.model().columnCount()):

                # print(col)
                width = self.columnWidth(col)
                if width + padding < min_size:
                    new_width = min_size
                else:
                    new_width = width + padding

                self.setColumnWidth(col, new_width)
                self.table.setColumnWidth(col, new_width)
        else:
            self.resizeColumnsToContents()
            for col in range(self.model().columnCount()):
                # for col in range(len(self.df.columns)):
                width = self.columnWidth(col)
                self.setColumnWidth(col, width + padding)

    # This sets spans to group together adjacent cells with the same values
    def set_spans(self):

        self.clearSpans()
        # Find spans for horizontal HeaderView
        if self.orientation == Qt.Horizontal:

            # Find how many levels the MultiIndex has
            if isinstance(self.df.columns, pd.MultiIndex):
                N = len(self.df.columns[0])
            else:
                N = 1

            for level in range(N):  # Iterates over the levels
                # Find how many segments the MultiIndex has
                if isinstance(self.df.columns, pd.MultiIndex):
                    arr = [self.df.columns[i][level]
                           for i in range(len(self.df.columns))]
                else:
                    arr = self.df.columns

                # Holds the starting index of a range of equal values.
                # None means it is not currently in a range of equal values.
                match_start = None

                for col in range(1, len(arr)):  # Iterates over cells in row
                    # Check if cell matches cell to its left
                    if arr[col] == arr[col - 1]:
                        if match_start is None:
                            match_start = col - 1
                        # If this is the last cell, need to end it
                        if col == len(arr) - 1:
                            match_end = col
                            span_size = match_end - match_start + 1
                            self.setSpan(level, match_start, 1, span_size)
                    else:
                        if match_start is not None:
                            match_end = col - 1
                            span_size = match_end - match_start + 1
                            self.setSpan(level, match_start, 1, span_size)
                            match_start = None

        # Find spans for vertical HeaderView
        else:
            # Find how many levels the MultiIndex has
            if isinstance(self.df.index, pd.MultiIndex):
                N = len(self.df.index[0])
            else:
                N = 1

            for level in range(N):  # Iterates over the levels

                # Find how many segments the MultiIndex has
                if isinstance(self.df.index, pd.MultiIndex):
                    arr = [self.df.index[i][level]
                           for i in range(len(self.df.index))]
                else:
                    arr = self.df.index

                # Holds the starting index of a range of equal values.
                # None means it is not currently in a range of equal values.
                match_start = None

                for row in range(1, len(arr)):  # Iterates over cells in column

                    # Check if cell matches cell above
                    if arr[row] == arr[row - 1]:
                        if match_start is None:
                            match_start = row - 1
                        # If this is the last cell, need to end it
                        if row == len(arr) - 1:
                            match_end = row
                            span_size = match_end - match_start + 1
                            self.setSpan(match_start, level, span_size, 1)
                    else:
                        if match_start is not None:
                            match_end = row - 1
                            span_size = match_end - match_start + 1
                            self.setSpan(match_start, level, span_size, 1)
                            # match_start = None

    def over_header_edge(self, mouse_position, margin=3):

        # Return the index of the column this x position is on the right edge of
        if self.orientation == Qt.Horizontal:
            x = mouse_position
            if self.columnAt(x - margin) != self.columnAt(x + margin):
                if self.columnAt(x + margin) == 0:
                    # We're at the left edge of the first column
                    return None
                else:
                    return self.columnAt(x - margin)
            else:
                return None

        # Return the index of the row this y position is on the top edge of
        elif self.orientation == Qt.Vertical:
            y = mouse_position
            if self.rowAt(y - margin) != self.rowAt(y + margin):
                if self.rowAt(y + margin) == 0:
                    # We're at the top edge of the first row
                    return None
                else:
                    return self.rowAt(y - margin)
            else:
                return None

    def eventFilter(self, object: QObject, event: QEvent):

        # If mouse is on an edge, start the drag resize process
        if event.type() == QEvent.MouseButtonPress:
            if self.orientation == Qt.Horizontal:
                mouse_position = event.pos().x()
            else:
                mouse_position = event.pos().y()

            if self.over_header_edge(mouse_position) is not None:
                self.header_being_resized = self.over_header_edge(
                    mouse_position)
                self.resize_start_position = mouse_position
                if self.orientation == Qt.Horizontal:
                    self.initial_header_size = self.columnWidth(
                        self.header_being_resized)
                elif self.orientation == Qt.Vertical:
                    self.initial_header_size = self.rowHeight(
                        self.header_being_resized)
                return True
            else:
                self.header_being_resized = None

        # End the drag process
        if event.type() == QEvent.MouseButtonRelease:
            self.header_being_resized = None

        # Auto size the column that was double clicked
        if event.type() == QEvent.MouseButtonDblClick:
            if self.orientation == Qt.Horizontal:
                mouse_position = event.pos().x()
            else:
                mouse_position = event.pos().y()

            # Find which column or row edge the mouse was over and auto size it
            if self.over_header_edge(mouse_position) is not None:
                header_index = self.over_header_edge(mouse_position)
                if self.orientation == Qt.Horizontal:
                    self.parent().auto_size_column(header_index)
                elif self.orientation == Qt.Vertical:
                    self.parent().auto_size_row(header_index)
                return True

        # Handle active drag resizing
        if event.type() == QEvent.MouseMove:
            if self.orientation == Qt.Horizontal:
                mouse_position = event.pos().x()
            elif self.orientation == Qt.Vertical:
                mouse_position = event.pos().y()

            # If this is None, there is no drag resize happening
            if self.header_being_resized is not None:
                self.drag_size = mouse_position - self.resize_start_position
                # print(self.drag_size)

                size = self.initial_header_size + self.drag_size

                if size > 10:
                    if self.orientation == Qt.Horizontal:
                        self.setColumnWidth(self.header_being_resized, size)
                        self.parent().dataView.setColumnWidth(self.header_being_resized, size)
                    if self.orientation == Qt.Vertical:
                        self.setRowHeight(self.header_being_resized, size)
                        self.parent().dataView.setRowHeight(self.header_being_resized, size)

                    self.updateGeometry()  # Column size
                    self.parent().dataView.updateGeometry()
                return True

            # Set the cursor shape
            if self.over_header_edge(mouse_position) is not None:
                if self.orientation == Qt.Horizontal:
                    self.viewport().setCursor(QCursor(Qt.SplitHCursor))
                elif self.orientation == Qt.Vertical:
                    self.viewport().setCursor(QCursor(Qt.SplitVCursor))
            else:
                self.viewport().setCursor(QCursor(Qt.ArrowCursor))

        return False

    # Return the size of the header needed to match the corresponding DataTableView
    def sizeHint(self):
        # Set width and height based on number of columns in model
        # Width
        width = 2 * self.frameWidth()  # Account for border & padding
        # width += self.verticalScrollBar().width()  # Dark theme has scrollbars always shown
        for i in range(len(self.df.columns)):
            width += self.columnWidth(i)

        # Height
        height = 2 * self.frameWidth()  # Account for border & padding
        # height += self.horizontalScrollBar().height()  # Dark theme has scrollbars always shown
        for i in range(len(self.df.index)):
            height += self.rowHeight(i)

        return QSize(width, height)

    # This is needed because otherwise when the horizontal header is a single row it will add whitespace to be bigger
    def minimumSizeHint(self):
        if self.orientation == Qt.Horizontal:
            return QSize(0, self.sizeHint().height())
        else:
            return QSize(self.sizeHint().width(), 0)


class HeaderModel(QAbstractTableModel):

    def __init__(self, df, orientation):
        super().__init__()
        self.orientation = orientation
        self.df = df
        self.colors = dict()

    def columnCount(self, parent=None):
        if self.orientation == Qt.Horizontal:
            return self.df.columns.shape[0]
        else:  # Vertical
            return self.df.index.nlevels

    def rowCount(self, parent=None):
        if self.orientation == Qt.Horizontal:
            return self.df.columns.nlevels
        elif self.orientation == Qt.Vertical:
            return self.df.index.shape[0]

    # Returns the data from the DataFrame
    def data(self, index, role=Qt.DisplayRole):
        row = index.row()
        col = index.column()
        cell = self.df.iloc[row, col]

        if role == Qt.DisplayRole or role == Qt.ToolTipRole:
            if self.orientation == Qt.Horizontal:
                if isinstance(self.df.columns, pd.MultiIndex):
                    return str(self.df.columns.values[col][row])
                else:
                    return str(self.df.columns.values[col])
            elif self.orientation == Qt.Vertical:
                if isinstance(self.df.index, pd.MultiIndex):
                    return str(self.df.index.values[row][col])
                else:
                    return str(self.df.index.values[row])

        if index.isValid():
            if (role == Qt.DisplayRole
                    or role == Qt.EditRole
                    or role == Qt.ToolTipRole):
                # Need to check type since a cell might contain a list or Series, then .isna returns a Series not a bool
                cell_is_na = pd.isna(cell)
                if type(cell_is_na) == bool and cell_is_na:
                    return ""

                # Float formatting
                if isinstance(cell, float):
                    if not role == Qt.ToolTipRole:
                        return "{:.2f}".format(cell)

                if isinstance(cell, float):
                    return Qt.AlignVCenter + Qt.AlignRight

                return str(cell)

            if role == Qt.BackgroundRole:
                color = self.colors.get((row, cell))
                if color is not None:
                    return color
            if role == Qt.TextColorRole:
                return QVariant(QColor(169, 170, 172))

            if role == Qt.BackgroundRole:
                return QVariant(QColor(37, 40, 44))

            if role == Qt.TextAlignmentRole:
                value = self.df.iloc[row, col]

        elif role == Qt.ToolTipRole:
            return str(cell)

    # The headers of this table will show the level names of the MultiIndex
    def headerData(self, section, orientation, role=None):
        if role in [Qt.DisplayRole, Qt.ToolTipRole]:

            if self.orientation == Qt.Horizontal and orientation == Qt.Vertical:
                if isinstance(self.df.columns, pd.MultiIndex):
                    return str(self.df.columns.names[section])
                else:
                    return str(self.df.columns.name)
            elif self.orientation == Qt.Vertical and orientation == Qt.Horizontal:
                if isinstance(self.df.index, pd.MultiIndex):
                    return str(self.df.index.names[section])
                else:
                    return str(self.df.index.name)
            else:
                return None  # These cells should be hidden anyways


class HeaderNamesView(QTableView):
    def __init__(self, df, orientation):
        # def __init__(self, parent: DataFrameViewer, orientation):
        # super().__init__(parent)
        super().__init__()

        self.df = df
        self.setProperty('orientation', 'horizontal' if orientation ==
                                                        1 else 'vertical')  # Used in stylesheet

        # Setup
        self.orientation = orientation
        self.setModel(HeaderNamesModel(self.df, orientation))

        # self.clicked.connect(self.on_clicked)

        self.setHorizontalScrollBarPolicy(Qt.ScrollBarAlwaysOff)
        self.setVerticalScrollBarPolicy(Qt.ScrollBarAlwaysOff)

        self.setHorizontalScrollMode(QAbstractItemView.ScrollPerPixel)
        self.setVerticalScrollMode(QAbstractItemView.ScrollPerPixel)

        self.horizontalHeader().hide()
        self.verticalHeader().hide()

        cor = """QTableView  {
            font:14pt Arial, sans-serif;
            color: #A9AAAC;
            selection-background-color: #043E4B;
            selection-color: #A9AAAC;
            }
            """
        self.setStyleSheet(cor)

        self.setSelectionMode(self.NoSelection)

        font = QFont()
        font.setBold(True)
        self.setFont(font)
        self.init_size()

    def on_clicked(self, ix: QModelIndex):
        # When the index header name is clicked, sort the index by that level
        if self.orientation == Qt.Vertical:
            self.df.sort_index(ix.column())
            # self.pgdf.sort_index(ix.column())

    def init_size(self):
        # Match vertical header name widths to vertical header
        if self.orientation == Qt.Vertical:
            for ix in range(len(self.df.columns)):
                self.setColumnWidth(ix, self.columnWidth(ix))

    def sizeHint(self):
        if self.orientation == Qt.Horizontal:
            width = self.columnWidth(0)
            height = self.parent().columnHeader.sizeHint().height()
        else:  # Vertical
            width = self.parent().indexHeader.sizeHint().width()
            height = self.rowHeight(0) + 2

        return QSize(width, height)

    def minimumSizeHint(self):
        return self.sizeHint()

    def rowHeight(self, row: int) -> int:
        return self.parent().columnHeader.rowHeight(row)

    def columnWidth(self, column: int) -> int:
        if self.orientation == Qt.Horizontal:
            if all(name is None for name in self.df.columns.names):
                return 0
            else:
                return super().columnWidth(column)
        else:
            return DataTableView(self.df).columnWidth(column)


class HeaderNamesModel(QAbstractTableModel):

    def __init__(self, df, orientation):
        super().__init__()
        self.orientation = orientation
        self.df = df
        self.colors = dict()

    def columnCount(self, parent=None):
        if self.orientation == Qt.Horizontal:
            return 1
        elif self.orientation == Qt.Vertical:
            return self.df.index.nlevels

    def rowCount(self, parent=None):
        if self.orientation == Qt.Horizontal:
            return self.df.columns.nlevels
        elif self.orientation == Qt.Vertical:
            return 1

    def data(self, index, role=Qt.DisplayRole):
        row = index.row()
        col = index.column()
        cell = self.df.iloc[row, col]

        if role == Qt.DisplayRole or role == Qt.ToolTipRole:

            if self.orientation == Qt.Horizontal:
                val = self.df.columns.names[row]
                if val is None:
                    val = ""
                return str(val)

            elif self.orientation == Qt.Vertical:
                val = self.df.index.names[col]
                if val is None:
                    val = "index"
                return str(val)

            if role == Qt.BackgroundRole:
                color = self.colors.get((row, cell))
                if color is not None:
                    return color
            if role == Qt.TextColorRole:
                return QVariant(QColor(169, 170, 172))

            if role == Qt.BackgroundRole:
                return QVariant(QColor(48, 49, 53))

            if role == Qt.TextAlignmentRole:
                value = self.df.iloc[row, col]

        elif role == Qt.ToolTipRole:
            return str(cell)


# This is a fixed size widget with a size that tracks some other widget
class TrackingSpacer(QFrame):
    def __init__(self, ref_x=None, ref_y=None):
        super().__init__()
        self.ref_x = ref_x
        self.ref_y = ref_y

    def minimumSizeHint(self):
        width = 0
        height = 0
        if self.ref_x:
            width = self.ref_x.width()
        if self.ref_y:
            height = self.ref_y.height()

        return QSize(width, height)


# Examples
if __name__ == "__main__":
    app = QApplication(sys.argv)
    df = pd.DataFrame()
    # df = pd.read_csv('../Pokemon.csv')
    view = DataFrameViewer(df.iloc[0:20, :])
    view.show()
    app.exec_()

    # def data(self, index, role=Qt.DisplayRole):
    #     row = index.row()
    #     col = index.column()

    #     if role == Qt.DisplayRole or role == Qt.ToolTipRole:
    #         if self.orientation == Qt.Horizontal:
    #             if isinstance(self.df.columns, pd.MultiIndex):
    #                 return str(self.df.columns.values[col][row])
    #             else:
    #                 return str(self.df.columns.values[col])
    #         elif self.orientation == Qt.Vertical:
    #             if isinstance(self.df.index, pd.MultiIndex):
    #                 return str(self.df.index.values[row][col])
    #             else:
    #                 return str(self.df.index.values[row])

    #         if role == Qt.BackgroundRole:
    #             color = self.colors.get((row, cell))
    #             if color is not None:
    #                 return color

    #         if role==Qt.TextColorRole:
    #             return QVariant(QColor(169, 170, 172))

    #         if role == Qt.BackgroundRole:
    #             if row%2:
    #                 return QVariant(QColor(41, 44, 49))
    #             else:
    #                 return QVariant(QColor(23, 23, 25))

    # if role == Qt.DecorationRole:
    #     if self.df.sort_is_ascending:
    #         icon = QtGui.QIcon(os.path.join(pandasgui.__path__[0], "resources/images/sort-ascending.png"))
    #     else:
    #         icon = QtGui.QIcon(os.path.join(pandasgui.__path__[0], "resources/images/sort-descending.png"))

    #     if col == self.pgdf.column_sorted and row == self.rowCount() - 1 and self.orientation == Qt.Horizontal:
    #         return icon

##############

# def data(self, index, role=Qt.DisplayRole):
#     row = index.row()
#     col = index.column()

#     if role == Qt.DisplayRole or role == Qt.ToolTipRole:

#         if self.orientation == Qt.Horizontal:
#             val = self.df.columns.names[row]
#             if val is None:
#                 val = ""
#             return str(val)

#         elif self.orientation == Qt.Vertical:
#             val = self.df.index.names[col]
#             if val is None:
#                 val = "index"
#             return str(val)

# if role == Qt.DecorationRole:
#     if self.pgdf.sort_is_ascending:
#         icon = QtGui.QIcon(os.path.join(pandasgui.__path__[0], "resources/images/sort-ascending.png"))
#     else:
#         icon = QtGui.QIcon(os.path.join(pandasgui.__path__[0], "resources/images/sort-descending.png"))

#     if col == self.pgdf.index_sorted and self.orientation == Qt.Vertical:
#         return icon
