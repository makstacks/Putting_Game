from game import Game
from menu import *
from settings import *
import pygame
import os

g = Game()

# Music ----------------------------------------------------------- #
pygame.mixer.music.load("assets\\zmeyev.mp3")
pygame.mixer.music.set_volume(MUSIC_VOLUME)
pygame.mixer.music.play(-1)

while g.running:
    g.curr_menu.display_menu()
    g.game_loop()
