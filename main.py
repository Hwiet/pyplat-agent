import arcade
import game_core
import threading
import time
import os
import pygame
import math
from queue import Queue
from enum import Enum
import heapq
import numpy

ROW_COUNT = 12
COL_COUNT = 20

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

        self.path = []
        self.prev_move = None

    def ai_function(self):
        Dir = Enum('Dir', 'UP DOWN LEFT RIGHT')

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


        def is_goal(row, col, terminals=[8, 9, 10]):
            return self.move_grid[row][col] in terminals

        def astar_search(row, col):
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
                return (is_goal(row, col) or
                    # target
                    self.move_grid[row][col] == 6 or
                    # bottom of a ladder
                    (self.move_grid[row+1][col] == 6 and (self.move_grid[row][col] == 1 or is_goal(row, col))))
                    # top of a ladder

            def seek_node(cur_node, direction):
                cur_row = cur_node.row
                cur_col = cur_node.col
                new_path_cost = 0
                if direction == Dir.UP:
                    if self.move_grid[cur_row][cur_col] != 6:
                        return None # abort, no node exists in this direction
                    while self.move_grid[cur_row][cur_col] == 6:   
                        if not within_bounds(cur_row-1, cur_col):
                            return None # abort, no node exists in this direction
                        cur_row -= 1
                    new_path_cost = cur_node.path_cost + abs(cur_node.row - cur_row)
                elif direction == Dir.DOWN:
                    if not within_bounds(cur_row+1, cur_col) or self.move_grid[cur_row+1][cur_col] != 6:
                        return None # abort, no node exists in this direction
                    while self.move_grid[cur_row+1][cur_col] == 6:
                        if not within_bounds(cur_row+1, cur_col):
                            return None # abort, no node exists in this direction
                        cur_row += 1
                    new_path_cost = cur_node.path_cost + abs(cur_node.row - cur_row)
                elif direction == Dir.LEFT:
                    while (self.game.floor_below_me(cur_row, cur_col-1) or
                        # can go left if there is a floor to the left
                        self.game.floor_below_me(cur_row, cur_col-2)):
                        # can go left if there is no floor beneath the left cell but the left cell has floors on both sides

                        if not within_bounds(cur_row, cur_col-1): # or self.move_grid[cur_row][cur_col-1] == 7:
                            return None # abort, no node exists in this direction
                        cur_col -= 1
                        if at_node(cur_row, cur_col):
                            new_path_cost = cur_node.path_cost + abs(cur_node.col - cur_col)
                            break
                elif direction == Dir.RIGHT:
                    while (self.game.floor_below_me(cur_row, cur_col+1) or
                        # can go right if there is a floor to the right
                        self.game.floor_below_me(cur_row, cur_col+2)):
                        # can go right if there is no floor beneath the right cell but the left cell has floors on both sides

                        if not within_bounds(cur_row, cur_col+1): # or self.move_grid[cur_row][cur_col+1] == 7:
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
                #print(f"({cur_node.row}, {cur_node.col}): ", end="")
                for direction in Dir:
                    new_node = seek_node(cur_node, direction)
                    if new_node is not None:
                        #print(f"{direction} ", end="")
                        #print(f"({new_node.row}, {new_node.col}) ", end="")
                        nodes.append(new_node)
                #print("")
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
                if is_goal(node.row, node.col):
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
            
            # DEGUG: print tanuki's next goal
            print(f"{node.row}, {node.col}")

            # backtrack
            while node.parent is not None:
                if node.row == node.parent.row:
                    if node.col < node.parent.col:
                        for i in range(abs(node.col - node.parent.col)):
                            path.append(Dir.LEFT)
                    else:
                        for i in range(abs(node.col - node.parent.col)):
                            path.append(Dir.RIGHT)
                elif node.col == node.parent.col:
                    if node.row < node.parent.row:
                        for i in range(abs(node.row - node.parent.row)):
                            path.append(Dir.UP)
                    else:
                        for i in range(abs(node.row - node.parent.row)):
                            path.append(Dir.DOWN)
                node = node.parent
                
            return (goal, path)
        
        next_move = None
        if self.path == []:
            if is_goal(self.tanuki_r, self.tanuki_c):
                # tanuki got a target/bonus! now we have to mark the cell empty
                self.move_grid[self.tanuki_r][self.tanuki_c] = 1
            self.goal, self.path = astar_search(self.tanuki_r, self.tanuki_c)

        next_move = self.path.pop()
        if next_move is Dir.UP:
            self.game.on_key_press(arcade.key.UP, None)
        elif next_move is Dir.DOWN:
            self.game.on_key_press(arcade.key.DOWN, None)
        elif next_move is Dir.LEFT:
            if self.move_grid[self.tanuki_r][self.tanuki_c-1] == 7 or not self.game.floor_below_me(self.tanuki_r, self.tanuki_c-1):
                self.game.on_key_press(arcade.key.SPACE, None)
            else:
                self.game.on_key_press(arcade.key.LEFT, None)
        elif next_move is Dir.RIGHT:
            if self.move_grid[self.tanuki_r][self.tanuki_c+1] == 7 or not self.game.floor_below_me(self.tanuki_r, self.tanuki_c+1):
                self.game.on_key_press(arcade.key.SPACE, None)
            else:
                self.game.on_key_press(arcade.key.RIGHT, None)

        self.prev_move = next_move

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