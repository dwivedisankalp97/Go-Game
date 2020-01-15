import json
import re
from sys import stdout, stdin
import contracts
from contracts import check
from board_components.board import Board
from board_components.definitions import MIN_HIST_LENGTH, MAX_HIST_LENGTH,\
    STONES, EMPTY_STONE, ERROR_MESSAGE

class PlayerContractCheck():

    def __init__(self, player):
        self.player = player
        self.registered = False
        self.received = False

    def register(self):
        if self.registered:
            return "Player not registered contract check"
        self.registered = True
        return self.player.register()

    def receive_stones(self, s):
        if self.received or not self.registered:
            return "Receive stones error contract check"
        self.received = True
        # check if s is a stone
        assert s in STONES, "Stone given is not valid!"
        return self.player.receive_stones(s)


    def make_a_move(self, hist_boards):
        if not self.received or not self.registered:
            return "Make a move error flags"
        try:
            check('list[>=$MIN_HIST_LENGTH,<=$MAX_HIST_LENGTH]($Board)', hist_boards)
            if not all(map(lambda b: b.repr, hist_boards)):
                return ERROR_MESSAGE
            return self.player.make_a_move(hist_boards)
        except contracts.ContractException as e:
            return "Make a move error contract check"

    def end_game(self):
        self.received = False
        return self.player.end_game()
