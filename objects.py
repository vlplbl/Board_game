''' Objects of the tilemap'''

import sys
from search import *
import pygame as pg
from settings import *
vec = pg.math.Vector2


class Camera:
    def __init__(self, game):
        self.game = game

    def apply_camera(self, game, object_pos):
        self.pos = object_pos
        game.offset[0] = BOARD_TOPLEFT[0] - self.pos.x * 64
        game.offset[1] = BOARD_TOPLEFT[1] - self.pos.y * 64


class Unit:
    def __init__(self, tilemap, start_tile, player):
        self.type = 'unit_template'
        self._class = 'units'
        self.image = pg.Surface((tilemap.tilesize, tilemap.tilesize))
        self.rect = self.image.get_rect()
        self.pos = vec(start_tile)
        self.rect.x = self.pos.x * TILESIZE
        self.rect.y = self.pos.y * TILESIZE
        self.allegiance = player
        self.total_MP = 2
        self.current_MP = self.total_MP
        self.total_AP = 2
        self.current_AP = self.total_AP
        self.total_HP = 100
        self.current_HP = self.total_HP
        self.defense = 50
        self.attack = 10
        self.range = 2
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

    def distance_between(self, node1, node2):
        return abs(node2.x - node1.x) + abs(node2.y - node1.y)

    def update(self, tilemap, destination):
        if self.is_valid_pos(tilemap, vec2int(destination)):
            self.last_pos = self.pos
            self.pos = destination
            self.rect = self.pos * TILESIZE
            self.current_MP -= int(
                self.distance_between(self.last_pos, destination))

    def move(self, tilemap, start):
        self.pos = start + tilemap.path[vec2int(start)]
        self.rect = self.pos * TILESIZE

    def attacking(self, chosen_attack, target_unit):
        if self.distance_between(self.pos, target_unit.pos) <= self.range:
            self.current_AP -= self.attacks[chosen_attack]['cost']
            target_unit.current_HP -= self.attacks[chosen_attack]['dmg']

    def turn_inactive(self):
        self.moved = True
        self.selected = False
        self.image = self.image.copy()
        self.image.fill((255, 255, 255, 210), None, pg.BLEND_RGBA_MULT)

    def is_valid_pos(self, tilemap, destination):
        if tilemap.nodes[destination[0]][destination[1]].type != 'W'\
                and tilemap.nodes[destination[0]][destination[1]].type != 'M':
            if self.distance_between(self.pos, vec(destination)) <= self.current_MP:
                return True
            else:
                return False

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

    def update(self):
        pass


class Swordsman(Unit):
    def __init__(self, tilemap, start_tile, player):
        super().__init__(tilemap, start_tile, player)
        self.type = 'swordsman'
        self.image = tilemap.game.unit_img
        self.active_image = self.image


class Axeman(Unit):
    def __init__(self, tilemap, start_tile, player):
        super().__init__(tilemap, start_tile, player)
        self.type = 'axeman'
        self.image = tilemap.game.unit_img
        self.active_image = self.image
        self.total_HP = 150
        self.current_HP = self.total_HP
        self.total_MP = 3
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
