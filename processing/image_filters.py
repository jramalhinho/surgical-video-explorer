# coding=utf-8

"""
A file with methods for image processing and analysis
"""


import cv2
import numpy as np


def resize_image(image,
                 factor):
    """
    Method to resize image
    :param image: input image
    :return new_image: resized image
    """
    # Scale dimensions
    new_width = int(image.shape[1] // factor)
    new_height = int(image.shape[0] // factor)
    # Resize
    new_image = cv2.resize(image, (new_width, new_height))
    return new_image

def convert_to_grayscale(image):
    """
    Simple RGB to grayscale conversion
    :param image:
    :return new_image: grayscale image
    """
    new_image = cv2.cvtColor(image, cv2.COLOR_BGR2GRAY)
    return new_image

def optical_flow(image_1,
                 image_2,
                 factor=2):

    """
    Method to estimate optical flow between two consecutive frames
    :param image_1: first image
    :param image_2: second image
    :param factor: a downsampling factor to increase efficiency
    :param colored_bool: a bool to define if the optical flow should be colored
    :return flow_image: the optical flow map
    """
    # Convert first images to gray scale
    gray_1 = convert_to_grayscale(image_1)
    gray_2 = convert_to_grayscale(image_2)

    # Resize the image for efficiency
    gray_1_sub = resize_image(gray_1, 2)
    gray_2_sub = resize_image(gray_2, 2)

    # Dense Optical Flow using values listed in the literature
    flow = cv2.calcOpticalFlowFarneback(gray_1_sub,
                                        gray_2_sub,
                                        None,
                                        0.5,
                                        3,
                                        15,
                                        3,
                                        5,
                                        1.2,
                                        0)

    # Create an output hsv map
    hsv = np.zeros_like(cv2.cvtColor(gray_1_sub, cv2.COLOR_GRAY2BGR))
    # Convert flow vectors to polar coordinates
    amplitude, angle = cv2.cartToPolar(flow[:, :, 0], flow[:, :, 1])
    norm_amplitude = cv2.normalize(amplitude, None, 0, 255, cv2.NORM_MINMAX)
    # Assemble HSV map, first angle
    hsv[:, :, 0] = np.rad2deg(angle) / 2
    # Saturation
    hsv[:, :, 1] = 255
    # Brightness
    hsv[:, :, 2] = norm_amplitude
    flow_image = cv2.cvtColor(hsv, cv2.COLOR_HSV2BGR)

    # Resize image back to original size
    flow_image = resize_image(flow_image, 1/factor)

    return flow_image

def bleeding_detector(image):
    """
    A simple method to highlight bleeding on a surgical image
    :param image: input image
    :return:
    """
    return 0