import arcade
import game_core
import threading
import time
import os
import pygame
import math
import queue
import numpy


class Agent(threading.Thread):

    def __init__(self, threadID, name, counter, show_grid_info=True):
        threading.Thread.__init__(self)
        self.threadID = threadID
        self.name = name
        self.counter = counter
        self.show_grid_info = show_grid_info

        self.game = []
        self.move_grid = []
        self.kill_grid = []
        self.isGameClear = False
        self.isGameOver = False
        self.current_stage = 0
        self.time_limit = 0
        self.total_score = 0
        self.total_time = 0
        self.total_life = 0
        self.tanuki_r = 0
        self.tanuki_c = 0

    #############################################################
    #      YOUR SUPER COOL ARTIFICIAL INTELLIGENCE HERE!!!      #
    #############################################################

        self.has_path = False
        self.curr_path = None

    def ai_function(self):
        def find_goals(grid):
            row_count = numpy.size(self.move_grid, 0)
            col_count = numpy.size(self.move_grid, 1)
            goals = []
            for row in range(row_count):
                for col in range(col_count):
                    if self.move_grid[row][col] == "#" or self.move_grid[row][col] == "a" or self.move_grid[row]:
                        goals.append((row, col))
            return goals


        def heuristic(curr_row, curr_col, goal_row, goal_col):
            return math.sqrt((curr_row - goal_row) ** 2 + (curr_col - goal_col) ** 2)

        def a_star(move_grid, cur_r, cur_c, target):
            row_count = numpy.size(move_grid, 0)
            col_count = numpy.size(move_grid, 1)

            visited = numpy.zeros_like(move_grid)
            parent = numpy.zeros_like(move_grid)

            dist_so_far = 0
            path_to_goal = None
            distance_to_goal = 0

            this_queue = queue.Queue()
            this_queue_item = None
            this_r = cur_r
            this_c = cur_c
            path_exists = False
            i = 0

            visited[this_r][this_c] = 1
            this_queue.put((this_r, this_c))

            while not this_queue.empty():
                this_queue_item = this_queue.get()
                this_r = this_queue_item[0]
                this_c = this_queue_item[1]
                # print(f"({this_r:02d},{this_c:02d}) = {move_grid[this_r][this_c]:d}")

                # if current cell is the target
                if move_grid[this_r][this_c] == target:
                    path_exists = True
                    break

                # if current cell = 0
                elif move_grid[this_r][this_c] == 0:

                    # queue left cell
                    if (this_c > 0 and visited[this_r][this_c - 1] == 0 and
                            allowed_cell(move_grid, this_r, this_c - 1)):
                        visited[this_r][this_c - 1] = 1
                        parent[this_r][this_c - 1] = 2
                        this_queue.put((this_r, this_c - 1))

                # if current cell = 1
                elif move_grid[this_r][this_c] == 1:

                    # queue some cells only if cell below is 4 or 6
                    if (this_r < numpy.size(move_grid, 0) - 1 and
                            (move_grid[this_r + 1][this_c] == 4 or move_grid[this_r + 1][this_c] == 6)):

                        # queue left cell
                        if (this_c > 0 and visited[this_r][this_c - 1] == 0 and
                                allowed_cell(move_grid, this_r, this_c - 1)):
                            visited[this_r][this_c - 1] = 1
                            parent[this_r][this_c - 1] = 2
                            this_queue.put((this_r, this_c - 1))

                        # queue right cell
                        if (this_c < numpy.size(move_grid, 1) - 1 and visited[this_r][this_c + 1] == 0 and
                                allowed_cell(move_grid, this_r, this_c + 1)):
                            visited[this_r][this_c + 1] = 1
                            parent[this_r][this_c + 1] = 4
                            this_queue.put((this_r, this_c + 1))

                        # queue cell below if it is 6
                        if visited[this_r + 1][this_c] == 0 and move_grid[this_r + 1][this_c] == 6:
                            visited[this_r + 1][this_c] = 1
                            parent[this_r + 1][this_c] = 1
                            this_queue.put((this_r + 1, this_c))

                # if current cell = 6
                elif move_grid[this_r][this_c] == 6:

                    # queue cell above
                    if (this_r > 0 and visited[this_r - 1][this_c] == 0 and
                            allowed_cell(move_grid, this_r - 1, this_c)):
                        visited[this_r - 1][this_c] = 1
                        parent[this_r - 1][this_c] = 3
                        this_queue.put((this_r - 1, this_c))

                    if this_r < numpy.size(move_grid, 0) - 1:

                        # queue cell below
                        if (visited[this_r + 1][this_c] == 0 and
                                allowed_cell(move_grid, this_r + 1, this_c)):
                            visited[this_r + 1][this_c] = 1
                            parent[this_r + 1][this_c] = 1
                            this_queue.put((this_r + 1, this_c))

                        # queue left and right cells also if cell below = 4
                        if move_grid[this_r + 1][this_c] == 4:

                            if (this_c > 0 and visited[this_r][this_c - 1] == 0 and
                                    allowed_cell(move_grid, this_r, this_c - 1)):
                                visited[this_r][this_c - 1] = 1
                                parent[this_r][this_c - 1] = 2
                                this_queue.put((this_r, this_c - 1))

                            if (this_c < numpy.size(move_grid, 1) - 1 and visited[this_r][this_c + 1] == 0 and
                                    allowed_cell(move_grid, this_r, this_c + 1)):
                                visited[this_r][this_c + 1] = 1
                                parent[this_r][this_c + 1] = 4
                                this_queue.put((this_r, this_c + 1))

            # begin backtrack
            if path_exists:
                while this_r != cur_r or this_c != cur_c:
                    path_to_goal.insert(0, (this_r, this_c))
                    distance_to_goal += 1

                    if parent[this_r][this_c] == 1:
                        this_r -= 1
                    elif parent[this_r][this_c] == 2:
                        this_c += 1
                    elif parent[this_r][this_c] == 3:
                        this_r += 1
                    elif parent[this_r][this_c] == 4:
                        this_c -= 1

                path_to_goal.insert(0, (this_r, this_c))

            return (path_to_goal, distance_to_goal)

        def allowed_cell(move_grid, this_r, this_c):
            unallowed = {0, 4}

            for unallowed_cell in unallowed:
                if move_grid[this_r][this_c] == unallowed_cell:
                    return False
            return True

        def check_for_safety():
            # check for enemies, gap, ladder, spikes...
            pass
            return

        """if (not self.has_path):
            this_goal_dist = 0
            this_goal_path = None
            closest_goal_dist = 0
            closest_goal_path = None
            
            for goal in find_goals(self.move_grid):
                this_goal_path, this_goal_dist = a_star(self.move_grid, self.tanuki_r, self.tanuki_c, goal)
                if (this_goal_dist < closest_goal_dist):
                    closest_goal_dist = this_goal_dist
                    closest_goal_path = this_goal_path

            curr_path = closest_goal_path
            print(curr_path)

        else:
            # move.
            # To send a key stroke to the game, use self.game.on_key_press() method
            if self.move_grid[self.tanuki_r][self.tanuki_c] == 6:
                self.game.on_key_press(arcade.key.UP, None)
            else:
                self.game.on_key_press(arcade.key.LEFT, None)"""
        return

    def run(self):
        print("Starting " + self.name)

        os.environ['SDL_VIDEO_WINDOW_POS'] = "%d,%d" % (50+320, 50)
