# runs as ./Reversi from command line
# run w -u flag to flush output
# chmod +x Reversi makes executable from script
# move = < letter >< number > indicating < column >< row >

import sys
import logging
import argparse
import copy
import random
import string

logging.basicConfig(level=logging.DEBUG)
logger = logging.getLogger(__name__)
log = False


VERSION = 0.1           # version number
AUTHOR = 'Jenna Cryan'  # author
PROGNAME = 'reversi'    # program executable name
VRSNSTR = 'Name     : ' + PROGNAME + '\n Version : ' + str(VERSION) + '\n Author  : ' + AUTHOR     # version info

LIGHT = 'L'             # represents a light disk
DARK = 'D'              # represents a dark disk
BLANK = ' '             # represents a blank disk


# simulates a game of Reversi
class Reversi:
    playing = False     # signals when game is currently happening
    size = 8            # default board size is 8 x 8
    # last_move = '--'    # stores last move

    # initializes game board of size n +
    # human and computer players as light or dark
    def __init__(self, n, l):
        self.size = n
        self.board = Board(self.size)
        if l is True:
            self.human = Player('Light', 'human')
            self.computer = Player('Dark', 'computer')
            self.current_player = self.computer
        else:
            self.computer = Player('Light', 'computer')
            self.human = Player('Dark', 'human')
            self.current_player = self.human

    # displays information about last move made, whose turn is next + current score
    def display_info(self):
        print 'Move played: ' + self.board.last_move
        print self.current_player.color + ' player ( ' + self.current_player.type + ' ) plays now'
        # print 'Score: ' + self.computer.color + ' ' + str(self.computer.score) \
        #       + ' - ' + self.human.color + ' ' + str(self.human.score)
        print 'Score: Light ' + str(len(self.board.light)) + ' - Dark ' + str(len(self.board.dark))
        # logger.debug('score from tiles : light : %d, dark : %d' % (len(self.board.light), len(self.board.dark)))

    # switches current player from human to computer or vice versa
    def switch_player(self):
        if self.current_player is self.computer:
            self.current_player = self.human
        else:
            self.current_player = self.computer

    # prompts opponent for a move
    def get_move(self):
        scores = []
        valid = False
        # get human move
        move = raw_input('play < move > : ')
        # get integer coordinate values
        col = self.board.get_col_num(move[0])
        row = self.board.get_row_num(move[1:])

        # check column is character in range for board size
        char = col in range(self.size)
        # check row is number in range for board size
        num = row in range(self.size)

        # check move is valid for current game board
        if char and num:
            scores = self.board.check_move(col, row, self.current_player.color[0])
            if len(scores) > 1:
                valid = True
        else:
            logger.debug('not char or num')
        while not char or not num or not valid:
            if not char:
                logger.debug('not char')
            elif not num:
                logger.debug('not num')
            elif not valid:
                logger.debug('not valid')

            valid = False
            move = raw_input('Invalid move : ' + move + '\nplay < letter >< number > : ')

            # get integer coordinate values
            col = self.board.get_col_num(move[0])
            row = self.board.get_row_num(move[1:])

            # check row, col in size range
            char = col in range(self.size)
            num = row in range(self.size)

            if char and num:
                scores = self.board.check_move(col, row, self.current_player.color[0])
                if len(scores) > 1:
                    valid = True
        return scores

    # initializes game play with opponent
    def play(self):
        logger.info('Welcome to Reversi!')
        logger.info('')
        self.playing = True
        self.board.init_game()
        # start a new game
        while self.playing:
            self.board.display_board()
            self.display_info()

            # check if we want to prompt for a move or make one ourselves
            if self.current_player is self.human:
                self.current_player.current_move = self.get_move()
            else:
                # self.current_player.current_move = self.board.get_minimax(self.current_player.color[0])
                self.current_player.current_move = self.board.make_move(self.current_player.color[0])

            # increment score, set move on game board + switch players
            # logger.debug('[ 130 ] setting move : ')
            # self.board.print_list(self.current_player.current_move)
            self.board.set_move(self.current_player.current_move, self.current_player.color[0])
            self.current_player.score = len(self.board.get_disk_list(self.current_player.color))
            # self.current_player = self.board.set_move(self.current_player)
            # self.current_player.score += len(self.current_player.current_move) - 1
            # self.board.set_move(self.current_player.current_move, self.current_player.color[0])
            self.switch_player()

            # TODO figure out how to tell when there's no more valid moves
            # TODO loop through neighbors and look for valid moves ?
            # if len(self.board.valid_moves) < 1:
            #     self.playing = False


