# coding=utf-8

"""
A Class for the reading and storing of surgical video
"""

import cv2
import os
import shutil

class VideoReader:
    """
    Class that holds tools for reading and sampling of videos
    """
    def __init__(self):
        # Define properties
        self.video_path = None
        self.video_format = None
        self.frames_path = None

        # On the video
        self.frame_number = None
        self.frames_rate = None
        self.image_width = None
        self.image_height = None

        # In case video is stored
        self.video_data = None


    def load_video(self,
                   video_path):
        """
        Function to load a video
        :param video_path: path of the video file
        :param video_format: format of the video file
        :param on_disk: boolean to decide if frames are extracted to disk
        :param delete_from_disk: boolean to decide if frames are deleted in the end
        """
        # Check if video path exists
        if not os.path.exists(video_path):
            raise ValueError('Video file not found')
        else:
            self.video_path = video_path

        # Check if video is valid
        if not check_valid_formats(video_path):
            raise ValueError("Video format is not valid.")

        # Open video reading object
        self.video = cv2.VideoCapture(video_path)

        # Get frame rate
        self.frame_rate = self.video.get(cv2.CAP_PROP_FPS)

        # And the image dimensions
        self.image_width = self.video.get(cv2.CAP_PROP_FRAME_WIDTH)
        self.image_height = self.video.get(cv2.CAP_PROP_FRAME_HEIGHT)

        # Save images to a path
        video_dir = os.path.abspath(os.path.join(video_path, os.pardir))
        self.frames_path = video_dir + "/frames/"
        counter = 0
        if not os.path.isdir(self.frames_path):
            # If the frames do not exist yet
            os.mkdir(self.frames_path)
            status = True
            while status:
                # Read image and
                status, frame = self.video.read()
                if status:
                    cv2.imwrite(self.frames_path + "frame_" + str(counter) + ".jpg", frame)
                    counter = counter + 1
        else:
            # Get frame number by scrolling files
            for file in os.listdir(self.frames_path):
                if file.endswith(".jpg"):
                    counter = counter + 1

        # Update frame number
        self.frame_number = counter
        # Then, close the video
        self.video.release()
        print("Video Frames extracted successfully")

        return 0


    def load_image(self,
                   frame_index):
        """
        Method to load an image
        :param frame_index: index of the frame to be loaded
        :return image: the RGB image of interest
        """
        # Check if frame is within bounds
        if frame_index < 0 or frame_index >= self.frame_number:
            raise ValueError("Frame index out of bounds")

        # Load the image from files
        image = cv2.imread(self.frames_path + "frame_" + str(frame_index) + ".jpg")

        # return the image
        return image


def check_valid_formats(input_path):
    """
    Method to check if input complies with video formats
    :param input_path: input path
    :return: a boolean
    """
    # Extract video format and check whether it is valid
    video_format = input_path[::-1][0:input_path[::-1].find('.') + 1][::-1]

    # Create list of possible formats (can be updated)
    possible_formats = [".mp4"]

    # Check if it is in the list
    check = video_format in possible_formats
    return check
