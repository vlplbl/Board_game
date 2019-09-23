'''This module controls the main game mechanics and game flow'''
import pygame as pg
# from pygame import *
from tilemap import *
from settings import *
from os import path
import random


class Game:
    def __init__(self):
        # initialize game window, etc.
        pg.init()
        pg.mixer.init()
        self.screen = pg.display.set_mode((WIDTH, HEIGHT))
        pg.display.set_caption(TITLE)
        self.clock = pg.time.Clock()
        self.load_data()
        self.running = True

    def load_data(self):
        game_dir = path.dirname(__file__)
        img_folder = path.join(game_dir, 'img')
        terrain_img_folder = path.join(img_folder, 'terrain')
        self.title_font = path.join(img_folder, 'ZOMBIE.TTF')
        self.hud_font = path.join(img_folder, 'Impacted2.0.ttf')
        # self.img_list = []
        # for filename in listdir(terrain_img_folder):
        #     x = pg.image.load(path.join(terrain_img_folder, filename)).convert()
        #     x = pg.transform.scale(x, (TILESIZE, TILESIZE))
        #     self.img_list.append(x)
        self.water_img = pg.image.load(
            path.join(terrain_img_folder, 'water.png')).convert()
        self.water_img = pg.transform.scale(
            self.water_img, (TILESIZE, TILESIZE))
        self.forest_img = pg.image.load(
            path.join(terrain_img_folder, 'forest.png')).convert()
        self.forest_img = pg.transform.scale(
            self.forest_img, (TILESIZE, TILESIZE))
        self.mountain_img = pg.image.load(
            path.join(terrain_img_folder, 'mountain.png')).convert()
        self.mountain_img = pg.transform.scale(
            self.mountain_img, (TILESIZE, TILESIZE))
        self.grass_img = pg.image.load(
            path.join(terrain_img_folder, 'grass.png')).convert()
        self.grass_img = pg.transform.scale(
            self.grass_img, (TILESIZE, TILESIZE))
        # load the main base image
        self.main_base_img = pg.image.load(
            path.join(img_folder, 'MainBase.png')).convert_alpha()
        self.main_base_img = pg.transform.scale(
            self.main_base_img, (TILESIZE, TILESIZE))
        self.baracks_img = pg.image.load(
            path.join(img_folder, 'Baracks.png')).convert_alpha()
        self.baracks_img = pg.transform.scale(
            self.baracks_img, (TILESIZE, TILESIZE))
        self.unit_img = pg.image.load(
            path.join(img_folder, 'unit_img.png')).convert_alpha()
        self.unit_img = pg.transform.scale(self.unit_img, (TILESIZE, TILESIZE))
        self.warrior_img = pg.image.load(
            path.join(img_folder, 'Warrior.png')).convert_alpha()
        self.warrior_img = pg.transform.scale(
            self.warrior_img, (TILESIZE, TILESIZE))
        # create a transparent surface
        self.dim_screen = pg.Surface((TILESIZE, TILESIZE)).convert_alpha()
        self.dim_screen.fill((0, 0, 0, 80))

    def new(self):
        # start a new game
        self.all_sprites = pg.sprite.Group()
        self.tilesize = TILESIZE
        # the offset moves the camera over the board
        self.offset = BOARD_CENTER
        self.tilemap = Tilemap(self)
        self.camera = Camera(self)
        for building in self.tilemap.players[self.tilemap.current_player]["buildings"]:
            self.camera.apply_camera(self, building.pos)
        # self.last_time = 0
        self.mx0, self.my0, self.mx1, self.my1 = 0, 0, 0, 0
        self.mouse_pos = []
        self.enable_ui = True
        self.show_path = False
        self.tooltips = True
        self.camera_counter = 0

        # self.offset[0] = self.tilemap.unit.pos[1] * 64 - 8*64-32
        # self.offset[1] = self.tilemap.unit.pos[0] * 64 - 6*64-32
        # self.camera = Camera(self, self.tilemap.unit.pos)
        # self.offset[0] = self.camera.camera_x
        # self.offset[1] = self.camera.camera_y
        self.clicked = False
        self.right_click = False
        self.run()

    def run(self):
        # Game loop
        self.playing = True
        while self.playing:
            self.clock.tick(FPS)
            self.events()
            self.update()
            self.draw()

    def update(self):
        # Game loop - update
        # now = pg.time.get_ticks()
        # if now - self.last_time > 20:
        #     mx0, my0 = pg.mouse.get_pos()
        #     self.last_time = now
        # mx1, my1 = pg.mouse.get_pos()
        self.all_sprites.update()
        # self.camera.apply_camera(self, self.tilemap.unit.pos)
        self.tilemap.update_map(self)
        self.get_key_input()

    def get_key_input(self):
        key = pg.mouse.get_pressed()
        button = pg.key.get_pressed()
        if button[pg.K_LEFT]:
            self.offset[0] += 10
        if button[pg.K_RIGHT]:
            self.offset[0] -= 10
        if button[pg.K_UP]:
            self.offset[1] += 10
        if button[pg.K_DOWN]:
            self.offset[1] -= 10

        # enable to drag the map with the mouse
        self.mouse_pos.append(pg.mouse.get_pos())
        if len(self.mouse_pos) > 2:
            self.mx0, self.my0 = self.mouse_pos.pop(0)
            self.mx1, self.my1 = self.mouse_pos.pop(0)
        self.mouse_pos = self.mouse_pos[:3]
        if key[0]:
            self.offset[0] += self.mx1 - self.mx0
            self.offset[1] += self.my1 - self.my0

    def events(self):
        for event in pg.event.get():
            if event.type == pg.QUIT:
                if self.playing:
                    self.playing = False
                self.running = False
            if event.type == pg.KEYDOWN:
                if event.key == pg.K_ESCAPE:
                    if self.playing:
                        self.playing = False
                    self.running = False
                if event.key == pg.K_RETURN:
                    self.tilemap.next_player()
                if event.key == pg.K_u:
                    self.enable_ui = not self.enable_ui
                if event.key == pg.K_h:
                    self.show_path = not self.show_path
                if event.key == pg.K_t:
                    self.tooltips = not self.tooltips
                if event.key == pg.K_SPACE:
                    self.show_next_unit()

            if event.type == pg.MOUSEBUTTONDOWN:
                if event.button == 1:
                    self.clicked = True

                if event.button == 3:
                    self.right_click = True

                # if event.button == 4:
                #     self.tilesize += 4
                #     if self.tilesize >= 104:
                #         self.tilesize = 104

                # if event.button == 5:
                #     self.tilesize -= 4
                #     if self.tilesize <= 36:
                #         self.tilesize = 36

    def draw(self):
        # Game loop - draw
        self.screen.fill(WHITE)
        # draw the map
        self.tilemap.draw_tilemap(self, self.screen)
        if self.enable_ui:
            self.draw_hud()
        # after drawing everything, flip the display
        pg.display.update()

    def draw_hud(self):
        pg.draw.rect(self.screen, WHITE, (0,
                                          0, WIDTH*4/8, 40))
        self.draw_on_hud()
        draw_text(self.screen, self.tilemap.current_player,
                  self.hud_font, 25, BLACK, 10, 10)
        draw_text(self.screen, "Money: " + str(self.tilemap.players[self.tilemap.current_player]['resources']['money']),
                  self.hud_font, 25, BLACK, WIDTH*1/8, 10)
        draw_text(self.screen, "Crystals: " + str(self.tilemap.players[self.tilemap.current_player]['resources']['crystals']),
                  self.hud_font, 25, BLACK, WIDTH*2/8, 10)
        pg.draw.circle(self.screen, BLACK,
                       (WIDTH*13//14, HEIGHT*12//13), 50, 5)
        pg.draw.circle(self.screen, LIGHTBLUE,
                       (WIDTH*13//14, HEIGHT*12//13), 45)
        draw_text(self.screen, "END TURN", self.hud_font, 20,
                  BLACK, WIDTH*13//14-40, HEIGHT*12//13-15)
        draw_button(self.screen, "QUIT", self.hud_font, 20,
                    BLACK, YELLOW, DARKYELLOW, WIDTH*9//10, 10, 70, 50, quit)

    def draw_on_hud(self):
        # draw building menu
        w = WIDTH*2//5
        h = HEIGHT*1//6
        building_menu = pg.Surface((w, h))
        building_menu.fill(WHITE)
        for player in self.tilemap.players.keys():
            for building in self.tilemap.players[player]["buildings"]:
                if building.selected and building.type == 'main_base':
                    building_menu.blit(
                        self.baracks_img, (w//20, h//15, w, h))
        pg.draw.rect(building_menu, BLUE, (0,
                                           0, w, h), 5)
        self.screen.blit(building_menu, (0,
                                         HEIGHT*5/6, WIDTH*2/5, HEIGHT))

    def show_start_menu(self):
        # game splash/start screen
        pass

    def show_go_screen(self):
        pass

    def show_next_unit(self):
        # center the camera on the next unit of the current player
        player_units = self.tilemap.players[self.tilemap.current_player]['units']
        index = self.camera_counter % len(player_units)
        self.camera_counter += 1
        self.camera.apply_camera(self, player_units[index].pos)


if __name__ == '__main__':
    g = Game()
    g.show_start_menu()
    while g.running:
        g.new()
        g.show_go_screen()

    pg.quit()
    sys.exit()
