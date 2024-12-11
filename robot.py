import pygame
import random



class Robot:
    def __init__(self, color, x, y):
        self.color = color
        self.x = x
        self.y = y
        self.attempts = 0
        self.target = None
        self.reached_target = False
       
    def move(self, x, y):
        self.x = x
        self.y = y

    def increment_attempts(self):
        self.attempts += 1