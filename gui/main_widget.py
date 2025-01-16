# coding=utf-8

"""
Main widget class, where all everything is displayed
"""
import cv2
import numpy as np
import time
import threading
from PyQt6.QtCore import Qt
from PyQt6.QtGui import QFont, QPixmap, QImage, QPainter, QPen, QColor
from PyQt6.QtWidgets import QWidget, QPushButton, QLabel, QVBoxLayout, QFileDialog, QMessageBox, QHBoxLayout, \
    QLineEdit, QSlider, QComboBox
import data_io.video_reader as vidr
import processing.image_filters as imf


class MainWidget(QWidget):
    """
    Main widget
    """
    def __init__(self):
        super().__init__()
        # Define elements, first title
        self.setWindowTitle("Cholec80 Video Explorer")

        # Create a background image to be placeholder (sizes are currently hardcoded, but can be changed)
        self.background_image = np.zeros((480, 854, 3), dtype=np.uint8)

        # a label of "patient"
        self.patient_label = QLabel("Patient ID:")
        self.patient_label.setFont(QFont("Arial", 12))

        # A label for current frame
        self.frame_label = QLabel("Current Frame")
        self.frame_label.setFont(QFont("Arial", 12))

        # A label with the total number of frames
        self.current_frame_label = QLabel("Frame 0/0")
        self.current_frame_label.setFont(QFont("Arial", 11))

        # a button for loading video
        self.load_button = QPushButton("Load Video")
        self.load_button.clicked.connect(self.on_load_button_click)

        # A label for the current frame rate
        self.navigate_label = QLabel("Go to Frame ")
        self.navigate_label.setFont(QFont("Arial", 11))

        # a video frame checker, an interactive text
        self.navigate_edit = QLineEdit()
        self.navigate_edit.setFont(QFont("Arial", 11))
        self.navigate_edit.setText("0")
        self.navigate_edit.setMaximumWidth(50)
        self.navigate_edit.setReadOnly(True)
        # Make label edit change something
        self.navigate_edit.returnPressed.connect(self.on_navigation_input)

        # A label for the current frame rate
        self.rate_label = QLabel("Playback speed")
        self.rate_label.setFont(QFont("Arial", 11))
        # Control this with a slider
        self.rate_slider = QSlider(Qt.Orientation.Horizontal)
        self.rate_slider.setMaximumWidth(150)
        self.rate_slider.setMinimum(1)
        self.rate_slider.setMaximum(5)
        self.rate_slider.setValue(1)
        self.rate_slider.setTickInterval(1)
        self.rate_slider.setTickPosition(QSlider.TickPosition.TicksBelow)
        self.rate_slider.valueChanged.connect(self.on_slider_change)

        # a display for video, initialised with background
        self.video_display = QLabel()
        displayed_qimage = convert_rgb_to_qimage(self.background_image)
        self.video_display.setPixmap(QPixmap(displayed_qimage))
        # Make a signal whenever the image is updated


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
        self.reset_button = QPushButton("Reset")
        self.reset_button.clicked.connect(self.on_reset_button_click)
        self.reset_button.setDisabled(True)

        # Second column, with resulting overlay
        self.middle_column_label = QLabel("Processed Video")
        self.middle_column_label.setFont(QFont("Arial", 11))

        # Label with analysis technique or method
        self.analysis_label = QLabel("Analysis: None")
        self.analysis_label.setFont(QFont("Arial", 11))

        # A drop down method to show possible methods
        self.analysis_combo = QComboBox()
        self.analysis_combo.addItems(["None",
                                      "Grayscale",
                                      "Movement Maps",
                                      "Bleeding Analysis",
                                      "Anatomical Maps",
                                      "Tool Identification"])
        self.analysis_combo.currentIndexChanged.connect(self.on_drop_down_change)
        # Methods to apply to images for analysis, as a string
        self.analysis_method = None

        # Label that will hold result display
        self.result_display = QLabel()
        # Initialise the result with black background as well
        displayed_qimage = convert_rgb_to_qimage(self.background_image)
        self.result_display.setPixmap(QPixmap(displayed_qimage))

        # A button to save results
        self.save_button = QPushButton("Save")
        self.save_button.setDisabled(True)

        # A button to export a report
        self.export_button = QPushButton("Export")
        self.export_button.setDisabled(True)

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
        load_row.addWidget(self.load_button)
        load_row.addWidget(self.frame_label)
        load_row.addWidget(self.current_frame_label)
        load_row.addWidget(self.navigate_label)
        load_row.addWidget(self.navigate_edit)
        load_row.addWidget(self.rate_label)
        load_row.addWidget(self.rate_slider)
        left_column.addLayout(load_row)

        # Add the video display
        left_column.addWidget(self.video_display)

        # Add the play buttons
        play_buttons_layout = QHBoxLayout()
        play_buttons_layout.addWidget(self.prev_button)
        play_buttons_layout.addWidget(self.play_button)
        play_buttons_layout.addWidget(self.next_button)
        play_buttons_layout.addWidget(self.reset_button)
        left_column.addLayout(play_buttons_layout)

        # Position the middle column
        middle_column.addWidget(self.middle_column_label)
        method_box = QHBoxLayout()
        method_box.addWidget(self.analysis_label)
        method_box.addWidget(self.analysis_combo)
        middle_column.addLayout(method_box)
        middle_column.addWidget(self.result_display)
        save_box = QHBoxLayout()
        save_box.addWidget(self.save_button)
        save_box.addWidget(self.export_button)
        middle_column.addLayout(save_box)

        # Directory of data to display
        self.video_path = None
        self.video_reader = None

        # Parameters on video display
        self.current_frame = None
        self.sampling_rate = 1
        self.display_rate = 0.25

        # Threads (a check to keep them)
        self.run_threads = True

        # Thread for video playback
        self.playing = False
        self.play_thread = threading.Thread(target=self.play_video)

        # Thread for checking prev and next button
        self.thread_prev_next = threading.Thread(target=self.check_next_and_prev_buttons)
        self.thread_prev_next.start()

        # Thread to update current frame
        self.thread_current_frame = threading.Thread(target=self.check_current_frame)
        self.thread_current_frame.start()

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

        # Change text of button
        self.load_button.setText("Loading")
        self.video_reader = vidr.VideoReader()
        self.video_reader.load_video(video_path=self.video_path)
        self.load_button.setText("Load Video")

        # Update patient code in the GUI
        patient_name = self.video_path.split("/")[-1]
        patient_name = patient_name.split(".")[0]
        self.patient_label.setText("Patient ID: " + patient_name)
        self.current_frame_label.setText("Frame 1/" + str(self.video_reader.frame_number))

        # Update video frame being shown
        self.current_frame = 0

        # Update video viewer
        self.update_image(self.current_frame)

        # Make play and next buttons togglable with qt
        self.next_button.setDisabled(False)
        self.play_button.setDisabled(False)
        self.reset_button.setDisabled(False)
        self.save_button.setDisabled(False)
        self.export_button.setDisabled(False)

        # Make squares editable
        self.navigate_edit.setReadOnly(False)

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


    def on_reset_button_click(self):
        """
        Method to retrocede one image in the video display
        """
        # Check if video thread is active
        if self.playing:
            # stop video playing
            self.on_play_button_click()

        # Update current frame, with current sampling rate
        self.current_frame = 0

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


    def on_navigation_input(self):
        """
        Function to change frame to number in navigation edit
        """
        # Current edit
        input = self.navigate_edit.text()
        if input.isdigit():
            intended_frame = int(input)
            if 0 < intended_frame < self.video_reader.frame_number:
                self.current_frame = intended_frame - 1
                # Stop video
                if self.playing:
                    self.on_play_button_click()
                # Update image
                self.update_image(self.current_frame)
            else:
                QMessageBox.information(self, "Error", "Invalid input number!")

        return 0


    def on_slider_change(self):
        """
        Method to change playback frame-rate
        """
        # Update display rate
        self.display_rate = 1 / (4 ** int(self.rate_slider.value()))
        return 0


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
            time.sleep(self.display_rate)
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
        # Update result window as well
        self.update_results_display()

        return 0


    def update_results_display(self):
        """
        Method that applies results of a pipeline on the result display
        :return:
        """
        # First, extract current image
        displayed_frame = self.video_reader.load_image(self.current_frame)
        if self.analysis_method is None:
            # No method, just convert to QImage
            displayed_qimage = convert_rgb_to_qimage(displayed_frame)
        elif self.analysis_method == "grayscale":
            # Convert to gray scale
            displayed_frame = imf.convert_to_grayscale(displayed_frame)
            displayed_frame = np.expand_dims(displayed_frame, axis=2)
            displayed_frame = np.tile(displayed_frame, (1, 1, 3))
            # Convert to QImage
            displayed_qimage = convert_rgb_to_qimage(displayed_frame)
        elif self.analysis_method == "opticalflow":
            # Update GUI
            displayed_qimage = convert_rgb_to_qimage(displayed_frame)
            # Not implemented yet, display text
            painter = QPainter(displayed_qimage)
            painter.setPen(QPen(QColor("green")))
            painter.setFont(QFont("Arial", 15))
            painter.drawText(50, 50, "Not implemented yet. Coming soon!")
            painter.end()
        elif self.analysis_method is "not implemented":
            # Update GUI
            displayed_qimage = convert_rgb_to_qimage(displayed_frame)
            # Not implemented yet, display text
            painter = QPainter(displayed_qimage)
            painter.setPen(QPen(QColor("green")))
            painter.setFont(QFont("Arial", 15))
            painter.drawText(50, 50, "Not implemented yet. Coming soon!")
            painter.end()

        self.result_display.setPixmap(QPixmap(displayed_qimage))

        return 0


    def on_drop_down_change(self):
        """
        Method to change current method of analysis
        :return:
        """
        # Check the text in the dropdown menu and change current method
        if self.analysis_combo.currentText() == "None":
            self.analysis_method = None
            self.analysis_label.setText("Analysis: None")
        elif self.analysis_combo.currentText() == "Grayscale":
            self.analysis_method = "grayscale"
            self.analysis_label.setText("Analysis: Gray scale")
        elif self.analysis_combo.currentText() == "Movement Maps":
            self.analysis_method = "opticalflow"
            self.analysis_label.setText("Analysis: Movement Maps")
        elif self.analysis_combo.currentText() == "Bleeding Analysis":
            self.analysis_method = "not implemented"
            self.analysis_label.setText("Analysis: Bleeding Analysis")
        elif self.analysis_combo.currentText() == "Anatomical Maps":
            self.analysis_method = "not implemented"
            self.analysis_label.setText("Analysis: Anatomical Maps")
        elif self.analysis_combo.currentText() == "Tool Identification":
            self.analysis_method = "not implemented"
            self.analysis_label.setText("Analysis: Tool Identification")
        return 0


    def check_next_and_prev_buttons(self):
        """
        Thread that checks if we are at end of video
        """
        while True and self.run_threads:
            if (self.video_reader is not None and
                    self.current_frame is not None):
                if self.current_frame == 0:
                    self.prev_button.setDisabled(True)
                else:
                    self.prev_button.setDisabled(False)

                if self.current_frame == self.video_reader.frame_number - 1:
                    self.next_button.setDisabled(True)
                else:
                    self.next_button.setDisabled(False)
            time.sleep(0.01)


    def check_current_frame(self):
        """
        Thread to update current frame
        """
        while True and self.run_threads:
            if self.current_frame is not None:
                # Update the text label with frame number
                self.current_frame_label.setText(str(self.current_frame + 1)
                                                 + "/" + str(self.video_reader.frame_number))
            time.sleep(0.01)


    def closeEvent(self, event):
        """
        Method for close confirmation
        """
        confirmation = QMessageBox.question(self, "Confirmation", "Are you done?",
                QMessageBox.StandardButton.Yes | QMessageBox.StandardButton.No)
        if confirmation == QMessageBox.StandardButton.Yes:
            # Finish threads
            self.run_threads = False
            if self.playing:
                print("Video is playing")
                self.on_play_button_click()
            event.accept()  # Close the app
        else:
            event.ignore()  # Don't close the app

    def finish_continuous_threads(self):
        """
        Method to end threads
        """
        self.thread_prev_next.join()
        self.thread_current_frame.join()


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