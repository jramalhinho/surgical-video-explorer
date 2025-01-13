# coding=utf-8

"""
Main widget class, where all everything is displayed
"""
from PyQt6.QtCore import Qt
from PyQt6.QtGui import QFont
from PyQt6.QtWidgets import QWidget, QPushButton, QLabel, QVBoxLayout, QFileDialog, QMessageBox
import data_io.video_reader as vidr


class MainWidget(QWidget):
    """
    Main widget
    """
    def __init__(self):
        super().__init__()
        # Define elements, first title
        self.setWindowTitle("Cholec80 Video Explorer")
        self.setFixedSize(1920, 1080)

        # Then button for loading video
        self.load_button = QPushButton("Load Video")
        self.load_button.clicked.connect(self.on_load_button_click)
        # Then label of "patient"
        self.patient_code = QLabel("Patient:")
        self.patient_code.setFont(QFont("Arial", 12))

        # Position objects
        layout = QVBoxLayout()
        self.setLayout(layout)

        layout.addWidget(self.patient_code)
        layout.addWidget(self.load_button)


        # Directory of data to display
        self.video_path = None

        # Show the widget to start
        self.show()

    def on_load_button_click(self):
        """
        Slot that prompts user to provide directory of data
        """
        # search directory
        self.video_path = QFileDialog.getOpenFileName()[0]

        # Load the data, checking if it is valid
        if not vidr.check_valid_formats(self.video_path):
            # raise warning window
            QMessageBox.information(self, "Error", "Invalid video file!")
            # return to stop
            return 0

        self.video_reader = vidr.VideoReader()
        self.video_reader.load_video(video_path=self.video_path)

        # Update patient code in the GUI
        patient_name = self.video_path.split("/")[-1]
        patient_name = patient_name.split(".")[0]
        self.patient_code.setText("Patient: " + patient_name)
        return 0
