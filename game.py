import pygame
import time
import cv2
import os
import pickle
import numpy as np
from settings import *
from mat_detect import *
from tracker import *


BACKGROUND = pygame.image.load(os.path.join("assets", "8bitbeachgolf.png"))
mainClock = pygame.time.Clock()

class Menu():
    def __init__(self, game):
        self.titfs = 80
        self.subfs = 30
        self.gm = "F"
        self.game = game
        self.mid_w, self.mid_h = self.game.DISPLAY_W / 2, self.game.DISPLAY_H / 2
        self.run_display = True
        self.cursor_rect = pygame.Rect(0, 0, 20, 20)
        self.offset = - 220

    def draw_cursor(self):
        # self.game.draw_text_black('*', 70, self.cursor_rect.x, self.cursor_rect.y)
        # self.game.draw_text('*', 60, self.cursor_rect.x, self.cursor_rect.y)
        self.game.draw_text_outline('*', 60, self.cursor_rect.x, self.cursor_rect.y)

    def blit_screen(self):
        self.game.window.blit(self.game.display, (0, 0))
        self.game.display.blit(BACKGROUND, (0, 0))
        pygame.display.update()
        self.game.reset_keys()

class MainMenu(Menu):
    def __init__(self, game):
        Menu.__init__(self, game)
        self.inputs = [1, 1, 1, 0, 0]
        self.state = "Start"
        self.startx, self.starty = self.mid_w, self.mid_h
        self.free_playx, self.free_playy = self.mid_w, self.mid_h + 70
        self.optionsx, self.optionsy = self.mid_w, self.mid_h + 140
        self.creditsx, self.creditsy = self.mid_w, self.mid_h + 210
        self.cursor_rect.midtop = (self.startx + self.offset, self.starty)

    def display_menu(self):
        self.run_display = True
        while self.run_display:
            self.game.check_events()
            self.check_input()
            self.game.display.fill(self.game.BLACK)
            self.game.display.blit(BACKGROUND, (0, 0))
            self.game.draw_text_outline('Main Menu', self.titfs + 5, SCREEN_WIDTH / 2, round(1.5 * self.titfs))
            self.game.draw_text_outline("Start Game", self.subfs, self.startx, self.starty)
            self.game.draw_text_outline("Free Play", self.subfs, self.free_playx, self.free_playy)
            self.game.draw_text_outline("Options", self.subfs, self.optionsx, self.optionsy)
            self.game.draw_text_outline("Credits", self.subfs, self.creditsx, self.creditsy)
            self.draw_cursor()
            self.blit_screen()

    def move_cursor(self):
        if self.game.DOWN_KEY:
            if self.state == 'Start':
                self.cursor_rect.midtop = (self.free_playx + self.offset, self.free_playy)
                self.state = 'Free Play'
            elif self.state == 'Free Play':
                self.cursor_rect.midtop = (self.optionsx + self.offset, self.optionsy)
                self.state = 'Options'
            elif self.state == 'Options':
                self.cursor_rect.midtop = (self.creditsx + self.offset, self.creditsy)
                self.state = 'Credits'
            elif self.state == 'Credits':
                self.cursor_rect.midtop = (self.startx + self.offset, self.starty)
                self.state = 'Start'
        elif self.game.UP_KEY:
            if self.state == 'Start':
                self.cursor_rect.midtop = (self.creditsx + self.offset, self.creditsy)
                self.state = 'Credits'
            elif self.state == 'Free Play':
                self.cursor_rect.midtop = (self.startx + self.offset, self.starty)
                self.state = 'Start'
            elif self.state == 'Options':
                self.cursor_rect.midtop = (self.free_playx + self.offset, self.free_playy)
                self.state = 'Free Play'
            elif self.state == 'Credits':
                self.cursor_rect.midtop = (self.optionsx + self.offset, self.optionsy)
                self.state = 'Options'

    def check_input(self):
        self.move_cursor()
        if self.game.START_KEY:
            if self.state == 'Start':
                self.game.curr_menu = self.game.game_select
            elif self.state == 'Free Play':
                with open("game_inputs.txt", "w") as f:
                    for i in self.inputs:
                        f.write(str(i) +"\n")
                self.game.playing = True
                self.run_display = False
            elif self.state == 'Options':
                self.game.curr_menu = self.game.options
            elif self.state == 'Credits':
                self.game.curr_menu = self.game.credits
            self.run_display = False

