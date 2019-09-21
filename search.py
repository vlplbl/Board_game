from collections import deque
import heapq
import pygame as pg
vec = pg.math.Vector2


class PriorityQueue:
    def __init__(self):
        self.nodes = []

    def put(self, node, cost):
        heapq.heappush(self.nodes, (cost, node))

    def get(self):
        return heapq.heappop(self.nodes)[1]

    def empty(self):
        return len(self.nodes) == 0


def heuristic(node1, node2):
    return (abs(node1.x - node2.x) + abs(node1.y - node2.y)) * 10


def a_star_search(tilemap, start, end):
    frontier = PriorityQueue()
    frontier.put(vec2int(start), 0)
    path = {}
    cost = {}
    path[vec2int(start)] = None
    cost[vec2int(start)] = 0

    while not frontier.empty():
        current = frontier.get()
        if current == end:
            break
        for next in tilemap.find_neighbours(vec(current)):
            next = vec2int(next)
            next_cost = cost[current] + tilemap.cost(current, next)
            if next not in cost or next_cost < cost[next]:
                cost[next] = next_cost
                priority = next_cost + heuristic(end, vec(next))
                frontier.put(next, priority)
                path[next] = vec(current) - vec(next)
    return path


def dijkstra_search(tilemap, start, end):
    frontier = PriorityQueue()
    frontier.put(vec2int(start), 0)
    path = {}
    cost = {}
    path[vec2int(start)] = None
    cost[vec2int(start)] = 0

    while not frontier.empty():
        current = frontier.get()
        if current == end:
            break
        for next in tilemap.find_neighbours(vec(current)):
            next = vec2int(next)
            next_cost = cost[current] + tilemap.cost(current, next)
            if next not in cost or next_cost < cost[next]:
                cost[next] = next_cost
                priority = next_cost
                frontier.put(next, priority)
                path[next] = vec(current) - vec(next)
    return path


def vec2int(v):
    # converts a vector to tuple
    return (int(v.x), int(v.y))


def breadth_first_search(tilemap, start_pos, target_pos):
    '''requires a dict of neighbour tiles, goal and start tiles'''
    frontier = deque()
    frontier.append(start_pos)
    path = {}
    path[vec2int(start_pos)] = None
    while len(frontier) > 0:
        current = frontier.popleft()
        if current == target_pos:
            break
        for next in tilemap.find_neighbours(current):
            if vec2int(next) not in path:
                frontier.append(next)
                path[vec2int(next)] = current - next
    return path
