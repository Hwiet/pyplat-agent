import arcade
import game_core
import threading
import time
import os
import pygame
import math
import heapq
import numpy

ROW_COUNT = 12
COL_COUNT = 20

UP = 1
DOWN = 2
RIGHT = 3
LEFT = 4
SPACE = 5

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
        self.previous_move = ''
        self.previous_jump = True

    #############################################################
    #      YOUR SUPER COOL ARTIFICIAL INTELLIGENCE HERE!!!      #
    #############################################################

        self.path = []
        self.next_goal = None
        self.searches = 0
        self.going_for_ladder = False

    def ai_function(self):

        class PriorityQueue():
            """A barebones queue prioritizing minimum values (minimum according to function 'func')."""

            def __init__(self, func=lambda x: x):
                self.heap = []
                self.func = func

            def push(self, item):
                """Push an item into the correct position."""
                heapq.heappush(self.heap, (self.func(item), item))

            def pop(self):
                """Pop and return the smallest item in the queue."""
                if self.heap:
                    return heapq.heappop(self.heap)[1]
                else:
                    return None

            def is_empty(self):
                return not bool(len(self.heap))

            def __len__(self):
                """Return current capacity of PriorityQueue."""
                return len(self.heap)

            def __contains__(self, key):
                """Return True if the key is in PriorityQueue."""
                return any([item == key for _, item in self.heap])

            def __getitem__(self, key):
                """Returns the first value associated with key in PriorityQueue.
                Raises KeyError if key is not present."""
                for value, item in self.heap:
                    if item == key:
                        return value
                raise KeyError(str(key) + " is not in the priority queue")

            def __delitem__(self, key):
                """Delete the first occurrence of key."""
                try:
                    del self.heap[[item == key for _, item in self.heap].index(True)]
                except ValueError:
                    raise KeyError(str(key) + " is not in the priority queue")
                heapq.heapify(self.heap)


        def heuristic(row1, col1, row2, col2):
            return math.sqrt((row1 - row2) ** 2 + (col1 - col2) ** 2)


        def within_bounds(row, col):
            """Determine whether the coordinates are within the bounds of the grid."""
            return 0 <= row < ROW_COUNT and 0 <= col < COL_COUNT


        def occupiable(row, col):
            return not (self.move_grid[row][col] == 7 and self.game.floor_below_me(row, col))


        def is_goal(row, col, terminals=[8, 9, 10, 11]):
            return self.move_grid[row][col] in terminals


        def is_mid_ladder(row, col):
            return self.move_grid[row][col] == 6 and not self.game.floor_below_me(row, col, True)


        def is_enemy(row, col):
            for enemy in self.game.enemy_list:
                if enemy.gridR == row and enemy.gridC == col and enemy.isActive:
                    return True
            return False


        def dist_enemy(row, col):
            """Return tanuki's distance (a positive distance) from an enemy if it is in the
            same row as tanuki. Return 999 if the current row is free of enemies."""
            for enemy in self.game.enemy_list:
                if enemy.gridR == row and enemy.isActive:
                    return abs(col - enemy.gridC)
            return 999


        def is_enemy_coming(row, col):
            """Determine if enemy is going toward or away from tanuki. Assumes that there
            is a max of only one enemy per row."""
            for enemy in self.game.enemy_list:
                if enemy.gridR == row and enemy.isActive:
                    return ((col <= enemy.gridC and enemy.isGoingLeft) or
                        (enemy.gridC <= col and not enemy.isGoingLeft))
            return False


        def astar_search(row, col, is_terminal=is_goal):
            class Node():
                """Encapsulate info about a node of an A* search tree."""
                def __init__(self, row, col, path_cost=0, parent=None):
                    self.row = row
                    self.col = col
                    self.path_cost = path_cost
                    self.parent = parent

                def __lt__(self, node):
                    # Required to define '<' operator between two nodes in priority queue.
                    return self.row + self.col < node.row + node.col

                def __eq__(self, other):
                    # Two nodes are considered to be equal if they have the same coordinates.
                    return isinstance(other, Node) and self.row == other.row and self.col == other.col

                def __hash__(self):
                    # hash the coordinate stored in the node instead of the node object itself to quickly search a node with the same state
                    return hash((self.row, self.col))

            def at_node(row, col):
                return (is_terminal(row, col) or
                    # target
                    self.move_grid[row][col] == 6 or
                    # bottom of a ladder
                    (self.move_grid[row+1][col] == 6 and (self.move_grid[row][col] == 1 or is_terminal(row, col))))
                    # top of a ladder

            def seek_node(cur_node, direction):
                cur_row = cur_node.row
                cur_col = cur_node.col
                new_path_cost = 0
                if direction == UP:
                    if self.move_grid[cur_row][cur_col] != 6:
                        return None # abort, no node exists in this direction
                    while self.move_grid[cur_row][cur_col] == 6:
                        if (not within_bounds(cur_row-1, cur_col) or
                            is_enemy(cur_row-1, cur_col)):
                            return None # abort, no node exists in this direction
                        cur_row -= 1
                        if at_node(cur_row, cur_col):
                            new_path_cost = cur_node.path_cost + abs(cur_node.col - cur_col)
                            break
                    new_path_cost = cur_node.path_cost + abs(cur_node.row - cur_row)
                elif direction == DOWN:
                    if not within_bounds(cur_row+1, cur_col) or self.move_grid[cur_row+1][cur_col] != 6:
                        return None # abort, no node exists in this direction
                    while self.move_grid[cur_row+1][cur_col] == 6:
                        if (not within_bounds(cur_row+1, cur_col) or
                            is_enemy(cur_row+1, cur_col)):
                            return None # abort, no node exists in this direction
                        cur_row += 1
                        if at_node(cur_row, cur_col):
                            new_path_cost = cur_node.path_cost + abs(cur_node.col - cur_col)
                            break
                    new_path_cost = cur_node.path_cost + abs(cur_node.row - cur_row)
                elif direction == LEFT:
                    while (self.game.floor_below_me(cur_row, cur_col-1) or
                        # can go left if there is a floor to the left
                        self.game.floor_below_me(cur_row, cur_col-2)):
                        # can go left if there is no floor beneath the left cell but the left cell has floors on both sides
                        try:
                            if ((self.move_grid[cur_row][cur_col-1] == 7 and not self.game.floor_below_me(cur_row, cur_col-2)) or
                                (self.move_grid[cur_row][cur_col-2] == 7 and not self.game.floor_below_me(cur_row, cur_col-1)) or
                                (is_enemy(cur_row, cur_col-1))):
                                return None
                        except:
                            return None # abort, no node exists in this direction
                        cur_col -= 1
                        if at_node(cur_row, cur_col):
                            new_path_cost = cur_node.path_cost + abs(cur_node.col - cur_col)
                            break
                elif direction == RIGHT:
                    while (self.game.floor_below_me(cur_row, cur_col+1) or
                        # can go right if there is a floor to the right
                        self.game.floor_below_me(cur_row, cur_col+2)):
                        # can go right if there is no floor beneath the right cell but the left cell has floors on both sides
                        try:
                            if ((self.move_grid[cur_row][cur_col+1] == 7 and not self.game.floor_below_me(cur_row, cur_col+2)) or
                                (self.move_grid[cur_row][cur_col+2] == 7 and not self.game.floor_below_me(cur_row, cur_col+1)) or
                                (is_enemy(cur_row, cur_col+1))):
                                return None
                        except:
                            return None # abort, no node exists in this direction
                        cur_col += 1
                        if at_node(cur_row, cur_col):
                            new_path_cost = cur_node.path_cost + abs(cur_node.col - cur_col)
                            break

                if new_path_cost != 0:
                    return Node(cur_row, cur_col, new_path_cost, cur_node)
                return None

            def expand(cur_node):
                """Branch out from the current position and identify 'nodes'.
                Nodes are located at either on goal objects or cells in the graph that have branches, such as at the two ends of a ladder."""
                nodes = []
                for direction in [UP, LEFT, RIGHT, DOWN]:
                    new_node = seek_node(cur_node, direction)
                    if new_node is not None:
                        nodes.append(new_node)
                return nodes

            def eval(node):
                """The A* evaluation function, which is f(n) = h(n) + g(n)"""
                return node.path_cost + heuristic(row, col, node.row, node.col)

            node = Node(row, col)
            goal = None
            frontier = PriorityQueue(eval)
            frontier.push(node)
            explored = set()
            path = []

            # perform A* search
            while frontier:
                node = frontier.pop()
                if is_terminal(node.row, node.col):
                    goal = node
                    break
                explored.add(node)
                for child in expand(node):
                    if child not in explored and child not in frontier:
                        frontier.push(child)
                    elif child in frontier:
                        if eval(child) < frontier[child]:
                            del frontier[child]
                            frontier.push(child)

            if goal is None:
                #print("target: None")
                #print(f"target not found. last node: {node.row}, {node.col}")
                return None

            # DEBUG: print tanuki's next goal
            #print(f"target: {node.row}, {node.col}")

            # backtrack
            while node.parent is not None:
                if node.row == node.parent.row:
                    if node.col < node.parent.col:
                        for i in range(abs(node.col - node.parent.col)):
                            path.append(LEFT)
                    else:
                        for i in range(abs(node.col - node.parent.col)):
                            path.append(RIGHT)
                elif node.col == node.parent.col:
                    if node.row < node.parent.row:
                        for i in range(abs(node.row - node.parent.row)):
                            path.append(UP)
                    else:
                        for i in range(abs(node.row - node.parent.row)):
                            path.append(DOWN)
                node = node.parent

            return (goal.row, goal.col, path)


        astar = None
        dist_ladder = 0
        goal_r = 0
        goal_c = 0
        ladder_path = None
        self.path = None

        if is_goal(self.tanuki_r, self.tanuki_c):
            # tanuki got a target/bonus! now we have to mark the cell empty
            self.move_grid[self.tanuki_r][self.tanuki_c] = 1

        if self.time_limit < 1.5 or self.time_limit > 99.5:
            # reset states during state transition
            # prevents tanuki from bugging out when skipping a tage
            self.previous_move = None
            return # pause on stage start and stage end

        if not self.game.floor_below_me(self.tanuki_r, self.tanuki_c):
            return # don't do anything when in mid air

        astar = astar_search(self.tanuki_r, self.tanuki_c, is_mid_ladder)
        if astar is not None:
            goal_r, goal_c, ladder_path = astar
            dist_ladder = abs(goal_c - self.tanuki_c)

        if (is_enemy_coming(self.tanuki_r, self.tanuki_c) and
            dist_enemy(self.tanuki_r, self.tanuki_c) <= 2 * dist_ladder + 1 and
            ladder_path is not None):
            self.path = ladder_path

        if not self.path:
            astar = astar_search(self.tanuki_r, self.tanuki_c)
            if astar is not None:
                goal_r, goal_c, self.path = astar

        #############################################################
        # Translate path to keystrokes                              #
        #############################################################

        if self.previous_move == None:
            self.previous_move = LEFT

        if not self.path:
            # don't do anything if for some reason these is no path to follow
            print("No next move to follow.")
            return

        if is_mid_ladder(self.tanuki_r, self.tanuki_c):
            if (self.path[len(self.path)-1] == UP and
                is_enemy_coming(self.tanuki_r-1, self.tanuki_c) and
                dist_enemy(self.tanuki_r-1, self.tanuki_c) <= 1):
                return # stall on the ladder
            if (self.path[len(self.path)-1] == DOWN and
                is_enemy_coming(self.tanuki_r+1, self.tanuki_c) and
                dist_enemy(self.tanuki_r+1, self.tanuki_c) <= 1):
                return # stall on the ladder

        next_move = self.path.pop()

        if next_move is UP:
            self.previous_jump = False
            self.game.on_key_press(arcade.key.UP, None)
            if self.previous_move != DOWN:
                # tanuki turned on the last move, need to move now
                self.game.on_key_press(arcade.key.UP, None)
        elif next_move is DOWN:
            self.previous_jump = False
            self.game.on_key_press(arcade.key.DOWN, None)
            if self.previous_move != UP:
                # tanuki turned on the last move, need to move now
                self.game.on_key_press(arcade.key.DOWN, None)
        elif next_move is LEFT:
            if not within_bounds(self.tanuki_r, self.tanuki_c-1):
                return
            if (self.move_grid[self.tanuki_r][self.tanuki_c-1] == 7 or
                not self.game.floor_below_me(self.tanuki_r, self.tanuki_c-1)):
                # tanuki needs to jump
                self.previous_jump = True
                if self.previous_move == UP or self.previous_move == DOWN or self.previous_jump == True:
                    # tanuki needs to turn first
                    self.game.on_key_press(arcade.key.LEFT, None)
                self.game.on_key_press(arcade.key.SPACE, None)
                self.path.pop() # jumping makes tanuki travel an extra cell so we need to pop an extra move
            else:
                self.previous_jump = False
                self.game.on_key_press(arcade.key.LEFT, None)
                if self.previous_move != next_move:
                    # tanuki turned on the last move, need to move now
                    self.game.on_key_press(arcade.key.LEFT, None)
        elif next_move is RIGHT:
            if not within_bounds(self.tanuki_r, self.tanuki_c+1):
                return
            if (self.move_grid[self.tanuki_r][self.tanuki_c+1] == 7 or
                not self.game.floor_below_me(self.tanuki_r, self.tanuki_c+1)):
                # tanuki needs to jump
                self.previous_jump = True
                if self.previous_move == UP or self.previous_move == DOWN or self.previous_jump == True:
                    # tanuki needs to turn first
                    self.game.on_key_press(arcade.key.RIGHT, None)
                self.game.on_key_press(arcade.key.SPACE, None)
                self.path.pop() # jumping makes tanuki travel an extra cell so we need to pop an extra move
            else:
                self.previous_jump = False
                self.game.on_key_press(arcade.key.RIGHT, None)
                if self.previous_move != next_move:
                    # tanuki turned on the last move, need to move now
                    self.game.on_key_press(arcade.key.RIGHT, None)

        # update the previous move
        # used to detect if tanuki is turning
        self.previous_move = next_move

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
            time.sleep(1)  # wait briefly so that main game can get ready

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
    ag.game.isDisableEnemy = False
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