class GameSelect(Menu):
    def __init__(self, game):
        Menu.__init__(self, game)
        # Setting up the default inputs (for 0th element different ints represent the game modes)
        self.inputs = [2, 2, 2, 3, 3]
        self.state = 'Points Game'
        self.teamvstring = "1 v 1"
        self.gmmdx, self.gmmdy = self.mid_w, self.mid_h
        self.numpx, self.numpy = self.mid_w, self.mid_h + 70
        self.teamsx, self.teamsy = self.mid_w, self.mid_h + 140
        self.roundsx, self.roundsy = self.mid_w, self.mid_h + 210
        self.cursor_rect.midtop = (self.gmmdx + self.offset, self.gmmdy)

    def display_menu(self):
        self.run_display = True
        while self.run_display:
            # Get user inputs
            self.game.check_events()
            self.inputs = self.check_input()
            # Calculate the string for teams based off number of players and number of teams
            # If number of players is 2...
            if self.inputs[1] == 2:
                if self.inputs[2] == 1:
                    teams = [[1, 2]]
                elif self.inputs[2] == 2:
                    teams = [[1], [2]]
            elif self.inputs[1] == 3:
                if self.inputs[2] == 1:
                    teams = [[1, 2, 3]]
                elif self.inputs[2] == 2:
                    teams = [[1], [2, 3]]
                elif self.inputs[2] == 3:
                    teams = [[1], [2], [3]]
            elif self.inputs[1] == 4:
                if self.inputs[2] == 1:
                    teams = [[1, 2, 3, 4]]
                elif self.inputs[2] == 2:
                    teams = [[1, 2], [3, 4]]
                elif self.inputs[2] == 3:
                    teams = [[1], [2], [3, 4]]
                elif self.inputs[2] == 4:
                    teams = [[1], [2], [3], [4]]
            elif self.inputs[1] == 5:
                if self.inputs[2] == 1:
                    teams = [[1, 2, 3, 4, 5]]
                elif self.inputs[2] == 2:
                    teams = [[1, 2], [3, 4, 5]]
                elif self.inputs[2] == 3:
                    teams = [[1], [2, 3], [4, 5]]
                elif self.inputs[2] == 4:
                    teams = [[1], [2], [3], [4, 5]]
                elif self.inputs[2] == 5:
                    teams = [[1], [2], [3], [4], [5]]
            elif self.inputs[1] == 6:
                if self.inputs[2] == 1:
                    teams = [[1, 2, 3, 4, 5, 6]]
                elif self.inputs[2] == 2:
                    teams = [[1, 2, 3], [4, 5, 6]]
                elif self.inputs[2] == 3:
                    teams = [[1, 2], [3, 4], [5, 6]]
                elif self.inputs[2] == 4:
                    teams = [[1], [2], [3, 4], [5, 6]]
                elif self.inputs[2] == 5:
                    teams = [[1], [2], [3], [4], [5, 6]]
                elif self.inputs[2] == 6:
                    teams = [[1], [2], [3], [4], [5], [6]]
            self.teamvstring = ""
            for team in range(self.inputs[2]):
                self.teamvstring = self.teamvstring + str(len(teams[team])) + " v "
            self.teamvstring = self.teamvstring[:-3]
            if self.inputs[2] == 1:
                self.teamvstring = "1 Team"
            if self.inputs[2] > self.inputs[1]:
                self.inputs[2] = self.inputs[1]
            if self.inputs[0] == 1:
                self.inputs[1] = 1
            #gm_inputs = ["P", 2, 2, 3, 3]
            self.game.display.fill((0, 0, 0))
            self.game.display.blit(BACKGROUND, (0, 0))
            self.game.draw_text_outline('Game Selection', self.titfs, self.game.DISPLAY_W / 2, round(1.5 * self.titfs))
            if self.inputs[0] == 2:
                self.game.draw_text_outline("Points Game", self.subfs, self.gmmdx, self.gmmdy)
            elif self.inputs[0] == 3:
                self.game.draw_text_outline("Timer", self.subfs, self.gmmdx, self.gmmdy)
            elif self.inputs[0] == 1:
                self.game.draw_text_outline("Free Play", self.subfs, self.gmmdx, self.gmmdy)
            if self.inputs[1] > 1:
                self.game.draw_text_outline(str(self.inputs[1]) + " Players", self.subfs, self.numpx, self.numpy)
            else:
                self.game.draw_text_outline(str(self.inputs[1]) + " Player", self.subfs, self.numpx, self.numpy)
            if self.inputs[1] != 1:
                self.game.draw_text_outline(self.teamvstring, self.subfs, self.teamsx, self.teamsy)
            #self.game.draw_text("3 Rounds", 15, self.roundsx, self.roundsy)
            self.draw_cursor()
            self.blit_screen()

    def check_input(self):
        if self.game.BACK_KEY:
            self.game.curr_menu = self.game.main_menu
            self.run_display = False
        elif self.game.UP_KEY:
            if self.state == 'Points Game':
                self.state = '1 v 1'
                self.cursor_rect.midtop = (self.teamsx + self.offset, self.teamsy)
            elif self.state == '2 Players':
                self.state = 'Points Game'
                self.cursor_rect.midtop = (self.gmmdx + self.offset, self.gmmdy)
            elif self.state == '1 v 1':
                self.state = '2 Players'
                self.cursor_rect.midtop = (self.numpx + self.offset, self.numpy)
        elif self.game.DOWN_KEY:
            if self.state == 'Points Game':
                self.state = '2 Players'
                self.cursor_rect.midtop = (self.numpx + self.offset, self.numpy)
            elif self.state == '2 Players':
                self.state = '1 v 1'
                self.cursor_rect.midtop = (self.teamsx + self.offset, self.teamsy)
            elif self.state == '1 v 1':
                self.state = 'Points Game'
                self.cursor_rect.midtop = (self.gmmdx + self.offset, self.gmmdy)
        elif self.game.LEFT_KEY:
            if self.state == "Points Game":
                if self.inputs[0] == 1:
                    self.inputs[0] = 3
                    self.inputs[1] = 2
                elif self.inputs[0] == 2:
                    self.inputs[0] = 1
                elif self.inputs[0] == 3:
                    self.inputs[0] = 2
            elif self.state == "2 Players" and self.inputs[0] != 1:
                if self.inputs[1] == 1:
                    self.inputs[1] = 6
                elif self.inputs[1] == 2:
                    self.inputs[1] = 1
                elif self.inputs[1] == 3:
                    self.inputs[1] = 2
                elif self.inputs[1] == 4:
                    self.inputs[1] = 3
                elif self.inputs[1] == 5:
                    self.inputs[1] = 4
                elif self.inputs[1] == 6:
                    self.inputs[1] = 5
                # want to initially set display as 1 v 1 v 1... for however many players there are
                self.inputs[2] = self.inputs[1]
            elif self.state == "1 v 1" and self.inputs[0] != 1:
                # If 2 players selected
                if self.inputs[1] == 2:
                    # If number of teams is 2 (1 v 1 in this case)
                    if self.inputs[2] == 2:
                        self.inputs[2] = 1
                    elif self.inputs[2] == 1:
                        self.inputs[2] = 2
                # If 3 players selected
                elif self.inputs[1] == 3:
                    if self.inputs[2] == 1:
                        self.inputs[2] = 3
                    elif self.inputs[2] == 2:
                        self.inputs[2] = 1
                    elif self.inputs[2] == 3:
                        self.inputs[2] = 2
                # If 4 players selected
                elif self.inputs[1] == 4:
                    if self.inputs[2] == 1:
                        self.inputs[2] = 4
                    elif self.inputs[2] == 2:
                        self.inputs[2] = 1
                    elif self.inputs[2] == 3:
                        self.inputs[2] = 2
                    elif self.inputs[2] == 4:
                        self.inputs[2] = 3
                # If 5 players selected
                elif self.inputs[1] == 5:
                    if self.inputs[2] == 1:
                        self.inputs[2] = 5
                    elif self.inputs[2] == 2:
                        self.inputs[2] = 1
                    elif self.inputs[2] == 3:
                        self.inputs[2] = 2
                    elif self.inputs[2] == 4:
                        self.inputs[2] = 3
                    elif self.inputs[2] == 5:
                        self.inputs[2] = 4
                # If 6 players selected
                elif self.inputs[1] == 6:
                    if self.inputs[2] == 1:
                        self.inputs[2] = 6
                    elif self.inputs[2] == 2:
                        self.inputs[2] = 1
                    elif self.inputs[2] == 3:
                        self.inputs[2] = 2
                    elif self.inputs[2] == 4:
                        self.inputs[2] = 3
                    elif self.inputs[2] == 5:
                        self.inputs[2] = 4
                    elif self.inputs[2] == 6:
                        self.inputs[2] = 5
        elif self.game.RIGHT_KEY:
            if self.state == "Points Game":
                if self.inputs[0] == 1:
                    self.inputs[0] = 2
                    self.inputs[1] = 2
                elif self.inputs[0] == 2:
                    self.inputs[0] = 3
                elif self.inputs[0] == 3:
                    self.inputs[0] = 1
            elif self.state == "2 Players" and self.inputs[0] != 1:
                if self.inputs[1] == 1:
                    self.inputs[1] = 2
                elif self.inputs[1] == 2:
                    self.inputs[1] = 3
                elif self.inputs[1] == 3:
                    self.inputs[1] = 4
                elif self.inputs[1] == 4:
                    self.inputs[1] = 5
                elif self.inputs[1] == 5:
                    self.inputs[1] = 6
                elif self.inputs[1] == 6:
                    self.inputs[1] = 1
                self.inputs[2] = self.inputs[1]
            elif self.state == "1 v 1" and self.inputs[0] != 1:
                # If 2 players selected
                if self.inputs[1] == 2:
                    # If number of teams is 2 (1 v 1 in this case)
                    if self.inputs[2] == 2:
                        self.inputs[2] = 1
                    elif self.inputs[2] == 1:
                        self.inputs[2] = 2
                # If 3 players selected
                elif self.inputs[1] == 3:
                    if self.inputs[2] == 1:
                        self.inputs[2] = 2
                    elif self.inputs[2] == 2:
                        self.inputs[2] = 3
                    elif self.inputs[2] == 3:
                        self.inputs[2] = 1
                # If 4 players selected
                elif self.inputs[1] == 4:
                    if self.inputs[2] == 1:
                        self.inputs[2] = 2
                    elif self.inputs[2] == 2:
                        self.inputs[2] = 3
                    elif self.inputs[2] == 3:
                        self.inputs[2] = 4
                    elif self.inputs[2] == 4:
                        self.inputs[2] = 1
                # If 5 players selected
                elif self.inputs[1] == 5:
                    if self.inputs[2] == 1:
                        self.inputs[2] = 2
                    elif self.inputs[2] == 2:
                        self.inputs[2] = 3
                    elif self.inputs[2] == 3:
                        self.inputs[2] = 4
                    elif self.inputs[2] == 4:
                        self.inputs[2] = 5
                    elif self.inputs[2] == 5:
                        self.inputs[2] = 1
                # If 6 players selected
                elif self.inputs[1] == 6:
                    if self.inputs[2] == 1:
                        self.inputs[2] = 2
                    elif self.inputs[2] == 2:
                        self.inputs[2] = 3
                    elif self.inputs[2] == 3:
                        self.inputs[2] = 4
                    elif self.inputs[2] == 4:
                        self.inputs[2] = 5
                    elif self.inputs[2] == 5:
                        self.inputs[2] = 6
                    elif self.inputs[2] == 6:
                        self.inputs[2] = 1

        elif self.game.START_KEY:
            with open("game_inputs.txt", "w") as f:
                for i in self.inputs:
                    f.write(str(i) +"\n")
            self.game.playing = True
            self.run_display = False
        return self.inputs


