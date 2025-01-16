# coding=utf-8
"""
Setup for surgical_video_explorer
"""

from setuptools import setup, find_packages


setup(
    name='surgical_video_explorer',
    version='1.0',
    url='https://github.com/jramalhinho/surgical_video_explorer',
    author='João Ramalhinho',
    author_email='jdmramalhinho@gmail.com',
    install_requires=[
            'opencv-python==4.10.0.84',
            'PyQt6==6.8.0',
            'numpy==2.2.1'
    ],
    packages=find_packages(),
    entry_points={
        'console_scripts':[
            'surgical_video_explorer=surgical_video_explorer:main',
        ]
    }
)