#        if self.show_grid_info:
        pygame.init()
#        else:
#            pygame = []

        # Prepare grid information display (can be turned off if performance issue exists)
        if self.show_grid_info:
            screen_size = [200, 120]
            backscreen_size = [40, 12]

            screen = pygame.display.set_mode(screen_size)
            backscreen = pygame.Surface(backscreen_size)
            arr = pygame.PixelArray(backscreen)
        else:
            time.sleep(0.5)  # wait briefly so that main game can get ready

        # roughly every 50 milliseconds, retrieve game state (average human response time for visual stimuli = 25 ms)
        go = True
        while go and (self.game is not []):
            # Dispatch events from pygame window event queue
            if self.show_grid_info:
                for event in pygame.event.get():
                    if event.type == pygame.QUIT:
                        go = False
                        break

            # RETRIEVE CURRENT GAME STATE
            self.move_grid, self.kill_grid, \
                self.isGameClear, self.isGameOver, self.current_stage, self.time_limit, \
                self.total_score, self.total_time, self.total_life, self.tanuki_r, self.tanuki_c \
                = self.game.get_game_state()

            self.ai_function()

            # Display grid information (can be turned off if performance issue exists)
            if self.show_grid_info:
                for row in range(12):
                    for col in range(20):
                        c = self.move_grid[row][col] * 255 / 12
                        arr[col, row] = (c, c, c)
                    for col in range(20, 40):
                        if self.kill_grid[row][col-20]:
                            arr[col, row] = (255, 0, 0)
                        else:
                            arr[col, row] = (255, 255, 255)

                pygame.transform.scale(backscreen, screen_size, screen)
                pygame.display.flip()

            # We must allow enough CPU time for the main game application
            # Polling interval can be reduced if you don't display the grid information
            time.sleep(0.05)

        print("Exiting " + self.name)


def main():
    ag = Agent(1, "My Agent", 1, True)
    ag.start()

    ag.game = game_core.GameMain()
    ag.game.isDisableEnemy = True
    ag.game.set_location(50, 50)

    # Uncomment below for recording
    # ag.game.isRecording = True
    # ag.game.replay('replay.rpy')  # You can specify replay file name or it will be generated using timestamp

    # Uncomment below to replay recorded play
    # ag.game.isReplaying = True
    # ag.game.replay('replay.rpy')

    ag.game.reset()
    arcade.run()


if __name__ == "__main__":
    main()