class OptionsMenu(Menu):
    def __init__(self, game):
        Menu.__init__(self, game)
        self.state = 'Volume'
        self.volx, self.voly = self.mid_w, self.mid_h
        self.controlsx, self.controlsy = self.mid_w, self.mid_h + 70
        self.cursor_rect.midtop = (self.volx + self.offset, self.voly)

    def display_menu(self):
        self.run_display = True
        while self.run_display:
            self.game.check_events()
            self.check_input()
            self.game.display.fill((0, 0, 0))
            self.game.display.blit(BACKGROUND, (0, 0))
            self.game.draw_text_outline('Options', self.titfs, self.game.DISPLAY_W / 2, round(1.5 * self.titfs))
            self.game.draw_text_outline("Volume", self.subfs, self.volx, self.voly)
            self.game.draw_text_outline("Controls", self.subfs, self.controlsx, self.controlsy)
            self.draw_cursor()
            self.blit_screen()

    def check_input(self):
        if self.game.BACK_KEY:
            self.game.curr_menu = self.game.main_menu
            self.run_display = False
        elif self.game.UP_KEY or self.game.DOWN_KEY:
            if self.state == 'Volume':
                self.state = 'Controls'
                self.cursor_rect.midtop = (self.controlsx + self.offset, self.controlsy)
            elif self.state == 'Controls':
                self.state = 'Volume'
                self.cursor_rect.midtop = (self.volx + self.offset, self.voly)
        elif self.game.START_KEY:
            # TO-DO: Create a Volume Menu and a Controls Menu
            pass

class CreditsMenu(Menu):
    def __init__(self, game):
        Menu.__init__(self, game)

    def display_menu(self):
        self.run_display = True
        while self.run_display:
            self.game.check_events()
            if self.game.START_KEY or self.game.BACK_KEY:
                self.game.curr_menu = self.game.main_menu
                self.run_display = False
            self.game.display.fill(self.game.BLACK)
            self.game.display.blit(BACKGROUND, (0, 0))
            self.game.draw_text('Credits', self.titfs, self.game.DISPLAY_W / 2, round(1.5 * self.titfs))
            self.game.draw_text_with_rect('Made by me', self.subfs, SCREEN_WIDTH / 2, SCREEN_HEIGHT /2, self.game.GREEN)
            self.blit_screen()

