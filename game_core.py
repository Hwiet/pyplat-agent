import arcade
import game_object as gobj
import game_data as gd
import pyglet
import timeit
from datetime import datetime

ROW_COUNT = 12
COL_COUNT = 20

GRID_W = 16
GRID_H = 16

SCREEN_W = 320
SCREEN_H = 240

MAX_STAGE = len(gd.stages)  # from 0 to 9


class GameMain(arcade.Window):

    def __init__(self, width=SCREEN_W, height=SCREEN_H):
        super().__init__(width, height)

        arcade.set_background_color(arcade.color.BLACK)

        self.proc_time = 0
        self.rendering_time = 0

        self.total_score = 0
        self.current_stage = 0

        self.isDebugMode = True
        self.isDisableEnemy = False

        self.isRecording = False
        self.replayFile = []
        self.isReplaying = False
        self.replay_list = []
        self.replay_count = 0

        self.total_life = 0
        self.total_time = 0.0
        self.time_limit = 0

        self.isGameClear = False
        self.isGameOver = False

        # setup grid cells
        self.plat_grid = []
        for row in range(ROW_COUNT):
            self.plat_grid.append([])
            for col in range(COL_COUNT):
                self.plat_grid[row].append(0)

        self.move_grid = []
        for row in range(ROW_COUNT):
            self.move_grid.append([])
            for col in range(COL_COUNT):
                self.move_grid[row].append(0)

        self.kill_grid = []
        for row in range(ROW_COUNT):
            self.kill_grid.append([])
            for col in range(COL_COUNT):
                self.kill_grid[row].append(False)

        self.all_sprites_list = []
        self.all_enemy_sprites_list = []
        self.enemy_list = []
        self.tanuki = []
        self.tanuki_r = ROW_COUNT-2
        self.tanuki_c = COL_COUNT-1

    def get_game_state(self):
        return self.move_grid, self.kill_grid, \
               self.isGameClear, self.isGameOver, self.current_stage, self.time_limit, \
               self.total_score, self.total_time, self.total_life, self.tanuki_r, self.tanuki_c

    def replay(self, replay_file_name=""):
        if self.isRecording and self.isReplaying:
            return False  # cannot do both at a time

        if self.isRecording:
            t = datetime.now()
            x = t.timetuple()
            if len(replay_file_name) == 0:
                replayfilename = f"r_{x[0]:04d}-{x[1]:02d}-{x[2]:02d}_{x[3]:02d}-{x[4]:02d}-{x[5]:02d}.rpy"
            else:
                replayfilename = replay_file_name
            self.replayFile = open('replay/' + replayfilename, 'wt')
        elif self.isReplaying:
            replayfilename = replay_file_name
            self.replay_list.clear()
            with open('replay/' + replayfilename, 'rt') as f:
                for read_data in f:
                    read_data = read_data.split(',')
                    read_data[0] = float(read_data[0])
                    read_data[1] = int(read_data[1])
                    self.replay_list.append(read_data)
            self.replay_count = 0

    # This method is called when the game starts from the beginning
    def reset(self):
        self.setup(self.current_stage)

        # reset life
        self.total_life = gd.life_limit

        # total time
        self.total_time = 0.0

        self.isGameClear = False
        self.isGameOver = False

    # This method is called when a new stage starts
    def setup(self, stage_num):
        # reset timer
        self.time_limit = gd.time_limit

        # Create your sprites and sprite lists here
        self.all_sprites_list = arcade.SpriteList()
        self.all_enemy_sprites_list = gobj.DeltaTimeSpriteList()

        # Enemy2
        self.enemy_list.clear()
        for r in range(4):
            spd = gd.enemy_speeds[stage_num][r]
            if spd > 0:
                self.enemy_list.append(gobj.Enemy2(spd, 1+r*3))  # enemy2 wonders in rows 1, 4, 7, 10

        # Platform and Enemy1
        self.load_stage(stage_num)
        for row in range(ROW_COUNT):
            for col in range(COL_COUNT):
                self.all_sprites_list.append(self.plat_grid[row][col])

        # When enemy (adversarial agent) disabled
        if self.isDisableEnemy:
            for enm in self.enemy_list:
                enm.isActive = False
        else:
            # Add enemies into SpriteList
            for enm in self.enemy_list:
                self.all_enemy_sprites_list.append(enm)

        # Tanuki
        self.tanuki = gobj.Tanuki()
        self.tanuki.set_gridRC(ROW_COUNT-2, COL_COUNT-1)
        self.tanuki_r = ROW_COUNT-2
        self.tanuki_c = COL_COUNT - 2

    def load_stage(self, stage_num):
        for r in range(ROW_COUNT):
            for c in range(COL_COUNT):
                if gd.stages[stage_num][r][c] == '.':
                    file_name = gd.img_world[0]
                    if c < COL_COUNT-1:
                        self.plat_grid[r][c] = gobj.Platform(file_name, r, c)
                        self.move_grid[r][c] = 1
                    else:  # cannot be here except the beginning of stage
                        if r < stage_num:
                            self.plat_grid[r][c] = gobj.Platform(gd.img_fruit[r], r, c)
                        else:
                            self.plat_grid[r][c] = gobj.Platform(file_name, r, c)
                        self.move_grid[r][c] = 0
                    self.kill_grid[r][c] = False
                elif gd.stages[stage_num][r][c] == '2':
                    file_name = gd.img_world[1]
                    self.plat_grid[r][c] = gobj.Platform(file_name, r, c)
                    self.move_grid[r][c] = 2
                    self.kill_grid[r][c] = False
                elif gd.stages[stage_num][r][c] == '3':
                    file_name = gd.img_world[2]
                    self.plat_grid[r][c] = gobj.Platform(file_name, r, c)
                    self.move_grid[r][c] = 3
                    self.kill_grid[r][c] = False
                elif gd.stages[stage_num][r][c] == '4':
                    file_name = gd.img_world[3]
                    self.plat_grid[r][c] = gobj.Platform(file_name, r, c)
                    self.move_grid[r][c] = 4
                    self.kill_grid[r][c] = False
                elif gd.stages[stage_num][r][c] == '5':
                    file_name = gd.img_world[4]
                    self.plat_grid[r][c] = gobj.Platform(file_name, r, c)
                    self.move_grid[r][c] = 5
                    self.kill_grid[r][c] = False
                elif gd.stages[stage_num][r][c] == '6':
                    file_name = gd.img_world[5]
                    self.plat_grid[r][c] = gobj.Platform(file_name, r, c)
                    self.move_grid[r][c] = 6
                    self.kill_grid[r][c] = False
                elif gd.stages[stage_num][r][c] == '7':
                    file_name = gd.img_world[6]
                    self.plat_grid[r][c] = gobj.Platform(file_name, r, c)
                    self.move_grid[r][c] = 7
                    self.kill_grid[r][c] = True
                elif gd.stages[stage_num][r][c] == '#':
                    file_name1 = gd.img_fruit[stage_num]
                    file_name2 = gd.img_world[0]
                    self.plat_grid[r][c] = gobj.Item(file_name1, file_name2, r, c)
                    self.move_grid[r][c] = 8
                    self.kill_grid[r][c] = False
                elif gd.stages[stage_num][r][c] == 'a':
                    file_name1 = gd.img_world[7]
                    file_name2 = gd.img_world[0]
                    self.plat_grid[r][c] = gobj.Item(file_name1, file_name2, r, c)
                    self.move_grid[r][c] = 9
                    self.kill_grid[r][c] = False
                elif gd.stages[stage_num][r][c] == 'b':
                    file_name1 = gd.img_world[7]
                    file_name2 = gd.img_world[0]
                    self.plat_grid[r][c] = gobj.Item(file_name1, file_name2, r, c)
                    self.move_grid[r][c] = 10
                    self.kill_grid[r][c] = False
                elif gd.stages[stage_num][r][c] == 'c':
                    file_name1 = gd.img_world[7]
                    file_name2 = gd.img_world[0]
                    self.plat_grid[r][c] = gobj.Item(file_name1, file_name2, r, c)
                    self.move_grid[r][c] = 11
                    self.kill_grid[r][c] = False
                    # Enemy1 is hidden inside this; it always appear on the right of the bonus bag
                    self.enemy_list.append(gobj.Enemy1(gd.enemy_speeds[stage_num][4], r, c+1))

    # MAIN RENDERING METHOD
    def on_draw(self):
        start_time = timeit.default_timer()

        # This command should happen before we start drawing. It will clear
        # the screen to the background color, and erase what we drew last frame.
        arcade.start_render()

        # Call draw() on all your sprite lists below
        if not (self.isGameClear or self.isGameOver):
            self.all_sprites_list.draw()
            if not self.isDisableEnemy:
                self.all_enemy_sprites_list.draw()
            self.tanuki.draw()

        # calc minutes
        minutes = int(self.total_time) // 60
        # calc seconds
        seconds = int(self.total_time) % 60
        # prepare output
        if self.isGameClear:
            output = f"Total Elapsed Time: {minutes:02d}:{seconds:02d} (GAME CLEAR)"
        elif self.isGameOver:
            output = f"Total Elapsed Time: {minutes:02d}:{seconds:02d} (GAME OVER)"
        else:
            output = f"Elapsed Time: {minutes:02d}:{seconds:02d}"
        arcade.draw_text(output, 0, 224, arcade.color.WHITE, 10)

        # output timer
        if not (self.isGameClear or self.isGameOver):
            seconds = int(self.time_limit)
            life = int(self.total_life)
            output = f"TIME: {seconds:03d} / LIFE: {life:01d}"
            arcade.draw_text(output, 0, 208, arcade.color.WHITE, 10)

        # Score
        score = int(self.total_score)
        output = f"Total Score: {score:06d}"
        arcade.draw_text(output, 0, 14, arcade.color.WHITE, 10)

        # FPS
        fps = 1.0 / (self.proc_time + self.rendering_time)
        output = \
            f"Proc Time: {self.proc_time:.3f} / Draw Time: {self.rendering_time:.3f} / FPS: {fps:3.1f}"
        arcade.draw_text(output, 0, 0, arcade.color.WHITE, 10)

        self.rendering_time = timeit.default_timer() - start_time

    # MAIN UPDATE (GAME LOGIC) METHOD
    def update(self, delta_time):
        # if game cleared or game over, no update needed; otherwise, check if game is over
        if self.isGameClear or self.isGameOver:
            return
        else:
            self.gameover_check()

        self.total_time += delta_time

        start_time = timeit.default_timer()

        # update location of all objects
        self.all_sprites_list.update()
        if not self.isDisableEnemy:
            self.all_enemy_sprites_list.update(delta_time)
        self.tanuki.update()
        self.tanuki_r, self.tanuki_c = self.tanuki.get_gridRC()

        # check if tanuki ate something with the move just now
        self.eat_check()

        # check whether tanuki should die
        self.recompute_kill_grid()
        self.kill_check()

        # reduce time limit
        if not (self.tanuki.isDying or self.tanuki.isDead):
            self.time_limit -= delta_time

        self.proc_time = timeit.default_timer() - start_time

        # if replaying, check whether it's near the next command, and simulate the keystroke
        if self.isReplaying:
            if abs(self.replay_list[self.replay_count][0] - self.total_time) < 0.05 or \
                    self.replay_list[self.replay_count][0] < self.total_time:
                self.on_key_press(self.replay_list[self.replay_count][1], 0)
                if self.replay_count < len(self.replay_list)-1:
                    self.replay_count += 1

    def gameover_check(self):
        if self.tanuki.isDead:
            if self.total_life > 0:
                self.total_life -= 1
                self.setup(self.current_stage)
            else:
                self.isGameOver = True
                if self.isRecording:
                    self.replayFile.close()
                    self.isRecording = False
        elif self.check_if_tanuki_ate_them_all():
            self.total_score += (int(self.time_limit) * gd.time_bonus)
            if self.current_stage == (MAX_STAGE-1):
                self.isGameClear = True
                if self.isRecording:
                    self.replayFile.close()
                    self.isRecording = False
            else:
                self.current_stage += 1
                self.setup(self.current_stage)

    def check_if_tanuki_ate_them_all(self):
        for row in range(ROW_COUNT):
            for col in range(COL_COUNT):
                if self.plat_grid[row][col].isActive:
                    if self.move_grid[row][col] == 8:  # eating bonus is optional
                        return False

        return True

    def eat_check(self):
        gridr = self.tanuki_r
        gridc = self.tanuki_c
        if self.plat_grid[gridr][gridc].isActive:
            if self.move_grid[gridr][gridc] == 8:
                self.total_score += 100
                self.plat_grid[gridr][gridc].isActive = False
            elif self.move_grid[gridr][gridc] == 9:
                self.total_score += 500
                self.plat_grid[gridr][gridc].isActive = False
                self.tanuki.ateSmallBonus = True
            elif self.move_grid[gridr][gridc] == 10:
                self.total_score += 1000
                self.plat_grid[gridr][gridc].isActive = False
                self.tanuki.ateBigBonus = True
            elif self.move_grid[gridr][gridc] == 11:
                self.plat_grid[gridr][gridc].isActive = False
                if not self.isDisableEnemy:
                    self.enemy_list[-1].isActive = True  # hidden enemy is always the last one in the list
            else:
                pass

    def recompute_kill_grid(self):
        for row in range(ROW_COUNT-1):
            for col in range(COL_COUNT-1):
                if self.move_grid[row][col] == 7:
                    self.kill_grid[row][col] = True
                else:
                    self.kill_grid[row][col] = False

        for enemy in self.enemy_list:
            if enemy.isActive:
                r, c = enemy.get_gridRC()
                self.kill_grid[r][c] = True

    def kill_check(self):
        gridr = self.tanuki_r
        gridc = self.tanuki_c
        if self.tanuki.isDying:
            if self.floor_below_me(gridr, gridc):
                self.tanuki.isDying = False
                self.tanuki.isDead = True
                return
            else:
                self.tanuki.change_y = 1
                return
        elif not self.tanuki.isDead:
            if not (self.tanuki.isJumping or self.tanuki.isGoingUpDown):
                if not self.floor_below_me(gridr, gridc):
                    self.tanuki.isDying = True
                    return

            for row in range(ROW_COUNT):
                for col in range(COL_COUNT):
                    if self.kill_grid[row][col]:
                        if gridr == row and gridc == col:
                            self.tanuki.isDying = True
                            return

            if self.total_time <= 0.0:
                self.tanuki.isDying = True
                self.total_time = 0.0

    # Is tanuki standing on a platform? (including or excluding ladder)
    def floor_below_me(self, r, c, exclude_ladder=False):
        if exclude_ladder:
            ub = 5
        else:
            ub = 6
        if (0 <= r < ROW_COUNT-1) and (0 <= c < COL_COUNT):
            if 2 <= self.move_grid[r+1][c] <= ub:
                return True
            else:
                return False

    # MAIN INPUT PROCESSING METHOD
    def on_key_press(self, key, key_modifiers):
        """
        For a full list of keys, see: http://arcade.academy/arcade.key.html
        """
        if self.isRecording and not self.replayFile.closed:
            self.replayFile.write(str(self.total_time) + ',' + str(key) + '\n')

        gridr = self.tanuki_r
        gridc = self.tanuki_c
        # DEBUG MODE KEYS
        if self.isDebugMode:
            if key == arcade.key.R:  # reset (from the beginning of the game)
                self.reset()
            elif key == arcade.key.E:  # reset (from the beginning of the stage)
                self.setup(self.current_stage)
            elif key == arcade.key.C:  # cheat (skip stage)
                for r in range(ROW_COUNT):
                    for c in range(COL_COUNT):
                        if self.move_grid[r][c] == 8:
                            self.plat_grid[r][c].isActive = False

        if key == arcade.key.S:  # screenshot
            t = datetime.now()
            x = t.timetuple()
            filename = f"ss_{x[0]:04d}-{x[1]:02d}-{x[2]:02d}_{x[3]:02d}-{x[4]:02d}-{x[5]:02d}.png"
            pyglet.image.get_buffer_manager().get_color_buffer().save('screenshot/' + filename)
        elif self.tanuki.isJumping or self.tanuki.isDying:
            return  # nothing can be done
        elif self.tanuki.isGoingUpDown:
            # Tanuki is allowed to leave the ladder only if it finished crawling up or down the ladder
            if key == arcade.key.LEFT:
                if (self.move_grid[gridr][gridc] != 6 and self.move_grid[gridr+1][gridc] == 6) or \
                        (self.move_grid[gridr][gridc] == 6 and self.floor_below_me(gridr, gridc, True)):
                    self.tanuki.isGoingLeft = True
                    self.tanuki.isGoingUpDown = False
            elif key == arcade.key.RIGHT:
                if (self.move_grid[gridr][gridc] != 6 and self.move_grid[gridr+1][gridc] == 6) or \
                        (self.move_grid[gridr][gridc] == 6 and self.floor_below_me(gridr, gridc, True)):
                    self.tanuki.isGoingLeft = False
                    self.tanuki.isGoingUpDown = False
            elif key == arcade.key.UP:
                if self.move_grid[gridr][gridc] == 6:
                    self.tanuki.change_y = -1
            elif key == arcade.key.DOWN:
                if self.move_grid[gridr+1][gridc] == 6:
                    self.tanuki.change_y = 1
        else:
            if key == arcade.key.SPACE:
                if self.tanuki.isGoingLeft:
                    if gridc > 1:
                        self.tanuki.isJumping = True
                        self.tanuki.change_x = -1
                else:
                    if gridc < (COL_COUNT-3):
                        self.tanuki.isJumping = True
                        self.tanuki.change_x = 1
            elif key == arcade.key.UP:
                if self.move_grid[gridr][gridc] == 6:
                    self.tanuki.isGoingUpDown = True
            elif key == arcade.key.DOWN:
                if self.move_grid[gridr][gridc] == 6 or self.move_grid[gridr + 1][gridc] == 6:
                    self.tanuki.isGoingUpDown = True
            elif key == arcade.key.LEFT:
                if not self.tanuki.isGoingLeft:
                    self.tanuki.isGoingLeft = True
                elif gridc > 0:
                    self.tanuki.change_x = -1
            elif key == arcade.key.RIGHT:
                if self.tanuki.isGoingLeft:
                    self.tanuki.isGoingLeft = False
                elif gridc < (COL_COUNT-2):
                    self.tanuki.change_x = 1

    # These input methods are not used
    def on_key_release(self, key, key_modifiers):
        pass  # intentionally did not use "continuous key press" to discretize every action of player/agent

    def on_mouse_motion(self, x, y, delta_x, delta_y):
        pass

    def on_mouse_press(self, x, y, button, key_modifiers):
        pass

    def on_mouse_release(self, x, y, button, key_modifiers):
        pass

