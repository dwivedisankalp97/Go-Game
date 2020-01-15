import json
import re
import random
from sys import stdout, stdin
from board_components.board import Board
from board_components.point import Point
from board_components.rule_checker import RuleChecker
from board_components.go_player_capture import GoPlayerCapture
from board_components.go_player import GoPlayer
import socket
import contracts

config_file = open("go.config", "r")
config_data = json.loads(config_file.read())
config_file.close()
server_ip = config_data["IP"]
server_port = config_data["port"]
command_list = []

conn = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
conn.connect((server_ip, server_port))
player = GoPlayerCapture(random.randint(0, 1000))
i = 1
try:
    while 1:
        i += 1
        #print('Connection address:', addr)
        data = conn.recv(6000).decode()
        print(data)
        print(i)
        command = json.loads(data)
        if command[0] == "end-game":
            res = "OK"
        elif command[0] == "register":
            res = player.register()
        elif command[0] == "receive-stones":
            res = player.receive_stones(command[1])
        else:
            hist_boards = list(map(lambda b: Board(b), command))
            res = player.make_a_move(hist_boards)
        #print(res)#
        # if i % 15 == 0:
        #     print("reached", i)
        #     conn.send("Hello".encode())
        #     continue
        if res is not None:
            conn.send(res.encode())
        else:
            continue
except contracts.ContractException:
    conn.send("GO has gone crazy!".encode())

