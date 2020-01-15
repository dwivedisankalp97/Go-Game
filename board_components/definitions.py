# Stone definitions
BLACK_STONE = "B"
WHITE_STONE = "W"
EMPTY_STONE = " "
POINT_REGEX = r'^[0-9]{1}-[0-9]{1}$' # 9-9
#POINT_REGEX = r'^[0-9]?[0-9]-[0-9]?[0-9]$'

# Stone groups
MAYBE_STONES = ["B", "W", " "]
STONES = ["B", "W"]

# Board constraints
BOARD_SIZE_X = 9
BOARD_SIZE_Y = 9

# Rule constraints
MIN_HIST_LENGTH = 1
MAX_HIST_LENGTH = 3
MAX_SCORE = 9*9

# Player constants
PLAYER_NAME = "local-player"
REMOTE_PLAYER_NAME = "remote-player"

EMPTY_BOARD = [[" "," "," "," "," "," "," "," "," "],
[" "," "," "," "," "," "," "," "," "],
[" "," "," "," "," "," "," "," "," "],
[" "," "," "," "," "," "," "," "," "],
[" "," "," "," "," "," "," "," "," "],
[" "," "," "," "," "," "," "," "," "],
[" "," "," "," "," "," "," "," "," "],
[" "," "," "," "," "," "," "," "," "],
[" "," "," "," "," "," "," "," "," "]]

# Illegal order of moves
ERROR_MESSAGE = "GO has gone crazy!"