class Game():
    def __init__(self):
        pygame.init()
        self.running, self.playing = True, False
        self.UP_KEY, self.DOWN_KEY, self.LEFT_KEY, self.RIGHT_KEY, self.START_KEY, self.BACK_KEY =\
            False, False, False, False, False, False
        self.DISPLAY_W, self.DISPLAY_H = 1280, 720
        self.display = pygame.Surface((self.DISPLAY_W,self.DISPLAY_H))
        self.window = pygame.display.set_mode(((self.DISPLAY_W,self.DISPLAY_H)))
        self.font_name = '8-BIT WONDER.TTF'
        self.font_name2 = 'Pixeboy.TTF'
        #self.font_name = pygame.font.get_default_font()
        self.BLACK, self.WHITE, self.GREEN, self.RED, self.PURPLE, self.ORANGE, self.BLUE, self.CORAL, self.GRAY =\
            (0, 0, 0), (255, 255, 255), (0, 154, 23), (255, 0, 0), (147, 112, 219), (255, 140, 0), (100, 149, 237),\
            (255, 127, 80), (169, 169, 169)
        self.team_colours = [self.GREEN, self.CORAL, self.BLUE, self.GRAY, self.ORANGE, self.PURPLE]
        self.main_menu = MainMenu(self)
        self.game_select = GameSelect(self)
        self.options = OptionsMenu(self)
        self.credits = CreditsMenu(self)
        self.curr_menu = self.main_menu
        self.sounds = {}
        self.sounds["hole1"] = pygame.mixer.Sound("assets\\reward1.mp3")
        self.sounds["hole1"].set_volume(SOUNDS_VOLUME)
        self.sounds["hole2"] = pygame.mixer.Sound("assets\\reward2.mp3")
        self.sounds["hole2"].set_volume(SOUNDS_VOLUME)
        self.sounds["miss"] = pygame.mixer.Sound("assets\\miss.mp3")
        self.sounds["miss"].set_volume(SOUNDS_VOLUME)
        self.sounds["dontmiss"] = pygame.mixer.Sound("assets\\dontmiss.mp3")
        self.sounds["dontmiss"].set_volume(SOUNDS_VOLUME)
        self.sounds["sadsong"] = pygame.mixer.Sound("assets\\sad_music.mp3")
        self.sounds["sadsong"].set_volume(SOUNDS_VOLUME)
        self.matvals = []

    def game_loop(self):

        gm_inputs = []
        # Reading in inputs for the game
        with open("game_inputs.txt", "r") as f:
            for line in f:
                gm_inputs.append(int(line.strip()))

        gmode_int = gm_inputs[0]
        num_players = gm_inputs[1]
        team_no = gm_inputs[2]
        rounds = gm_inputs[3]
        shotspround = gm_inputs[4]
        if gmode_int == 1:
            game_mode = "F"
        elif gmode_int == 2:
            game_mode = "P"
        elif gmode_int == 3:
            game_mode = "T"

        while self.playing:
            # Load Camera
            self.cap = cv2.VideoCapture(0)

            # Wait for camera to warm up
            time.sleep(2)
            self.check_events()
            if self.BACK_KEY:
                self.playing = False
            #self.display.fill(self.BLACK)
            if not self.matvals:
                self.draw_text("Calibrating", 40, self.DISPLAY_W/2, 100)
                self.draw_text("Press enter when ready", 20, self.DISPLAY_W/2, 300)
                self.window.blit(self.display, (0,0))
                pygame.display.update()
                self.reset_keys()
                self.matvals = detect_mat(self.cap)

            #self.window.blit(self.display, (0,0))
            pygame.display.update()
            self.reset_keys()

            p_strings = ["P1", "P2", "P3", "P4", "P5", "P6"]
            t_strings = ["Team 1", "Team 2", "Team 3", "Team 4", "Team 5", "Team 6"]
            cv2.destroyAllWindows()
            t_count = 30
            players = [] * num_players
            # define points amount for points game
            s_pts = 1.5
            b_pts = 1
            # define points amount for points game

            if game_mode == "F":
                game_string = "Free Play"
                shotspround = 5
            elif game_mode == "P":
                game_string = "Points Game"
            elif game_mode == "T":
                game_string = "Timer"

            for n in range(num_players):
                players.append(n + 1)

            if num_players == 1:
                teams = [[1]]
                team_no = 1
            elif num_players != 1:
                # team_no = int(input("Select how many teams (e.g. 4p, 2 teams = 2v2\n> "))
                teams = [[] for i in range(team_no)]
                if num_players == 2:
                    if team_no == 1:
                        teams = [[1, 2]]
                    elif team_no == 2:
                        teams = [[1], [2]]
                elif num_players == 3:
                    if team_no == 1:
                        teams = [[1, 2, 3]]
                    elif team_no == 2:
                        teams = [[1], [2, 3]]
                    elif team_no == 3:
                        teams = [[1], [2], [3]]
                elif num_players == 4:
                    if team_no == 1:
                        teams = [[1, 2, 3, 4]]
                    elif team_no == 2:
                        teams = [[1, 2], [3, 4]]
                    elif team_no == 3:
                        teams = [[1], [2], [3, 4]]
                    elif team_no == 4:
                        teams = [[1], [2], [3], [4]]
                elif num_players == 5:
                    if team_no == 1:
                        teams = [[1, 2, 3, 4, 5]]
                    elif team_no == 2:
                        teams = [[1, 2], [3, 4, 5]]
                    elif team_no == 3:
                        teams = [[1], [2, 3], [4, 5]]
                    elif team_no == 4:
                        teams = [[1], [2], [3], [4, 5]]
                    elif team_no == 5:
                        teams = [[1], [2], [3], [4], [5]]
                elif num_players == 6:
                    if team_no == 1:
                        teams = [[1, 2, 3, 4, 5, 6]]
                    elif team_no == 2:
                        teams = [[1, 2, 3], [4, 5, 6]]
                    elif team_no == 3:
                        teams = [[1, 2], [3, 4], [5, 6]]
                    elif team_no == 4:
                        teams = [[1], [2], [3, 4], [5, 6]]
                    elif team_no == 5:
                        teams = [[1], [2], [3], [4], [5, 6]]
                    elif team_no == 6:
                        teams = [[1], [2], [3], [4], [5], [6]]
            team_string = ""
            for team in range(team_no):
                team_string = team_string + str(len(teams[team])) + " v "
            team_string = team_string[:-3]

            if team_no == num_players:
                team_bool = False
            else:
                team_bool = True

            # Create tracker object
            tracker = EuclideanDistTracker()

            # Object detection from Stable camera
            object_detector = cv2.createBackgroundSubtractorMOG2(history=100, varThreshold=25)

            shot_count = 0
            hole1_count = 0
            hole2_count = 0
            missed_count = 0
            object_shot = []
            object_hole1 = []
            object_hole2 = []
            object_holes = []
            object_missed = []
            shot_pcnt = 0
            shot_record = []
            p_ind = 1
            p_shots = 0
            cur_rnd = 1
            t_ind = 1
            # points per shot
            pps = 0
            streak_count = 0
            max_streak_count = 0
            H1streak_count = 0
            H2streak_count = 0
            time_count = 0
            init_time = 0
            timers_done = 0

            # array to store how many rounds a player has completed
            p_rnd_comp = [0] * num_players
            stats_a = [[0 for h in range(9)] for i in range(num_players)]
            cyo = [[] for i in range(1000)]
            cxo = [[] for i in range(1000)]
            cymax = [0 for i in range(1000)]
            cxmax = [0 for i in range(1000)]
            p_pts = [[0] for i in range(num_players)]
            sum_p_pts = [0 for i in range(num_players)]
            pps_a = [[0] for i in range(num_players)]
            streak_count_s = [[0] for i in range(num_players)]
            streak_count_b = [[0] for i in range(num_players)]
            streak_count_a = [[0] for i in range(num_players)]
            missed_strk_cnt_a = [[] for i in range(num_players)]
            max_streak_a = [[0] for i in range(num_players)]
            H_count_a = [[] for i in range(num_players)]
            H1_count_a = [[] for i in range(num_players)]
            H1_rndcount_a = [0 for i in range(num_players)]
            H2_count_a = [[] for i in range(num_players)]
            H2_rndcount_a = [0 for i in range(num_players)]
            H_rndcount_a = [0 for i in range(num_players)]
            t_rndcount_a = [0 for i in range(num_players)]
            missed_count_a = [[] for i in range(num_players)]
            missed_rndcount_a = [0 for i in range(num_players)]
            shot_count_a = [[] for i in range(num_players)]
            shot_pcnt_a = [[0] for i in range(num_players)]
            t_pts = [[] for i in range(team_no)]
            tot_scores = [0 for j in range(team_no)]
            p_colour = [0 for i in range(num_players)]
            missed_points = []
            shot_bool = False
            t_started = False
            t_ended = False
            # read in streak highscore
            streakHS = []
            with open("streakHS.txt", "r") as f:
                for line in f:
                    streakHS.append(int(line.strip()))
            # self.matvals = [minx, maxx, miny, maxy, minxmin, maxxmin, n3ay, H1_cx, H1_cy, H1_ax_l, r1, h1, H2_cx, H2_cy, H2_ax_l, r2, h2]
            minx = self.matvals[0]
            maxx = self.matvals[1]
            miny = self.matvals[2]
            maxy = self.matvals[3]
            minxmin = self.matvals[4]
            maxxmin = self.matvals[5]
            n3ay = self.matvals[6]
            H1_cx = self.matvals[7]
            H1_cy = self.matvals[8]
            H1_ax_l = self.matvals[9]
            r1 = self.matvals[10]
            h1 = self.matvals[11]
            H2_cx = self.matvals[12]
            H2_cy = self.matvals[13]
            H2_ax_l = self.matvals[14]
            r2 = self.matvals[15]
            h2 = self.matvals[16]

            # defining left/right/up/down points on holes
            H1_xl = H1_cx - r1
            H1_xr = H1_cx + r1
            H1_yu = H1_cy - h1
            H1_yd = H1_cy + h1
            H2_xl = H2_cx - r1
            H2_xr = H2_cx + r1
            H2_yu = H2_cy - h2
            H2_yd = H2_cy + h2

            # Ratio of width, drawn mat to real mat
            w_mat = maxx - minx

            # gaps between shot zones
            szy_adj = 150
            szy_inter = 50
            # nodes coordinates
            n1x = minxmin
            n1y = miny
            n2x = maxxmin
            n2y = n1y
            n3x = minx
            n3y = n3ay
            n4x = maxx
            n4y = maxy
            n5x = minx
            n5y = n1y + szy_adj
            n6x = maxx
            n6y = n5y
            n7x = n5y
            n7y = n5y
            n8x = n5y
            n8y = n5y

            node1 = (n1x, n1y)
            node2 = (n2x, n2y)
            node3 = (n3x, n3y)
            node4 = (n4x, n4y)
            node5 = (n5x, n5y)
            node6 = (n6x, n6y)

            # defining shot zones
            sz3n1y = n5y + szy_inter
            sz3n1 = (n5x, sz3n1y)
            sz3n2 = (n6x, sz3n1y)

            angle = 0
            startAngle = 0
            endAngle = 360

            sz1list = []
            sz2list = []
            sz3list = []

            # drawing
            STATS_SHOWN = 7
            TITLE_Y_DIST = 100
            UNDER_Y_DIST = 250
            STAT_HEAD_Y_DIST = 50
            STAT_HEAD_Y_START = round(TITLE_Y_DIST + STAT_HEAD_Y_DIST / 2)
            SCORES_Y_DIST = SCREEN_HEIGHT - TITLE_Y_DIST - UNDER_Y_DIST - STAT_HEAD_Y_DIST
            SCORECARD_X_INDENT = 50
            DIST_X_SCORE = SCREEN_WIDTH - SCORECARD_X_INDENT * 2
            ST_DIST = round(DIST_X_SCORE / STATS_SHOWN)
            P_Y_SPLIT = round(SCORES_Y_DIST / num_players)
            P_Y_DIST = round(P_Y_SPLIT * 2 / 3)
            P_Y_GAP = round((SCORES_Y_DIST - num_players * P_Y_DIST) / (num_players + 1))
            W_MATDR = 200
            L_MATDR = W_MATDR * 3
            MATDR_SX = 50
            MATDR_SY = round((SCREEN_HEIGHT - UNDER_Y_DIST) + ((UNDER_Y_DIST - W_MATDR) / 2))
            MATDR_EX = MATDR_SX + L_MATDR
            MATDR_EY = MATDR_SY + W_MATDR
            T_SCORESX_ST = MATDR_EX + SCORECARD_X_INDENT * 2
            T_SCORESX = round(SCREEN_WIDTH - L_MATDR - 2 * SCORECARD_X_INDENT)
            T_SCORESY = L_MATDR
            T_SCORES_DIST = round(T_SCORESX / team_no)

            mat_ratio = W_MATDR / w_mat
            R1_RATIO = round(6.5 / w_mat, 5)
            R2_RATIO = round(8.5 / w_mat, 5)
            D1_RATIO = round(4.5 / w_mat, 5)
            D2_RATIO = round(3.5 / w_mat, 5)
            HR1 = round(W_MATDR / 8)
            HR2 = round(W_MATDR / 6)
            H1DRX = round(MATDR_SX + HR1 * 3)
            H1DRY = round(MATDR_SY + W_MATDR / 4)
            H2DRX = H1DRX
            H2DRY = round(MATDR_SY + W_MATDR - W_MATDR / 3.5)
            CENTRE_MATY = round(MATDR_SY + W_MATDR / 2)
            mat_centrex = round(minx + w_mat / 2)
            H2DRXU = H2DRX + HR2
            H1DRYR = H1DRY + HR1

            P_X_START = round(SCORECARD_X_INDENT + ST_DIST / 2)
            P_Y_START = round(TITLE_Y_DIST + STAT_HEAD_Y_DIST + P_Y_SPLIT / 2)

            stx_x = 1040
            stx_y = 510
            stcs_y = 555
            sths_y = 660
            sths_x = 780
            sths1_x = 930
            sths2_x = sths1_x + 120
            sths3_x = sths2_x + 125
            holes_y = round((sths_y + stcs_y )/ 2)

            # Setting up timer
            passed_time = 0
            shown_time = 30
            timer_started = False
            done = False


            stats_strings = ["", "Holes", "Shots", "%", "Points", "PPS", "Max.Strk", "Hole 1", "Hole 2"]

            count = 0
