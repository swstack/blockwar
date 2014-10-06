import logging
import os
import time

import pygame
from pygame.locals import QUIT, KEYUP, MOUSEBUTTONUP, K_LEFT, K_ESCAPE, K_RIGHT, K_w, \
    K_a, K_UP, K_d, K_DOWN, K_s
from util import paths


logger = logging.getLogger('blockwar')

COLOR_TURF = (34, 139, 34)
COLOR_EDGE = (160, 82, 45)

WINDOW_HEIGHT = 400
WINDOW_WIDTH = 400


class BlockWarException(Exception):
    """Base class for all exceptions raised from blockwar"""


class QuitEvent(BlockWarException):
    """Someone has requested to quit the game"""


class BlockWar(object):
    def __init__(self):
        self._fps_clock = None
        self._display_surface = None

    # ------------------------------------------------------------------------------------
    # Private
    # ------------------------------------------------------------------------------------
    def _update_display(self):
        pygame.display.update()

    def _check_for_quit(self):
        if pygame.event.get(QUIT):
            raise QuitEvent()

        for event in pygame.event.get(KEYUP):  # get all the KEYUP events
            if event.key == K_ESCAPE:
                raise QuitEvent()
            pygame.event.post(event)  # put the other KEYUP event objects back

    #------------------------------------------------------------------------------------
    # Public
    #------------------------------------------------------------------------------------
    def initialize(self):
        """Initialize pygame and the main surface and textures"""

        pygame.init()

        pygame.display.set_caption('Block War')
        self._fps_clock = pygame.time.Clock()

        self._display_surface = pygame.display.set_mode((WINDOW_WIDTH, WINDOW_HEIGHT))
        self._display_surface.fill(COLOR_EDGE)

        turf = pygame.Surface((WINDOW_WIDTH - 50, WINDOW_HEIGHT - 50))
        turf.fill(COLOR_TURF)
        self._display_surface.blit(turf, (25, 25))

        entrance = pygame.Surface((50, 50))
        entrance.fill(COLOR_TURF)
        self._display_surface.blit(entrance, (175, 0))

        hero = pygame.image.load(os.path.join(paths.resources(), 'img', 'hero-sm.png'))
        self._display_surface.blit(hero, (182, 2))

        self._update_display()

    def run(self):
        logger.critical('Starting BlockWar...')
        while True:  # main game loop
            time.sleep(1)

    def quit(self):
        """Quit Block War, must be called outside of the main execution loop"""
        logger.critical('Quitting BlockWar, until next time...')
        pygame.quit()
