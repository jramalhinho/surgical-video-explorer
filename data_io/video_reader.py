# coding=utf-8

"""
A Class for the reading and storing of surgical video
"""

import cv2
import os


class VideoReader:
    """
    Class that holds tools for reading and sampling of videos
    """
    def __init__(self,
                 display_rate=None,
                 display_dims=None):
        # Define properties
        self.video_path = None
        self.video_format = None
        self.cpu_loaded = False
        self.frames_path = None

        # On the video
        self.frame_number = None
        self.frames_rate = None
        self.image_width = None
        self.image_height = None

        # For further display
        self.display_rate = None
        self.display_width = None
        self.display_height = None

        # In case video is stored
        self.video_data = None


    def load_video(self,
                   video_path,
                   cpu_loaded=False):
        """
        Function to load a video
        :param video_path: path of the video file
        :param video_format: format of the video file
        """

        # Check if video path exists
        if not os.path.exists(video_path):
            raise ValueError('Video file not found')
        else:
            self.video_path = video_path

        # Extract video format and check whether it is valid
        video_format = video_path[::-1][0:video_path[::-1].find('.') + 1][::-1]

        # Create list of possible formats (can be updated)
        possible_formats = [".mp4"]
        if video_format not in possible_formats:
            raise ValueError("Video format must be one of the list {}".format(possible_formats))
        else:
            self.video_format = video_format

        # Open video reading object
        video = cv2.VideoCapture(video_path)

        return 0
