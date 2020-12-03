import math
import numpy as np
import time as time
import sys
import random as random
from LengthNestProCalculate import length_nest_pro
from PyQt5 import QtWidgets, QtGui, QtCore, uic
from PyQt5.QtWidgets import QApplication, QMainWindow, QWidget, QTableWidget, QTableWidgetItem, QGridLayout, QSizePolicy
from PyQt5.QtGui import QPalette, QColor
from PyQt5.QtCore import Qt
from random import randint

app = QApplication(sys.argv)
# Force the style to be the same on all OSs:
app.setStyle("Fusion")

# Use a palette to switch to dark colors:
palette = QPalette()
palette.setColor(QPalette.Window, QColor(53, 53, 53))
palette.setColor(QPalette.WindowText, QColor(255, 255, 255))
palette.setColor(QPalette.Base, QColor(25, 25, 25))
palette.setColor(QPalette.AlternateBase, QColor(53, 53, 53))
palette.setColor(QPalette.ToolTipBase, QColor(255, 255, 255))
palette.setColor(QPalette.ToolTipText, QColor(255, 255, 255))
palette.setColor(QPalette.Text, QColor(255, 255, 255))
palette.setColor(QPalette.Button, QColor(53, 53, 53))
palette.setColor(QPalette.ButtonText, QColor(255, 255, 255))
palette.setColor(QPalette.BrightText, QColor(255, 0, 0))
palette.setColor(QPalette.Link, QColor(42, 130, 218))
palette.setColor(QPalette.Highlight, QColor(42, 130, 218))
palette.setColor(QPalette.HighlightedText, QColor(0, 0, 0))

app.setPalette(palette)


