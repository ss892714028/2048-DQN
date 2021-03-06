import gym
from random import randint, random
import numpy as np
from gym import spaces
import sys


class GameEnv(gym.Env):
    metadata = {'render.modes': ['human']}

    def __init__(self):
        super(GameEnv, self).__init__()

        self.action_space = spaces.Discrete(4)
        self.observation_space = spaces.Box(low=0, high=2048, shape=(4, 4, 1))
        self.board = np.zeros((4, 4), dtype=np.int)
        self.game_over = False
        self.new_board = np.zeros((4, 4), dtype=np.int)
        self.score = 0
        self.empty = 0
        self.joinable = []
        self.moved = False
        self.joined_cells = 0
        self.gained_score = 0
        self.fill_cell()

    def fill_cell(self):
        i, j = (self.board == 0).nonzero()
        if i.size != 0:
            rnd = randint(0, i.size - 1)
            self.board[i[rnd], j[rnd]] = 2 * ((random() > .9) + 1)
            self.empty = list(self.board.flatten()).count(0)

    def move_left(self, col):
        score = 0
        new_col = np.zeros((4), dtype=col.dtype)
        j = 0
        previous = None
        for i in range(col.size):
            if col[i] != 0:  # number different from zero
                if previous is None:
                    previous = col[i]
                else:
                    if previous == col[i]:
                        new_col[j] = 2 * col[i]
                        score += new_col[j]
                        j += 1
                        previous = None
                    else:
                        new_col[j] = previous
                        j += 1
                        previous = col[i]
        if previous is not None:
            new_col[j] = previous
        return new_col, score

    def move(self, direction):
        # 0: left, 1: up, 2: right, 3: down
        if direction not in [0, 1, 2, 3]:
            sys.exit("move not identified")
        rotated_board = np.rot90(self.board, direction)
        cols = [rotated_board[i, :] for i in range(4)]
        new_board = np.array([self.move_left(col)[0] for col in cols])
        score = sum([self.move_left(col)[1] for col in cols])
        return np.rot90(new_board, -direction), score

    def is_game_over(self):
        temp = []
        for i in range(4):
            temp.append((self.board == self.move(i)[0]).all())
        if False not in temp:
            self.game_over = True

    def step(self, direction):
        self.new_board = self.move(direction)[0]
        score = self.move(direction)[1]

        if (self.new_board == self.board).all():

            # move is invalid
            self.moved = False
            self.count()
        else:
            self.moved = True
            self.joined_cells = list(self.new_board.flatten()).count(0) - list(self.board.flatten()).count(0)
            self.board = self.new_board
            self.fill_cell()
            self.count()
            self.score += score
            self.gained_score = score

        if 0 not in self.board:
            self.is_game_over()
        if self.game_over:
            print(self.score)
        return self.board.reshape([4,4,1]), self.calculate_reward(), self.game_over, {}

    def count(self):

        join = []

        for i in range(4):
            moved_m = self.move(i)[0]
            join.append(list(moved_m.flatten()).count(0) - self.empty)

        self.joinable = join

    def calculate_reward(self):
        if self.moved:

            return self.gained_score * 10/self.board.mean() + np.max(self.joinable) + self.empty
        else:
            return -5

    def reset(self):
        self.board = np.zeros((4, 4), dtype=np.int)
        self.game_over = False
        self.new_board = np.zeros((4, 4), dtype=np.int)
        self.score = 0
        self.empty = 0
        self.joinable = []
        self.moved = False
        self.joined_cells = 0
        self.gained_score = 0
        self.fill_cell()
        return self.board.reshape([4,4,1])

    def render(self, mode='human', close=False):
        return self.board.reshape([4,4,1])
