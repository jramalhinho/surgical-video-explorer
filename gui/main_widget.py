# coding=utf-8

"""
Main widget class, where all everything is displayed
"""


from PyQt6.QtCore import Qt
from PyQt6.QtGui import QFont, QPixmap, QImage
from PyQt6.QtWidgets import QWidget, QPushButton, QLabel, QVBoxLayout, QFileDialog, QMessageBox, QComboBox, QHBoxLayout, \
    QLineEdit
import data_io.video_reader as vidr
import threading


class MainWidget(QWidget):
    """
    Main widget
    """
    def __init__(self):
        super().__init__()
        # Define elements, first title
        self.setWindowTitle("Cholec80 Video Explorer")
        # self.setFixedSize(1920, 1080)

        # a label of "patient"
        self.patient_label = QLabel("Patient ID:")
        self.patient_label.setFont(QFont("Arial", 12))

        # A label for current frame
        self.frame_label = QLabel("Current Frame")
        self.frame_label.setFont(QFont("Arial", 12))

        # A label for the current frame rate
        self.rate_label = QLabel("Frame Rate")
        self.rate_label.setFont(QFont("Arial", 11))


        # a button for loading video
        self.load_button = QPushButton("Load Video")
        self.load_button.clicked.connect(self.on_load_button_click)

        # a video frame checker, an interactive text
        self.frame_edit = QLineEdit()
        self.frame_edit.setFont(QFont("Arial", 11))
        self.frame_edit.setText("0")
        self.frame_edit.setMaximumWidth(30)
        self.frame_edit.setReadOnly(True)

        # A label with the total number of frames
        self.total_label = QLabel("out of 0")
        self.total_label.setFont(QFont("Arial", 11))

        # a video frame checker, an interactive text
        self.rate_edit = QLineEdit()
        self.rate_edit.setFont(QFont("Arial", 11))
        self.rate_edit.setText("1")
        self.rate_edit.setMaximumWidth(30)
        self.rate_edit.setReadOnly(True)

        # a display for video
        self.video_display = QLabel()
        # Buttons for playing and stepping
        self.next_button = QPushButton(">")
        self.next_button.clicked.connect(self.on_next_button_click)
        self.next_button.setDisabled(True)
        self.prev_button = QPushButton("<")
        self.prev_button.clicked.connect(self.on_prev_button_click)
        self.prev_button.setDisabled(True)
        self.play_button = QPushButton("Play")
        self.play_button.clicked.connect(self.on_play_button_click)
        self.play_button.setDisabled(True)
        # Make a button with drop menu
        self.sampling_button = QComboBox()

        # Position objects
        main_layout = QHBoxLayout()
        self.setLayout(main_layout)
        # Set three columns as sublayouts
        left_column = QVBoxLayout()
        middle_column = QVBoxLayout()
        right_column = QVBoxLayout()
        # Add the three columns
        main_layout.addLayout(left_column)
        main_layout.addLayout(middle_column)
        main_layout.addLayout(right_column)

        # Add objects to the left column, first a row
        patient_row = QHBoxLayout()
        patient_row.addWidget(self.patient_label)

        left_column.addLayout(patient_row)

        # Add load and frame checker in the next row
        load_row = QHBoxLayout()
        frame_box = QHBoxLayout()
        frame_box.addWidget(self.frame_edit)
        frame_box.addWidget(self.total_label)
        load_row.addWidget(self.load_button)
        load_row.addWidget(self.frame_label)
        load_row.addLayout(frame_box)
        load_row.addWidget(self.rate_label)
        load_row.addWidget(self.rate_edit)
        left_column.addLayout(load_row)

        # Add the video display
        left_column.addWidget(self.video_display)

        # Add the play buttons
        play_buttons_layout = QHBoxLayout()
        play_buttons_layout.addWidget(self.prev_button)
        play_buttons_layout.addWidget(self.play_button)
        play_buttons_layout.addWidget(self.next_button)
        left_column.addLayout(play_buttons_layout)






        # Directory of data to display
        self.video_path = None
        self.video_reader = None

        # Parameters on video display
        self.current_frame = None
        self.sampling_rate = 1

        # Threads
        self.playing = False
        self.play_thread = threading.Thread(target=self.play_video)

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
        self.patient_label.setText("Patient ID: " + patient_name)

        # Update video viewer
        displayed_frame = self.video_reader.load_image(0)
        displayed_qimage = convert_rgb_to_qimage(displayed_frame)
        self.video_display.setPixmap(QPixmap(displayed_qimage))

        # Update video frame being shown
        self.current_frame = 0

        # Make play and next buttons togglable with qt
        self.next_button.setDisabled(False)
        self.play_button.setDisabled(False)

        # Make edits possible
        self.frame_edit.setReadOnly(False)
        self.rate_edit.setReadOnly(False)

        return 0

    def on_next_button_click(self):
        """
        Method to advance one image in the video display
        """
        # Check if video thread is active
        if self.playing:
            # stop video playing
            self.on_play_button_click()

        # Update current frame, with current sampling rate
        self.current_frame = min(self.current_frame + self.sampling_rate,
                                 self.video_reader.frame_number - 1)

        # Update with the function
        self.update_image(self.current_frame)

        return 0

    def on_prev_button_click(self):
        """
        Method to retrocede one image in the video display
        """
        # Check if video thread is active
        if self.playing:
            # stop video playing
            self.on_play_button_click()

        # Update current frame, with current sampling rate
        self.current_frame = max(self.current_frame - self.sampling_rate, 0)

        # Update with the function
        self.update_image(self.current_frame)

        return 0

    def on_play_button_click(self):
        """
        Button to play and stop video
        """
        # Video is played starting from the current point with a thread
        if not self.playing:
            self.playing = True
            self.play_thread.start()
            self.play_button.setText("Playing")
        else:
            self.playing = False
            self.play_thread.join()
            self.play_button.setText("Play")
            # Restart the thread
            self.play_thread = threading.Thread(target=self.play_video)


    def play_video(self):
        """
        Thread to play video
        """
        # Loop to update video
        while self.current_frame <= self.video_reader.frame_number:
            self.current_frame = min(self.current_frame + self.sampling_rate,
                                     self.video_reader.frame_number - 1)
            # Update
            self.update_image(self.current_frame)
            # time.sleep(0.01)
            if not self.playing:
                break

        return 0


    def update_image(self,
                     frame):
        """
        Method to change the display on the current video overlay
        :param current_frame: the frame to display
        """
        # Load the image and display
        displayed_frame = self.video_reader.load_image(frame)
        # Convert to QImage
        displayed_qimage = convert_rgb_to_qimage(displayed_frame)
        self.video_display.setPixmap(QPixmap(displayed_qimage))

        return 0



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