class Table(QTableWidget):
    def __init__(self):
        super().__init__()

        # self.setStyleSheet("gridline-color: #fffff8; border-width: 50px")

        # Fix width of left header and center labels
        self.verticalHeader().setFixedWidth(25)
        self.verticalHeader().setDefaultAlignment(Qt.AlignHCenter)

        # Fix height of table
        self.setFixedHeight(265)

        self.starting_num_rows = 8
        self.setRowCount(self.starting_num_rows)
        self.setColumnCount(2)
        self.setColumnWidth(0, 60)
        self.setColumnWidth(1, 60)
        self.setHorizontalHeaderLabels(["Qty", "Length"])
        self.cellChanged.connect(self.cell_was_changed)

        self.setShowGrid(False)
        self.setStyleSheet('QTableView::item {border-right: 1px solid #909090; border-bottom: 1px solid #909090;}')

    def add_row(self):
        current_row_count = self.rowCount()
        if current_row_count > 6:
            self.insertRow(current_row_count)
            for i in range(self.columnCount()):
                self.new_item = QTableWidgetItem("")
                self.new_item.setTextAlignment(Qt.AlignCenter)
                self.setItem(current_row_count, i, self.new_item)
            # self.width_adjust_needed = 1

    def remove_row(self):
        current_row_count = self.rowCount()
        self.removeRow(current_row_count - 1)
        rows_need_deleted = 1
        while rows_need_deleted == 1:
            last_row_index = self.rowCount() - 1
            is_qty_text = 0
            is_length_text = 0
            is_name_text = 0
            is_qty = self.item(last_row_index - 1, 0)
            if is_qty and is_qty.text() != "":
                is_qty_text = self.item(last_row_index - 1, 0).text()
            is_length = self.item(last_row_index - 1, 1)
            if is_length and is_length.text() != "":
                is_length_text = self.item(last_row_index - 1, 1).text()
            is_name = self.item(last_row_index - 1, 2)
            if is_name and is_name.text() != "":
                is_name_text = self.item(last_row_index - 1, 2).text()
            if not is_qty_text and not is_length_text and not is_name_text and self.rowCount() > self.starting_num_rows:
                current_row_count = self.rowCount()
                self.removeRow(current_row_count - 1)
            else:
                rows_need_deleted = 0

    def cell_was_changed(self):
        self.update_num_rows()
        self.updateGeometries()
        self.update_table_width(self)

    def update_num_rows(self):
        is_qty_text = 0
        is_length_text = 0
        is_name_text = 0
        last_row_index = self.rowCount() - 1

        # Add logic to add a row
        # Check for contents in the qty field
        is_qty = self.item(last_row_index, 0)
        if is_qty and is_qty.text() != "":
            is_qty_text = self.item(last_row_index, 0).text()

        # Check for contents in the length field
        is_length = self.item(last_row_index, 1)
        if is_length and is_length.text() != "":
            is_length_text = self.item(last_row_index, 1).text()

        # Check for contents in the name field
        is_name = self.item(last_row_index, 2)
        if is_name and is_name.text() != "":
            is_name_text = self.item(last_row_index, 2).text()

        if is_qty_text or is_length_text or is_name_text:
            self.add_row()

        # Add logic to remove a row
        else:
            is_qty_text = 0
            is_length_text = 0
            is_name_text = 0

            is_qty = self.item(last_row_index - 1, 0)
            if is_qty and is_qty.text() != "":
                is_qty_text = self.item(last_row_index - 1, 0).text()

            is_length = self.item(last_row_index - 1, 1)
            if is_length and is_length.text() != "":
                is_length_text = self.item(last_row_index - 1, 1).text()

            is_name = self.item(last_row_index - 1, 2)
            if is_name and is_name.text() != "":
                is_name_text = self.item(last_row_index - 1, 2).text()

            if not is_qty_text and not is_length_text and not is_name_text and self.rowCount() > self.starting_num_rows:
                self.remove_row()

    def update_table_width(self, table):
        if self:
            width = table.verticalHeader().width()
            width += table.horizontalHeader().length()
            if table.verticalScrollBar().isVisible():
                width += table.verticalScrollBar().width()
            width += table.frameWidth() * 2
            table.setFixedWidth(width)

    def keyPressEvent(self, event):
        if event.key() == 16777223:  # Delete
            self.delete_cell_contents()
        elif event.key() == 16777221 or event.key() == 16777220:  # Enter
            self.enter_was_pressed()
        else:
            super().keyPressEvent(event)
            # print(event.key())

    def delete_cell_contents(self):
        indices = self.selectedIndexes()
        for index in indices[::-1]:
            i = index.row()
            j = index.column()
            self.setItem(i, j, QTableWidgetItem(""))
            # Make sure row still exists before trying to align contents
            if self.rowCount() > i:
                self.item(i, j).setTextAlignment(Qt.AlignCenter)

    def enter_was_pressed(self):
        # Record the indices of the current cell
        current_row = self.currentRow()
        current_column = self.currentColumn()

        # Set another cell as the current cell so that the previous current cell can be extracted
        self.setCurrentCell(0, 0)
        self.setCurrentCell(1, 0)
        self.setCurrentCell(0, 0)

        # Extract value of cell that was active when user pressed enter
        cell_value = self.item(current_row, current_column).text()

        # Highlight the correct cell based on the status of the table
        if self.rowCount() != current_row + 1 or cell_value != "" and self.rowCount() > 6:
            self.setCurrentCell(current_row + 1, current_column)
        else:
            self.setCurrentCell(current_row, current_column)

    def resizeEvent(self, *args, **kwargs):
        self.cell_was_changed()


