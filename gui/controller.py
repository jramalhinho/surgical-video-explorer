# coding=utf-8

"""
A Controller class, checking threads
"""


import threading
import gui.main_widget as mwi
import time as time


class ThreadManager:
    # Class that will contain multiple threads
    def __init__(self,
                 main_widget):
        # Keep main widget inside
        self.widget = main_widget
        # Create threads
        self.thread_prev_next = threading.Thread(target=self.check_next_and_prev_buttons)
        self.thread_prev_next.start()

    def check_next_and_prev_buttons(self):
        """
        Thread that checks if we are at end of video
        """
        while True:
            if (self.widget.video_reader is not None and
                    self.widget.current_frame is not None):
                if self.widget.current_frame == 0:
                    self.widget.prev_button.setDisabled(True)
                else:
                    self.widget.prev_button.setDisabled(False)

                if self.widget.current_frame == self.widget.video_reader.frame_number - 1:
                    self.widget.next_button.setDisabled(True)
                else:
                    self.widget.next_button.setDisabled(False)

    def finish_threads(self):
        """
        Place-holder to finish all these threads
        """

