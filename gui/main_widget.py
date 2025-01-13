# coding=utf-8

"""
Main widget class, where all everything is displayed
"""
from PyQt6.QtCore import Qt
from PyQt6.QtGui import QFont, QPixmap, QImage
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

        # a button for loading video
        self.load_button = QPushButton("Load Video")
        self.load_button.clicked.connect(self.on_load_button_click)
        # a label of "patient"
        self.patient_label = QLabel("Patient:")
        self.patient_label.setFont(QFont("Arial", 12))
        # a display for video
        self.video_display = QLabel()
        # Buttons for playing and stepping
        self.next_button = QPushButton(">")
        self.next_button.clicked.connect(self.on_next_button_click)
        self.prev_button = QPushButton("<")
        self.prev_button.clicked.connect(self.on_prev_button_click)
        self.play_button = QPushButton("Play")
        self.prev_button.clicked.connext(self.on_play_button_click)


        # Position objects
        layout = QVBoxLayout()
        self.setLayout(layout)

        layout.addWidget(self.patient_label)
        layout.addWidget(self.load_button)
        layout.addWidget(self.video_display)

        # Directory of data to display
        self.video_path = None

        # Parameters on video display
        self.current_frame = None
        self.sampling_rate = 1

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
        self.patient_label.setText("Patient: " + patient_name)

        # Update video viewer
        displayed_frame = self.video_reader.load_image(0)
        displayed_qimage = convert_rgb_to_qimage(displayed_frame)
        self.video_display.setPixmap(QPixmap(displayed_qimage))

        # Update video frame being shown
        self.current_frame = 0

        return 0

    def on_next_button_click(self):
        """

        """

    def on_prev_button_click(self):
        """

        """

    def on_play_button_click(self):
        """

        """

def convert_rgb_to_qimage(rgb):
    """
    Function that converts an RGB image from OpenCV to
    a QImage
    :param rgb: input image
    :return new_image: a QImage
    """
    # Get image dimensions
    height, width, channels = rgb.shape
    # Define the image
    new_image = QImage(rgb, width, height, width * 3, QImage.Format.Format_BGR888)
    # return
    return new_image