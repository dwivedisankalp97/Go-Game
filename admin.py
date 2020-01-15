import json
import socket
import sys
from board_components.GUI import mywindow
from PyQt5 import QtWidgets
from PyQt5.QtWidgets import QApplication

# app = QApplication([])
app = QtWidgets.QApplication([])
a=mywindow()
# a.show()

# application = mywindow()

a.show()


command_list = sys.argv
print(command_list[1])
print("running admin")
a.update_Status("running admin")
num_of_remote_players = int(command_list[2])
config_file = open("go.config", "r")
config_data = json.loads(config_file.read())
s = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
print("socket created")
a.update_Status("socket created")
s.bind((config_data["IP"], config_data["port"]))
s.setsockopt(socket.SOL_SOCKET,socket.SO_REUSEADDR,1)
s.listen()
print("socket started listening")
connections = []
# a.update_table("1-1","b")
for i in range(num_of_remote_players):
    conn, addr = s.accept()
    QApplication.processEvents()
    print("received conn, ", i)
    a.update_Status("recieved conn"+str(i))
    connections.append(conn)

print("connections all established")
a.update_Status("connections all established")
tournament = None
if command_list[1] == "--league":
    tournament = "round-robin"
elif command_list[1] == "--cup":
    tournament = "elimination"
print("tournament type: ", tournament)

i = 1
num_of_players=0
while 2**i < num_of_remote_players:i += 1
num_of_players = 2**i
num_of_default_players = num_of_players - num_of_remote_players
print("num_of_players: ", num_of_players)
print("num_of_remote_players: ", num_of_remote_players)
print("num_of_default_players: ", num_of_default_players)



from board_components.go_player_capture import GoPlayerCapture
from board_components.player_proxy import GoPlayerCaptureProxy
from board_components.referee import Referee
from board_components.player_contract_check import PlayerContractCheck
import importlib.util
import math 
import random


players = []
scores = {}
ranks = []

config_file.close()
path_to_default_player = config_data["default-player"]
spec = importlib.util.spec_from_file_location("", path_to_default_player)
foo = importlib.util.module_from_spec(spec)
spec.loader.exec_module(foo)

for i in range(num_of_default_players):
    local_player = foo.GoPlayer(i)
    local_player_contract = PlayerContractCheck(local_player)
    name = local_player_contract.register()
    players.append((name, local_player_contract))
    scores[name] = 0
    
    next_default_idx = num_of_default_players

for conn in connections:
    remote_player = GoPlayerCaptureProxy(conn)
    remote_player_contract = PlayerContractCheck(remote_player)
    name = remote_player_contract.register()
    if name!="dropped connection": 
        players.append((name, remote_player_contract))
    else:
        print("local player added")
        local_player = foo.GoPlayer(next_default_idx)
        next_default_idx += 1
        local_player_contract = PlayerContractCheck(local_player)
        name = local_player_contract.register()
        players.append((name, local_player_contract))
    scores[name] = 0

for i in range(0,num_of_players):
    print(players[i][0])
a.reset_table()

def play_one_game(player1_idx, player2_idx):
    player1_name, player1 = players[player1_idx]
    player2_name, player2 = players[player2_idx]
    finished = False
    a.reset_table()
    print("playing game btw", player1_name, player2_name)
    curr_play=player1_name+" "+player2_name
    a.update_curr_players(curr_play)
    ref = Referee()
    stone1 = ref.register(player1_name)
    stone2 = ref.register(player2_name)
    res1=player1.receive_stones(stone1)
    res2=player2.receive_stones(stone2)
    # dealt with dropped connection / illegal responses from receive_stones
    if res1!= None:
        winner, cheater = [player2_name], [player1_name]
        finished = True
    elif res2 != None:
        winner, cheater = [player1_name], [player2_name]
        finished = True
    current_player = player1
    if not finished:
        while not ref.game_end :
            move = current_player.make_a_move(ref.get_board_hist())
            a.update_player(current_player.player.name)
            a.update_move(move)
            print(current_player.player.name, "move: ", move)
            # a.update_table(move,ref.current_player)
            hist=ref.get_board_hist()
            a.set_table(hist[0].get_board_repr())
            # print(ref.current_player)
            ref.make_a_move(move)
            if current_player == player1:
                current_player = player2
            else:
                current_player = player1

        winner = ref.get_winner()
        cheater = ref.get_cheater()
    player1.end_game()
    player2.end_game()
    # a.onClick2(winner)
    print("winner", winner)
    a.update_winner(winner)
    print("cheater",cheater)
    return winner, cheater