# class to simulate a Reversi game board of given size
class Board:
    size = 8
    board = []
    light = set()
    dark = set()
    current_neighbs = set()
    last_move = '--'

    # initialize game board of size n
    def __init__(self, n=8):
        self.size = n
        self.board = self.init_board()

    # def __init__(self, n=8, board=Board.init_board(), light=set(), dark=set(), current_neighbs=set(), last_move='--'):
    #     self.size = n
    #     self.board = board
        # self.board = self.init_board()

    # returns deep copy of current game board
    def copy(self):
        copy_board = Board()
        copy_board.size = self.size
        copy_board.board = list(self.board)
        copy_board.light = self.light.copy()
        copy_board.dark = self.dark.copy()
        copy_board.current_neighbs = self.current_neighbs.copy()
        copy_board.last_move = self.last_move

        return copy_board

    def set_tile(self, col, row, color):
        self.board[col][row] = color

    def get_tile(self, col, row):
        return self.board[col][row]

    def is_blank(self, col, row):
        if self.get_tile(col, row) is BLANK:
            return True
        else:
            return False

    # create a new game board, initially cleared out
    def init_board(self):
        for i in range(self.size):
            self.board.append([' '] * self.size)
        return self.board

    # clears out game board for a new game, with initial center spaces
    def init_game(self):
        # clear board
        for c in range(self.size):
            for r in range(self.size):
                self.set_tile(c, r, BLANK)

        # set up center pieces
        center_1 = self.size / 2 - 1
        center_2 = self.size / 2

        # set color on board + add to color list
        self.set_tile(center_1, center_1, LIGHT)
        self.light.add((center_1, center_1))

        self.set_tile(center_2, center_2, LIGHT)
        self.light.add((center_2, center_2))

        self.set_tile(center_1, center_2, DARK)
        self.dark.add((center_1, center_2))

        self.set_tile(center_2, center_1, DARK)
        self.dark.add((center_2, center_1))

        # add neighbors to available neighbor list
        self.update_neighbors(center_1, center_1)
        self.update_neighbors(center_2, center_2)
        self.update_neighbors(center_1, center_2)
        self.update_neighbors(center_2, center_1)

        return self.board

    # adds new neighbors to set
    def update_neighbors(self, col, row):
        # remove tile if currently in list of available neighbors
        if (col, row) in self.current_neighbs:
                self.current_neighbs.remove((col, row))
        # update neighbor list with new blank boundary tiles
        self.current_neighbs.update(self.get_boundary_list(col, row, True))

    # check move is into valid neighbor space
    def check_move(self, col, row, color):
        scores = []
        if (col, row) in self.current_neighbs:
            # check for disks in straight lines
            scores = self.check_bounds(col, row, color[0])
            self.last_move = self.display_move(col, row)
        return scores

    # checks bounds for line of bounded opponent disks
    #       +---+---+---+
    #       | 5 | 4 | 3 |
    #       +---+---+---+
    #       | 6 | X | 2 |
    #       +---+---+---+
    #       | 7 | 0 | 1 |
    #       +---+---+---+
    def check_bounds(self, col, row, b_color):
        scores = set()
        opp_color = self.get_opp_color(b_color)

        # loop through neighbors and check for valid move
        for c, r in self.get_boundary_list(col, row, False):
            move = []
            c_next = 0
            r_next = 0

            if self.get_tile(c, r) is opp_color:
                move.append((c, r))
                c_next += c - col
                r_next += r - row
                # logger.debug('appending %s' % self.display_move(c, r))
                # logger.debug('c_next, r_next %s' % self.display_move(c + c_next, r + r_next))
                # logger.debug('next tile %s, opp_color %s' % (self.get_tile(c + c_next, r + r_next), opp_color))
                # logger.debug('next tile = opp_color %s' % str(self.get_tile(c + c_next, r + r_next) is opp_color))

            while c + c_next in range(self.size) and r + r_next in range(self.size) \
                    and self.get_tile(c + c_next, r + r_next) is opp_color:
                    # and self.get_tile(c + c_next, r + r_next) is not BLANK:
                # add any tiles that need to be flipped
                # if self.get_tile(c + c_next, r + r_next) is opp_color:
                move.append((c + c_next, r + r_next))
                # logger.debug('appending %s' % self.display_move(c, r))
                c_next += c - col
                r_next += r - row
            # check that move is bounded + flipped at least 1 tile
            # logger.debug('-=c_next, -=r_next %s' % self.display_move(c + c_next - (c - col), r + r_next - (r - row)))
            # if self.get_tile(c + c_next - (c - col), r + r_next - (r - row)) is b_color and len(move) > 0:
            if c + c_next in range(self.size) and r + r_next in range(self.size) \
                    and self.get_tile(c + c_next, r + r_next) is b_color and len(move) > 0:
                # logger.debug('scores : %d' % len(scores))
                scores.update(move)

        scores = list(scores)
        scores.insert(0, (col, row))

        return scores

    # check current neighbors for best possible move
    def make_move(self, b_color):
        # best_scores = []
        # best_move = []

        # check all available tiles to place a disk + pick best move
        # for c, r in self.current_neighbs:
        #     move = self.check_bounds(c, r, b_color)
        #     if len(move) > len(best_scores):
        #         best_scores = move
        #         best_move = (c, r)

        best_move = self.get_minimax(b_color)
        # logger.debug('[ 305 ] best_scores ( %d ) :' % len(best_move))
        # self.print_list(best_move)
        self.last_move = self.display_move(best_move[0][0], best_move[0][1])

        return best_move

    # use minimax algorithm to find next best move
    def get_minimax(self, b_color):
        my_moves = []
        min_moves = []
        opp_color = self.get_opp_color(b_color)

        # find all available moves
        for c, r in self.current_neighbs:
            move = Move(b_color, self)
            move.scores = move.board.check_bounds(c, r, b_color)
            if len(move.scores) > 1:
                my_moves.append(move)

        # self.print_list(my_moves)
        # logger.debug('[ 325 ] my_moves ( %d )' % len(my_moves))
        # move_board = copy.deepcopy(self)

        # find all available opposing moves for all possible moves
        for move in my_moves:
            # update game board
            # logger.debug('[ 331 ] setting scores ( %d ) :' % len(move.scores))
            # self.print_list(move.scores)
            # move_board = copy.deepcopy(move.board)
            move.board.set_move(move.scores, move.color)
            # opp_moves = Move(opp_color, move.board)
            best_opp_move = move

            # find all possible opposing moves + add to move
            # move_board = copy.deepcopy(move.board)
            for c, r in move.board.current_neighbs.copy():
                opp_move = Move(opp_color, move.board)
                opp_move.scores = opp_move.board.check_bounds(c, r, opp_color)

                # check for valid move
                if len(opp_move.scores) > 1:
                    # opp_move.board = move.board
                    # opp_move.board.set_move(opp_move.scores, opp_color)
                    move.opp_moves.append(opp_move)
                    opp_move.score = len(opp_move.board.get_disk_list(b_color)) + len(opp_move.scores)
                    # check if move is minimum
                    if opp_move.score < best_opp_move.score:
                        best_opp_move = opp_move
            # add move to list of min opponent moves
            min_moves.append(best_opp_move)

        # look for max of mins
        max_move = min_moves[0]
        for move in min_moves:
            if len(move.board.get_disk_list(b_color)) > len(max_move.board.get_disk_list(b_color)):
                max_move = move

        # set move as last move
        # logger.debug('[ 363 ] best_move : %s' % str((max_move.scores[0][0], max_move.scores[0][1])))
        self.last_move = self.display_move(max_move.scores[0][0], max_move.scores[0][1])

        return max_move.scores

    # set move on board + update color, neighbor lists
    def set_move(self, scores, color):
        # self.display_board()
        # self.print_disks()
        for col, row in scores:
            # update board + neighbors
            # logger.debug('[ 397 ] setting %s on board : %s' % (str((col, row)), color))
            self.set_tile(col, row, color)
            # logger.debug('move  : %s,   color : %s' % (str((col, row)), color))
            # self.display_board()
            # self.print_disks()
            self.update_neighbors(col, row)

            if self.get_tile(col, row) is LIGHT:
                if self.get_tile(col, row) in self.dark:
                    self.dark.remove((col, row))
                # add to light list
                self.light.add((col, row))
            # tile is DARK
            else:
                if self.get_tile(col, row) in self.light:
                    self.light.remove((col, row))
                self.dark.add((col, row))

            # player.tiles.append((col, row))
            # if (col, row) in player.tiles and self.get_tile(col, row) is not player.color[0]:
            #     player.tiles.remove((col, row))

            # update color lists for flipped disks
            # if self.get_tile(col, row) is LIGHT:
            #     self.light.remove((col, row))
            # elif self.get_tile(col, row) is DARK:
            #     self.dark.remove((col, row))

        # return player

    # returns opposite disk color
    def get_opp_color(self, color):
        if color is LIGHT:
            return DARK
        else:
            return LIGHT

    # returns column letter from index value
    def get_col_num(self, col):
        return ord(col) - 97

    # returns integer row number from index value
    def get_row_num(self, row):
        return int(row) - 1

    # returns disk list for specified color
    def get_disk_list(self, color):
        if color is LIGHT:
            return self.light
        else:
            return self.dark

    # returns list containing coordinates for bounding tiles
    def get_boundary_list(self, col, row, blank):
        bounds = []

        if row - 1 in range(self.size) and self.is_blank(col, row - 1) is blank:
            bounds.append((col, row - 1))

        if col + 1 in range(self.size) and self.is_blank(col + 1, row) is blank:
            bounds.append((col + 1, row))

        if col + 1 in range(self.size) and row + 1 in range(self.size) \
                and self.is_blank(col + 1, row + 1) is blank:
            bounds.append((col + 1, row + 1))

        if col + 1 in range(self.size) and row - 1 in range(self.size) \
                and self.is_blank(col + 1, row - 1) is blank:
            bounds.append((col + 1, row - 1))

        if col - 1 in range(self.size) and self.is_blank(col - 1, row) is blank:
            bounds.append((col - 1, row))

        if col - 1 in range(self.size) and row + 1 in range(self.size) \
                and self.is_blank(col - 1, row + 1) is blank:
            bounds.append((col - 1, row + 1))

        if col - 1 in range(self.size) and row - 1 in range(self.size) \
                and self.is_blank(col - 1, row - 1) is blank:
            bounds.append((col - 1, row - 1))

        if row + 1 in range(self.size) and self.is_blank(col, row + 1) is blank:
            bounds.append((col, row + 1))

        return bounds

    # displays Reversi game board on screen with ASCII art
    def display_board(self):
        print '      a',
        for c in range(self.size - 1):
            print '  ' + chr(ord('b') + c),
        self.print_line()
        for r in range(self.size):
            print ' ' + str(r + 1).ljust(2) + ' |',
            for c in range(self.size):
                print self.get_tile(c, r) + ' |',
            self.print_line()
        print ''

    # prints a horizontal line of dashes + pluses
    def print_line(self):
        line = '\n    +' + '---+' * self.size
        print line[0:self.size * len(line)]

    # returns string representation of move ( ie 'a1', 'd3' )
    def display_move(self, col, row):
        return str(chr(ord('a') + col) + str(row + 1))

    # print contents of specific list, formatted for col, row
    def print_list(self, l):
        logger.debug('list contents ( %d items ) :' % len(l))
        for col, row in l:
            logger.debug(str((col, row)) + '  ' + str(chr(ord('a') + col)) + '' + str(row + 1))

    # print all disks in light + dark lists
    def print_disks(self):
        logger.debug('light : ')
        for col, row in self.light:
            logger.debug(str((col, row)) + '  ' + str(self.get_tile(col, row)))
        logger.debug('dark : ')
        for col, row in self.dark:
            logger.debug(str((col, row)) + '  ' + str(self.get_tile(col, row)))


