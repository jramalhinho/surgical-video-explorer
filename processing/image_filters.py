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
    # Bleeding will be detected by thresholding. To adapt the threshold for red channel,
    # remove specularities first
    specularity_limit = 200
    # Find pixels that are all above 200 (white light)
    _, red_spec = cv2.threshold(image[:, :, 2], specularity_limit, 255, cv2.THRESH_BINARY)
    _, green_spec = cv2.threshold(image[:, :, 1], specularity_limit, 255, cv2.THRESH_BINARY)
    _, blue_spec = cv2.threshold(image[:, :, 0], specularity_limit, 255, cv2.THRESH_BINARY)
    spec = cv2.bitwise_and(cv2.bitwise_and(red_spec, green_spec), blue_spec)
    image_without_spec = cv2.bitwise_and(image, image, mask=cv2.bitwise_not(spec))

    # Now, find all the maximum red values in pixels with low green and low blue
    _, green_thresholded = cv2.threshold(image_without_spec[:, :, 1], 10, 255, cv2.THRESH_BINARY_INV)
    _, blue_thresholded = cv2.threshold(image_without_spec[:, :, 0], 10, 255, cv2.THRESH_BINARY_INV)
    only_red = cv2.bitwise_and(green_thresholded, blue_thresholded)
    # Get a map of only red pixels
    only_red = cv2.bitwise_and(image_without_spec, image_without_spec, mask=only_red)
    # Find the maximum
    red_threshold = np.max(only_red[:, :, 2])
    # Threshold with a percentage of max value
    factor_to_max = 0.5
    _, red_thresholded = cv2.threshold(image_without_spec[:, :, 2], red_threshold * factor_to_max, 255, cv2.THRESH_BINARY)

    # Finally, create the blood map
    blood_map = cv2.bitwise_and(cv2.bitwise_and(red_thresholded, green_thresholded), blue_thresholded)

    # For visualisation, count the number of blood pixels
    # and establish a score
    blood_score = (np.sum(blood_map) / 255) / np.prod(blood_map.shape) * 100

    # Now mask the image
    visualisation_mask = (cv2.bitwise_not(blood_map) * 0.5).astype(np.uint8) + blood_map
    visualisation_mask = np.tile(np.expand_dims(visualisation_mask, axis=2), (1, 1, 3))

    # Create a new image for visualisation
    new_image = cv2.multiply(image, visualisation_mask, scale=1/255)
    new_image[:, :, 2] = new_image[:, :, 2] + (blood_map * 0.3).astype(np.uint8)

    return new_image, blood_score