a.update_mode(tournament)

if tournament == "round-robin":
    games_played = []
    cheaters = []
    for i in range(num_of_players):
        for j in range(i+1, num_of_players):
            a.update_total_player(players)
            winner, cheater = play_one_game(i, j)
            for player_name in winner:
                scores[player_name] += 1
            if cheater: 
                local_player = foo.GoPlayer(next_default_idx)
                local_player_contract = PlayerContractCheck(local_player)
                name = local_player_contract.register()
                scores[name] = 0
                next_default_idx += 1

                if cheater[0] == players[i][0]:
                    cheater_idx = i
                    players[i] = (name, local_player_contract)
                elif cheater[0] == players[j][0]: 
                    cheater_idx = j
                    players[j] = (name, local_player_contract)
                if scores[cheater[0]] > 0:
                    # updating the scores for the cheater's previous opponents
                    for x, y, winner in games_played:
                        if cheater[0] in winner and len(winner) == 1:
                            # make sure the cheater is not trying to give back scores to an already deleted cheater
                            if cheater_idx==x and players[y][0] in scores:
                                scores[players[y][0]] += 1
                            elif cheater_idx == y and players[x][0] in scores:
                                scores[players[x][0]] += 1
                cheaters.append(cheater[0])
                del scores[cheater[0]]    
            else: 
                games_played.append((i, j, winner))
    cur_score, cur_rank, num_of_same_score = -1, 0, 1
    for k,v in sorted(scores.items(), key=lambda x: x[1], reverse=True):
        if cur_score!= v:
            cur_score = v
            cur_rank+=num_of_same_score
            num_of_same_score = 1
        else: 
            num_of_same_score+=1
        ranks.append(str(cur_rank)+": "+k)
    for cheater in cheaters:
        ranks.append(str(num_of_players+1)+"(cheater): "+cheater)

elif tournament == "elimination":
    alive_player_index = [i for i in range(num_of_players)]
    cur_rank = int(num_of_players/2+1)
    for i_round in range(int(math.sqrt(num_of_players))):
        # print(alive_player_index)
        # num_of_alive_players = num_of_players/(i_round+1)
        new_alive_player_idx = []
        for j in range(0, len(alive_player_index), 2):
            a.update_total_player(players)
            idx1, idx2 = alive_player_index[j], alive_player_index[j+1]
            winner, cheater = play_one_game(idx1, idx2)
            if len(winner) == 2:
                if random.randint(0, 1) < 0.5: 
                    ranks.insert(0, str(cur_rank)+": "+players[idx1][0])
                    new_alive_player_idx.append(idx2)
                else:
                    ranks.insert(0, str(cur_rank)+": "+players[idx2][0])
                    new_alive_player_idx.append(idx1)
            elif len(winner) == 1:
                if winner[0] == players[idx2][0]:
                    ranks.insert(0, str(cur_rank)+": "+players[idx1][0])
                    new_alive_player_idx.append(idx2)
                elif winner[0] == players[idx1][0]:
                    ranks.insert(0, str(cur_rank)+": "+players[idx2][0])
                    new_alive_player_idx.append(idx1)
        cur_rank = int(len(new_alive_player_idx)/2+1)
        alive_player_index = new_alive_player_idx
    ranks.insert(0, str(1)+": "+ players[alive_player_index[0]][0])

print("Final Ranking")
# a.onClick3(ranks)
for i in ranks:
    print(i)

a.update_ranks(ranks)
s.close()
if not a.closed:
    sys.exit(app.exec())
# sys.exit(app.exec_())





