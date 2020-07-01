import pygame
import constants as c

def draw(self):
    """argument self is game"""
    # clear
    self.screen_surface.fill(c.BLACK)

    # draw
    if self.my_role:
        draw_logged_in_state(self)
    else:
        draw_not_logged_in_state(self)

    # flip
    pygame.display.flip()

def draw_logged_in_state(self):
    # draw map
    now_map = self.my_role.map
    if now_map == 'port' or now_map == 'sea':
        self.screen_surface.blit(self.images[now_map], (0, 0))
    else:
        self.screen_surface.blit(self.images['battle'], (0, 0))

    # draw based on map
    if now_map == 'port':
        draw_in_port(self)
    elif now_map == 'sea':
        draw_at_sea(self)
    else:
        draw_in_battle(self)

    # draw speach
    draw_speech(self)

    # draw ui
    self.ui_manager.draw_ui(self.screen_surface)

def draw_in_port(self):
    # draw my role
    self.screen_surface.blit(self.images['person_in_port'], (self.my_role.x, self.my_role.y))

    # draw other roles
    for role in self.other_roles.values():
        self.screen_surface.blit(self.images['person_in_port'], (role.x, role.y))

def draw_at_sea(self):
    # draw my role
    self.screen_surface.blit(self.images['ship_at_sea'], (self.my_role.x, self.my_role.y))

    # draw other roles
    for role in self.other_roles.values():
        self.screen_surface.blit(self.images['ship_at_sea'], (role.x, role.y))

def draw_in_battle(self):
    draw_my_ships(self)
    draw_enemy_ships(self)
    draw_battle_timer(self)

def draw_my_ships(self):
    # my ships
    index = 0
    for ship in self.my_role.ships:
        index += 30

        # ship
        self.screen_surface.blit(self.images['ship_at_sea'], (10, 10 + index))

        # # state
        # if ship.state == 'shooting':
        #     self.screen_surface.blit(Ship.shooting_img, (60, 10 + index))
        # elif ship.state == 'shot':
        #     damage_img = g_font.render(ship.damage_got, True, COLOR_BLACK)
        #     self.screen_surface.blit(damage_img, (60, 10 + index))

        # hp
        now_hp_img = self.font.render(str(ship.now_hp), True, c.BLACK)
        self.screen_surface.blit(now_hp_img, (20 + 20, 10 + index))

def draw_enemy_ships(self):
    # enemy ships
    index = 0
    for ship in self.other_roles[self.my_role.enemy_name].ships:
        index += 30

        # ship
        self.screen_surface.blit(self.images['ship_at_sea'], (c.WINDOW_WIDTH - 50, 10 + index))

        # # state
        # if ship.state == 'shooting':
        #     g_screen.blit(Ship.shooting_img, (WIDTH - 100, 10 + index))
        # elif ship.state == 'shot':
        #     damage_img = g_font.render(ship.damage_got, True, COLOR_BLACK)
        #     g_screen.blit(damage_img, (WIDTH - 100, 10 + index))

        # hp
        now_hp_img = self.font.render(str(ship.now_hp), True, c.BLACK)
        self.screen_surface.blit(now_hp_img, (c.WINDOW_WIDTH - 70 - 10, 10 + index))

def draw_battle_timer(self):
    # me
    my_timer_text = None
    if self.my_role.your_turn_in_battle:
        my_timer_text = 'Your Turn'
    else:
        my_timer_text = 'Please Wait...'

    my_timer_img = self.font.render(my_timer_text, True, c.BLACK)
    self.screen_surface.blit(my_timer_img, (20, 5))

    # enemy
    enemy_timer_text = None
    if self.other_roles[self.my_role.enemy_name].your_turn_in_battle:
        enemy_timer_text = 'Your Turn'
    else:
        enemy_timer_text = 'Please Wait...'

    enemy_timer_img = self.font.render(enemy_timer_text, True, c.BLACK)
    self.screen_surface.blit(enemy_timer_img, (c.WINDOW_WIDTH - 150, 5))

def draw_speech(self):
    # my
    my_speak_img = self.font.render(self.my_role.speak_msg, True, c.BLACK)
    self.screen_surface.blit(my_speak_img, (self.my_role.x, self.my_role.y - 40))

    # others
    for role in self.other_roles.values():
        speak_img = self.font.render(role.speak_msg, True, c.BLACK)
        self.screen_surface.blit(speak_img, (role.x, role.y - 40))

def draw_not_logged_in_state(self):
    """argument self is game"""
    text_surface = self.font.render('Please Login', True, c.WHITE)
    self.screen_surface.blit(text_surface, (5, 5))