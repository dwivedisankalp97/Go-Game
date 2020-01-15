from abc import abstractmethod
import contracts
from contracts import contract, ContractsMeta, with_metaclass
from board_components.point import Point
from board_components.board import Board
from board_components.rule_checker import RuleChecker
from board_components.go_player import GoPlayer
from board_components.definitions import MIN_HIST_LENGTH, MAX_HIST_LENGTH, BOARD_SIZE_X, BOARD_SIZE_Y, PLAYER_NAME, \
    STONES, EMPTY_STONE, EMPTY_BOARD
import functools


class RefereeInterface(with_metaclass(ContractsMeta, object)):
    @abstractmethod
    @contract(returns='bool')
    def check_game_end(self):
        """
        Returns true if the game has ended else false
        """
        pass

    @abstractmethod
    @contract(returns='list[>=$MIN_HIST_LENGTH,<=$MAX_HIST_LENGTH]($Board)')
    def get_board_hist(self):
        """
        Returns the current history of the board basis the moves played
        """
        pass

    @abstractmethod
    @contract(returns='list[>=1,<=2](str)')
    def get_winner(self):
        """
        Returns the winner of the game.
        In case of a tied game return the list of both the players.
        """
        pass

    @abstractmethod
    @contract(returns='list[>=0,<=1](str)')
    def get_cheater(self):
        """
        Returns the cheater of the game if there is any.
        """
        pass

    @abstractmethod
    @contract(name='str', returns='str')
    def register(self, name):
        """
        Register the player and return the corresponding stone.
        In case of more than two register requests ,return error string.
        """
        pass

    @abstractmethod
    @contract(returns='None')
    def next_player(self):
        """
        Sets the corresponding next player as the current player
        """
        pass

    @abstractmethod
    @contract(board='$Board', returns='None')
    def ready_next_turn(self, board):
        """
        Adds the latest board to the list of boards based on the move played by the player
        """
        pass

    @abstractmethod
    @contract(move='str', returns='None')
    def make_a_move(self, move):
        """

        """
        pass

# Implementation

class Referee(RefereeInterface):
    def __init__(self):
        self.player_b = None
        self.player_w = None
        self.board_hist = [Board(EMPTY_BOARD)]
        self.current_player = "B"
        self.prev_move = None
        self.rc = RuleChecker()
        self.game_end = False
        self.winner = []
        self.cheater = []
        self.current_move = None

    def check_game_end(self):
        return self.game_end

    def get_board_hist(self):
        return self.board_hist

    def get_winner(self):
        return self.winner
    
    def get_cheater(self):
        return self.cheater

    def register(self, name):
        if self.player_b is None:
            self.player_b = name
            return "B"
        elif self.player_w is None:
            self.player_w = name
            return "W"
        else:
            "Only two players allowed!"

    def next_player(self):
        if self.current_player == "B":
            self.current_player = "W"
        else:
            self.current_player = "B"

    def ready_next_turn(self, board):
        self.board_hist.insert(0, board)
        if len(self.board_hist) > 3:
            self.board_hist.pop(3)
        self.prev_move = self.current_move
        self.next_player()

    def make_a_move(self, move):
        if self.player_b is None or self.player_w is None:
            return "GO has gone crazy!"
        self.current_move = move
        if move == 'pass':
            if self.prev_move == 'pass':
                score = self.rc.count_score(self.board_hist[0])
                if score["B"] > score["W"]:
                    self.winner = [self.player_b]
                elif score["W"] > score["B"]:
                    self.winner = [self.player_w]
                else:
                    self.winner = sorted([self.player_w, self.player_b])
                self.game_end = True
            self.ready_next_turn(self.board_hist[0])
            #return list(map(lambda s: s.get_board_repr(), self.board_hist))
        else:
            try:
                pp = Point(move)
                if self.rc.move_play(self.current_player, pp, self.board_hist):
                    new_board = self.rc.place_and_remove(self.current_player, pp, self.board_hist[0])
                    self.ready_next_turn(new_board)
                    #return list(map(lambda s: s.get_board_repr(), self.board_hist))
                else:
                    if self.current_player == "B":
                        self.winner = [self.player_w]
                        self.cheater = [self.player_b]
                    else:
                        self.winner = [self.player_b]
                        self.cheater = [self.player_w]
                    self.game_end = True
            except:
                if self.current_player == "B":
                    self.winner = [self.player_w]
                    self.cheater = [self.player_b]
                else:
                    self.winner = [self.player_b]
                    self.cheater = [self.player_w]
                self.game_end = True