################ Start of while loop to track shots ##################
            while self.cap.isOpened():
                # Initialise various boolean statements for tracking shots
                miss_bool = False
                miss_left = False
                miss_right = False
                miss_end = False
                rb_miss = False
                small_hole_bool = False
                big_hole_bool = False
                hole_bool = False
                # Draw scoreboard
                self.display.fill(self.BLACK)
                self.draw_text(game_string, 40, self.DISPLAY_W/2, 50)
                # Add info for current streaks and highscores
                self.draw_scores("Current Streaks", 50, stx_x, stx_y)
                self.draw_scores(str(sum(streak_count_s[p_ind - 1])), 65, sths1_x, stcs_y)
                self.draw_scores(str(sum(streak_count_b[p_ind - 1])), 65, sths2_x, stcs_y)
                self.draw_scores(str(sum(streak_count_a[p_ind - 1])), 65, sths3_x, stcs_y)
                pygame.draw.circle(self.display, self.WHITE, (sths1_x, holes_y), 7)
                pygame.draw.circle(self.display, self.WHITE, (sths2_x, holes_y), 12)
                pygame.draw.circle(self.display, self.WHITE, (sths3_x - 15, holes_y), 7)
                pygame.draw.circle(self.display, self.WHITE, (sths3_x + 15, holes_y), 12)
                self.draw_scores("HIGHSCORES:", 45, sths_x, sths_y)
                self.draw_scores(str(streakHS[0]), 65, sths1_x, sths_y)
                self.draw_scores(str(streakHS[1]), 65, sths2_x, sths_y)
                self.draw_scores(str(streakHS[2]), 65, sths3_x, sths_y)

                if game_mode != "F":
                    self.draw_text(team_string, 20, round(self.DISPLAY_W/8), 25)
                    self.draw_text("Rounds " + str(rounds), 20, self.DISPLAY_W/8, 50)
                    self.draw_text("Shots  " + str(shotspround), 20, self.DISPLAY_W/8, 75)

                if game_mode == "T":
                    self.draw_text(str(shown_time), 40, round(7 * self.DISPLAY_W/8), 600)
                for p in range(num_players):
                    for t in range(team_no):
                        if p + 1 in teams[t]:
                            p_colour[p] = self.team_colours[t]
                    # Draw rect representing team by colour
                    pygame.draw.rect(self.display, p_colour[p], pygame.Rect(round(SCORECARD_X_INDENT),
                        round(P_Y_START - P_Y_SPLIT / 2 + P_Y_SPLIT * p), DIST_X_SCORE, P_Y_SPLIT))
                    pygame.draw.rect(self.display, p_colour[p], pygame.Rect(round(SCORECARD_X_INDENT),
                        round(P_Y_START - P_Y_SPLIT / 2 + P_Y_SPLIT * p), DIST_X_SCORE, P_Y_SPLIT), 3)
                    for s in range(STATS_SHOWN):
                        # Draw scores/stats for each player
                        self.draw_scores(str(stats_a[p][s]), 50, P_X_START + s * ST_DIST, round(P_Y_START + p * P_Y_SPLIT))
                        if s < len(stats_strings):
                            self.draw_scores(str(stats_strings[s]), 50, round(P_X_START + ST_DIST * s), STAT_HEAD_Y_START)

                # Draw box to indicate player turn
                pygame.draw.rect(self.display, self.WHITE, pygame.Rect(round(SCORECARD_X_INDENT),
                    round(P_Y_START - P_Y_SPLIT / 2 + P_Y_SPLIT * (p_ind - 1)), DIST_X_SCORE, P_Y_SPLIT), 8)
                pygame.draw.rect(self.display, self.BLACK, pygame.Rect(round(SCORECARD_X_INDENT),
                    round(P_Y_START - P_Y_SPLIT / 2 + P_Y_SPLIT * (p_ind - 1)), DIST_X_SCORE, P_Y_SPLIT), 3)
                # Draw mat holes etc. on scoreboard
                pygame.draw.rect(self.display, self.GREEN, pygame.Rect(MATDR_SX, MATDR_SY, L_MATDR, W_MATDR))
                pygame.draw.circle(self.display, self.BLACK, (H1DRX, H1DRY), HR1)
                pygame.draw.circle(self.display, self.BLACK, (H2DRX, H2DRY), HR2)
                sholesinrnd = H1_rndcount_a[p_ind - 1]
                bholesinrnd = H2_rndcount_a[p_ind - 1]
                shotsinrnd = t_rndcount_a[p_ind - 1]
                pmissedrnd = missed_rndcount_a[p_ind - 1]
                if pmissedrnd > 0:
                    for i in range(pmissedrnd):
                        self.draw_x("x", 50, missed_points[-1 - i][0], missed_points[- 1 - i][1])
                if sholesinrnd > 0:
                    self.draw_text("x" + str(sholesinrnd), 20, H1DRX, H1DRY)
                if bholesinrnd > 0:
                    self.draw_text("x" + str(bholesinrnd), 20, H2DRX, H2DRY)

                # Draw balls and player indicator on mat
                p_txt = 60
                self.draw_text_with_rect(p_strings[p_ind - 1], p_txt, round(MATDR_EX + 2*p_txt),
                                         round(MATDR_SY + p_txt), p_colour[p_ind - 1])
                # pygame.draw.rect(self.display, self.WHITE, pygame.Rect(round(MATDR_EX + 2*p_txt),
                #                         round(MATDR_SY + p_txt), p_txt, p_txt), 6)
                if game_mode != "F":
                    for ball in range(shotspround):
                        ball_rad = round(HR1 / 2)
                        ball_xpos = round(MATDR_SX + 7 * L_MATDR / 8)
                        ball_ypos = MATDR_SY + (ball + 1) * (W_MATDR / (shotspround + 1))
                        if ball + 1 > shotsinrnd:
                            # if shots have been taken we want to display outline of these balls
                            pygame.draw.circle(self.display, self.WHITE, (ball_xpos, ball_ypos), ball_rad)
                        else:
                            # draw filled in ball/circle for shots yet to be taken
                            pygame.draw.circle(self.display, self.WHITE, (ball_xpos, ball_ypos), ball_rad, 4)
                        if ball == shotsinrnd:
                            fsind = 40
                            self.draw_ind("<", fsind, ball_xpos + ball_rad + fsind / 2, ball_ypos)
                            pygame.draw.circle(self.display, self.BLACK, (ball_xpos, ball_ypos), ball_rad + 2, 4)
                    # Draw on total scores in bottom right
                    tot_scores_x = round(MATDR_EX + 150)
                    tot_scores_y = MATDR_SY
                    scoresbigfs = 30
                    # for t in range(team_no):
                    #     sc_fs = 30
                    #     stringscx = MATDR_EX + 250
                    #     stringscy = tot_scores_y + 50 + t * 50
                    #     scorescx = MATDR_EX + 450
                    #     scorescy = stringscy
                    #     if team_bool:
                    #         scorescx = MATDR_EX + 500
                    #         self.draw_text(str(t_strings[t]), sc_fs, stringscx, stringscy)
                    #         self.draw_scores(str(sum(t_pts[t])), sc_fs * 2, scorescx, scorescy)
                    #     else:
                    #         self.draw_text(str(p_strings[t]), sc_fs, stringscx, stringscy)
                    #         self.draw_scores(str(sum(p_pts[t])), sc_fs * 2, scorescx, scorescy)

                self.window.blit(self.display, (0, 0))
                pygame.display.update()

                ret, frame = self.cap.read()

                height, width, _ = frame.shape

                # fill shapes to only reveal mat
                polyfill1 = np.array([[0, 0], [minxmin, 0], [minx, n3ay], [0, n3ay]])
                polyfill2 = np.array([[0, n3ay], [minx, n3ay], [minx, height], [0, height]])
                polyfill3 = np.array([[maxx, n3ay], [width, n3ay], [width, height], [maxx, height]])
                polyfill4 = np.array([[maxxmin, 0], [width, 0], [width, maxy], [maxx, maxy]])
                polyfill5 = np.array([[minx, maxy], [maxx, maxy], [maxx, height], [minx, height]])
                cv2.fillPoly(frame, pts=[polyfill1], color=(255, 255, 255))
                cv2.fillPoly(frame, pts=[polyfill2], color=(255, 255, 255))
                cv2.fillPoly(frame, pts=[polyfill3], color=(255, 255, 255))
                cv2.fillPoly(frame, pts=[polyfill4], color=(255, 255, 255))
                cv2.fillPoly(frame, pts=[polyfill5], color=(255, 255, 255))

                ################################# Start of shot tracking #################################
                # Object Detection
                mask = object_detector.apply(frame)
                kernel = np.ones((8, 8), np.uint8)
                mask = cv2.erode(mask, kernel)

                _, mask = cv2.threshold(mask, 254.9, 255, cv2.THRESH_BINARY)
                contours, _ = cv2.findContours(mask, cv2.RETR_TREE, cv2.CHAIN_APPROX_SIMPLE)

                no_detection = False
                detections = []
                contr = 0
                for cnt in contours:
                    # Calculate area and remove small elements
                    area = cv2.contourArea(cnt)
                    if area > 40:
                        x, y, w, h = cv2.boundingRect(cnt)
                        detections.append([x, y, w, h])
                    contr += 1

                if is_empty(contours):
                    no_detection = True

                boxes_ids = tracker.update(detections, H1_xl, H1_xr, H2_xl, H2_xr, maxy, sz3n1y)
                a, b, c, d = [255, 390, 515, 480]

                for box_id in boxes_ids:
                    x, y, w, h, id = box_id
                    cv2.putText(frame, str(id), (x, y - 15), cv2.FONT_HERSHEY_PLAIN, 2, (255, 0, 0), 2)
                    cv2.rectangle(frame, (x, y), (x + w, y + h), (0, 0, 255), 3)

                centr_dict = tracker.center_points

                ########### Main loop to identify shots/holes/misses ##########
                for key in centr_dict:
                    cx = centr_dict[key][0]
                    cy = centr_dict[key][1]

                    cyo[key].append(cy)
                    cxo[key].append(cx)
                    xinit = cxo[key][0]
                    yinit = cyo[key][0]
                    if key in object_shot:
                        oldy = cyo[key][-2]
                        oldyint = int(oldy)

                        oldx = cxo[key][-2]
                        oldxint = int(oldx)

                        # check intersections of ball path with lines at end of holes (to check misses)
                        miss_end = intersect((cx, cy), (xinit, yinit), node3, node4)
                        miss_left = intersect((cx, cy), (xinit, yinit), node3, node1)
                        miss_right = intersect((cx, cy), (xinit, yinit), node4, node2)

                        distH1x = ((cx - H1_cx) ** 2) ** 0.5
                        distH1y = ((cy - H1_cy) ** 2) ** 0.5
                        distH1 = (distH1x ** 2 + distH1y ** 2) ** 0.5
                        distH1xo = ((oldxint - H1_cx) ** 2) ** 0.5
                        distH1yo = ((oldyint - H1_cy) ** 2) ** 0.5
                        distH1o = (distH1xo ** 2 + distH1yo ** 2) ** 0.5

                        distH2x = ((cx - H2_cx) ** 2) ** 0.5
                        distH2y = ((cy - H2_cy) ** 2) ** 0.5
                        distH2 = (distH2x ** 2 + distH2y ** 2) ** 0.5
                        distH2xo = ((oldxint - H1_cx) ** 2) ** 0.5
                        distH2yo = ((oldyint - H1_cy) ** 2) ** 0.5
                        distH2o = (distH2xo ** 2 + distH2yo ** 2) ** 0.5

                    sz1bool = intersect((cx, cy), (xinit, yinit), node1, node2)
                    sz2bool = intersect((cx, cy), (xinit, yinit), node5, node6)
                    sz3bool = intersect((cx, cy), (xinit, yinit), sz3n1, sz3n2)

                    if len(cyo[key]) > 1 and cyo[key][-1] > cyo[key][-2]:
                        # if sz1bool and key not in sz1list and key not in sz2list and key not in sz3list and key not in object_shot:
                        #     sz1list.append(key)
                        if key not in sz2list and sz2bool:
                            sz2list.append(key)
                        if key not in sz3list and key in sz2list and sz3bool:
                            sz3list.append(key)

                        # if ball goes through zone register it as a shot if current y value greater than previous y position
                        if key not in object_shot and key in sz3list and len(cyo[key]) > 2:
                            if minx < cx < maxx and cy < maxy and cyo[key][-1] > cyo[key][-2] > cyo[key][-3]:
                                shot_count += 1
                                object_shot.append(key)
                                shot_bool = True
                                p_shots += 1

                                # if previous shot result not tracked register as miss
                                if len(object_shot) > 1:
                                    if object_shot[-2] not in object_holes and object_shot[-2] not in object_missed:
                                        object_missed.append(object_shot[-2])

                    if key in object_shot and key not in object_missed and key not in object_holes:
                        #start tracking y and x vals for max value of y
                        if cy > cymax[key]:
                            cymax[key] = cy
                            cxmax[key] = cx
                        if miss_end or miss_left or miss_right:
                            object_missed.append(key)
                            missed_count += 1
                            streak_count = 0
                            H1streak_count = 0
                            H2streak_count = 0
                            shot_record.append(0)
                            miss_bool = True
                            print("miss wide/far")

                        elif minx < cx < maxx and cy < H2_yu - 2 * r2 and cyo[key][-1] < cyo[key][-2] < cyo[key][-3]:
                            missed_count += 1
                            streak_count = 0
                            H1streak_count = 0
                            H2streak_count = 0
                            object_missed.append(key)
                            shot_record.append(0)
                            miss_bool = True
                            rb_miss = True
                            print("rolled back miss")

                # if a shot has been missed/holed set shot bool to false as shot is finished
                if miss_bool or hole_bool:
                    shot_bool = False

                # if no object is being tracked and last shot result not tracked we check if it was a hole or miss
                if len(object_shot) > 0:
                    last_shot_key = object_shot[-1]
                    cxls = int(cxo[last_shot_key][-1])
                    cyls = int(cyo[last_shot_key][-1])
                    if no_detection and shot_bool:
                        # Check if last traced location was within small hole
                        if is_in_hole(cxls, cyls, H1_cx, H1_cy, r1, h1):
                            hole1_count += 1
                            streak_count += 1
                            H1streak_count += 1
                            H2streak_count = 0
                            object_hole1.append(key)
                            object_holes.append(key)
                            shot_record.append(1)
                            small_hole_bool = True
                            hole_bool = True
                            print("small hole")
                        # check if ball in big hole
                        elif is_in_hole(cxls, cyls, H2_cx, H2_cy, r2, h2):
                            hole2_count += 1
                            streak_count += 1
                            H2streak_count += 1
                            H1streak_count = 0
                            object_hole2.append(key)
                            object_holes.append(key)
                            shot_record.append(2)
                            big_hole_bool = True
                            hole_bool = True
                            print("big hole")
                        else:
                            missed_count += 1
                            streak_count = 0
                            H1streak_count = 0
                            H2streak_count = 0
                            object_missed.append(key)
                            shot_record.append(0)
                            miss_bool = True
                            if cyls > H2_yd:
                                miss_end = True
                            print("missed")

                if miss_bool or hole_bool:
                    last_shot_key = object_shot[-1]
                    misspx = int(cxo[last_shot_key][-1])
                    misspy = int(cyo[last_shot_key][-1])

                    if small_hole_bool:
                        H1_rndcount_a[p_ind - 1] += 1
                    elif big_hole_bool:
                        H2_rndcount_a[p_ind - 1] += 1
                    elif miss_bool:
                        missed_rndcount_a[p_ind - 1] += 1
                        if rb_miss:
                            misspy = int(cymax[last_shot_key])
                            misspx = int(cxmax[last_shot_key])
                        dy_act = H2_yu - misspy
                        dx_act = H1_xr - misspx
                        dy_mat = dx_act * mat_ratio
                        dx_mat = dy_act * mat_ratio
                        draw_missx = H2DRXU + dx_mat
                        draw_missy = H1DRYR - dy_mat
                        # if draw_missx > H2DRXU:
                        #     draw_missx = draw_missx + 0.5 * (draw_missx - H2DRXU)
                        if miss_end and not rb_miss:
                            print("ENDMISS")
                            draw_missx = MATDR_SX
                        missed_points.append((draw_missx, draw_missy))
                        print("drawing x")

