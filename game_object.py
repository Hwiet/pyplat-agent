import arcade
import game_data as gd
import game_core as gc


class DeltaTimeSpriteList(arcade.SpriteList):

    def __init__(self):
        super().__init__()

    def update(self, delta_time):
        for sprite in self.sprite_list:
            sprite.update(delta_time)


class GameObject(arcade.Sprite):

    def __init__(self):
        super().__init__()
        self.isActive = True
        self.gridR = 0
        self.gridC = 0

    def set_gridRC(self, r, c):
        self.gridR = r
        self.gridC = c
        self.recalculate_position()

    def recalculate_position(self):
        self.set_position(gc.GRID_W * self.gridC + gc.GRID_W / 2,
                          gc.GRID_H * (gc.ROW_COUNT - self.gridR) + gc.GRID_H / 2)

    def get_gridRC(self):
        return self.gridR, self.gridC

    def update(self):
        pass


class Platform(GameObject):

    def __init__(self, file_name, r, c):
        super().__init__()

        self.texture = arcade.load_texture(gd.data_path + file_name)
        self.set_gridRC(r, c)

    def update(self):
        pass


class Item(GameObject):

    def __init__(self, file_name1, file_name2, r, c):
        super().__init__()

        self.texture_avail = arcade.load_texture(gd.data_path + file_name1)
        self.texture_gone = arcade.load_texture(gd.data_path + file_name2)

        self.texture = self.texture_avail  # set default texture to avoid crash

        self.set_gridRC(r, c)

    def update(self):
        if self.isActive:
            self.texture = self.texture_avail
        else:
            self.texture = self.texture_gone


class Tanuki(GameObject):

    def __init__(self):
        super().__init__()

        self.texture_l = arcade.load_texture(gd.data_path + gd.img_tanuki[0][0])
        self.texture_l_j1 = arcade.load_texture(gd.data_path + gd.img_tanuki[0][1][0])
        self.texture_l_j2 = arcade.load_texture(gd.data_path + gd.img_tanuki[0][1][1])

        self.texture_r = arcade.load_texture(gd.data_path + gd.img_tanuki[1][0])
        self.texture_r_j1 = arcade.load_texture(gd.data_path + gd.img_tanuki[1][1][0])
        self.texture_r_j2 = arcade.load_texture(gd.data_path + gd.img_tanuki[1][1][1])

        self.texture_u = arcade.load_texture(gd.data_path + gd.img_tanuki[2])

        self.texture_k1 = arcade.load_texture(gd.data_path + gd.img_tanuki[3][0])
        self.texture_k2 = arcade.load_texture(gd.data_path + gd.img_tanuki[3][1])
        self.texture_k3 = arcade.load_texture(gd.data_path + gd.img_tanuki[3][2])
        self.texture_k4 = arcade.load_texture(gd.data_path + gd.img_tanuki[3][3])
        self.texture_k5 = arcade.load_texture(gd.data_path + gd.img_tanuki[3][4])

        self.texture_al = arcade.load_texture(gd.data_path + gd.img_tanuki[4][0])
        self.texture_ar = arcade.load_texture(gd.data_path + gd.img_tanuki[4][1])

        self.texture_bl = arcade.load_texture(gd.data_path + gd.img_tanuki[5][0])
        self.texture_br = arcade.load_texture(gd.data_path + gd.img_tanuki[5][1])

        self.texture = self.texture_l  # set default texture to avoid crash

        self.isActive = True
        self.isGoingLeft = True
        self.isJumping = False
        self.jump_state = 0
        self.isGoingUpDown = False
        self.isDying = False
        self.dying_state = 0
        self.isDead = False
        self.ateSmallBonus = False
        self.ateBigBonus = False

    def update(self):
        if self.ateSmallBonus:
            if self.isGoingLeft:
                self.texture = self.texture_al
            else:
                self.texture = self.texture_ar
            self.ateSmallBonus = False
            return
        elif self.ateBigBonus:
            if self.isGoingLeft:
                self.texture = self.texture_bl
            else:
                self.texture = self.texture_br
            self.ateBigBonus = False
            return

        if self.isDying:
            if self.dying_state == 0:
                self.texture = self.texture_k1
                self.dying_state += 1
            elif self.dying_state == 1:
                self.texture = self.texture_k2
                self.dying_state += 1
            elif self.dying_state == 2:
                self.texture = self.texture_k3
                self.dying_state += 1
            elif self.dying_state == 3:
                self.texture = self.texture_k4
                self.dying_state += 1
            elif self.dying_state == 4:
                self.texture = self.texture_k5
                self.dying_state = 0
            # update location if falling
            if self.change_y != 0:
                self.gridR += self.change_y
                self.recalculate_position()
        elif self.isDead:
            self.texture = self.texture_k1
        elif self.isGoingUpDown:
            self.texture = self.texture_u
            if self.change_y != 0:
                self.gridR += self.change_y
                self.recalculate_position()
                self.change_y = 0
        elif self.isJumping:
            if self.jump_state == 0:
                self.gridC += self.change_x
                self.gridR -= 1
                self.jump_state = 1
            elif self.jump_state == 1:
                self.jump_state = 2
            else:
                self.gridC += self.change_x
                self.gridR += 1
                self.jump_state = 0
                self.isJumping = False
            self.recalculate_position()
            if self.isGoingLeft:
                if self.jump_state == 1:
                    self.texture = self.texture_l_j1
                elif self.jump_state == 2:
                    self.texture = self.texture_l_j2
                else:
                    self.texture = self.texture_l
                    self.change_x = 0
            else:
                if self.jump_state == 1:
                    self.texture = self.texture_r_j1
                elif self.jump_state == 2:
                    self.texture = self.texture_r_j2
                else:
                    self.texture = self.texture_r
                    self.change_x = 0
        elif self.isGoingLeft:
            self.texture = self.texture_l
            if self.change_x != 0 and self.gridC > 0:
                self.gridC += self.change_x
                self.recalculate_position()
                self.change_x = 0
        else:
            self.texture = self.texture_r
            if self.change_x != 0 and self.gridC < gc.COL_COUNT-2:
                self.gridC += self.change_x
                self.recalculate_position()
                self.change_x = 0


