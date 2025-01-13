# coding=utf-8

"""
Main widget class, where all everything is displayed
"""
from PyQt6.QtWidgets import QWidget


class MainWidget(QWidget):
    """
    Main widget
    """
    def __init__(self):
        super().__init__()
        self.setWindowTitle("Cholec80 Video Explorer")


        # Show the widget to start
        self.show()