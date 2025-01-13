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
        self.on_disk = False
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
                   on_disk=False):
        """
        Function to load a video
        :param video_path: path of the video file
        :param video_format: format of the video file
        :param on_disk: boolean to decide if frames are extracted to disk
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
        self.video = cv2.VideoCapture(video_path)

        # Get number of frames and frame rate
        self.frame_number = int(self.video.get(cv2.CAP_PROP_FRAME_COUNT))
        self.frame_rate = self.video.get(cv2.CAP_PROP_FPS)

        # Define the loading mode, whether from the video or from saved images
        self.on_disk = on_disk
        if self.on_disk:
            # Save images to a path
            video_dir = os.path.abspath(os.path.join(video_path, os.pardir))
            self.frames_path = video_dir + "/frames/"
            if not os.path.isdir(self.frames_path):
                os.mkdir(self.frames_path)

            counter = 0
            status = True
            while status:
                # Read image and
                status, frame = self.video.read()
                if status:
                    cv2.imwrite(self.frames_path + "frame_" + str(counter) + ".jpg", frame)
                    counter = counter + 1

            # Then, close the video
            self.video.release()

        # If frames are not saved, video is not closed

        return 0