class Enemy1(GameObject):

    def __init__(self, speed, row, col):
        super().__init__()

        self.texture_l1 = arcade.load_texture(gd.data_path + gd.img_enemy1[0][0])
        self.texture_l2 = arcade.load_texture(gd.data_path + gd.img_enemy1[0][1])
        self.texture_r1 = arcade.load_texture(gd.data_path + gd.img_enemy1[1][0])
        self.texture_r2 = arcade.load_texture(gd.data_path + gd.img_enemy1[1][1])

        self.texture = self.texture_l1  # set default texture to avoid crash

        self.isActive = False
        self.isGoingLeft = False
        self.speed = speed / 10.0  # speed of 10 is roughly 1 cell/second

        self.gridR = row
        self.gridC = col

        self.acc_delta_time = 0

    def update(self, delta_time):
        self.acc_delta_time += delta_time

        if not self.isActive:
            return

        if self.acc_delta_time < self.speed:
            if self.isGoingLeft:
                if self.texture == self.texture_l1:
                    self.texture = self.texture_l2
                else:
                    self.texture = self.texture_l1
            else:
                if self.texture == self.texture_r1:
                    self.texture = self.texture_r2
                else:
                    self.texture = self.texture_r1
        else:
            self.acc_delta_time = 0
            if self.isGoingLeft:
                if self.gridC > 0:
                    self.gridC -= 1
                else:
                    self.isGoingLeft = False
                self.recalculate_position()
                if self.texture == self.texture_l1:
                    self.texture = self.texture_l2
                else:
                    self.texture = self.texture_l1
            else:
                if self.gridC < gc.COL_COUNT-2:
                    self.gridC += 1
                else:
                    self.isGoingLeft = True
                self.recalculate_position()
                if self.texture == self.texture_r1:
                    self.texture = self.texture_r2
                else:
                    self.texture = self.texture_r1


class Enemy2(GameObject):

    def __init__(self, speed, row):
        super().__init__()

        self.texture_l = arcade.load_texture(gd.data_path + gd.img_enemy2[0])
        self.texture_r = arcade.load_texture(gd.data_path + gd.img_enemy2[1])

        self.texture = self.texture_l  # set default texture to avoid crash

        self.isActive = True
        self.isGoingLeft = False
        self.speed = speed / 10.0

        self.gridR = row
        self.gridC = 0

        self.acc_delta_time = 0

    def update(self, delta_time):
        self.acc_delta_time += delta_time

        if self.acc_delta_time < self.speed:
            if self.isGoingLeft:
                self.texture = self.texture_l
            else:
                self.texture = self.texture_r
        else:
            self.acc_delta_time = 0
            if self.isGoingLeft:
                if self.gridC > 0:
                    self.gridC -= 1
                else:
                    self.isGoingLeft = False
                self.recalculate_position()
                self.texture = self.texture_l
            else:
                if self.gridC < gc.COL_COUNT-2:
                    self.gridC += 1
                else:
                    self.isGoingLeft = True
                self.recalculate_position()
                self.texture = self.texture_r

