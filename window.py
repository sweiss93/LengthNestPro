# import math
import numpy as np
# import time
import math
# import sys
import os
from PyQt5 import QtWidgets, QtGui, QtCore
from PyQt5.QtWidgets import QMainWindow, QTableWidget, QTableWidgetItem, QGridLayout, QAction, QFileDialog
from PyQt5.QtGui import QColor, QIcon, QBrush, QLinearGradient
from PyQt5.QtCore import Qt, QThread
from xml.etree import ElementTree
from nest_calculation import CalculateThread
# from fractions import Fraction


# Create subclass of QMainWindow for the application window
class Window(QMainWindow):
    def __init__(self):
        super().__init__()

        # Initialize attributes
        self.part_quantities = []
        self.part_lengths = []
        self.part_names = []

        # Initialize error code to 0 to signify no errors (to be used in length_nest_pro_calculate)
        self.error = 0

        # Create a default file path for saving and opening files
        user = os.getlogin()
        self.default_path_string = "C:/Users/" + user + "/Documents"

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
        self.setGeometry(150, 35, 1000, 600)  # TODO make window and contents adjustable to any size, allow zooming

        self.setWindowTitle(f"LengthNestPro, The free 1D nesting optimizer")
        self.setWindowIcon(QtGui.QIcon("C:/Program Files (x86)/LengthNestPro v1.3/icon.ico"))
        self.statusBar().showMessage('Ready')

        # Setup menu bar options
        # Create new action
        new_action = QAction(QIcon('new.png'), '&New', self)
        new_action.setShortcut('Ctrl+N')
        new_action.setStatusTip('New document')
        new_action.triggered.connect(self.new_call)

        # Create open action
        open_action = QAction(QIcon('open.png'), '&Open', self)
        open_action.setShortcut('Ctrl+O')
        open_action.setStatusTip('Open document')
        open_action.triggered.connect(self.open_call)

        # Create save action
        save_action = QAction(QIcon('save.png'), '&Save', self)
        save_action.setShortcut('Ctrl+S')
        save_action.setStatusTip('Save document')
        save_action.triggered.connect(self.save_call)

        # Create quit action
        quit_action = QAction(QIcon('quit.png'), '&Quit', self)
        quit_action.setShortcut('Ctrl+Q')
        quit_action.setStatusTip('Quit application')
        quit_action.triggered.connect(self.quit_call)

        # Create menu bar and add actions
        menu_bar = self.menuBar()
        file_menu = menu_bar.addMenu('&File')
        file_menu.addAction(new_action)
        file_menu.addAction(open_action)
        file_menu.addAction(save_action)
        file_menu.addAction(quit_action)

        # Create headers
        self.header1()
        # self.header2()
        self.header3()

        # Create blank canvas by placing a label object in the window and setting its properties
        self.nest_image = QtWidgets.QLabel()
        canvas = QtGui.QPixmap(1100, 360)
        canvas.fill(QColor(150, 150, 150))
        self.nest_image.setPixmap(canvas)

        # Place nest_image inside of a scroll area
        self.scroll_area = QtWidgets.QScrollArea()
        self.scroll_area.setFixedWidth(1116)
        self.scroll_area.setFixedHeight(362)
        self.scroll_area.setWidgetResizable(True)
        self.scroll_area.setWidget(self.nest_image)
        self.scroll_area.setVerticalScrollBarPolicy(Qt.ScrollBarAlwaysOn)
        self.nest_image.setAlignment(Qt.AlignCenter)

        # Set up "Required Parts" table
        self.t1 = self.Table()
        self.t1.expandable = True

        # Connect cellChanged signal to a function that can update the table dimensions based on the new entry
        self.t1.cellChanged.connect(self.t1.cell_was_changed)

        # Fix width of left header and center labels
        self.t1.verticalHeader().setFixedWidth(25)
        self.t1.verticalHeader().setDefaultAlignment(Qt.AlignHCenter)

        # Fix height of table
        # self.t1.setFixedHeight(265)

        self.t1.starting_num_rows = 6
        self.t1.setFixedHeight(21 + 30 * self.t1.starting_num_rows)
        self.t1.setRowCount(self.t1.starting_num_rows)
        self.t1.setColumnCount(3)
        self.t1.setColumnWidth(0, 60)
        self.t1.setColumnWidth(1, 60)
        self.t1.setColumnWidth(2, 120)
        self.t1.setHorizontalHeaderLabels(["Qty", "Length", "Name / ID"])

        self.t1.update_table_width(self.t1)

        qty = ["", "", "", "", "", "", "", ""]

        qty[0] = QTableWidgetItem("9000")
        qty[1] = QTableWidgetItem("3500")
        qty[2] = QTableWidgetItem("2500")
        qty[3] = QTableWidgetItem("")
        qty[4] = QTableWidgetItem("")
        qty[5] = QTableWidgetItem("")
        qty[6] = QTableWidgetItem("")
        qty[7] = QTableWidgetItem("")

        qty[0].setTextAlignment(Qt.AlignCenter)
        qty[1].setTextAlignment(Qt.AlignCenter)
        qty[2].setTextAlignment(Qt.AlignCenter)
        qty[3].setTextAlignment(Qt.AlignCenter)
        qty[4].setTextAlignment(Qt.AlignCenter)
        qty[5].setTextAlignment(Qt.AlignCenter)
        qty[6].setTextAlignment(Qt.AlignCenter)
        qty[7].setTextAlignment(Qt.AlignCenter)

        length = ["", "", "", "", "", "", "", ""]

        length[0] = QTableWidgetItem("44.9")
        length[1] = QTableWidgetItem("79.11")
        length[2] = QTableWidgetItem("31.25")
        length[3] = QTableWidgetItem("")
        length[4] = QTableWidgetItem("")
        length[5] = QTableWidgetItem("")
        length[6] = QTableWidgetItem("")
        length[7] = QTableWidgetItem("")

        length[0].setTextAlignment(Qt.AlignCenter)
        length[1].setTextAlignment(Qt.AlignCenter)
        length[2].setTextAlignment(Qt.AlignCenter)
        length[3].setTextAlignment(Qt.AlignCenter)
        length[4].setTextAlignment(Qt.AlignCenter)
        length[5].setTextAlignment(Qt.AlignCenter)
        length[6].setTextAlignment(Qt.AlignCenter)
        length[7].setTextAlignment(Qt.AlignCenter)

        name = ["", "", "", "", "", "", "", ""]

        name[0] = QTableWidgetItem("L15762")
        name[1] = QTableWidgetItem("N42719")
        name[2] = QTableWidgetItem("P58634")
        name[3] = QTableWidgetItem("")
        name[4] = QTableWidgetItem("")
        name[5] = QTableWidgetItem("")
        name[6] = QTableWidgetItem("")
        name[7] = QTableWidgetItem("")

        name[0].setTextAlignment(Qt.AlignCenter)
        name[1].setTextAlignment(Qt.AlignCenter)
        name[2].setTextAlignment(Qt.AlignCenter)
        name[3].setTextAlignment(Qt.AlignCenter)
        name[4].setTextAlignment(Qt.AlignCenter)
        name[5].setTextAlignment(Qt.AlignCenter)
        name[6].setTextAlignment(Qt.AlignCenter)
        name[7].setTextAlignment(Qt.AlignCenter)

        self.t1.setItem(0, 0, qty[0])
        self.t1.setItem(1, 0, qty[1])
        self.t1.setItem(2, 0, qty[2])
        self.t1.setItem(3, 0, qty[3])
        self.t1.setItem(4, 0, qty[4])
        self.t1.setItem(5, 0, qty[5])
        self.t1.setItem(6, 0, qty[6])
        self.t1.setItem(7, 0, qty[7])
        self.t1.setItem(0, 1, length[0])
        self.t1.setItem(1, 1, length[1])
        self.t1.setItem(2, 1, length[2])
        self.t1.setItem(3, 1, length[3])
        self.t1.setItem(4, 1, length[4])
        self.t1.setItem(5, 1, length[5])
        self.t1.setItem(6, 1, length[6])
        self.t1.setItem(7, 1, length[7])
        self.t1.setItem(0, 2, name[0])
        self.t1.setItem(1, 2, name[1])
        self.t1.setItem(2, 2, name[2])
        self.t1.setItem(3, 2, name[3])
        self.t1.setItem(4, 2, name[4])
        self.t1.setItem(5, 2, name[5])
        self.t1.setItem(6, 2, name[6])
        self.t1.setItem(7, 2, name[7])

        # Set up "Nesting Settings" table
        self.t2 = self.Table()
        self.t2.expandable = False

        # Fix width of left header and center labels
        self.t2.verticalHeader().setFixedWidth(150)
        self.t2.verticalHeader().setDefaultAlignment(Qt.AlignHCenter)

        self.t2.starting_num_rows = 6
        # Fix height of table
        self.t2.setFixedHeight(21 + 30 * self.t2.starting_num_rows)
        self.t2.setRowCount(self.t2.starting_num_rows)
        self.t2.setColumnCount(1)
        self.t2.setColumnWidth(0, 150)
        self.t2.setHorizontalHeaderLabels([""])
        self.t2.setVerticalHeaderLabels(["Stock Length", "Left Waste", "Right Waste", "Spacing", "Max Parts Per Nest "
                                                                                                 "(goal)",
                                         "Max # of Containers (goal)"])

        self.stock_length = QTableWidgetItem("240")
        self.left_waste = QTableWidgetItem("4.72")
        self.right_waste = QTableWidgetItem("0.5")
        self.spacing = QTableWidgetItem("0.29")
        self.max_parts_per_nest = QTableWidgetItem("4")
        self.max_containers = QTableWidgetItem("4")

        self.stock_length.setTextAlignment(Qt.AlignCenter)
        self.left_waste.setTextAlignment(Qt.AlignCenter)
        self.right_waste.setTextAlignment(Qt.AlignCenter)
        self.spacing.setTextAlignment(Qt.AlignCenter)
        self.max_parts_per_nest.setTextAlignment(Qt.AlignCenter)
        self.max_containers.setTextAlignment(Qt.AlignCenter)

        self.t2.setItem(0, 0, self.stock_length)
        self.t2.setItem(1, 0, self.left_waste)
        self.t2.setItem(2, 0, self.right_waste)
        self.t2.setItem(3, 0, self.spacing)
        self.t2.setItem(4, 0, self.max_parts_per_nest)
        self.t2.setItem(5, 0, self.max_containers)

        # Enter function to create calculate button
        self.calculate()

        # Enter function to create calculate button
        self.cancel()

        # Create status messages
        self.error_message = QtWidgets.QLabel(self)
        self.error_message.setHidden(True)
        self.error_message.setFont(QtGui.QFont('Arial', 12))
        self.error_message.setAlignment(Qt.AlignCenter)
        self.error_message.setText("One or more of the parts is too long for the available nesting length.")
        self.error_message.setWordWrap(True)
        self.error_message.setFixedWidth(200)
        self.error_message.setFixedHeight(100)
        self.error_message.setStyleSheet("margin:0px 20px 0px 0px; padding:0px 10px 0px 10px; background-color: red")
        self.grid_layout.addWidget(self.error_message, 1, 2, Qt.AlignCenter)

        self.error_message2 = QtWidgets.QLabel(self)
        self.error_message2.setHidden(True)
        self.error_message2.setFont(QtGui.QFont('Arial', 12))
        self.error_message2.setAlignment(Qt.AlignCenter)
        self.error_message2.setText("Some values still need to be entered.")
        self.error_message2.setWordWrap(True)
        self.error_message2.setFixedWidth(200)
        self.error_message2.setFixedHeight(100)
        self.error_message2.setStyleSheet("margin:0px 20px 0px 0px; padding:0px 10px 0px 10px; background-color: red")
        self.grid_layout.addWidget(self.error_message2, 1, 2, Qt.AlignCenter)

        self.error_message3 = QtWidgets.QLabel(self)
        self.error_message3.setHidden(True)
        self.error_message3.setFont(QtGui.QFont('Arial', 12))
        self.error_message3.setAlignment(Qt.AlignCenter)
        self.error_message3.setText("Nested quantities do not match required quantities.")
        self.error_message3.setWordWrap(True)
        self.error_message3.setFixedWidth(200)
        self.error_message3.setFixedHeight(100)
        self.error_message3.setStyleSheet("margin:0px 20px 0px 0px; padding:0px 10px 0px 10px; background-color: red")
        self.grid_layout.addWidget(self.error_message3, 1, 2, Qt.AlignCenter)

        self.error_message4 = QtWidgets.QLabel(self)
        self.error_message4.setHidden(True)
        self.error_message4.setFont(QtGui.QFont('Arial', 12))
        self.error_message4.setAlignment(Qt.AlignCenter)
        self.error_message4.setText("Calculation was canceled.")
        self.error_message4.setWordWrap(True)
        self.error_message4.setFixedWidth(200)
        self.error_message4.setFixedHeight(100)
        self.error_message4.setStyleSheet("margin:0px 20px 0px 0px; padding:0px 10px 0px 10px; background-color: rgb("
                                          "100, 100, 0)")
        self.grid_layout.addWidget(self.error_message4, 1, 2, Qt.AlignCenter)

        self.success_message = QtWidgets.QLabel(self)
        self.success_message.setHidden(True)
        self.success_message.setFont(QtGui.QFont('Arial', 12))
        self.success_message.setAlignment(Qt.AlignCenter)
        self.success_message.setText("Parts were nested successfully.")
        self.success_message.setWordWrap(True)
        self.success_message.setFixedWidth(200)
        self.success_message.setFixedHeight(100)
        self.success_message.setStyleSheet("margin:0px 20px 0px 0px; padding:0px 10px 0px 10px; background-color: "
                                           "green")
        self.grid_layout.addWidget(self.success_message, 1, 2, Qt.AlignCenter)

        self.status_message = QtWidgets.QLabel(self)
        self.status_message.setHidden(True)
        self.status_message.setFont(QtGui.QFont('Arial', 12))
        self.status_message.setAlignment(Qt.AlignCenter)
        self.status_message.setText("Calculating new nest...")
        self.status_message.setWordWrap(True)
        self.status_message.setFixedWidth(200)
        self.status_message.setFixedHeight(100)
        self.status_message.setStyleSheet("margin:0px 20px 0px 0px; padding:0px 10px 0px 10px; background-color: blue")
        self.grid_layout.addWidget(self.status_message, 1, 2, Qt.AlignCenter)

        self.status_message2 = QtWidgets.QLabel(self)
        self.status_message2.setHidden(True)
        self.status_message2.setFont(QtGui.QFont('Arial', 12))
        self.status_message2.setAlignment(Qt.AlignCenter)
        self.status_message2.setText("Click 'Calculate' to begin nesting.")
        self.status_message2.setWordWrap(True)
        self.status_message2.setFixedWidth(200)
        self.status_message2.setFixedHeight(100)
        self.status_message2.setStyleSheet("margin:0px 20px 0px 0px; padding:0px 10px 0px 10px; background-color: "
                                           "rgb(100, 100, 100); color: rgb(255, 255, 255)")
        self.grid_layout.addWidget(self.status_message2, 1, 2, Qt.AlignCenter)

        self.status_message2.setVisible(True)

        self.grid_layout.addWidget(self.h1, 0, 1, Qt.AlignHCenter)
        self.grid_layout.addWidget(self.h3, 0, 3, Qt.AlignHCenter)
        self.grid_layout.addWidget(self.t1, 1, 1, 2, 1, Qt.AlignLeft)
        self.grid_layout.addWidget(self.t2, 1, 3, 2, 1, Qt.AlignTop)
        # self.grid_layout.addWidget(self.cancel_btn, 2, 0, 1, 5, Qt.AlignCenter)
        self.grid_layout.addWidget(self.calc_btn, 2, 2, 1, 1, Qt.AlignCenter)
        self.grid_layout.addWidget(self.scroll_area, 4, 0, 1, 5, Qt.AlignHCenter)
        self.scroll_area.show()

        self.grid_layout.setColumnStretch(0, 11)
        self.grid_layout.setColumnStretch(1, 13)
        self.grid_layout.setColumnStretch(2, 10)
        self.grid_layout.setColumnStretch(3, 13)
        self.grid_layout.setColumnStretch(4, 9)

        self.grid_layout.setRowStretch(0, 1)
        self.grid_layout.setRowStretch(1, 1)
        self.grid_layout.setRowStretch(2, 1)
        self.grid_layout.setRowStretch(3, 1)

    # Create table class
    class Table(QTableWidget):
        def __init__(self):
            super().__init__()
            # Adjust style of grid lines
            self.setShowGrid(False)
            self.setStyleSheet('QTableView::item {border-right: 1px solid #909090; border-bottom: 1px solid #909090;}')

        def check_row_for_contents(self, row_number):
            num_columns = self.columnCount()
            for i in range(num_columns):
                if hasattr(self.item(row_number, i), 'text'):
                    if self.item(row_number, i).text() != '':
                        return True
            # If this code is reached, then there were no contents in any cells in the specified row
            return False

        def add_row(self):
            current_row_count = self.rowCount()
            if self.expandable:
                self.insertRow(current_row_count)
                for i in range(self.columnCount()):
                    self.new_item = QTableWidgetItem("")
                    self.new_item.setTextAlignment(Qt.AlignCenter)
                    self.setItem(current_row_count, i, self.new_item)

        def remove_row(self):
            # Check number of rows in table
            num_rows = self.rowCount()
            last_row_index = num_rows - 1

            # Remove last row
            self.removeRow(last_row_index)

            # Check if more empty rows need to be deleted from the end of the table
            rows_need_deleted = 1
            while rows_need_deleted == 1:
                if not self.check_row_for_contents(last_row_index - 1) and num_rows > self.starting_num_rows:
                    self.removeRow(last_row_index)
                    num_rows -= 1
                    last_row_index -= 1
                else:
                    rows_need_deleted = 0

        def cell_was_changed(self):
            self.update_num_rows()
            self.updateGeometries()
            self.update_table_width(self)

        def update_num_rows(self):
            # Check number of rows in table
            num_rows = self.rowCount()
            last_row_index = num_rows - 1

            # Add a row to the table if the last row has any contents
            if self.check_row_for_contents(last_row_index):
                self.add_row()

            # Remove a row from the table if the second to last row has no contents (assumes there will always be an
            #   empty row after any contents)
            if not self.check_row_for_contents(last_row_index - 1) and num_rows > self.starting_num_rows:
                self.remove_row()

        def update_table_width(self, table):
            if self:
                width = table.verticalHeader().width()
                width += table.horizontalHeader().length()
                if table.verticalScrollBar().isVisible():
                    width += table.verticalScrollBar().width() - 1
                width += 1
                width += table.frameWidth() * 2
                table.setFixedWidth(width)

        def keyPressEvent(self, event):
            if event.key() == 16777223:  # Delete
                self.delete_cell_contents()
            elif event.key() == 16777221 or event.key() == 16777220:  # Enter
                self.enter_was_pressed()
            else:
                super().keyPressEvent(event)

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

            # Temporarily change the current cell so that cell_value can update to the typed value before it is checked
            self.setCurrentCell(current_row + 1, current_column)

            # Extract value of cell that was active when user pressed enter
            cell_value = self.item(current_row, current_column).text()

            # Highlight the correct cell based on the status of the table
            # TODO remove last condition after adding max_containers functionality since no rows will be hidden
            if self.rowCount() != current_row + 1 or (cell_value != "" and self.expandable):
                self.setCurrentCell(current_row + 1, current_column)
            else:
                self.setCurrentCell(current_row, current_column)

        def resizeEvent(self, *args, **kwargs):
            self.cell_was_changed()

    # Functions to setup widgets

    def new_call(self):
        self.t1.clearContents()

    def open_call(self):

        # Allow user to select xml file to open
        file_path = 0
        if file_path == 0:
            file_path = QFileDialog.getOpenFileName(QFileDialog(), "", self.default_path_string,
                                                    "LengthNestPro xml (*.LNP.xml)")[0]
            if file_path:
                tree = ElementTree.parse(file_path)
                nesting_job = tree.getroot()

                # Create blank list with length equal to the number of parts in the nesting job
                blank_list = []
                required_parts = nesting_job.find('requiredParts')
                for i in range(len(required_parts)):
                    blank_list.append(QTableWidgetItem(""))

                # Copy blank list to initialize each attribute
                name = blank_list.copy()
                qty = blank_list.copy()
                length = blank_list.copy()

                # Clear contents from table
                self.t1.clearContents()

                # Extract info for each part and add it to "required parts" table
                for i, part in enumerate(required_parts):
                    name[i] = QTableWidgetItem(part.find('name').text)
                    qty[i] = QTableWidgetItem(part.find('qty').text)
                    length[i] = QTableWidgetItem(part.find('length').text)
                    name[i].setTextAlignment(Qt.AlignCenter)
                    qty[i].setTextAlignment(Qt.AlignCenter)
                    length[i].setTextAlignment(Qt.AlignCenter)
                    self.t1.setItem(i, 0, qty[i])
                    self.t1.setItem(i, 1, length[i])
                    self.t1.setItem(i, 2, name[i])

                # Extract nesting settings and add them to "nesting settings" table
                nesting_settings = nesting_job.find('nestingSettings')

                if hasattr(nesting_settings.find('stockLength'), 'text'):
                    stock_length = QTableWidgetItem(nesting_settings.find('stockLength').text)
                    stock_length.setTextAlignment(Qt.AlignCenter)
                    self.t2.setItem(0, 0, stock_length)

                if hasattr(nesting_settings.find('leftWaste'), 'text'):
                    left_waste = QTableWidgetItem(nesting_settings.find('leftWaste').text)
                    left_waste.setTextAlignment(Qt.AlignCenter)
                    self.t2.setItem(1, 0, left_waste)

                if hasattr(nesting_settings.find('rightWaste'), 'text'):
                    right_waste = QTableWidgetItem(nesting_settings.find('rightWaste').text)
                    right_waste.setTextAlignment(Qt.AlignCenter)
                    self.t2.setItem(2, 0, right_waste)

                if hasattr(nesting_settings.find('spacing'), 'text'):
                    spacing = QTableWidgetItem(nesting_settings.find('spacing').text)
                    spacing.setTextAlignment(Qt.AlignCenter)
                    self.t2.setItem(3, 0, spacing)

                if hasattr(nesting_settings.find('maxPartsPerNest'), 'text'):
                    max_parts_per_nest = QTableWidgetItem(nesting_settings.find('maxPartsPerNest').text)
                    max_parts_per_nest.setTextAlignment(Qt.AlignCenter)
                    self.t2.setItem(4, 0, max_parts_per_nest)

                if hasattr(nesting_settings.find('maxContainers'), 'text'):
                    max_containers = QTableWidgetItem(nesting_settings.find('maxContainers').text)
                    max_containers.setTextAlignment(Qt.AlignCenter)
                    self.t2.setItem(5, 0, max_containers)

                self.name_of_open_file = file_path
                self.setWindowTitle(f"LengthNestPro, The free 1D nesting optimizer - {self.name_of_open_file}")
                self.statusBar().showMessage('Ready')

    def save_call(self):
        # Allow user to select where to save xml file
        file_path = 0
        if file_path == 0:
            file_path = QFileDialog.getSaveFileName(QFileDialog(), "", self.default_path_string,
                                                    "LengthNestPro xml (*.LNP.xml)")[0]
            if file_path:
                # Construct xml file structure
                nesting_job = ElementTree.Element('nestingJob')
                required_parts = ElementTree.SubElement(nesting_job, 'requiredParts')
                nesting_settings = ElementTree.SubElement(nesting_job, 'nestingSettings')
                stock_length = ElementTree.SubElement(nesting_settings, 'stockLength')
                left_waste = ElementTree.SubElement(nesting_settings, 'leftWaste')
                right_waste = ElementTree.SubElement(nesting_settings, 'rightWaste')
                spacing = ElementTree.SubElement(nesting_settings, 'spacing')
                max_parts_per_nest = ElementTree.SubElement(nesting_settings, 'maxPartsPerNest')
                max_containers = ElementTree.SubElement(nesting_settings, 'maxContainers')

                # Add current data for nesting settings
                try:
                    stock_length.text = self.t2.item(0, 0).text()
                except 1:
                    pass
                try:
                    left_waste.text = self.t2.item(1, 0).text()
                except 1:
                    pass
                try:
                    right_waste.text = self.t2.item(2, 0).text()
                except 1:
                    pass
                try:
                    spacing.text = self.t2.item(3, 0).text()
                except 1:
                    pass
                try:
                    max_parts_per_nest.text = self.t2.item(4, 0).text()
                except 1:
                    pass
                try:
                    max_containers.text = self.t2.item(5, 0).text()
                except 1:
                    pass

                # Check how many parts have data in the "Required Parts" table
                # Assume that all rows could have data
                num_parts = self.t1.rowCount()

                # Extract number of columns in "Required Parts" table
                num_columns = self.t1.columnCount()

                # Initialize parameter to enter while loop
                no_data_found = 1
                while no_data_found:
                    # Check if there is any text in each cell
                    for i in range(num_columns):
                        if self.t1.item(num_parts - 1, i) is not None:
                            if self.t1.item(num_parts - 1, i).text() != "":
                                no_data_found = 0
                                break
                    else:
                        # At the end of the row's for loop, decrement num_parts, and return to start of while loop
                        num_parts -= 1
                        continue

                # Create blank list with length equal to the number of parts in the "required parts" table
                blank_list = []
                for i in range(num_parts):
                    blank_list.append(ElementTree.Element)

                # Copy blank list to initialize each attribute
                part = blank_list.copy()
                name = blank_list.copy()
                qty = blank_list.copy()
                length = blank_list.copy()

                # Add current data for required parts
                # for i in range(len(self.t1))
                for i in range(num_parts):
                    part[i] = ElementTree.SubElement(required_parts, 'part')
                    qty[i] = ElementTree.SubElement(part[i], 'qty')
                    length[i] = ElementTree.SubElement(part[i], 'length')
                    name[i] = ElementTree.SubElement(part[i], 'name')
                    qty[i].text = self.t1.item(i, 0).text()
                    length[i].text = self.t1.item(i, 1).text()
                    name[i].text = self.t1.item(i, 2).text()

                # create a new XML file with the results
                save_data_string = ElementTree.tostring(nesting_job)
                save_data_file = open(file_path, "wb")
                save_data_file.write(save_data_string)
                self.name_of_open_file = file_path
                self.setWindowTitle(f"LengthNestPro, The free 1D nesting optimizer - {self.name_of_open_file}")
                self.statusBar().showMessage('Ready')

    def save_results_call(self):
        # Make sure a file is open, and exit function if it is not
        try:
            self.name_of_open_file
        except AttributeError:
            # Exit function
            return
        # Create a file path where the results can be saved
        file_path = 0
        if file_path == 0:
            file_path = f"{self.name_of_open_file[:-4]}.results.xml"
            if file_path:
                # Construct xml file structure
                nesting_job = ElementTree.Element('nestingJob')
                required_parts = ElementTree.SubElement(nesting_job, 'requiredParts')
                nesting_settings = ElementTree.SubElement(nesting_job, 'nestingSettings')
                result = ElementTree.SubElement(nesting_job, 'result')
                stock_length = ElementTree.SubElement(nesting_settings, 'stockLength')
                left_waste = ElementTree.SubElement(nesting_settings, 'leftWaste')
                right_waste = ElementTree.SubElement(nesting_settings, 'rightWaste')
                spacing = ElementTree.SubElement(nesting_settings, 'spacing')
                max_parts_per_nest = ElementTree.SubElement(nesting_settings, 'maxPartsPerNest')
                max_containers = ElementTree.SubElement(nesting_settings, 'maxContainers')
                num_lengths_required = ElementTree.SubElement(result, 'numLengthsRequired')
                num_lengths_required.text = f"{self.calculator.final_required_lengths_minus_drop}"
                scrap_rate = ElementTree.SubElement(result, 'scrapRate')
                scrap_rate.text = f"{self.calculator.scrap_without_drop}"
                num_containers_required = ElementTree.SubElement(result, 'numContainersRequired')
                num_containers_required.text = f"{self.calculator.actual_max_containers}"

                # Add current data for nesting settings
                try:
                    stock_length.text = self.t2.item(0, 0).text()
                except 1:
                    pass
                try:
                    left_waste.text = self.t2.item(1, 0).text()
                except 1:
                    pass
                try:
                    right_waste.text = self.t2.item(2, 0).text()
                except 1:
                    pass
                try:
                    spacing.text = self.t2.item(3, 0).text()
                except 1:
                    pass
                try:
                    max_parts_per_nest.text = self.t2.item(4, 0).text()
                except 1:
                    pass
                try:
                    max_containers.text = self.t2.item(5, 0).text()
                except 1:
                    pass

                # Check how many parts have data in the "Required Parts" table
                # Assume that all rows could have data
                num_parts = self.t1.rowCount()

                # Extract number of columns in "Required Parts" table
                num_columns = self.t1.columnCount()

                # Initialize parameter to enter while loop
                no_data_found = 1
                while no_data_found:
                    # Check if there is any text in each cell
                    for i in range(num_columns):
                        if self.t1.item(num_parts - 1, i) is not None:
                            if self.t1.item(num_parts - 1, i).text() != "":
                                no_data_found = 0
                                break
                    else:
                        # At the end of the row's for loop, decrement num_parts, and return to start of while loop
                        num_parts -= 1
                        continue

                # Create blank list with length equal to the number of parts in the "required parts" table
                blank_list = []
                for i in range(num_parts):
                    blank_list.append(ElementTree.Element)

                # Copy blank list to initialize each attribute
                part = blank_list.copy()
                name = blank_list.copy()
                qty = blank_list.copy()
                length = blank_list.copy()

                # Add current data for required parts
                for i in range(num_parts):
                    part[i] = ElementTree.SubElement(required_parts, 'part')
                    qty[i] = ElementTree.SubElement(part[i], 'qty')
                    length[i] = ElementTree.SubElement(part[i], 'length')
                    name[i] = ElementTree.SubElement(part[i], 'name')
                    qty[i].text = self.t1.item(i, 0).text()
                    length[i].text = self.t1.item(i, 1).text()
                    name[i].text = self.t1.item(i, 2).text()

                # Create blank list with length equal to the number of patterns in the result
                blank_list = []
                num_patterns = len(self.calculator.final_allocations)
                for i in range(num_patterns):
                    blank_list.append(ElementTree.Element)

                # Copy blank list to initialize each attribute
                pattern = blank_list.copy()
                pattern_label = blank_list.copy()
                pattern_qty = blank_list.copy()

                # Create blank list of lists with length equal to the number of patterns in the result
                blank_list = []
                for i in range(num_patterns):
                    num_unique_parts = np.count_nonzero(self.calculator.final_patterns.T[i])
                    blank_list.append([])
                    for j in range(num_unique_parts):
                        blank_list[i].append(ElementTree.Element)

                nested_part = blank_list.copy()

                # Create blank list of lists with length equal to the number of patterns in the result
                blank_list = []
                for i in range(num_patterns):
                    num_unique_parts = np.count_nonzero(self.calculator.final_patterns.T[i])
                    blank_list.append([])
                    for j in range(num_unique_parts):
                        blank_list[i].append(ElementTree.Element)

                nested_part_name = blank_list.copy()

                # Create blank list of lists with length equal to the number of patterns in the result
                blank_list = []
                for i in range(num_patterns):
                    num_unique_parts = np.count_nonzero(self.calculator.final_patterns.T[i])
                    blank_list.append([])
                    for j in range(num_unique_parts):
                        blank_list[i].append(ElementTree.Element)

                nested_part_qty = blank_list.copy()

                # Add current data for required parts
                for i in range(num_patterns):
                    pattern[i] = ElementTree.SubElement(result, 'pattern')
                    pattern_label[i] = ElementTree.SubElement(pattern[i], 'patternLabel')
                    pattern_qty[i] = ElementTree.SubElement(pattern[i], 'patternQty')
                    pattern_label[i].text = f"{i}"
                    pattern_qty[i].text = f"{int(self.calculator.final_allocations[i])}"

                    # Cycle through nested parts in each pattern
                    for j in range(len(self.calculator.final_patterns)):
                        ii = 0
                        if self.calculator.final_patterns[j, i]:
                            nested_part[i][ii] = ElementTree.SubElement(pattern[i], 'nestedPart')
                            nested_part_name[i][ii] = ElementTree.SubElement(nested_part[i][ii], 'nestedPartName')
                            nested_part_qty[i][ii] = ElementTree.SubElement(nested_part[i][ii], 'nestedPartQty')
                            nested_part_name[i][ii].text = f"{self.part_names[j]}"
                            nested_part_qty[i][ii].text = f"{int(self.calculator.final_patterns[j, i])}"
                            ii += 1

                # create a new XML file with the results
                save_data_string = ElementTree.tostring(nesting_job)
                save_data_file = open(file_path, "wb")
                save_data_file.write(save_data_string)

    @staticmethod
    def quit_call():
        quit()

    def header1(self):
        # Create a label object in the window and set its properties
        self.h1 = QtWidgets.QLabel(self)
        self.h1.setFont(QtGui.QFont('Arial', 16))
        self.h1.setText("Required Parts")
        self.h1.adjustSize()
        self.h1.setFixedWidth(280)
        self.h1.setStyleSheet("padding:0px 0px")
        self.h1.setAlignment(Qt.AlignHCenter)

    def header3(self):
        # Create a label object in the window and set its properties
        self.h3 = QtWidgets.QLabel(self)
        self.h3.setFont(QtGui.QFont('Arial', 16))
        self.h3.setText("Nesting Settings")
        self.h3.adjustSize()
        self.h3.setStyleSheet("padding:0px 0px")
        self.h3.setAlignment(Qt.AlignHCenter)

    def calculate(self):
        self.calc_btn = QtWidgets.QPushButton(self)
        self.calc_btn.setText("Calculate")
        self.calc_btn.setFont(QtGui.QFont('Arial', 12))
        self.calc_btn.clicked.connect(self.gather_inputs)

    def cancel(self):
        self.cancel_btn = QtWidgets.QPushButton(self)
        self.cancel_btn.setText("Cancel")
        self.cancel_btn.setFont(QtGui.QFont('Arial', 12))
        self.cancel_btn.clicked.connect(self.cancel_calculate)
        self.cancel_btn.setVisible(False)

    def cancel_calculate(self):
        # Set cancellation flag so that length_nest_pro_calculate can check whether it should stop
        self.calculator.calculation_was_canceled = 1

    # Other functions

    def get_results(self):
        # self.final_patterns = results_list[0]
        # self.final_allocations = results_list[1]
        self.new_thread.exit()

    def gather_inputs(self):

        # Reinitialize error code
        self.error = 0

        # Initialize vectors to be extracted from table
        self.part_lengths = []
        self.part_quantities = []
        self.part_names = []

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
                try:
                    self.part_lengths = np.append(self.part_lengths, [float(length_text)], 0)
                except ValueError:
                    pass
                try:
                    self.part_quantities = np.append(self.part_quantities, [float(qty_text)], 0)
                except ValueError:
                    pass
                try:
                    self.part_names = np.append(self.part_names, [name_text], 0)
                except ValueError:
                    pass

        # Change row vectors to column vectors
        self.part_lengths = np.transpose([self.part_lengths])
        self.part_quantities = np.transpose([self.part_quantities])

        # Delete and recreate blank canvas
        self.nest_image.clear()
        self.nest_image = QtWidgets.QLabel()
        canvas = QtGui.QPixmap(1100, 400)
        canvas.fill(QColor(150, 150, 150))
        self.nest_image.setPixmap(canvas)
        self.scroll_area.setWidget(self.nest_image)
        self.nest_image.setAlignment(Qt.AlignCenter)

        # Initialize parameters
        self.stock_length = -1
        self.left_waste = -1
        self.right_waste = -1
        self.spacing = -1
        self.max_parts_per_nest = -1
        self.max_containers = -1

        # Extract "Nesting Settings" cells if available
        if self.t2.item(0, 0).text() != "":
            try:
                self.stock_length = float(self.t2.item(0, 0).text())
            except ValueError:
                pass
        if self.t2.item(1, 0).text() != "":
            try:
                self.left_waste = float(self.t2.item(1, 0).text())
            except ValueError:
                pass
        if self.t2.item(2, 0).text() != "":
            try:
                self.right_waste = float(self.t2.item(2, 0).text())
            except ValueError:
                pass
        if self.t2.item(3, 0).text() != "":
            try:
                self.spacing = float(self.t2.item(3, 0).text())
            except ValueError:
                pass
        if self.t2.item(4, 0).text() != "":
            # Make sure max_parts_per_nest is numeric, and change it to an integer
            if self.t2.item(4, 0).text().isnumeric():
                self.max_parts_per_nest = int(self.t2.item(4, 0).text())
            else:
                try:
                    # Try changing it to a float since a decimal would make it non-numeric
                    self.max_parts_per_nest = math.floor(float(self.t2.item(4, 0).text()))
                except ValueError:
                    # Must be a string, don't restrain the solution
                    self.max_parts_per_nest = -2
        if self.t2.item(5, 0).text() != "":
            # Make sure max_containers is numeric, and change it to an integer
            if self.t2.item(5, 0).text().isnumeric():
                self.max_containers = int(self.t2.item(5, 0).text())
            else:
                try:
                    # Try changing it to a float since a decimal would make it non-numeric
                    self.max_containers = math.floor(float(self.t2.item(5, 0).text()))
                except ValueError:
                    # Must be a string, don't restrain the solution
                    self.max_containers = -2

        # TODO ? add warning message if multiple parts have the same name but different lengths

        # Hide all messages except for "calculating new nest" message
        self.status_message2.setVisible(False)
        self.success_message.setVisible(False)
        self.error_message.setVisible(False)
        self.error_message2.setVisible(False)
        self.error_message3.setVisible(False)
        self.error_message4.setVisible(False)
        self.status_message.setVisible(True)

        # Run nesting code if the user has given enough values
        if len(self.part_lengths) != 0 and self.stock_length != -1 and self.left_waste != -1 \
                and self.right_waste != -1 and self.spacing != -1 and self.max_parts_per_nest != -1 \
                and self.max_containers != -1:

            # Run the nesting calculation thread.
            self.new_thread = QThread()

            self.calculator = CalculateThread(self)

            self.calculator.moveToThread(self.new_thread)

            self.calculator.results_signal.connect(self.get_results)
            self.new_thread.started.connect(self.calculator.run)

            # Replace calc_btn with cancel_btn
            self.calc_btn.setVisible(False)
            self.grid_layout.removeWidget(self.calc_btn)
            self.grid_layout.addWidget(self.cancel_btn, 2, 2, 1, 1, Qt.AlignCenter)
            self.cancel_btn.setVisible(True)

            self.new_thread.start()

            while self.new_thread.isRunning():
                self.app.processEvents()  # This keeps the GUI responsive.

            if self.calculator.calculation_was_canceled:
                # Adjust message
                self.status_message.setVisible(False)
                self.error_message4.setVisible(True)

                # Prevent further code from executing until calculator thread has finished.
                self.new_thread.wait()

                # Replace cancel_btn with calc_btn
                self.cancel_btn.setVisible(False)
                self.grid_layout.removeWidget(self.cancel_btn)
                self.grid_layout.addWidget(self.calc_btn, 2, 2, 1, 1, Qt.AlignCenter)
                self.calc_btn.setVisible(True)
            else:
                # Prevent further code from executing until calculator thread has finished.
                self.new_thread.wait()

                # Replace cancel_btn with calc_btn
                self.cancel_btn.setVisible(False)
                self.grid_layout.removeWidget(self.cancel_btn)
                self.grid_layout.addWidget(self.calc_btn, 2, 2, 1, 1, Qt.AlignCenter)
                self.calc_btn.setVisible(True)

                # Return error if one of the parts is too long
                if self.error == 1:
                    self.status_message.setVisible(False)
                    self.error_message.setVisible(True)
                # Check if the nested quantities match required quantities
                elif (np.dot(self.calculator.final_patterns,
                             self.calculator.final_allocations) != self.part_quantities).all():
                    self.status_message.setVisible(False)
                    self.error_message3.setVisible(True)
                # Show success message if there are no issues
                else:
                    self.status_message.setVisible(False)
                    self.success_message.setVisible(True)

                    # Call function to display the nests that were returned by length_nest_pro_calculate()
                    self.draw_nests()
        else:
            # Adjust message
            self.status_message.setVisible(False)
            self.error_message2.setVisible(True)

    def draw_nests(self):

        # Find number of patterns
        (num_rows, num_columns) = np.shape(self.calculator.final_patterns)

        if num_columns > 15:
            canvas = QtGui.QPixmap(1100, 422 + (num_columns - 15) * 20)
            canvas.fill(QColor(150, 150, 150))
            self.nest_image.setPixmap(canvas)
            self.nest_image.setAlignment(Qt.AlignCenter)

        pixel_scale_factor = 1000 / self.stock_length
        self.part_lengths = self.part_lengths * pixel_scale_factor
        self.spacing = self.spacing * pixel_scale_factor
        self.left_waste = self.left_waste * pixel_scale_factor
        self.right_waste = self.right_waste * pixel_scale_factor

        # Create painter for empty stock
        painter = QtGui.QPainter(self.nest_image.pixmap())

        # Create pen for painter
        pen = QtGui.QPen()
        pen.setWidth(1)
        pen.setColor(QtGui.QColor(100, 100, 100))
        painter.setPen(pen)

        # Create brush for painter
        brush = QtGui.QBrush()
        # brush.setColor(QtGui.QColor(200, 200, 200))
        brush.setStyle(Qt.SolidPattern)
        painter.setBrush(brush)

        # Draw stock lengths
        for i in range(num_columns):
            brush.setColor(QtGui.QColor(200, 200, 200))
            painter.setBrush(brush)
            painter.drawRects(QtCore.QRect(70, 75 + 20 * i, 1000, 16))
            brush.setColor(QtGui.QColor(100, 100, 100))
            painter.setBrush(brush)
            painter.drawRects(QtCore.QRect(70, 78 + 20 * i, int(round(self.left_waste)), 10))
            painter.drawRects(
                QtCore.QRect(int(round(70 + 1000 - self.right_waste)), 78 + 20 * i, int(round(self.right_waste)), 10))
        painter.end()

        red_list = np.array([255, 160, 160])
        orange_list = np.array([255, 200, 120])
        yellow_list = np.array([255, 255, 140])
        green_list = np.array([160, 255, 160])
        blue_list = np.array([150, 200, 255])
        purple_list = np.array([220, 170, 255])
        white_list = np.array([240, 240, 240])

        red = QtGui.QColor(red_list[0], red_list[1], red_list[2])
        orange = QtGui.QColor(orange_list[0], orange_list[1], orange_list[2])
        yellow = QtGui.QColor(yellow_list[0], yellow_list[1], yellow_list[2])
        green = QtGui.QColor(green_list[0], green_list[1], green_list[2])
        blue = QtGui.QColor(blue_list[0], blue_list[1], blue_list[2])
        purple = QtGui.QColor(purple_list[0], purple_list[1], purple_list[2])
        white = QtGui.QColor(white_list[0], white_list[1], white_list[2])

        color_adjustment_value = -35
        darker_red_list = red_list + color_adjustment_value
        darker_orange_list = orange_list + color_adjustment_value
        darker_yellow_list = yellow_list + color_adjustment_value
        darker_green_list = green_list + color_adjustment_value
        darker_blue_list = blue_list + color_adjustment_value
        darker_purple_list = purple_list + color_adjustment_value
        darker_white_list = white_list + color_adjustment_value

        darker_red = QtGui.QColor(darker_red_list[0], darker_red_list[1], darker_red_list[2])
        darker_orange = QtGui.QColor(darker_orange_list[0], darker_orange_list[1], darker_orange_list[2])
        darker_yellow = QtGui.QColor(darker_yellow_list[0], darker_yellow_list[1], darker_yellow_list[2])
        darker_green = QtGui.QColor(darker_green_list[0], darker_green_list[1], darker_green_list[2])
        darker_blue = QtGui.QColor(darker_blue_list[0], darker_blue_list[1], darker_blue_list[2])
        darker_purple = QtGui.QColor(darker_purple_list[0], darker_purple_list[1], darker_purple_list[2])
        darker_white = QtGui.QColor(darker_white_list[0], darker_white_list[1], darker_white_list[2])

        color_set = []
        for i in range(num_rows):
            if i % 7 == 0:
                color_set = np.append(color_set, [red], 0)
            if i % 7 == 1:
                color_set = np.append(color_set, [yellow], 0)
            if i % 7 == 2:
                color_set = np.append(color_set, [white], 0)
            if i % 7 == 3:
                color_set = np.append(color_set, [green], 0)
            if i % 7 == 4:
                color_set = np.append(color_set, [purple], 0)
            if i % 7 == 5:
                color_set = np.append(color_set, [orange], 0)
            if i % 7 == 6:
                color_set = np.append(color_set, [blue], 0)

        darker_color_set = []
        for i in range(num_rows):
            if i % 7 == 0:
                darker_color_set = np.append(darker_color_set, [darker_red], 0)
            if i % 7 == 1:
                darker_color_set = np.append(darker_color_set, [darker_yellow], 0)
            if i % 7 == 2:
                darker_color_set = np.append(darker_color_set, [darker_white], 0)
            if i % 7 == 3:
                darker_color_set = np.append(darker_color_set, [darker_green], 0)
            if i % 7 == 4:
                darker_color_set = np.append(darker_color_set, [darker_purple], 0)
            if i % 7 == 5:
                darker_color_set = np.append(darker_color_set, [darker_orange], 0)
            if i % 7 == 6:
                darker_color_set = np.append(darker_color_set, [darker_blue], 0)

        painter2 = QtGui.QPainter(self.nest_image.pixmap())
        pen2 = QtGui.QPen()
        pen2.setWidth(1)
        pen2.setColor(QtGui.QColor(0, 0, 0))
        painter2.setPen(pen2)

        brush2 = QtGui.QBrush()
        brush2.setColor(red)
        brush2.setStyle(Qt.SolidPattern)
        painter2.setBrush(brush2)

        color_sequence = self.calculator.sorted_by_length.copy()

        # Draw parts in each nest
        for i in range(num_columns):
            nested_length = self.left_waste
            for j in range(num_rows):
                for k in range(int(self.calculator.final_patterns[j, i])):

                    # Solid style
                    if 0 <= color_sequence[j] % 28 < 7:
                        pen2.setWidth(1)
                        pen2.setColor(QtGui.QColor(0, 0, 0))
                        painter2.setPen(pen2)
                        brush2.setColor(color_set[color_sequence[j]])
                        brush2.setStyle(Qt.SolidPattern)
                        painter2.setBrush(brush2)
                        painter2.drawRects(QtCore.QRect(int(round(70 + nested_length)), 
                                                        75 + 20 * i, 
                                                        int(round(self.part_lengths[j].item())), 
                                                        16))

                    # Diagonal style
                    if 7 <= color_sequence[j] % 28 < 14:
                        pen2.setWidth(1)
                        pen2.setColor(QtGui.QColor(0, 0, 0))
                        painter2.setPen(pen2)
                        brush2.setColor(color_set[color_sequence[j]])
                        brush2.setStyle(Qt.SolidPattern)
                        painter2.setBrush(brush2)
                        painter2.drawRects(QtCore.QRect(int(round(70 + nested_length)), 
                                                        75 + 20 * i, 
                                                        int(round(self.part_lengths[j].item())), 
                                                        16))

                        brush2.setColor(darker_color_set[color_sequence[j]])
                        brush2.setStyle(Qt.BDiagPattern)
                        painter2.setBrush(brush2)
                        painter2.drawRects(QtCore.QRect(int(round(70 + nested_length)), 
                                                        75 + 20 * i, 
                                                        int(round(self.part_lengths[j].item())), 
                                                        16))

                    # Border style
                    if 14 <= color_sequence[j] % 28 < 21:
                        pen2.setWidth(1)
                        pen2.setColor(QtGui.QColor(0, 0, 0))
                        painter2.setPen(pen2)
                        brush2.setColor(color_set[color_sequence[j]])
                        brush2.setStyle(Qt.SolidPattern)
                        painter2.setBrush(brush2)
                        painter2.drawRects(QtCore.QRect(int(round(70 + nested_length)), 
                                                        75 + 20 * i, 
                                                        int(round(self.part_lengths[j].item())), 
                                                        16))

                        brush2.setStyle(Qt.NoBrush)
                        painter2.setBrush(brush2)
                        pen2.setWidth(3)
                        pen2.setColor(darker_color_set[color_sequence[j]])
                        painter2.setPen(pen2)
                        painter2.drawRects(QtCore.QRect(int(round(70 + nested_length)) + 4, 
                                                        79 + 20 * i, 
                                                        int(round(self.part_lengths[j].item())) - 8, 
                                                        8))

                    # Double diagonal style
                    if 21 <= color_sequence[j] % 28 < 28:
                        pen2.setWidth(1)
                        pen2.setColor(QtGui.QColor(0, 0, 0))
                        painter2.setPen(pen2)
                        brush2.setColor(color_set[color_sequence[j]])
                        brush2.setStyle(Qt.SolidPattern)
                        painter2.setBrush(brush2)
                        painter2.drawRects(QtCore.QRect(int(round(70 + nested_length)), 
                                                        75 + 20 * i, 
                                                        int(round(self.part_lengths[j].item())), 
                                                        16))

                        brush2.setColor(darker_color_set[color_sequence[j]])
                        brush2.setStyle(Qt.DiagCrossPattern)
                        painter2.setBrush(brush2)
                        painter2.drawRects(QtCore.QRect(int(round(70 + nested_length)), 
                                                        75 + 20 * i, 
                                                        int(round(self.part_lengths[j].item())), 
                                                        16))

                    nested_length += self.part_lengths[j].item() + self.spacing
        painter2.end()

        # Create painter for text
        painter3 = QtGui.QPainter(self.nest_image.pixmap())
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
        painter3.drawText(70, 55, 1000, 16, Qt.AlignCenter, 'PATTERN')

        font.setBold(False)
        font.setUnderline(False)
        font.setPointSize(9)
        painter3.setFont(font)

        # Draw part names on each part
        for i in range(num_columns):
            nested_length = self.left_waste
            for j in range(num_rows):
                for k in range(int(self.calculator.final_patterns[j, i])):
                    width = 13 * len(self.part_names[j])
                    height = 14
                    gradient_width = width + 50
                    x_pos = int(round(70 + nested_length) + round((self.part_lengths[j].item() - gradient_width) / 2))
                    y_pos = 76 + 20 * i

                    linear_gradient = QLinearGradient(0, 0, gradient_width, 0)
                    linear_gradient.setColorAt(0, QtGui.QColor(255, 255, 255, 0))
                    linear_gradient.setColorAt(0.3, QtGui.QColor(255, 255, 255, 40))
                    linear_gradient.setColorAt(0.7, QtGui.QColor(255, 255, 255, 40))
                    linear_gradient.setColorAt(1, QtGui.QColor(255, 255, 255, 0))
                    painter3.setBrush(QBrush(linear_gradient))
                    painter3.setPen(Qt.NoPen)
                    painter3.setTransform(QtGui.QTransform().translate(x_pos, y_pos))
                    painter3.drawRect(QtCore.QRect(max(0, round((gradient_width - self.part_lengths[j].item()) / 2)), 
                                                   0, 
                                                   min(round(self.part_lengths[j].item()), gradient_width), 
                                                   height
                                                   ))

                    painter3.setBrush(Qt.NoBrush)
                    painter3.setPen(pen3)
                    painter3.setTransform(QtGui.QTransform().translate(0, 0))
                    painter3.setFont(font)
                    painter3.drawText(int(round(70 + nested_length)), 
                                      75 + 20 * i, 
                                      int(round(self.part_lengths[j].item())), 
                                      16, 
                                      Qt.AlignCenter, 
                                      self.part_names[j]
                                      )
                    nested_length += self.part_lengths[j].item() + self.spacing

        # TODO add legend with part info?

        font.setBold(True)
        font.setUnderline(True)
        font.setPointSize(10)
        painter3.setFont(font)
        painter3.drawText(0, 55, 65, 16, Qt.AlignRight, 'QTY')

        font.setBold(False)
        font.setUnderline(False)
        painter3.setFont(font)
        qty = np.zeros((num_columns, 1))
        for i in range(num_columns):
            qty[i] = self.calculator.final_allocations[i]
            painter3.drawText(0, 76 + 20 * i, 65, 16, Qt.AlignRight, str(int(qty[i].item())) + ' X')
        painter3.end()

        painter4 = QtGui.QPainter(self.nest_image.pixmap())
        brush4 = QtGui.QBrush()
        brush4.setColor(QtGui.QColor(210, 255, 210))
        brush4.setStyle(Qt.SolidPattern)
        pen4 = QtGui.QPen()
        pen4.setWidth(2)
        pen4.setColor(QtGui.QColor(0, 0, 0))
        painter4.setBrush(brush4)
        painter4.setPen(pen4)
        painter4.drawRect(245, 18, 610, 22)

        painter4.setPen(pen3)
        font.setBold(True)
        font.setUnderline(False)
        font.setPointSize(12)
        painter4.setFont(font)
        num_lengths_int = int(self.calculator.final_required_lengths)
        num_lengths_2place = round(self.calculator.final_required_lengths_minus_drop, 2)
        scrap = round(self.calculator.scrap_without_drop * 100, 1)
        containers = int(self.calculator.actual_max_containers)

        painter4.drawText(250, 20, 600, 16, Qt.AlignCenter,
                          f'- - - - - - - - {num_lengths_int} lengths ({num_lengths_2place}) '
                          f'- - - - - {scrap}% scrap - - - - - {containers} containers - - - - - - - -')
        painter4.end()

        self.nest_image.update()

        self.save_results_call()
