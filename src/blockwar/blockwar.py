import random
import logging

import pygame
from pygame.locals import QUIT, KEYUP, MOUSEBUTTONUP, K_LEFT, K_ESCAPE, K_RIGHT, K_w, \
    K_a, K_UP, K_d, K_DOWN, K_s
from constants import *


logger = logging.getLogger('blockwar')


class BlockWarException(Exception):
    """Base class for all exceptions raised from blockwar"""


class QuitEvent(BlockWarException):
    """Someone has requested to quit the game"""


class BlockWar(object):
    def __init__(self):
        self._fps_clock = None
        self._display_surface = None
        self._basic_font = None
        self._reset_surface = None
        self._reset_rect = None
        self._new_surface = None
        self._new_rect = None
        self._solve_surface = None
        self._solve_rect = None
        self._solved_board = None

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

    def _get_starting_board(self):
        # Return a board data structure with tiles in the solved state.
        # For example, if BOARDWIDTH and BOARDHEIGHT are both 3, this function
        # returns [[1, 4, 7], [2, 5, 8], [3, 6, BLANK]]
        counter = 1
        board = []
        for x in range(BOARDWIDTH):
            column = []
            for y in range(BOARDHEIGHT):
                column.append(counter)
                counter += BOARDWIDTH
            board.append(column)
            counter -= BOARDWIDTH * (BOARDHEIGHT - 1) + BOARDWIDTH - 1

        board[BOARDWIDTH - 1][BOARDHEIGHT - 1] = BLANK
        return board

    def _get_blank_position(self, board):
        # Return the x and y of board coordinates of the blank space.
        for x in range(BOARDWIDTH):
            for y in range(BOARDHEIGHT):
                if board[x][y] == BLANK:
                    return (x, y)

    def _make_move(self, board, move):
        # This function does not check if the move is valid.
        blankx, blanky = self._get_blank_position(board)

        if move == UP:
            board[blankx][blanky], board[blankx][blanky + 1] = board[blankx][blanky + 1], \
                                                               board[blankx][blanky]
        elif move == DOWN:
            board[blankx][blanky], board[blankx][blanky - 1] = board[blankx][blanky - 1], \
                                                               board[blankx][blanky]
        elif move == LEFT:
            board[blankx][blanky], board[blankx + 1][blanky] = board[blankx + 1][blanky], \
                                                               board[blankx][blanky]
        elif move == RIGHT:
            board[blankx][blanky], board[blankx - 1][blanky] = board[blankx - 1][blanky], \
                                                               board[blankx][blanky]

    def _is_valid_move(self, board, move):
        blankx, blanky = self._get_blank_position(board)

        return (move == UP and blanky != len(board[0]) - 1) or \
               (move == DOWN and blanky != 0) or \
               (move == LEFT and blankx != len(board) - 1) or \
               (move == RIGHT and blankx != 0)

    def _get_random_move(self, board, lastMove=None):
        # start with a full list of all four moves
        validMoves = [UP, DOWN, LEFT, RIGHT]

        # remove moves from the list as they are disqualified
        if lastMove == UP or not self._is_valid_move(board, DOWN):
            validMoves.remove(DOWN)
        if lastMove == DOWN or not self._is_valid_move(board, UP):
            validMoves.remove(UP)
        if lastMove == LEFT or not self._is_valid_move(board, RIGHT):
            validMoves.remove(RIGHT)
        if lastMove == RIGHT or not self._is_valid_move(board, LEFT):
            validMoves.remove(LEFT)

        # return a random move from the list of remaining moves
        return random.choice(validMoves)

    def _get_left_top_of_file(self, tileX, tileY):
        left = XMARGIN + (tileX * TILESIZE) + (tileX - 1)
        top = YMARGIN + (tileY * TILESIZE) + (tileY - 1)
        return left, top

    def _get_spot_clicked(self, board, x, y):
        # from the x & y pixel coordinates, get the x & y board coordinates
        for tileX in range(len(board)):
            for tileY in range(len(board[0])):
                left, top = self._get_left_top_of_file(tileX, tileY)
                tileRect = pygame.Rect(left, top, TILESIZE, TILESIZE)
                if tileRect.collidepoint(x, y):
                    return (tileX, tileY)
        return (None, None)

    def _draw_tile(self, tilex, tiley, number, adjx=0, adjy=0):
        # draw a tile at board coordinates tilex and tiley, optionally a few
        # pixels over (determined by adjx and adjy)
        left, top = self._get_left_top_of_file(tilex, tiley)
        pygame.draw.rect(self._display_surface, TILECOLOR,
                         (left + adjx, top + adjy, TILESIZE, TILESIZE))
        textSurf = self._basic_font.render(str(number), True, TEXTCOLOR)
        textRect = textSurf.get_rect()
        textRect.center = left + int(TILESIZE / 2) + adjx, top + int(TILESIZE / 2) + adjy
        self._display_surface.blit(textSurf, textRect)

    def _make_text(self, text, color, bgcolor, top, left):
        # create the Surface and Rect objects for some text.
        text_surface = self._basic_font.render(text, True, color, bgcolor)
        text_rectangle = text_surface.get_rect()
        text_rectangle.topleft = (top, left)
        return text_surface, text_rectangle

    def _draw_board(self, board, message):
        self._display_surface.fill(BGCOLOR)
        if message:
            text_surface, text_rectangle = self._make_text(message, MESSAGECOLOR, BGCOLOR, 5, 5)
            self._display_surface.blit(text_surface, text_rectangle)

        for tilex in range(len(board)):
            for tiley in range(len(board[0])):
                if board[tilex][tiley]:
                    self._draw_tile(tilex, tiley, board[tilex][tiley])

        left, top = self._get_left_top_of_file(0, 0)
        width = BOARDWIDTH * TILESIZE
        height = BOARDHEIGHT * TILESIZE
        pygame.draw.rect(self._display_surface, BORDERCOLOR,
                         (left - 5, top - 5, width + 11, height + 11), 4)

        self._display_surface.blit(self._reset_surface, self._reset_rect)
        self._display_surface.blit(self._new_surface, self._new_rect)
        self._display_surface.blit(self._solve_surface, self._solve_rect)

    def _slide_animation(self, board, direction, message, animation_speed):
        # Note: This function does not check if the move is valid.

        blankx, blanky = self._get_blank_position(board)
        if direction == UP:
            movex = blankx
            movey = blanky + 1
        elif direction == DOWN:
            movex = blankx
            movey = blanky - 1
        elif direction == LEFT:
            movex = blankx + 1
            movey = blanky
        elif direction == RIGHT:
            movex = blankx - 1
            movey = blanky

        # prepare the base surface
        self._draw_board(board, message)
        baseSurf = self._display_surface.copy()
        # draw a blank space over the moving tile on the baseSurf Surface.
        moveLeft, moveTop = self._get_left_top_of_file(movex, movey)
        pygame.draw.rect(baseSurf, BGCOLOR, (moveLeft, moveTop, TILESIZE, TILESIZE))

        for i in range(0, TILESIZE, animation_speed):
            # animate the tile sliding over
            self._check_for_quit()
            self._display_surface.blit(baseSurf, (0, 0))
            if direction == UP:
                self._draw_tile(movex, movey, board[movex][movey], 0, -i)
            if direction == DOWN:
                self._draw_tile(movex, movey, board[movex][movey], 0, i)
            if direction == LEFT:
                self._draw_tile(movex, movey, board[movex][movey], -i, 0)
            if direction == RIGHT:
                self._draw_tile(movex, movey, board[movex][movey], i, 0)

            pygame.display.update()
            self._fps_clock.tick(FPS)

    def _reset_animation(self, board, all_moves):
        # make all of the moves in all_moves in reverse.
        revall_moves = all_moves[:]  # gets a copy of the list
        revall_moves.reverse()

        for move in revall_moves:
            if move == UP:
                oppositeMove = DOWN
            elif move == DOWN:
                oppositeMove = UP
            elif move == RIGHT:
                oppositeMove = LEFT
            elif move == LEFT:
                oppositeMove = RIGHT
            self._slide_animation(board, oppositeMove, '',
                                  animation_speed=int(TILESIZE / 2))
            self._make_move(board, oppositeMove)

    def _generate_new_puzzle(self, num_slides):
        # From a starting configuration, make numSlides number of moves (and
        # animate these moves).
        sequence = list()
        board = self._get_starting_board()  # 2d array representing 4x4 tile values
        self._draw_board(board, '')
        pygame.display.update()
        pygame.time.wait(500)  # pause 500 milliseconds for effect
        lastMove = None
        for i in range(num_slides):
            move = self._get_random_move(board, lastMove)
            self._slide_animation(board, move, 'Generating new puzzle...',
                                  animation_speed=int(TILESIZE / 3))
            self._make_move(board, move)
            sequence.append(move)
            lastMove = move
        return board, sequence

    def _tick(self, main_board, solution_seq, all_moves):
        slide_to = None  # the direction, if any, a tile should slide
        msg = 'Click tile or press arrow keys to slide.'  # contains the message to show in the upper left corner.
        if main_board == self._solved_board:
            msg = 'Solved!'

        self._draw_board(main_board, msg)

        self._check_for_quit()
        for event in pygame.event.get():  # event handling loop
            if event.type == MOUSEBUTTONUP:
                spotx, spoty = self._get_spot_clicked(main_board, event.pos[0],
                                                      event.pos[1])

                if (spotx, spoty) == (None, None):
                    # check if the user clicked on an option button
                    if self._reset_rect.collidepoint(event.pos):
                        self._reset_animation(main_board,
                                              all_moves)  # clicked on Reset button
                        all_moves = []
                    elif self._new_rect.collidepoint(event.pos):
                        main_board, solution_seq = self._generate_new_puzzle(
                            80)  # clicked on New Game button
                        all_moves = []
                    elif self._solve_rect.collidepoint(event.pos):
                        self._reset_animation(main_board,
                                              solution_seq + all_moves)  # clicked on Solve button
                        all_moves = []
                else:
                    # check if the clicked tile was next to the blank spot

                    blankx, blanky = self._get_blank_position(main_board)
                    if spotx == blankx + 1 and spoty == blanky:
                        slide_to = LEFT
                    elif spotx == blankx - 1 and spoty == blanky:
                        slide_to = RIGHT
                    elif spotx == blankx and spoty == blanky + 1:
                        slide_to = UP
                    elif spotx == blankx and spoty == blanky - 1:
                        slide_to = DOWN

            elif event.type == KEYUP:
                # check if the user pressed a key to slide a tile
                if event.key in (K_LEFT, K_a) and self._is_valid_move(main_board,
                                                                      LEFT):
                    slide_to = LEFT
                elif event.key in (K_RIGHT, K_d) and self._is_valid_move(main_board,
                                                                         RIGHT):
                    slide_to = RIGHT
                elif event.key in (K_UP, K_w) and self._is_valid_move(main_board, UP):
                    slide_to = UP
                elif event.key in (K_DOWN, K_s) and self._is_valid_move(main_board,
                                                                        DOWN):
                    slide_to = DOWN

        if slide_to:
            self._slide_animation(main_board, slide_to,
                                  'Click tile or press arrow keys to slide.',
                                  8)  # show slide on screen
            self._make_move(main_board, slide_to)
            all_moves.append(slide_to)  # record the slide
        pygame.display.update()
        self._fps_clock.tick(FPS)

    #------------------------------------------------------------------------------------
    # Public
    #------------------------------------------------------------------------------------
    def setup(self):

        pygame.init()
        pygame.display.set_caption('Block War')

        self._fps_clock = pygame.time.Clock()
        self._display_surface = pygame.display.set_mode((WINDOWWIDTH, WINDOWHEIGHT))
        self._basic_font = pygame.font.Font('freesansbold.ttf', BASICFONTSIZE)

        # Store the option buttons and their rectangles in OPTIONS.
        self._reset_surface, self._reset_rect = self._make_text('Reset', TEXTCOLOR,
                                                                TILECOLOR,
                                                                WINDOWWIDTH - 120,
                                                                WINDOWHEIGHT - 90)
        self._new_surface, self._new_rect = self._make_text('New Game', TEXTCOLOR,
                                                            TILECOLOR,
                                                            WINDOWWIDTH - 120,
                                                            WINDOWHEIGHT - 60)
        self._solve_surface, self._solve_rect = self._make_text('Solve', TEXTCOLOR,
                                                                TILECOLOR,
                                                                WINDOWWIDTH - 120,
                                                                WINDOWHEIGHT - 30)

    def run(self):
        logger.critical('Starting BlockWar...')
        main_board, solution_seq = self._generate_new_puzzle(80)
        self._solved_board = self._get_starting_board()  # a solved board is the same as the board in a start state.
        all_moves = []  # list of moves made from the solved configuration
        while True:  # main game loop
            self._tick(main_board, solution_seq, all_moves)

    def quit(self):
        """Quit Block War, must be called outside of the main execution loop"""
        logger.critical('Quitting BlockWar, until next time...')
        pygame.quit()
