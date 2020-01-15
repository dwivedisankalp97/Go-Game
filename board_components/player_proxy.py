import os
from abc import abstractmethod
import contracts
import json
from contracts import contract, ContractsMeta, with_metaclass
from board_components.point import Point
from board_components.board import Board
from board_components.rule_checker import RuleChecker
from board_components.definitions import MIN_HIST_LENGTH, MAX_HIST_LENGTH, BOARD_SIZE_X, BOARD_SIZE_Y, PLAYER_NAME, \
    STONES, EMPTY_STONE, REMOTE_PLAYER_NAME
import functools
import socket


class GoPlayerCaptureInterface(with_metaclass(ContractsMeta, object)):
    @abstractmethod
    @contract(returns='str')
    def register(self):
        """
            should reply with the name "no name" of the player.
        """
        pass

    @abstractmethod
    @contract(s='str', returns='valid_ret')
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


class GoPlayerCaptureProxy(GoPlayerCaptureInterface):
    def __init__(self,conn):
        self.name = REMOTE_PLAYER_NAME
        self.conn = conn

    ## private helpers
    def send_receive_message(self, message):
        try:
            self.conn.send(message.encode())
            data = self.conn.recv(6000).decode()
            if data=="":
                raise Exception("connection error")
            return data
        except :
            print("dropped",self.name)
            return "dropped connection"


    def register(self):
        self.name = self.send_receive_message('["register"]')
        return self.name


    def receive_stones(self, s):
        send_message_str = '["receive-stones", ' + '"{}"'.format(s) + ']'
        try:
            self.conn.send(send_message_str.encode())
        except:
            print("dropped in receive")
            return "dropped connection"

    def make_a_move(self, hist, n=1):
        return self.send_receive_message(json.dumps(list(map(lambda b: b.get_board_repr(), hist))))

    def end_game(self):
        return self.send_receive_message(json.dumps(["end-game"]))

