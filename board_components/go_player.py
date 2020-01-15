from abc import abstractmethod
import contracts
import random
from contracts import contract, ContractsMeta, with_metaclass
from board_components.point import Point
from board_components.board import Board
from board_components.rule_checker import RuleChecker
from board_components.definitions import MIN_HIST_LENGTH, MAX_HIST_LENGTH, BOARD_SIZE_X, BOARD_SIZE_Y, PLAYER_NAME, \
    STONES, EMPTY_STONE

class GoPlayerInterface(with_metaclass(ContractsMeta, object)):
    @abstractmethod
    @contract(returns='str')
    def register(self):
        """
            should reply with the name "no name" of the player.
        """
        pass

    @abstractmethod
    @contract(s='str', returns='None')
    def receive_stones(self, s):
        """
            set the internal state of the registered player to start a game playing as the player with the given Stone
        """
        pass

    @abstractmethod
    @contract(hist='list[>=$MIN_HIST_LENGTH,<=$MAX_HIST_LENGTH]($Board)', returns='str')
    def make_a_move(self, hist):
        """
            If hist is valid, replies with Point that is a a legal placement for the player’ s Stone taking into account Boards
            and selecting for smallest col index followed by row index
        """
        pass

######## Implementation below ########

class GoPlayer(GoPlayerInterface):
    def __init__(self, i):
        self.name = PLAYER_NAME+"-"+str(i)
        self.stone = None
        self.rc = RuleChecker()

    def register(self):
        return self.name

    def receive_stones(self, s):
        self.stone = s
    
    def make_a_move(self, hist):
        if not self.rc.verify_history_jr(hist, self.stone):
            return "This history makes no sense!"
        recent_board = hist[0].get_board_repr()
        random_num = random.random()
        # return "2-1"
        # make a valid move
        if random_num < 1:
            # loop boards by column then row
            for i in range(BOARD_SIZE_X):
                for j in range(BOARD_SIZE_Y):
                    pos = Point("{}-{}".format(i+1, j+1))
                    if recent_board[j][i] == EMPTY_STONE and self.rc.move_play(self.stone, pos, hist):
                        return pos.get_point_repr()
        # make a move at a non-valid position
        elif random_num <0.75:
            # loop boards by column then row
            for i in range(BOARD_SIZE_X):
                for j in range(BOARD_SIZE_Y):
                    pos = Point("{}-{}".format(i+1, j+1))
                    if recent_board[j][i] == EMPTY_STONE and not self.rc.move_play(self.stone, pos, hist):
                        return pos.get_point_repr()
        # make a move of the wrong format 
        elif random_num <0.8:
            return  "{}{}".format(3, 3)
        # make an non-valid move that's out of the board's range
        elif random_num <0.9:
            return  "{}-{}".format(20, 20)
        # pass
        return "pass"

    def end_game(self):
        self.stone = None
        return "OK"

