# import math
# import numpy as np
import time
# import math
import sys
# import os
# from PyQt5 import QtWidgets, QtGui, QtCore
from PyQt5.QtWidgets import QApplication
# from PyQt5.QtWidgets import QTableWidgetItem
from PyQt5.QtGui import QPalette, QColor
# from PyQt5.QtCore import Qt
# from xml.etree import ElementTree
# from nest_calculation import CalculateThread
# from fractions import Fraction
from window import Window

# TODO add results outputs such as scrap %
# TODO number or letter each pattern
# TODO add scale to patterns display (possibly behind them), or add person or car to side for size reference
# TODO add explain on hover
# TODO add help documentation to explain nesting algorithms and how to use the application
# TODO add more colors and/or patterns for part display
# TODO allow user to click on a nest pattern to show it in more detail
# TODO implement a xml template for default settings that opens on launch

# Start timer
start_time = time.time()

# Create the application
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


def main():
    # Create window
    window = Window()
    window.app = app

    # Show window
    window.show()
    window.t1.update_table_width(window.t1)

    # TODO change this to a default file that is always opened on start up; put file in lengthnestpro path
    # Allow user to select xml file to open
    # file_path = 0
    # if file_path == 0:
    #     file_path = window.default_path_string + "/container test.xml"
    #     if file_path:
    #         tree = ElementTree.parse(file_path)
    #         nesting_job = tree.getroot()
    #
    #         # Create blank list with length equal to the number of parts in the nesting job
    #         blank_list = []
    #         required_parts = nesting_job.find('requiredParts')
    #         for i in range(len(required_parts)):
    #             blank_list.append("")
    #
    #         # Copy blank list to initialize each attribute
    #         name = blank_list.copy()
    #         qty = blank_list.copy()
    #         length = blank_list.copy()
    #
    #         # Clear contents from table
    #         window.t1.clearContents()
    #
    #         # Extract info for each part and add it to "required parts" table
    #         i = 0
    #         for part in required_parts:
    #             name[i] = QTableWidgetItem(part.find('name').text)
    #             qty[i] = QTableWidgetItem(part.find('qty').text)
    #             length[i] = QTableWidgetItem(part.find('length').text)
    #             name[i].setTextAlignment(Qt.AlignCenter)
    #             qty[i].setTextAlignment(Qt.AlignCenter)
    #             length[i].setTextAlignment(Qt.AlignCenter)
    #             window.t1.setItem(i, 0, qty[i])
    #             window.t1.setItem(i, 1, length[i])
    #             window.t1.setItem(i, 2, name[i])
    #             i += 1
    #
    #         # Extract nesting settings and add them to "nesting settings" table
    #         nesting_settings = nesting_job.find('nestingSettings')
    #
    #         if hasattr(nesting_settings.find('stockLength'), 'text'):
    #             stock_length = QTableWidgetItem(nesting_settings.find('stockLength').text)
    #             stock_length.setTextAlignment(Qt.AlignCenter)
    #             window.t2.setItem(0, 0, stock_length)
    #
    #         if hasattr(nesting_settings.find('leftWaste'), 'text'):
    #             left_waste = QTableWidgetItem(nesting_settings.find('leftWaste').text)
    #             left_waste.setTextAlignment(Qt.AlignCenter)
    #             window.t2.setItem(1, 0, left_waste)
    #
    #         if hasattr(nesting_settings.find('rightWaste'), 'text'):
    #             right_waste = QTableWidgetItem(nesting_settings.find('rightWaste').text)
    #             right_waste.setTextAlignment(Qt.AlignCenter)
    #             window.t2.setItem(2, 0, right_waste)
    #
    #         if hasattr(nesting_settings.find('spacing'), 'text'):
    #             spacing = QTableWidgetItem(nesting_settings.find('spacing').text)
    #             spacing.setTextAlignment(Qt.AlignCenter)
    #             window.t2.setItem(3, 0, spacing)
    #
    #         if hasattr(nesting_settings.find('maxPartsPerNest'), 'text'):
    #             max_parts_per_nest = QTableWidgetItem(nesting_settings.find('maxPartsPerNest').text)
    #             max_parts_per_nest.setTextAlignment(Qt.AlignCenter)
    #             window.t2.setItem(4, 0, max_parts_per_nest)
    #
    #         if hasattr(nesting_settings.find('maxContainers'), 'text'):
    #             max_containers = QTableWidgetItem(nesting_settings.find('maxContainers').text)
    #             max_containers.setTextAlignment(Qt.AlignCenter)
    #             window.t2.setItem(5, 0, max_containers)

    sys.exit(app.exec_())


# Run Program
main()
