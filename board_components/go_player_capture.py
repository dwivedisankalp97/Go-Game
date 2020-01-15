from abc import abstractmethod
import contracts
from contracts import contract, ContractsMeta, with_metaclass,new_contract
from board_components.point import Point
from board_components.board import Board
from board_components.rule_checker import RuleChecker
from board_components.definitions import MIN_HIST_LENGTH, MAX_HIST_LENGTH, BOARD_SIZE_X, BOARD_SIZE_Y, PLAYER_NAME, \
    STONES, EMPTY_STONE, REMOTE_PLAYER_NAME
import functools
import json

class GoPlayerCaptureInterface(with_metaclass(ContractsMeta, object)):
    @abstractmethod
    @contract(returns='str')
    def register(self):
        """
            should reply with the name "no name" of the player.
        """
        pass

    new_contract('valid_ret', lambda s: isinstance(s, str) or s is None)
    new_contract('valid_stone', lambda s: s in STONES)
    @abstractmethod
    @contract(s='valid_stone', returns='valid_ret')
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

    @abstractmethod
    @contract(hist='list[>=$MIN_HIST_LENGTH,<=$MAX_HIST_LENGTH]($Board)', n='int', other_player_move='$Point', returns='bool')
    def move_sequence_possible(self, hist, n, other_player_move):
        """
            Checks if other_player_move is a viable move, if so, proceed to call make_a_move to find the other n-1 moves.
            Overall, returns true or false whether n moves is capable of capturing pieces.
        """
        pass


######## Implementation below ########
f = open("go-player.config")
g = json.loads(f.read())
depth = g["depth"]
f.close()


class GoPlayerCapture(GoPlayerCaptureInterface):
    def __init__(self, i):
        self.name = REMOTE_PLAYER_NAME+"-"+str(i)
        self.stone = None
        self.other_player = None
        self.ai_used_flag = False
        self.rc = RuleChecker()


    ## private helpers
    def __remove_duplicates(self, list_of_points):
        return list(dict.fromkeys(list_of_points))

    def register(self):
        return self.name

    def receive_stones(self, s):
        self.stone = s
        if s == "B":
            self.other_player = "W"
        else:
            self.other_player = "B"

    def move_sequence_possible(self, hist, n, other_player_move):
        if n == 0:
            return True
        # if the other_player can't move to the given point he will pass
        if self.rc.move_play(self.other_player, other_player_move, hist):
            temp_board = self.rc.place_and_remove(self.other_player, other_player_move, hist[0])
            hist[2] = hist[1]
            hist[1] = hist[0]
            hist[0] = temp_board
            # print("n in move_seq ",n)
            self.make_a_move(hist, n)
            if self.ai_used_flag:
                return True
        # print("return False")
        return False

    def make_a_move(self, hist, n = depth):
        if not self.rc.verify_history_jr(hist, self.stone):
            return "This history makes no sense!"
            
        recent_board = hist[0].get_board_repr()
        other_player_points = hist[0].get_points_without_sort(self.other_player)
        # loop boards by column then row
        possible_move_list = []
        for p in other_player_points:
            pp = Point(p)
            liberty_list = hist[0].reachable_bfs(pp, EMPTY_STONE)
            liberty_list = self.__remove_duplicates(liberty_list)
            count = len(liberty_list)
            if count == n:
                for l in liberty_list:
                    if self.rc.move_play(self.stone, l, hist):
                        if n == 1:
                            possible_move_list.append(l)
                        else:
                            temp_board = self.rc.place_and_remove(self.stone, l, hist[0])
                            new_hist = [temp_board, hist[0], hist[1]]
                            temp_list = list(x for x in liberty_list if x != l)
                            #print("temp_list", list(map(lambda s: s.get_point_repr(), temp_list)))
                            if any(list(map(lambda other_player_move:
                                            self.move_sequence_possible(new_hist, n - 1, other_player_move),
                                            temp_list))):
                                possible_move_list.append(l)

        if not len(possible_move_list) == 0:
            def point_sort(p1, p2):
                if p1.y > p2.y:
                    return 1
                elif p1.y < p2.y:
                    return -1
                elif p1.y == p2.y:
                    if p1.x > p2.x:
                        return 1
                    elif p1.x < p2.x:
                        return -1
                    else:
                        return 0
            possible_move_list = sorted(possible_move_list, key=functools.cmp_to_key(point_sort))
            self.ai_used_flag = True
            #print(list(map(lambda s:s.get_point_repr(),possible_move_list)))
            #possible_move_list = remove_duplicates(possible_move_list)
            return possible_move_list[0].get_point_repr()

        self.ai_used_flag = False
        for i in range(BOARD_SIZE_X):
            for j in range(BOARD_SIZE_Y):
                pos = Point("{}-{}".format(i + 1, j + 1))
                if recent_board[j][i] == EMPTY_STONE and self.rc.move_play(self.stone, pos, hist):
                    return pos.get_point_repr()

        return "pass"

    def end_game(self):
        return "OK"
