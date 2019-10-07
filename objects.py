''' Objects of the tilemap'''

import sys

import pygame as pg

from search import vec2int
from settings import *

vec = pg.math.Vector2


class Camera:
    def __init__(self, game):
        self.game = game
        self.pos = None

    def apply_camera(self, game, object_pos):
        ''' Apply the camera to an object'''
        self.pos = object_pos
        game.offset[0] = BOARD_TOPLEFT[0] - self.pos.x * 64
        game.offset[1] = BOARD_TOPLEFT[1] - self.pos.y * 64


class Unit:
    def __init__(self, tilemap, start_tile, player):
        self.type = 'unit_template'
        self.class_ = 'units'
        self.image = pg.Surface((tilemap.tilesize, tilemap.tilesize))
        self.rect = self.image.get_rect()
        self.pos = vec(start_tile)
        self.rect.x = self.pos.x * TILESIZE
        self.rect.y = self.pos.y * TILESIZE
        self.allegiance = player
        self.destination = None
        self.total_MP = 20
        self.current_MP = self.total_MP
        self.total_AP = 2
        self.current_AP = self.total_AP
        self.total_HP = 100
        self.current_HP = self.total_HP
        self.defense = 50
        self.attack = 10
        self.range = 1
        self.kill_count = 0
        self.exp = 0
        self.exp_reward = 50
        self.selected = False
        self.moved = False
        self.can_cross_water = False
        self.attacks = {
            'slash':
            {'cost': 1,
             'dmg': 60,
             'special_effect': None}
        }
        self.last_time = 0

    def distance_between(self, node1, node2):
        # the distance from the unit in a straight line
        if abs(node2.x - node1.x) >= abs(node2.y - node1.y):
            return abs(node2.x - node1.x)
        else:
            return abs(node2.y - node1.y)

    def move(self, tilemap, start, goal_pos):
        next_pos = start + tilemap.path[vec2int(start)]
        next_node = tilemap.nodes[int(next_pos.x)][int(next_pos.y)]
        if self.current_MP >= next_node.entering_cost:
            self.pos = next_pos
            self.rect = self.pos * TILESIZE
            self.current_MP -= next_node.entering_cost
            while self.pos != goal_pos:
                now = pg.time.get_ticks()
                if now - self.last_time >= 200:
                    self.last_time = now
                    next_pos = self.pos + tilemap.path[vec2int(self.pos)]
                    next_node = tilemap.nodes[int(next_pos.x)][int(next_pos.y)]
                    if self.current_MP >= next_node.entering_cost:
                        if next_pos == goal_pos and next_node.occupants is not None:
                            print('target reached')
                            break
                        self.pos = next_pos
                        self.rect = self.pos * TILESIZE
                        self.current_MP -= next_node.entering_cost
                        tilemap.game.draw()

    def attacking(self, chosen_attack, target_unit):
        if self.distance_between(self.pos, target_unit.pos) <= self.range:
            self.current_AP -= self.attacks[chosen_attack]['cost']
            target_unit.current_HP -= self.attacks[chosen_attack]['dmg']

    def turn_inactive(self):
        self.moved = True
        self.selected = False
        self.image = self.image.copy()
        self.image.fill((255, 255, 255, 210), None, pg.BLEND_RGBA_MULT)

    def draw(self, tilemap, screen):
        screen.blit(
            self.image, (tilemap.offset[0] + self.rect.x, tilemap.offset[1] + self.rect.y))
        if self.selected:
            pg.draw.rect(screen, BLUE, (self.rect.x + tilemap.offset[0],
                                        self.rect.y + tilemap.offset[1],
                                        tilemap.tilesize, tilemap.tilesize), 3)


class MainBase(Unit):
    def __init__(self, tilemap, start_tile, player):
        super().__init__(tilemap, start_tile, player)
        self.image = tilemap.game.main_base_img
        self.selected = False
        self.type = 'main_base'

    # def draw_building_menu(self, game):
    #     if self.selected:
    #         game.screen.blit(
    #             game.baracks_img, (WIDTH*1//20, HEIGHT*18//20))


class Baracks(Unit):
    def __init__(self, tilemap, start_tile, player):
        super().__init__(tilemap, start_tile, player)
        self.image = tilemap.game.baracks_img
        self.selected = False


class Scout(Unit):
    def __init__(self, tilemap, start_tile, player):
        super().__init__(tilemap, start_tile, player)
        self.type = 'scout'
        self.image = tilemap.game.unit_img
        self.active_image = self.image
        self.total_MP = 30
        self.current_MP = self.total_MP


class Warrior(Unit):
    def __init__(self, tilemap, start_tile, player):
        super().__init__(tilemap, start_tile, player)
        self.type = 'warrior'
        self.image = tilemap.game.unit_img
        self.image.set_colorkey(WHITE)
        self.active_image = self.image
        self.total_MP = 20
        self.current_MP = self.total_MP


class Horseman(Unit):
    def __init__(self, tilemap, start_tile, player):
        super().__init__(tilemap, start_tile, player)
        self.type = 'horseman'
        self.image = tilemap.game.unit_img
        self.active_image = self.image
        self.total_HP = 80
        self.current_HP = self.total_HP
        self.total_MP = 60
        self.current_MP = self.total_MP


class Axeman(Unit):
    def __init__(self, tilemap, start_tile, player):
        super().__init__(tilemap, start_tile, player)
        self.type = 'axeman'
        self.image = tilemap.game.unit_img
        self.active_image = self.image
        self.total_HP = 150
        self.current_HP = self.total_HP
        self.total_MP = 30
        self.current_MP = self.total_MP


def draw_text(screen, text, font_name, size, color, x, y, align="nw", background_color=None):
    font = pg.font.Font(font_name, size)
    text_surface = font.render(text, True, color, background_color)
    text_rect = text_surface.get_rect()
    if align == "nw":
        text_rect.topleft = (x, y)
    if align == "ne":
        text_rect.topright = (x, y)
    if align == "sw":
        text_rect.bottomleft = (x, y)
    if align == "se":
        text_rect.bottomright = (x, y)
    if align == "n":
        text_rect.midtop = (x, y)
    if align == "s":
        text_rect.midbottom = (x, y)
    if align == "e":
        text_rect.midright = (x, y)
    if align == "w":
        text_rect.midleft = (x, y)
    if align == "center":
        text_rect.center = (x, y)
    screen.blit(text_surface, text_rect)


def draw_button(screen, text, font_name, size, text_color, inactive_color, active_color, x, y, w, h, action=None):
    mouse = pg.mouse.get_pos()
    click = pg.mouse.get_pressed()
    button_rect = pg.Rect(x, y, w, h)
    font = pg.font.Font(font_name, size)
    pg.draw.rect(screen, inactive_color, button_rect)
    pg.draw.rect(screen, BLACK, (x+1, y+1, w, h), 2)
    if button_rect.collidepoint(mouse):
        pg.draw.rect(screen, active_color, button_rect)
        if click[0] == 1 and action != None:
            action()
    text_surface = font.render(text, True, text_color)
    text_rect = text_surface.get_rect()
    text_rect.center = ((x+(w/2)), (y+(h/2)))
    screen.blit(text_surface, text_rect)


# def draw_circular_button(screen, text, font_name, size, text_color, inactive_color, active_color, x, y, rad, action=None):
#     pg.draw.circle(screen, inactive_color, (x, y), rad, 3)
#     pg.draw.circle(screen, active_color, (x, y), rad)
#     draw_text(screen, "END TURN", font_name, size,
#               text_color, x, HEIGHT*12//13-15)


def quit():
    pg.quit()
    sys.exit()
