''' Tilemap object and game logic on the tilemap'''

import random
from collections import deque
import pygame as pg
from objects import *
from settings import *
from search import *
vec = pg.math.Vector2


class BoardImage:
    def __init__(self, tilemap):
        self.tilemap = tilemap
        self.image = pg.Surface(
            (BOARDWIDTH * self.tilemap.tilesize, BOARDHEIGHT * self.tilemap.tilesize))
        self.rect = self.image.get_rect()

    def update(self):
        self.rect.x += self.tilemap.offset[0]
        self.rect.y += self.tilemap.offset[1]

    def draw(self, screen):
        screen.blit(
            self.image, (self.tilemap.offset[0], self.tilemap.offset[1]))


class Node:
    def __init__(self, tilemap, position, terrain_letter):
        self.tilemap = tilemap
        self.type = terrain_letter
        self.frequency = self.tilemap.terrain_dict[self.type]['frequency']
        self.name = self.tilemap.terrain_dict[self.type]['name']
        self.entering_cost = self.tilemap.terrain_dict[self.type]['entering_cost']
        self.resorces = self.tilemap.terrain_dict[self.type]['resorces']
        self.defence = self.tilemap.terrain_dict[self.type]['defence']
        self.occupants = self.tilemap.terrain_dict[self.type]['occupants']
        self.image = self.tilemap.terrain_dict[self.type]['img']
        self.rect = self.image.get_rect()
        self.rect.topleft = position
        self.pos = vec((self.rect.x - self.tilemap.offset[0]) // self.tilemap.tilesize,
                       (self.rect.y - self.tilemap.offset[1]) // self.tilemap.tilesize)

    def update(self, position):
        self.rect.topleft = position


class Tilemap:
    def __init__(self, game):
        '''show a map image with number of tiles and TILESIZE'''
        self.game = game
        self.tilesize = game.tilesize
        self.offset = game.offset
        self.terrain_dict = {
            "F":
            {'name': "forest",
             'frequency': FOREST_FREQUENCY,
             'entering_cost': FOREST_ENTERING_COST,
             'img': game.forest_img,
             'defence': FOREST_DEFENCE,
             'resorces': {'wood': 2, 'stone': 0, 'iron': 0},
             'occupants': None},
            "G":
            {'name': "grassland",
             'frequency': GRASS_FREQUENCY,
             'entering_cost': GRASS_ENTERING_COST,
             'defence': GRASS_DEFENCE,
             'img': game.grass_img,
             'resorces': {'wood': 0, 'stone': 0, 'iron': 0},
             'occupants': None},
            "W":
            {'name': "water",
             'frequency': WATER_FREQUENCY,
             'entering_cost': WATER_ENTERING_COST,
             'defence': WATER_DEFENCE,
             'img': game.water_img,
             'resorces': {'wood': 0, 'stone': 0, 'iron': 0},
             'occupants': None},
            "M":
            {'name': "mountain",
             'frequency': MOUNTAIN_FREQUENCY,
             'entering_cost': MOUNTAIN_ENTERING_COST,
             'defence': MOUNTAIN_DEFENCE,
             'img': game.mountain_img,
             'resorces': {'wood': 0, 'stone': 2, 'iron': 0},
             'occupants': None}
        }
        self.players = {
            "player1":
            {"units": [Swordsman(self, vec(10, 7), 'player1'), Axeman(self, vec(11, 7), 'player1')],
             "buildings": [MainBase(self, vec(12, 7), 'player1')]},
            "player2":
            {"units": [Swordsman(self, vec(i, 4), 'player2')
                       for i in range(10, 14)],
             "buildings": [MainBase(self, vec(12, 4), 'player2')]}
            # }
            # self.teams = {
            #     'team1': self.players['player1'],
            #     'team2': self.players['player2']
            # }
        }
        self.teams = {
            'player1': 'team1',
            'player2': 'team2'
        }
        self.players_list = [key for key in self.players.keys()]
        self.current_player = "player1"
        self.pos = (0, 0)
        self.generate_terrain()
        self.nodes = [[Node(self, [j*self.tilesize + self.offset[0], i*self.tilesize + self.offset[1]],
                            random.choice(self.terrain_list)) for i in range(BOARDHEIGHT)] for j in range(BOARDWIDTH)]
        # define a list of unpassable tiles
        self.walls = [[j, i] for i in range(BOARDHEIGHT) for j in range(
            BOARDWIDTH) if self.nodes[j][i].type == 'M']
        # draw each tile image on the tilemap surface to avoid drawing every tile every turn
        self.board_image = BoardImage(self)
        for lst in self.nodes:
            for node in lst:
                self.board_image.image.blit(
                    node.image, (node.rect.x - self.offset[0], node.rect.y - self.offset[1]))
        self.connections = [vec(1, 0), vec(1, 1), vec(0, 1),
                            vec(-1, 1), vec(-1, 0), vec(-1, -1), vec(0, -1), vec(1, -1)]
        self.weights = {
            vec2int(node.pos): node.entering_cost for row in self.nodes for node in row}
        self.path = {}
        # self.assign_objects_to_map()
        self.target_tile = vec(0, 0)
        self.target_pos = vec(0, 0)
        self.last_time = 0
        self.from_node = None

    def assign_objects_to_map(self):
        # map each unit to it's tile
        for i, col in enumerate(self.nodes):
            for j, node in enumerate(col):
                for player in self.players:
                    for unit in self.players[player]['units']:
                        if node.pos == unit.pos:
                            node.occupants = unit

    def generate_terrain(self):
        # make random weighed terrain nodes by the terrain type frequency from the terrain dict
        terrain_letters = [i for i in self.terrain_dict.keys()]
        frequency = [self.terrain_dict[i][j] for i in self.terrain_dict.keys(
        ) for j in self.terrain_dict[i].keys() if j == 'frequency']
        self.terrain_list = random.choices(
            terrain_letters, weights=frequency, k=100)

    def cost(self, from_node, to_node):
        if (vec(to_node) - vec(from_node)).length_squared() == 1:
            return self.weights.get(to_node, 0) + 10
        else:
            return self.weights.get(to_node, 0) + 14

    def in_bounds(self, node):
        return 0 <= node.x < BOARDWIDTH and 0 <= node.y < BOARDHEIGHT

    def passable(self, node):
        return node not in self.walls

    def find_neighbours(self, node):
        neighbors = [node + connection for connection in self.connections]
        neighbors = filter(self.in_bounds, neighbors)
        neighbors = filter(self.passable, neighbors)
        return neighbors

    # def shortest_distance(self, start_vec, end_vec):
    #     for col in self.nodes:
    #         for node in col:
    #             current = start_vec + self.path[vec2int(start_vec)]
    #             while current != end_vec:
    #                 if node.pos == vec2int(current):
    #                     self.node_path.append(vec2int(current))
    #                 current = current + self.path[vec2int(current)]
    #     self.node_path.append(vec2int(end_vec))
    #     return self.node_path

    def next_player(self):
        for unit in self.players[self.current_player]['units']:
            unit.selected = False
            unit.turn_inactive()
        if self.current_player == self.players_list[-1]:
            self.current_player = self.players_list[0]
        else:
            i = self.players_list.index(self.current_player)
            self.current_player = self.players_list[i+1]
        for unit in self.players[self.current_player]['units']:
            unit.current_AP = unit.total_AP
            unit.current_MP = unit.total_MP
            unit.moved = False
            unit.image = unit.active_image
            unit.selected = False

    def get_mouse_pos(self):
        mx, my = pg.mouse.get_pos()
        mx_pos = (mx - self.offset[0]) // TILESIZE
        my_pos = (my - self.offset[1]) // TILESIZE
        return vec(mx_pos, my_pos)

    def update_map(self, game):
        self.board_image.update()
        # update the position of the maptiles
        for i, col in enumerate(self.nodes):
            for j, node in enumerate(col):
                node.update([i*self.tilesize + self.offset[0],
                             j*self.tilesize + self.offset[1]])
                # # map each unit to it's tile
                for player in self.players:
                    for unit in self.players[player]['units']:
                        if node.pos == unit.pos:
                            node.occupants = unit
                # for building in self.players[player]['buildings']:
                #     if node.pos == building.pos:
                #         node.pos == building.pos
                if node.pos == self.get_mouse_pos():
                    if game.clicked:
                        # deselect all other selections
                        for all_units in self.players[self.current_player]["units"]:
                            all_units.selected = False
                        for all_buildings in self.players[self.current_player]['buildings']:
                            all_buildings.selected = False
                        # select a unit with left click
                        if node.occupants != None:
                            node.occupants.selected = True
                            # self.from_node = node
                        game.clicked = False
                        game.right_click = False

        # move the selected unit on the click position
        for i, col in enumerate(self.nodes):
            for j, node in enumerate(col):
                if node.pos == self.get_mouse_pos():
                    for unit in self.players[self.current_player]["units"]:
                        from_node = self.nodes[int(
                            unit.pos.x)][int(unit.pos.y)]
                        # move the unit
                        if game.right_click and unit.selected and not unit.moved:
                            if node.pos == unit.pos:
                                game.right_click = False
                            elif node.occupants == None:
                                unit.move(self, vec(unit.rect.x // self.tilesize,
                                                    (unit.rect.y // self.tilesize)))
                                # update the starting node and make the new one starting
                                from_node.occupants = None
                                node.occupants = unit
                                # self.from_node.occupants = None
                                # self.from_node = node
                                game.right_click = False
                        # attack
                        if game.right_click and unit.selected and node.occupants != None:
                            unit_team = self.teams[node.occupants.allegiance]
                            target_team = self.teams[unit.allegiance]
                            target_player = node.occupants.allegiance
                            target_class = node.occupants._class
                            if unit_team != target_team:
                                if unit.selected and unit.current_AP > 0:
                                    print('attacking')
                                    unit.attacking('slash', node.occupants)
                                    game.right_click = False
                                    if unit.current_AP <= 0:
                                        unit.turn_inactive()
                                    if node.occupants.current_HP <= 0:
                                        index = self.players[target_player][target_class].index(
                                            node.occupants)
                                        del self.players[target_player][target_class][index]
                                        unit.kill_count += 1
                                        unit.exp += node.occupants.exp_reward
                                        node.occupants = None
                            # switch position with a friendly unit
                            else:
                                last_pos = from_node.rect
                                target_rect = node.rect
                                if unit.is_valid_pos(self, vec2int(node.pos)) and node.occupants.is_valid_pos(self, vec2int(self.from_node.pos)):
                                    unit.update(self, vec((target_rect.x - self.offset[0]) // self.tilesize,
                                                          (target_rect.y - self.offset[1]) // self.tilesize))
                                    node.occupants.update(self, vec((last_pos.x - self.offset[0]) // self.tilesize,
                                                                    (last_pos.y - self.offset[1]) // self.tilesize))
                                    from_node = node
                                    from_node.occupants = node.occupants
                                    game.right_click = False
                                game.right_click = False

        # deselect if clicking outside of the map
        if self.mouse_outside_board_surf() and game.clicked:
            game.clicked = False
            for unit in self.players[self.current_player]["units"]:
                unit.selected = False

    def mouse_outside_board_surf(self):
        if self.board_image.rect.collidepoint(pg.mouse.get_pos()):
            return False
        return True

    def draw_tilemap(self, game, screen):
        '''build a map with number of tiles and TILESIZE'''
        now = pg.time.get_ticks()
        self.board_image.draw(screen)
        # draw a grid
        for i in range(BOARDHEIGHT):
            for j in range(BOARDWIDTH):
                rect = pg.Rect(self.offset[0] + j * self.tilesize,
                               self.offset[1] + i * self.tilesize, self.tilesize, self.tilesize)
                pg.draw.rect(screen, DARKGREY, (rect), 1)
        # draw the objects on the screen
        for player in self.players.keys():
            for building in self.players[player]["buildings"]:
                building.draw(self, screen)
        for player in self.players.keys():
            for unit in self.players[player]["units"]:
                unit.draw(self, screen)
        # draw movement path of the selected unit
        for unit in self.players[self.current_player]["units"]:
            if unit.selected and self.get_mouse_pos() != unit.pos:
                self.path = a_star_search(
                    self, self.get_mouse_pos(), unit.pos)
                self.draw_path(screen, self.get_mouse_pos(), unit.pos)
        if game.show_path:
            self.draw_explored_tiles(screen)
        # draw tooltips
        self.draw_tooltips(game, screen)

    def draw_tooltips(self, game, screen):
        now = pg.time.get_ticks()
        mx, my = pg.mouse.get_pos()
        click = pg.mouse.get_pressed()
        if pg.mouse.get_rel() != (0, 0) or click[0]:
            self.last_time = now + TOOLTIP_DELAY
        if game.tooltips:
            for i, col in enumerate(self.nodes):
                for j, node in enumerate(col):
                    if self.get_mouse_pos() == node.pos and now > self.last_time:
                        if node.occupants != None:
                            pg.draw.rect(
                                screen, BLACK, (mx+15, my, 150, 130))
                        else:
                            pg.draw.rect(
                                screen, BLACK, (mx+15, my, 150, 60))
                        draw_text(screen, node.name,
                                  game.hud_font, 15, WHITE, mx+20, my, background_color=BLACK)
                        draw_text(screen, "Movement cost: " + str(node.entering_cost),
                                  game.hud_font, 15, WHITE, mx+20, my + 18, background_color=BLACK)
                        draw_text(screen, "Defence: " + str(node.defence),
                                  game.hud_font, 15, WHITE, mx+20, my + 36, background_color=BLACK)
                        if node.occupants != None:
                            draw_text(screen, "occupied by: ",
                                      game.hud_font, 15, WHITE, mx+20, my + 54, background_color=BLACK)
                            draw_text(screen, str(node.occupants.allegiance + ' ' + str(node.occupants.type)),
                                      game.hud_font, 15, WHITE, mx+20, my + 72, background_color=BLACK)
                            draw_text(screen, "Current MP: " + str(node.occupants.current_MP),
                                      game.hud_font, 15, WHITE, mx+20, my + 90, background_color=BLACK)

                            draw_text(screen, "Current HP: " + str(node.occupants.current_HP),
                                      game.hud_font, 15, WHITE, mx+20, my + 108, background_color=BLACK)

    def draw_path(self, screen, target_pos, start_pos):
        # draw the shortest path
        current = start_pos + self.path[vec2int(start_pos)]
        while current != target_pos:
            pg.draw.circle(screen, RED, (int(current.x * 64 + 32 + self.offset[0]),
                                         int(current.y * 64 + 32 + self.offset[1])), 10)
            current = current + self.path[vec2int(current)]

    def draw_explored_tiles(self, screen):
        # draw the explored tiles
        for key in self.path.keys():
            screen.blit(self.game.dim_screen, (int(key[0] * 64 + self.offset[0]),
                                               int(key[1] * 64 + self.offset[1]), 64, 64))
