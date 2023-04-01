"""
Created by: William Chang Liu, Eugene Cho, Hamin Lee
Date created: April 1, 2023
Course: CSC111H1S
Instructor: Mario Badr

-- Main file to run the Course Project: Versify --

Versify aims to utilize natural language processing and lyrical databases to generate completely new song lyrics in the
style of a given musical artist. This will be entirely based on their most commonly used vocabulary and semantic
patterns which are derived from existing songs.
"""
from versify_gui import VersifyGUI

if __name__ == "__main__":
    # creates an instance of the VersifyGUI class, commencing the program
    VersifyGUI()
