import random

import pygame
from pygame.locals import QUIT, KEYUP, MOUSEBUTTONUP, K_LEFT, K_ESCAPE, K_RIGHT, K_w, \
    K_a, K_UP, K_d, K_DOWN, K_s
from constants import *


# Global state
FPSCLOCK = None
DISPLAYSURF = None
BASICFONT = None
RESET_SURF = None
RESET_RECT = None
NEW_SURF = None
NEW_RECT = None
SOLVE_SURF = None
SOLVE_RECT = None


class BlockWar(object):
    def __init__(self):
        pass

    # ------------------------------------------------------------------------------------
    # Private
    # ------------------------------------------------------------------------------------
    def _check_for_quit(self):
        for event in pygame.event.get(QUIT):  # get all the QUIT events
            self.terminate()  # terminate if any QUIT events are present

        for event in pygame.event.get(KEYUP):  # get all the KEYUP events
            if event.key == K_ESCAPE:
                self.terminate()  # terminate if the KEYUP event was for the Esc key
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
        pygame.draw.rect(DISPLAYSURF, TILECOLOR,
                         (left + adjx, top + adjy, TILESIZE, TILESIZE))
        textSurf = BASICFONT.render(str(number), True, TEXTCOLOR)
        textRect = textSurf.get_rect()
        textRect.center = left + int(TILESIZE / 2) + adjx, top + int(TILESIZE / 2) + adjy
        DISPLAYSURF.blit(textSurf, textRect)

    def _make_text(self, text, color, bgcolor, top, left):
        # create the Surface and Rect objects for some text.
        textSurf = BASICFONT.render(text, True, color, bgcolor)
        textRect = textSurf.get_rect()
        textRect.topleft = (top, left)
        return textSurf, textRect

    def _draw_board(self, board, message):
        DISPLAYSURF.fill(BGCOLOR)
        if message:
            textSurf, textRect = self._make_text(message, MESSAGECOLOR, BGCOLOR, 5, 5)
            DISPLAYSURF.blit(textSurf, textRect)

        for tilex in range(len(board)):
            for tiley in range(len(board[0])):
                if board[tilex][tiley]:
                    self._draw_tile(tilex, tiley, board[tilex][tiley])

        left, top = self._get_left_top_of_file(0, 0)
        width = BOARDWIDTH * TILESIZE
        height = BOARDHEIGHT * TILESIZE
        pygame.draw.rect(DISPLAYSURF, BORDERCOLOR,
                         (left - 5, top - 5, width + 11, height + 11), 4)

        DISPLAYSURF.blit(RESET_SURF, RESET_RECT)
        DISPLAYSURF.blit(NEW_SURF, NEW_RECT)
        DISPLAYSURF.blit(SOLVE_SURF, SOLVE_RECT)

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
        baseSurf = DISPLAYSURF.copy()
        # draw a blank space over the moving tile on the baseSurf Surface.
        moveLeft, moveTop = self._get_left_top_of_file(movex, movey)
        pygame.draw.rect(baseSurf, BGCOLOR, (moveLeft, moveTop, TILESIZE, TILESIZE))

        for i in range(0, TILESIZE, animation_speed):
            # animate the tile sliding over
            self._check_for_quit()
            DISPLAYSURF.blit(baseSurf, (0, 0))
            if direction == UP:
                self._draw_tile(movex, movey, board[movex][movey], 0, -i)
            if direction == DOWN:
                self._draw_tile(movex, movey, board[movex][movey], 0, i)
            if direction == LEFT:
                self._draw_tile(movex, movey, board[movex][movey], -i, 0)
            if direction == RIGHT:
                self._draw_tile(movex, movey, board[movex][movey], i, 0)

            pygame.display.update()
            FPSCLOCK.tick(FPS)

    def _reset_animation(self, board, allMoves):
        # make all of the moves in allMoves in reverse.
        revAllMoves = allMoves[:]  # gets a copy of the list
        revAllMoves.reverse()

        for move in revAllMoves:
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

    def _generate_new_puzzle(self, numSlides):
        # From a starting configuration, make numSlides number of moves (and
        # animate these moves).
        sequence = []
        board = self._get_starting_board()
        self._draw_board(board, '')
        pygame.display.update()
        pygame.time.wait(500)  # pause 500 milliseconds for effect
        lastMove = None
        for i in range(numSlides):
            move = self._get_random_move(board, lastMove)
            self._slide_animation(board, move, 'Generating new puzzle...',
                                  animation_speed=int(TILESIZE / 3))
            self._make_move(board, move)
            sequence.append(move)
            lastMove = move
        return board, sequence

    #------------------------------------------------------------------------------------
    # Public
    #------------------------------------------------------------------------------------
    def run(self):
        global FPSCLOCK, DISPLAYSURF, BASICFONT, RESET_SURF, RESET_RECT, NEW_SURF, NEW_RECT, SOLVE_SURF, SOLVE_RECT

        pygame.init()
        pygame.display.set_caption('Block War')

        FPSCLOCK = pygame.time.Clock()
        DISPLAYSURF = pygame.display.set_mode((WINDOWWIDTH, WINDOWHEIGHT))
        BASICFONT = pygame.font.Font('freesansbold.ttf', BASICFONTSIZE)

        # Store the option buttons and their rectangles in OPTIONS.
        RESET_SURF, RESET_RECT = self._make_text('Reset', TEXTCOLOR, TILECOLOR,
                                                 WINDOWWIDTH - 120,
                                                 WINDOWHEIGHT - 90)
        NEW_SURF, NEW_RECT = self._make_text('New Game', TEXTCOLOR, TILECOLOR,
                                             WINDOWWIDTH - 120,
                                             WINDOWHEIGHT - 60)
        SOLVE_SURF, SOLVE_RECT = self._make_text('Solve', TEXTCOLOR, TILECOLOR,
                                                 WINDOWWIDTH - 120,
                                                 WINDOWHEIGHT - 30)

        mainBoard, solutionSeq = self._generate_new_puzzle(80)
        SOLVEDBOARD = self._get_starting_board()  # a solved board is the same as the board in a start state.
        allMoves = []  # list of moves made from the solved configuration

        while True:  # main game loop
            slideTo = None  # the direction, if any, a tile should slide
            msg = 'Click tile or press arrow keys to slide.'  # contains the message to show in the upper left corner.
            if mainBoard == SOLVEDBOARD:
                msg = 'Solved!'

            self._draw_board(mainBoard, msg)

            self._check_for_quit()
            for event in pygame.event.get():  # event handling loop
                if event.type == MOUSEBUTTONUP:
                    spotx, spoty = self._get_spot_clicked(mainBoard, event.pos[0],
                                                          event.pos[1])

                    if (spotx, spoty) == (None, None):
                        # check if the user clicked on an option button
                        if RESET_RECT.collidepoint(event.pos):
                            self._reset_animation(mainBoard,
                                                  allMoves)  # clicked on Reset button
                            allMoves = []
                        elif NEW_RECT.collidepoint(event.pos):
                            mainBoard, solutionSeq = self._generate_new_puzzle(
                                80)  # clicked on New Game button
                            allMoves = []
                        elif SOLVE_RECT.collidepoint(event.pos):
                            self._reset_animation(mainBoard,
                                                  solutionSeq + allMoves)  # clicked on Solve button
                            allMoves = []
                    else:
                        # check if the clicked tile was next to the blank spot

                        blankx, blanky = self._get_blank_position(mainBoard)
                        if spotx == blankx + 1 and spoty == blanky:
                            slideTo = LEFT
                        elif spotx == blankx - 1 and spoty == blanky:
                            slideTo = RIGHT
                        elif spotx == blankx and spoty == blanky + 1:
                            slideTo = UP
                        elif spotx == blankx and spoty == blanky - 1:
                            slideTo = DOWN

                elif event.type == KEYUP:
                    # check if the user pressed a key to slide a tile
                    if event.key in (K_LEFT, K_a) and self._is_valid_move(mainBoard,
                                                                          LEFT):
                        slideTo = LEFT
                    elif event.key in (K_RIGHT, K_d) and self._is_valid_move(mainBoard,
                                                                             RIGHT):
                        slideTo = RIGHT
                    elif event.key in (K_UP, K_w) and self._is_valid_move(mainBoard, UP):
                        slideTo = UP
                    elif event.key in (K_DOWN, K_s) and self._is_valid_move(mainBoard,
                                                                            DOWN):
                        slideTo = DOWN

            if slideTo:
                self._slide_animation(mainBoard, slideTo,
                                      'Click tile or press arrow keys to slide.',
                                      8)  # show slide on screen
                self._make_move(mainBoard, slideTo)
                allMoves.append(slideTo)  # record the slide
            pygame.display.update()
            FPSCLOCK.tick(FPS)

    def quit(self):
        pygame.quit()
