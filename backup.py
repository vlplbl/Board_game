# attack
if game.right_click and unit.selected and node.occupants != None:
        unit_team = self.teams[node.occupants.allegiance]
        target_team = self.teams[unit.allegiance]
        target_player = node.occupants.allegiance
        target_class = node.occupants._class
        if unit_team != target_team:
            if unit.selected and unit.current_AP > 0:
                if unit.distance_between(unit.pos, self.get_mouse_pos()) > 1:
                    unit.move(self, unit.pos,
                              (self.get_mouse_pos() - self.path[vec2int(unit.pos)]))
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