# class to simulate Reversi player
class Player:
    color = 'Dark'
    type = 'human'
    score = 0
    tiles = []
    current_move = []

    # initialize a Player with color + type
    def __init__(self, c, t):
        self.color = c
        self.type = t


# class to represent a move on the board
class Move:
    score = 0
    scores = []
    opp_moves = []

    def __init__(self, color, current_board):
        self.color = color
        # self.board = current_board
        self.board = copy.deepcopy(current_board)
        # self.board = current_board.board
        # self.neighbs = current_board.current_neighbs
        self.light = current_board.light.copy()
        self.dark = current_board.dark.copy()
        if color is LIGHT:
            self.score = len(self.light)
        else:
            self.score = len(self.dark)



# main function to parse command line arguments and create new Reversi game
def main():

    parseargs = argparse.ArgumentParser()

    parseargs.add_argument('-v', '--version', action='version', version=VRSNSTR,
                           help='print version and author information and exit')
    parseargs.add_argument('-n', '--size', default=8, type=int,
                           help='specify board size ( even number in range 4-26, default = 8 x 8 )')
    parseargs.add_argument('-l', '--light', action='store_true',
                           help='specify to play with light colors, default is dark colors')
    args = parseargs.parse_args()

    if args.size not in range(4, 27, 2):
        exit_msg('Invalid board size : %d' % args.size)

    # create + start a new Reversi game
    game = Reversi(args.size, args.light)
    game.play()


# logs debug message and exits program
def exit_msg(msg):
    logger.debug(msg)
    sys.exit(1)


if __name__ == '__main__':
    main()