# Create subclass of QMainWindow for the application window
class Window(QMainWindow):
    def __init__(self):
        super().__init__()

        # Create and set main widget object
        self.main_widget = QtWidgets.QWidget(self)
        self.main_widget.setFocus()
        self.setCentralWidget(self.main_widget)

        # Create a grid layout object in the main widget
        self.grid_layout = QGridLayout(self.main_widget)
        self.setLayout(self.grid_layout)
        self.grid_layout.setContentsMargins(30, 10, 30, 10)
        self.grid_layout.setHorizontalSpacing(20)
        self.grid_layout.setVerticalSpacing(20)

        # Set properties of the window
        self.setGeometry(150, 35, 1000, 700)  # TODO make window and contents adjustable to any size, allow zooming
        self.setWindowTitle("LengthNestPro, The free 1D nesting optimizer")
        self.setWindowIcon(QtGui.QIcon("C:/Users/Owner/PycharmProjects/LengthNestPro/icon.ico"))

        # Create headers
        self.header1()
        self.header2()
        self.header3()

        # Create blank canvas by placing a label object in the window and setting its properties
        self.label = QtWidgets.QLabel()
        canvas = QtGui.QPixmap(1100, 400)
        canvas.fill(QColor(150, 150, 150))
        self.label.setPixmap(canvas)

        # Place label inside of a scroll area
        self.scroll_area = QtWidgets.QScrollArea()
        # self.scroll_area.setGeometry(QtCore.QRect(100, 100, 400, 400))
        self.scroll_area.setFixedWidth(1116)
        self.scroll_area.setFixedHeight(402)
        self.scroll_area.setWidgetResizable(True)
        self.scroll_area.setWidget(self.label)
        self.scroll_area.setVerticalScrollBarPolicy(Qt.ScrollBarAlwaysOn)
        self.label.setAlignment(Qt.AlignCenter)

        # Create a table object in the window
        self.t1 = Table()

        # Add column for part name / ID
        self.t1.setColumnCount(3)
        self.t1.setHorizontalHeaderLabels(["Qty", "Length", "Name / ID"])
        self.t1.setColumnWidth(2, 120)
        self.t1.update_table_width(self.t1)

        qty1 = QTableWidgetItem("9000")
        qty2 = QTableWidgetItem("3500")
        qty3 = QTableWidgetItem("2500")
        qty4 = QTableWidgetItem("")
        qty5 = QTableWidgetItem("")
        qty6 = QTableWidgetItem("")
        qty7 = QTableWidgetItem("")
        qty8 = QTableWidgetItem("")

        qty1.setTextAlignment(Qt.AlignCenter)
        qty2.setTextAlignment(Qt.AlignCenter)
        qty3.setTextAlignment(Qt.AlignCenter)
        qty4.setTextAlignment(Qt.AlignCenter)
        qty5.setTextAlignment(Qt.AlignCenter)
        qty6.setTextAlignment(Qt.AlignCenter)
        qty7.setTextAlignment(Qt.AlignCenter)
        qty8.setTextAlignment(Qt.AlignCenter)

        length1 = QTableWidgetItem("44.9")
        length2 = QTableWidgetItem("79.11")
        length3 = QTableWidgetItem("31.25")
        length4 = QTableWidgetItem("")
        length5 = QTableWidgetItem("")
        length6 = QTableWidgetItem("")
        length7 = QTableWidgetItem("")
        length8 = QTableWidgetItem("")

        length1.setTextAlignment(Qt.AlignCenter)
        length2.setTextAlignment(Qt.AlignCenter)
        length3.setTextAlignment(Qt.AlignCenter)
        length4.setTextAlignment(Qt.AlignCenter)
        length5.setTextAlignment(Qt.AlignCenter)
        length6.setTextAlignment(Qt.AlignCenter)
        length7.setTextAlignment(Qt.AlignCenter)
        length8.setTextAlignment(Qt.AlignCenter)

        name1 = QTableWidgetItem("L15762")
        name2 = QTableWidgetItem("N42719")
        name3 = QTableWidgetItem("P58634")
        name4 = QTableWidgetItem("")
        name5 = QTableWidgetItem("")
        name6 = QTableWidgetItem("")
        name7 = QTableWidgetItem("")
        name8 = QTableWidgetItem("")

        name1.setTextAlignment(Qt.AlignCenter)
        name2.setTextAlignment(Qt.AlignCenter)
        name3.setTextAlignment(Qt.AlignCenter)
        name4.setTextAlignment(Qt.AlignCenter)
        name5.setTextAlignment(Qt.AlignCenter)
        name6.setTextAlignment(Qt.AlignCenter)
        name7.setTextAlignment(Qt.AlignCenter)
        name8.setTextAlignment(Qt.AlignCenter)

        self.t1.setItem(0, 0, qty1)
        self.t1.setItem(1, 0, qty2)
        self.t1.setItem(2, 0, qty3)
        self.t1.setItem(3, 0, qty4)
        self.t1.setItem(4, 0, qty5)
        self.t1.setItem(5, 0, qty6)
        self.t1.setItem(6, 0, qty7)
        self.t1.setItem(7, 0, qty8)
        self.t1.setItem(0, 1, length1)
        self.t1.setItem(1, 1, length2)
        self.t1.setItem(2, 1, length3)
        self.t1.setItem(3, 1, length4)
        self.t1.setItem(4, 1, length5)
        self.t1.setItem(5, 1, length6)
        self.t1.setItem(6, 1, length7)
        self.t1.setItem(7, 1, length8)
        self.t1.setItem(0, 2, name1)
        self.t1.setItem(1, 2, name2)
        self.t1.setItem(2, 2, name3)
        self.t1.setItem(3, 2, name4)
        self.t1.setItem(4, 2, name5)
        self.t1.setItem(5, 2, name6)
        self.t1.setItem(6, 2, name7)
        self.t1.setItem(7, 2, name8)

        self.t2 = Table()

        self.t3 = Table()

        # Fix width of left header and center labels
        self.t3.verticalHeader().setFixedWidth(100)
        self.t3.verticalHeader().setDefaultAlignment(Qt.AlignHCenter)

        # Fix height of table
        self.t3.setFixedHeight(141)

        self.t3.starting_num_rows = 4
        self.t3.setRowCount(self.t3.starting_num_rows)
        self.t3.setColumnCount(1)
        self.t3.setColumnWidth(0, 150)
        self.t3.setHorizontalHeaderLabels([""])
        self.t3.setVerticalHeaderLabels(["Stock Length", "Left Waste", "Right Waste", "Spacing"])

        stock_length = QTableWidgetItem("240")
        left_waste = QTableWidgetItem("0.12")
        right_waste = QTableWidgetItem("4.75")
        spacing = QTableWidgetItem("0.25")

        stock_length.setTextAlignment(Qt.AlignCenter)
        left_waste.setTextAlignment(Qt.AlignCenter)
        right_waste.setTextAlignment(Qt.AlignCenter)
        spacing.setTextAlignment(Qt.AlignCenter)

        self.t3.setItem(0, 0, stock_length)
        self.t3.setItem(1, 0, left_waste)
        self.t3.setItem(2, 0, right_waste)
        self.t3.setItem(3, 0, spacing)

        # Enter function to create calculate button
        self.calculate()

        self.grid_layout.addWidget(self.h1, 0, 1, Qt.AlignHCenter)
        # self.grid_layout.addWidget(self.h2, 0, 2, Qt.AlignHCenter)
        self.h2.setHidden(1)
        self.grid_layout.addWidget(self.h3, 0, 3, Qt.AlignHCenter)
        self.grid_layout.addWidget(self.t1, 1, 1, Qt.AlignLeft)
        # self.grid_layout.addWidget(self.t2, 1, 2, Qt.AlignTop)
        self.grid_layout.addWidget(self.t3, 1, 3, Qt.AlignTop)
        self.grid_layout.addWidget(self.calc_btn, 2, 0, 1, 5, Qt.AlignHCenter)
        self.grid_layout.addWidget(self.scroll_area, 3, 0, 1, 5, Qt.AlignHCenter)###

        self.grid_layout.setColumnStretch(0, 11)
        self.grid_layout.setColumnStretch(1, 13)
        self.grid_layout.setColumnStretch(2, 10)
        self.grid_layout.setColumnStretch(3, 13)
        self.grid_layout.setColumnStretch(4, 9)

        self.grid_layout.setRowStretch(0, 1)
        self.grid_layout.setRowStretch(1, 1)
        self.grid_layout.setRowStretch(2, 1)
        self.grid_layout.setRowStretch(3, 1)

    # Functions to setup widgets

    def header1(self):
        # Create a label object in the window and set its properties
        self.h1 = QtWidgets.QLabel(self)
        self.h1.setFont(QtGui.QFont('Arial', 20))
        self.h1.setText("Required Parts")
        self.h1.adjustSize()
        self.h1.setFixedWidth(280)
        self.h1.setStyleSheet("padding:0px 0px")
        self.h1.setAlignment(Qt.AlignHCenter)

    def header2(self):
        # Create a label object in the window and set its properties
        self.h2 = QtWidgets.QLabel(self)
        self.h2.setFont(QtGui.QFont('Arial', 20))
        self.h2.setText("Stock Material")
        self.h2.adjustSize()
        self.h2.setStyleSheet("padding:0px 0px")

    def header3(self):
        # Create a label object in the window and set its properties
        self.h3 = QtWidgets.QLabel(self)
        self.h3.setFont(QtGui.QFont('Arial', 20))
        self.h3.setText("Other Information")
        self.h3.adjustSize()
        self.h3.setStyleSheet("padding:0px 0px")
        self.h3.setAlignment(Qt.AlignHCenter)

    def calculate(self):
        self.calc_btn = QtWidgets.QPushButton(self)
        self.calc_btn.setText("Calculate")
        self.calc_btn.setFont(QtGui.QFont('Arial', 12))
        self.calc_btn.clicked.connect(self.gather_inputs)
        self.calc_btn.move(400, 500)

    # Other functions

    def gather_inputs(self):
        # Initialize vectors to be extracted from table
        part_lengths = []
        b = []
        part_names = []

        # Extract values from table if they are filled out correctly
        for i in range(self.t1.rowCount()):
            # Extract qty cell in ith row
            qty_i = self.t1.item(i, 0)
            qty_text = 0
            # If object exists, extract text from the cell
            if qty_i:
                qty_text = qty_i.text()

            # Extract length cell in ith row
            length_i = self.t1.item(i, 1)
            length_text = 0
            # If object exists, extract text from the cell
            if length_i:
                length_text = length_i.text()

            # Extract name cell in ith row
            name_i = self.t1.item(i, 2)
            name_text = 0
            # If object exists, extract text from the cell
            if name_i:
                name_text = name_i.text()

            # Extract row if required values are present
            if qty_text and length_text and name_text:
                part_lengths = np.append(part_lengths, [float(length_text)], 0)
                b = np.append(b, [float(qty_text)], 0)
                part_names = np.append(part_names, [name_text], 0)
            # elif (length_i and length_text) and not (qty_i and qty_text):
            #     print("missing value1")  # TODO remove when code is proven
            # elif (qty_i and qty_text) and not (length_i and length_text):
            #     print("missing value2")  # TODO remove when code is proven

        # Change row vectors to column vectors
        part_lengths = np.transpose([part_lengths])
        b = np.transpose([b])
        # Run nesting code if the user has given enough values

        # Delete and recreate blank canvas
        self.label.clear()
        self.label = QtWidgets.QLabel()
        canvas = QtGui.QPixmap(1100, 400)
        canvas.fill(QColor(150, 150, 150))
        self.label.setPixmap(canvas)
        self.scroll_area.setWidget(self.label)
        self.label.setAlignment(Qt.AlignCenter)

        # Initialize parameters
        stock_length = -1
        left_waste = -1
        right_waste = -1
        spacing = -1

        # Extract "Other Information" cells if available
        if self.t3.item(0, 0).text() != "":
            stock_length = float(self.t3.item(0, 0).text())
        if self.t3.item(1, 0).text() != "":
            left_waste = float(self.t3.item(1, 0).text())
        if self.t3.item(2, 0).text() != "":
            right_waste = float(self.t3.item(2, 0).text())
        if self.t3.item(3, 0).text() != "":
            spacing = float(self.t3.item(3, 0).text())

        self.error_message = QtWidgets.QLabel(self)
        self.error_message.setHidden(1)
        self.error_message.setFont(QtGui.QFont('Arial', 12))
        self.error_message.setAlignment(Qt.AlignCenter)
        self.error_message.setText("One or more of the parts is too long for the available nesting length.")
        self.error_message.setWordWrap(1)
        self.error_message.setFixedWidth(200)
        self.error_message.setFixedHeight(100)
        self.error_message.setStyleSheet("margin:0px 20px 0px 0px; background-color: red")
        self.grid_layout.addWidget(self.error_message, 1, 2, Qt.AlignTop)

        self.error_message2 = QtWidgets.QLabel(self)
        self.error_message2.setHidden(1)
        self.error_message2.setFont(QtGui.QFont('Arial', 12))
        self.error_message2.setAlignment(Qt.AlignCenter)
        self.error_message2.setText("Some values still need to be entered.")
        self.error_message2.setWordWrap(1)
        self.error_message2.setFixedWidth(200)
        self.error_message2.setFixedHeight(100)
        self.error_message2.setStyleSheet("margin:0px 20px 0px 0px; background-color: red")
        self.grid_layout.addWidget(self.error_message2, 1, 2, Qt.AlignTop)

        self.error_message3 = QtWidgets.QLabel(self)
        self.error_message3.setHidden(1)
        self.error_message3.setFont(QtGui.QFont('Arial', 12))
        self.error_message3.setAlignment(Qt.AlignCenter)
        self.error_message3.setText("Nested quantities do not match required quantities.")
        self.error_message3.setWordWrap(1)
        self.error_message3.setFixedWidth(200)
        self.error_message3.setFixedHeight(100)
        self.error_message3.setStyleSheet("margin:0px 20px 0px 0px; background-color: red")
        self.grid_layout.addWidget(self.error_message3, 1, 2, Qt.AlignTop)

        self.success_message = QtWidgets.QLabel(self)
        self.success_message.setHidden(1)
        self.success_message.setFont(QtGui.QFont('Arial', 12))
        self.success_message.setAlignment(Qt.AlignCenter)
        self.success_message.setText("Parts were nested successfully.")
        self.success_message.setWordWrap(1)
        self.success_message.setFixedWidth(200)
        self.success_message.setFixedHeight(100)
        self.success_message.setStyleSheet("margin:0px 20px 0px 0px; background-color: green")
        self.grid_layout.addWidget(self.success_message, 1, 2, Qt.AlignTop)

        self.status_message = QtWidgets.QLabel(self)
        self.status_message.setHidden(1)
        self.status_message.setFont(QtGui.QFont('Arial', 12))
        self.status_message.setAlignment(Qt.AlignCenter)
        self.status_message.setText("Calculating new nest...")
        self.status_message.setWordWrap(1)
        self.status_message.setFixedWidth(200)
        self.status_message.setFixedHeight(100)
        self.status_message.setStyleSheet("margin:0px 20px 0px 0px; background-color: blue")
        self.grid_layout.addWidget(self.status_message, 1, 2, Qt.AlignTop)

        self.status_message.setVisible(1)

        self.grid_layout.addWidget(self.scroll_area, 3, 0, 1, 5, Qt.AlignHCenter)###
        self.scroll_area.show()

        self.repaint()

        if len(part_lengths) != 0 and stock_length != -1 and left_waste != -1 and right_waste != -1 and spacing != -1:
            (final_patterns, final_allocations, part_lengths, part_names, b, spacing, left_waste, right_waste,
             stock_length) = length_nest_pro(part_lengths, b, part_names, spacing, left_waste, right_waste,
                                             stock_length)

            if len(final_patterns) == 0:
                self.status_message.setVisible(0)
                self.error_message.setVisible(1)
            elif (np.dot(final_patterns, final_allocations) != b).all():
                self.status_message.setVisible(0)
                self.error_message3.setVisible(1)
            else:
                self.status_message.setVisible(0)
                self.success_message.setVisible(1)

                self.draw_nests(final_patterns, final_allocations, part_lengths, part_names, spacing, left_waste,
                                right_waste, stock_length)
        else:
            self.status_message.setVisible(0)
            self.error_message2.setVisible(1)

    def draw_nests(self, final_patterns, final_allocations, part_lengths, part_names, spacing, left_waste,
                   right_waste, stock_length):

        # Find number of patterns
        (num_rows, num_columns) = np.shape(final_patterns)

        if num_columns > 15:
            canvas = QtGui.QPixmap(1100, 402 + (num_columns - 15) * 20)
            canvas.fill(QColor(150, 150, 150))
            self.label.setPixmap(canvas)
            self.label.setAlignment(Qt.AlignCenter)

        part_lengths = part_lengths * 1000 / stock_length
        # b = b * 1000 / stock_length  # TODO find out if this is needed
        spacing = spacing * 1000 / stock_length
        left_waste = left_waste * 1000 / stock_length
        right_waste = right_waste * 1000 / stock_length

        # Create painter for empty stock
        painter = QtGui.QPainter(self.label.pixmap())

        # Create pen for painter
        pen = QtGui.QPen()
        pen.setWidth(1)
        pen.setColor(QtGui.QColor(100, 100, 100))
        painter.setPen(pen)

        # Create brush for painter
        brush = QtGui.QBrush()
        brush.setColor(QtGui.QColor(200, 200, 200))
        brush.setStyle(Qt.SolidPattern)
        painter.setBrush(brush)

        # Draw stock lengths
        for i in range(num_columns):
            brush.setColor(QtGui.QColor(200, 200, 200))
            painter.setBrush(brush)
            painter.drawRects(QtCore.QRect(70, 50 + 20 * i, 1000, 16))
            brush.setColor(QtGui.QColor(100, 100, 100))
            painter.setBrush(brush)
            painter.drawRects(QtCore.QRect(70, 53 + 20 * i, int(round(left_waste)), 10))
            painter.drawRects(
                QtCore.QRect(int(round(70 + 1000 - right_waste)), 53 + 20 * i, int(round(right_waste)), 10))
        painter.end()

        pastel_red = QtGui.QColor(255, 154, 162)
        pastel_peach = QtGui.QColor(255, 183, 178)
        pastel_orange = QtGui.QColor(255, 218, 193)
        pastel_yellow = QtGui.QColor(226, 240, 203)
        pastel_green = QtGui.QColor(181, 234, 215)
        pastel_blue = QtGui.QColor(199, 206, 234)

        color_set = []
        for i in range(num_rows):
            if i % 6 == 0:
                color_set = np.append(color_set, [pastel_red], 0)
            if i % 6 == 1:
                color_set = np.append(color_set, [pastel_peach], 0)
            if i % 6 == 2:
                color_set = np.append(color_set, [pastel_orange], 0)
            if i % 6 == 3:
                color_set = np.append(color_set, [pastel_yellow], 0)
            if i % 6 == 4:
                color_set = np.append(color_set, [pastel_green], 0)
            if i % 6 == 5:
                color_set = np.append(color_set, [pastel_blue], 0)

        style_set = []
        for i in range(num_rows):
            if math.floor(i / 6) == 0:
                style_set = np.append(style_set, [Qt.SolidPattern], 0)
            if math.floor(i / 6) == 1:
                style_set = np.append(style_set, [Qt.SolidPattern], 0)
            if math.floor(i / 6) == 2:
                style_set = np.append(style_set, [Qt.SolidPattern], 0)
            if math.floor(i / 6) == 3:
                style_set = np.append(style_set, [Qt.SolidPattern], 0)
            if math.floor(i / 6) == 4:
                style_set = np.append(style_set, [Qt.SolidPattern], 0)
            if math.floor(i / 6) == 5:
                style_set = np.append(style_set, [Qt.SolidPattern], 0)

        painter2 = QtGui.QPainter(self.label.pixmap())
        pen2 = QtGui.QPen()
        pen2.setWidth(1)
        pen2.setColor(QtGui.QColor(0, 0, 0))
        painter2.setPen(pen2)

        brush2 = QtGui.QBrush()
        brush2.setColor(pastel_red)
        brush2.setStyle(Qt.SolidPattern)
        painter2.setBrush(brush2)

        # Draw parts in each nest
        for i in range(num_columns):
            nested_length = left_waste
            for j in range(num_rows):
                for k in range(int(final_patterns[j, i])):
                    brush2.setColor(color_set[j])
                    brush2.setStyle(int(style_set[j]))
                    painter2.setBrush(brush2)
                    painter2.drawRects(
                        QtCore.QRect(int(round(70 + nested_length)), 50 + 20 * i, int(round(part_lengths[j].item())),
                                     16))
                    if j >= 6:
                        brush2.setStyle(Qt.NoBrush)
                        painter2.setBrush(brush2)
                        painter2.drawRects(QtCore.QRect(int(round(70 + nested_length)) + 3, 53 + 20 * i,
                                                        int(round(part_lengths[j].item())) - 6, 10))
                    nested_length += part_lengths[j].item() + spacing
        painter2.end()

        # Create painter for text
        painter3 = QtGui.QPainter(self.label.pixmap())
        pen3 = QtGui.QPen()
        pen3.setWidth(1)
        pen3.setColor(QtGui.QColor(0, 0, 0))
        painter3.setPen(pen3)

        font = QtGui.QFont()
        font.setFamily('Times')
        font.setBold(True)
        font.setUnderline(True)
        font.setPointSize(10)
        painter3.setFont(font)
        painter3.drawText(70, 25, 1000, 16, Qt.AlignCenter, 'PATTERN')

        font.setBold(False)
        font.setUnderline(False)
        font.setPointSize(8)
        painter3.setFont(font)

        # Draw part names on each part
        for i in range(num_columns):
            nested_length = left_waste
            for j in range(num_rows):
                for k in range(int(final_patterns[j, i])):
                    painter3.drawText(int(round(70 + nested_length)), 50 + 20 * i, int(round(part_lengths[j].item())),
                                      16, Qt.AlignCenter, part_names[j])
                    nested_length += part_lengths[j].item() + spacing

        # TODO add legend with part info

        # painter3.drawText(50, 50, 100, 16, Qt.AlignCenter, 'name1')
        # painter3.drawText(50, 70, 100, 16, Qt.AlignCenter, 'name2')
        # painter3.drawText(50, 90, 100, 16, Qt.AlignCenter, 'name3')
        # painter3.drawText(50, 110, 100, 16, Qt.AlignCenter, 'name4')
        # painter3.drawText(50, 130, 100, 16, Qt.AlignCenter, 'name5')
        # painter3.drawText(50 + 100, 130, 100, 16, Qt.AlignCenter, 'name6')
        # painter3.end()

        # painter3 = QtGui.QPainter(self.label.pixmap())
        # pen3 = QtGui.QPen()
        # pen3.setWidth(1)
        # pen3.setColor(QtGui.QColor(0, 0, 0))
        # painter3.setPen(pen3)

        # font = QtGui.QFont()
        # font.setFamily('Times')
        font.setBold(True)
        font.setUnderline(True)
        font.setPointSize(10)
        painter3.setFont(font)
        painter3.drawText(0, 25, 65, 16, Qt.AlignRight, 'QTY')

        font.setBold(False)
        font.setUnderline(False)
        painter3.setFont(font)
        qty = np.zeros((num_columns, 1))
        for i in range(num_columns):
            qty[i] = final_allocations[i]
            painter3.drawText(0, 51 + 20 * i, 65, 16, Qt.AlignRight, str(int(qty[i].item())) + ' X')

        font.setBold(True)
        font.setUnderline(True)
        font.setPointSize(10)
        painter3.setFont(font)
        painter3.drawText(0, 65 + 20 * num_columns, 150, 16, Qt.AlignRight,
                          'TOTAL: ' + str(int(np.sum(final_allocations))) + ' lengths')
        painter3.end()

        self.label.update()


def main():
    # Create window
    window = Window()

    # Show window
    window.show()
    window.t1.update_table_width(window.t1)

    sys.exit(app.exec_())


# Run Program
main()