################################# End of shot tracking #################################
                # Play sounds if holed
                if hole_bool:
                    if sum(streak_count_a[p_ind - 1]) == 5:
                        self.sounds["dontmiss"].play()
                    elif small_hole_bool:
                        self.sounds["hole1"].play()
                    elif big_hole_bool:
                        self.sounds["hole2"].play()
                elif miss_bool:
                    # if sum(missed_strk_cnt_a[p_ind - 1]) == 1:
                    #     self.sounds["sadsong"].play()
                    # else:
                    self.sounds["miss"].play()

                if game_mode == "T" and shot_bool and not timer_started:
                    while not done:
                        if passed_time == 30:
                            pygame.time.wait(5000)
                            done = True
                        if not timer_started:
                            start_time = pg.time.get_ticks()
                            timer_started = True
                if timer_started:
                    passed_time = pg.time.get_ticks() - start_time
                    shown_time = 30 - passed_time

                # if shot has ended
                if miss_bool or hole_bool:
                    shot_bool = False

                total_holes = hole1_count + hole2_count
                sum_points = sum(p_pts[0])
                # Recording holes/misses in current round
                H_rndcount_a[p_ind - 1] = H1_rndcount_a[p_ind - 1] + H2_rndcount_a[p_ind - 1]
                t_rndcount_a[p_ind - 1] = H_rndcount_a[p_ind - 1] + missed_rndcount_a[p_ind - 1]

                # assign points and record stats etc for players
                for player in range(num_players):
                    if p_ind == player + 1 and len(object_shot) > 0:
                        if hole_bool:
                            streak_count_a[player].append(1)
                            H_count_a[player].append(1)
                            missed_strk_cnt_a[player].clear()
                        if small_hole_bool:
                            streak_count_s[player].append(1)
                            streak_count_b[player].clear()
                            H1_count_a[player].append(1)
                            p_pts[p_ind - 1].append(s_pts)
                            for team in range(team_no):
                                if p_ind in teams[team]:
                                    t_pts[team].append(s_pts)
                        elif big_hole_bool:
                            streak_count_b[player].append(1)
                            streak_count_s[player].clear()
                            H2_count_a[player].append(1)
                            p_pts[p_ind - 1].append(b_pts)
                            for team in range(team_no):
                                if p_ind in teams[team]:
                                    t_pts[team].append(b_pts)
                        elif miss_bool:
                            missed_count_a[player].append(1)
                            missed_strk_cnt_a[player].append(1)
                            streak_count_a[player].clear()
                            streak_count_b[player].clear()
                            streak_count_s[player].clear()
                            p_pts[player].append(0)
                            for team in range(team_no):
                                if p_ind in teams[team]:
                                    t_pts[team].append(0)
                        missed_temp = int(sum(missed_count_a[player]))
                        holes_temp = int(sum(H_count_a[player]))
                        if miss_bool or hole_bool:
                            shtpct = round(holes_temp * 100 / (missed_temp + holes_temp))
                            shot_pcnt_a[player].append(shtpct)
                            shot_count_a[p_ind - 1].append(1)
                            sum_p_pts[player] = sum(p_pts[player])
                            if sum(p_pts[player]) > 0:
                                sum_shots_temp = sum(shot_count_a[player])
                                pps_temp = round(sum_p_pts[player] / sum_shots_temp, 2)
                                pps_a[player].append(pps_temp)
                        # record maximum streak for each player
                        max_str_temp = sum(streak_count_a[player])
                        if max_str_temp < sum(streak_count_b[player]):
                            max_str_temp = sum(streak_count_b[player])
                        if max_str_temp < sum(streak_count_s[player]):
                            max_str_temp = sum(streak_count_s[player])
                        if max_str_temp > max_streak_a[player][0]:
                            max_streak_a[player][0] = max_str_temp
                        # Check if we need to update highscores text file
                        if sum(streak_count_s[player]) > streakHS[0]:
                            streakHS[0] = sum(streak_count_s[player])
                            with open("streakHS.txt", "w") as f:
                                for i in streakHS:
                                    f.write(str(i) +"\n")
                        if sum(streak_count_b[player]) > streakHS[1]:
                            streakHS[1] = sum(streak_count_b[player])
                            with open("streakHS.txt", "w") as f:
                                for i in streakHS:
                                    f.write(str(i) +"\n")
                        if sum(streak_count_a[player]) > streakHS[2]:
                            streakHS[2] = sum(streak_count_a[player])
                            with open("streakHS.txt", "w") as f:
                                for i in streakHS:
                                    f.write(str(i) +"\n")
                        #play sound if impressive streak reached


                    stats_a[player][0] = p_strings[player]
                    stats_a[player][1] = sum(H_count_a[player])
                    stats_a[player][2] = sum(shot_count_a[player])
                    stats_a[player][3] = shot_pcnt_a[player][-1]
                    stats_a[player][4] = sum_p_pts[player]
                    stats_a[player][5] = pps_a[player][-1]
                    stats_a[player][6] = sum(max_streak_a[player])
                    stats_a[player][7] = sum(H1_count_a[player])
                    stats_a[player][8] = sum(H2_count_a[player])



