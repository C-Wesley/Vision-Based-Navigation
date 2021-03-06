"""
Vision Based Navigation Project
Augusta University
3/11/2022

File aquired from: https://github.com/Kazuhito00/cvfpscalc
File contains the CvFpsCalc class. 
This class can be used to determine the 
fps between two function calls. 

cvfpscalc.py
"""
from collections import deque
import cv2 as cv


class CvFpsCalc(object):
    def __init__(self, buffer_len=1):
        self._start_tick = cv.getTickCount()
        self._freq = 1000.0 / cv.getTickFrequency()
        self._difftimes = deque(maxlen=buffer_len)

    def get(self):
        """
        Calculates the fps between the last call and current call. 
        """
        current_tick = cv.getTickCount()
        different_time = (current_tick - self._start_tick) * self._freq
        self._start_tick = current_tick

        self._difftimes.append(different_time)

        fps = 1000.0 / (sum(self._difftimes) / len(self._difftimes))
        fps_rounded = round(fps, 2)

        return fps_rounded