################################# End of stats calculation #################################

                # loop to find indicator for next player/team turn
                if (game_mode == "P" and (miss_bool or hole_bool) and p_shots == shotspround) or \
                        (game_mode == "T" and done):

                    H1_rndcount_a[p_ind - 1] = 0
                    H2_rndcount_a[p_ind - 1] = 0
                    H_rndcount_a[p_ind - 1] = 0
                    missed_rndcount_a[p_ind - 1] = 0
                    t_rndcount_a[p_ind - 1] = 0

                    if game_mode == "T":
                        shown_time = 30
                        passed_time = 0
                        timers_done += 1
                        timer_started = False

                    p_rnd_comp[p_ind - 1] = int(p_rnd_comp[p_ind - 1]) + 1
                    p_shots = 0
                    t_ind += 1


                    if (missed_count + hole1_count + hole2_count) % (num_players * shotspround) == 0:
                        cur_rnd = int(shot_count / (num_players * shotspround)) + 1
                    if t_ind > team_no:
                        t_ind = 1
                    while True:
                        p_ind += 1
                        if p_ind > num_players:
                            p_ind = 1
                        if p_ind not in teams[t_ind - 1]:
                            continue
                        else:
                            posit = teams[t_ind - 1].index(p_ind)
                        if posit > 0 and shot_count_a[p_ind - 1] < shot_count_a[p_ind - 2]:
                            break
                        elif posit == 0 and shot_count_a[p_ind - 1] == shot_count_a[teams[t_ind - 1][-1] - 1]:
                            break

                    # if game finished we want to find winner
                    if (game_mode == "P" and total_holes + missed_count == num_players * shotspround * rounds) \
                            or (game_mode == "T" and timers_done == num_players):
                        if not team_bool:
                            winning_pts = sum(p_pts[0])
                            winning_p = 1
                            for i in range(len(p_pts)):
                                if sum(p_pts[i]) > winning_pts:
                                    winning_pts = sum(p_pts[i])
                                    winning_p = i + 1
                                elif sum(p_pts[i]) > winning_pts:
                                    winning_pts = 0
                                    winning_p = 0
                            if winning_p > 0:
                                print("winner")
                            else:
                                print("draw")
                        elif team_bool:
                            winning_pts = sum(t_pts[0])
                            winning_p = 1
                            for i in range(len(t_pts)):
                                if sum(t_pts[i]) > winning_pts:
                                    winning_pts = sum(p_pts[i])
                                    winning_p = i + 1
                                elif sum(p_pts[i]) > winning_pts:
                                    winning_pts = 0
                                    winning_p = 0
                            if winning_p > 0:
                                print("winner")
                            else:
                                print("draw")

                        k1 = cv2.waitKey(0)
                        if k1 == 13:  # wait for ENTER key to proceed
                            # self.cap.release()
                            cv2.destroyAllWindows()



                if total_holes > 0:
                    shot_pcnt = int(round(100 * (total_holes) / (total_holes + missed_count)))
                    pps = round(sum_points / (total_holes + missed_count), 2)
                if streak_count > max_streak_count:
                    max_streak_count = streak_count
                round_stats = [total_holes, shot_pcnt, sum(p_pts[0]), pps, hole1_count, hole2_count]

                cv2.imshow("frame for main", frame)
                pygame.display.update()

                key = cv2.waitKey(30)

                if key == 27:
                    self.cap.release()
                    cv2.destroyAllWindows()
                    self.playing = False
                elif key == ord("r"):
                    break
                elif key == ord("c"):
                    self.matvals = detect_mat(self.cap)
                    # self.matvals = [minx, maxx, miny, maxy, minxmin, maxxmin, n3ay, H1_cx, H1_cy, H1_ax_l, r1, h1, H2_cx, H2_cy, H2_ax_l, r2, h2]
                    minx = self.matvals[0]
                    maxx = self.matvals[1]
                    miny = self.matvals[2]
                    maxy = self.matvals[3]
                    minxmin = self.matvals[4]
                    maxxmin = self.matvals[5]
                    n3ay = self.matvals[6]
                    H1_cx = self.matvals[7]
                    H1_cy = self.matvals[8]
                    H1_ax_l = self.matvals[9]
                    r1 = self.matvals[10]
                    h1 = self.matvals[11]
                    H2_cx = self.matvals[12]
                    H2_cy = self.matvals[13]
                    H2_ax_l = self.matvals[14]
                    r2 = self.matvals[15]
                    h2 = self.matvals[16]

                    # defining left/right/up/down points on holes
                    H1_xl = H1_cx - r1
                    H1_xr = H1_cx + r1
                    H1_yu = H1_cy - h1
                    H1_yd = H1_cy + h1
                    H2_xl = H2_cx - r1
                    H2_xr = H2_cx + r1
                    H2_yu = H2_cy - h2
                    H2_yd = H2_cy + h2

                    # hw_ratio = round(hmax_mat / wmax_mat, 1)
                    # gaps between shot zones
                    szy_adj = 150
                    szy_inter = 50
                    # nodes coordinates
                    n1x = minxmin
                    n1y = miny
                    n2x = maxxmin
                    n2y = n1y
                    n3x = minx
                    n3y = n3ay
                    n4x = maxx
                    n4y = maxy
                    n5x = minx
                    n5y = n1y + szy_adj
                    n6x = maxx
                    n6y = n5y
                    n7x = n5y
                    n7y = n5y
                    n8x = n5y
                    n8y = n5y

                    node1 = (n1x, n1y)
                    node2 = (n2x, n2y)
                    node3 = (n3x, n3y)
                    node4 = (n4x, n4y)
                    node5 = (n5x, n5y)
                    node6 = (n6x, n6y)

                    # defining shot zones
                    sz3n1y = n5y + szy_inter
                    sz3n1 = (n5x, sz3n1y)
                    sz3n2 = (n6x, sz3n1y)
                    sz3n2 = (n6x, sz3n1y)
                count += 1

    def check_events(self):
        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                self.running, self.playing = False, False
                self.curr_menu.run_display = False
            if event.type == pygame.KEYDOWN:
                if event.key == pygame.K_RETURN:
                    self.START_KEY = True
                if event.key == pygame.K_BACKSPACE:
                    self.BACK_KEY = True
                if event.key == pygame.K_DOWN:
                    self.DOWN_KEY = True
                if event.key == pygame.K_UP:
                    self.UP_KEY = True
                if event.key == pygame.K_LEFT:
                    self.LEFT_KEY = True
                if event.key == pygame.K_RIGHT:
                    self.RIGHT_KEY = True

    def reset_keys(self):
        self.UP_KEY, self.DOWN_KEY, self.LEFT_KEY, self.RIGHT_KEY, self.START_KEY, self.BACK_KEY = \
            False, False, False, False, False, False

    def draw_text(self, text, size, x, y):
        font = pygame.font.Font(self.font_name,size)
        text_surface = font.render(text, True, self.WHITE)
        text_rect = text_surface.get_rect()
        text_rect.center = (x,y)
        self.display.blit(text_surface,text_rect)

    def draw_text_black(self, text, size, x, y):
        font = pygame.font.Font(self.font_name,size)
        text_surface = font.render(text, True, self.BLACK)
        text_rect = text_surface.get_rect()
        text_rect.center = (x,y)
        self.display.blit(text_surface,text_rect)

    def draw_text_outline(self, text, size, x, y):
        font = pygame.font.Font(self.font_name, round(size * 1.07))
        text_surface = font.render(text, True, self.BLACK)
        text_rect = text_surface.get_rect()
        text_rect.center = (x,y)
        self.display.blit(text_surface,text_rect)
        font = pygame.font.Font(self.font_name, size)
        text_surface = font.render(text, True, self.WHITE)
        text_rect = text_surface.get_rect()
        text_rect.center = (x,y)
        self.display.blit(text_surface,text_rect)

    def draw_text_with_rect(self, text, size, x, y, colour):
        font = pygame.font.Font(self.font_name,size)
        text_surface = font.render(text, True, self.WHITE)
        text_rect = text_surface.get_rect()
        lenrec = round(text_rect[2] * 1.1)
        hrec = round(text_rect[3] * 2)
        lenrechlf = round(lenrec / 2)
        hrechlf = round(hrec / 2)
        text_rect.center = (x, y)
        pygame.draw.rect(self.display, colour, pygame.Rect(x - lenrechlf, y - hrechlf, lenrec, hrec))
        self.display.blit(text_surface,text_rect)

    def draw_scores(self, text, size, x, y):
        font = pygame.font.Font(self.font_name2,size)
        text_surface = font.render(text, True, self.WHITE)
        text_rect = text_surface.get_rect()
        text_rect.center = (x,y)
        self.display.blit(text_surface,text_rect)

    def draw_ind(self, text, size, x, y):
        font = pygame.font.Font(self.font_name2,size)
        text_surface = font.render(text, True, self.WHITE)
        text_rect = text_surface.get_rect()
        text_rect.center = (x,y)
        self.display.blit(text_surface,text_rect)

    def draw_x(self, text, size, x, y):
        font = pygame.font.Font(self.font_name2,size)
        text_surface = font.render(text, True, self.RED)
        text_rect = text_surface.get_rect()
        text_rect.center = (x,y)
        self.display.blit(text_surface,text_rect)

# Functions to determine if two lines intersect
def ccw(A, B, C):
    return (C[1] - A[1]) * (B[0] - A[0]) > (B[1] - A[1]) * (C[0] - A[0])

# Return true if line segments AB and CD intersect
def intersect(A, B, C, D):
    return ccw(A, C, D) != ccw(B, C, D) and ccw(A, B, C) != ccw(A, B, D)

def is_empty(any_structure):
    if any_structure:
        return False
    else:
        return True

# function to check if point is within ellipse (hole)
def is_in_hole(x, y, hx, hy, rx, ry):
    if ((x - hx) ** 2) / rx ** 2 + ((y - hy) ** 2) / ry ** 2 <= 1:
        return True
    else:
        return False
