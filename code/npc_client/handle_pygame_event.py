import pygame
from twisted.internet import reactor, task

# add relative directory to python_path
import sys, os
sys.path.append(os.path.join(os.path.dirname(__file__), '..', 'common'))

# import from common(dir)
import constants as c
from hashes.hash_ports_meta_data import hash_ports_meta_data
import gui
from pygame_gui._constants import UI_WINDOW_CLOSE
from port_npc import Dog, OldMan, Agent, Man, Woman
import port_npc

EVENT_MOVE = pygame.USEREVENT + 1
EVENT_HEART_BEAT = pygame.USEREVENT + 2

def handle_pygame_event(self, event):
    """argument self is game"""
    # quit
    if event.type == pygame.QUIT:
        quit(self, event)

    # key down
    elif event.type == pygame.KEYDOWN:

        # return (focus text entry)
        if event.key == pygame.K_RETURN:
            self.text_entry.focus()
            self.text_entry_active = True

        # escape
        if event.key == pygame.K_ESCAPE:
            escape(self, event)

        # other keys
        if not self.text_entry_active:
            other_keys_down(self, event)

    # key up
    elif event.type == pygame.KEYUP:
            key_up(self, event)

    # mouse button down
    elif event.type == pygame.MOUSEBUTTONDOWN:
        # left button
        if event.button == 1:
            if self.other_roles_rects:
                # set target
                for name, rect in self.other_roles_rects.items():
                    if rect.collidepoint(event.pos):
                        self.my_role.enemy_name = name
                        print('target set to:', name)
                        return

                # clear target
                # if self.menu_stack == 0:
                #     if self.my_role.map == 'sea' or str(self.my_role.map).isdigit():
                #         self.my_role.enemy_name = ''

        # right button
        elif event.button == 3:
            if self.other_roles_rects:
                # set target
                for name, rect in self.other_roles_rects.items():
                    if rect.collidepoint(event.pos):
                        self.my_role.enemy_name = name
                        print('target set to:', name)
                        gui.target_clicked(self)
                        return

                # clear target
                # if self.menu_stack == 0:
                #     if self.my_role.map == 'sea' or str(self.my_role.map).isdigit():
                #         self.my_role.enemy_name = ''

    # user defined events
    elif event.type == EVENT_MOVE:
        user_event_move(self, event)
    elif event.type == EVENT_HEART_BEAT:
        self.change_and_send('heart_beat', [])

    elif event.type == pygame.USEREVENT:
        if event.user_type == UI_WINDOW_CLOSE:
            self.menu_stack.pop()
            self.selection_list_stack.pop()
            print('event ui window close!')
            print('stack length:', len(self.menu_stack))

def quit(self, event):
    # when in game
    if self.my_role:
        if self.my_role.map.isdigit():
            reactor.stop()
            pygame.quit()
            sys.exit()
        else:
            self.button_click_handler. \
                make_message_box('Exit while in port please.')
            print('Exit while in port please.')
    # when not in game
    else:
        pygame.quit()
        reactor.stop()
        sys.exit()

def escape(self, event):

    # exit building
    if len(self.menu_stack) == 1:
        if self.my_role:
            self.my_role.in_building_type = None

    # pop menu_stack
    if len(self.menu_stack) > 0:
        menu_to_kill = self.menu_stack[-1]
        menu_to_kill.kill()
    print('escape pressed!')

    # clear buttons_in_windows dict
    self.buttons_in_windows.clear()
    print('buttons_in_windows dict cleared!')

    # deactivate text entry
    self.text_entry_active = False

# def init_key_mappings(self):
#     """cmds that change local state and sent to server"""
#     self.key_mappings = {
#         # battle
#         'b': ['try_to_fight_with', ['b']],
#         'e': ['exit_battle', []],
#         'k': ['shoot_ship', [0, 0]],
#     }

def other_keys_down(self, event):

    # start move
    if event.key == ord('d'):
        self.change_and_send('start_move', [self.my_role.x, self.my_role.y, 'right'])
    elif event.key == ord('a'):
        self.change_and_send('start_move', [self.my_role.x, self.my_role.y, 'left'])
    elif event.key == ord('w'):
        self.change_and_send('start_move', [self.my_role.x, self.my_role.y, 'up'])
    elif event.key == ord('s'):
        self.change_and_send('start_move', [self.my_role.x, self.my_role.y, 'down'])

    elif event.key == ord('e'):
        self.change_and_send('start_move', [self.my_role.x, self.my_role.y, 'ne'])
    elif event.key == ord('q'):
        self.change_and_send('start_move', [self.my_role.x, self.my_role.y, 'nw'])
    elif event.key == ord('z'):
        self.change_and_send('start_move', [self.my_role.x, self.my_role.y, 'sw'])
    elif event.key == ord('x'):
        self.change_and_send('start_move', [self.my_role.x, self.my_role.y, 'se'])

    # logins
    if chr(event.key).isdigit():
        self.connection.send('login', [chr(event.key), chr(event.key)])

    # change map to sea
    if event.key == ord('n'):
        self.button_click_handler.menu_click_handler.port.port.sail_ok()

    # change map to port
    elif event.key == ord('m'):
        if not self.my_role.map.isdigit():
            port_id = get_nearby_port_index(self)
            if port_id or port_id == 0:
                self.connection.send('change_map', [str(port_id), self.days_spent_at_sea])
                self.timer_at_sea.stop()

                # make npcs
                if port_id < 100:
                    port_npc.init_static_npcs(self, port_id)
                    port_npc.init_dynamic_npcs(self, port_id)
                else:
                    self.dog = None
                    self.old_man = None
                    self.agent = None

                    self.man = None
                    self.woman = None

    # enter building
    if event.key == ord('f'):
        self.button_click_handler.menu_click_handler.cmds.enter_building()

    # battle
    if event.key == ord('b'):
        if self.my_role.enemy_name:
            enemy_role = self.my_role._get_other_role_by_name(self.my_role.enemy_name)
            my_role = self.my_role
            if abs(enemy_role.x - my_role.x) <= 50 and abs(enemy_role.y - my_role.y) <= 50:
                self.connection.send('try_to_fight_with', [self.my_role.enemy_name])
            else:
                self.button_click_handler. \
                    make_message_box("Target too far!")
    elif event.key == ord('e'):
        if 'battle' in self.my_role.map:
            if self.my_role.your_turn_in_battle:
                self.connection.send('exit_battle', [])
    elif event.key == ord('k'):
        self.button_click_handler.menu_click_handler.battle.all_ships_move()

    # developer keys
    if c.DEVELOPER_MODE_ON:

        # # change and send keys
        # if chr(event.key) in self.key_mappings:
        #     cmd = self.key_mappings[chr(event.key)][0]
        #     params = self.key_mappings[chr(event.key)][1]
        #     self.change_and_send(cmd, params)

        # auto move
        if event.key == ord('o'):
            print('auto moving!')

            self.timer = task.LoopingCall(move_right_and_then_back, self)
            self.timer.start(5)

        # stop timer
        elif event.key == ord('p'):
            self.timer.stop()

        if event.key == ord('t'):
            self.change_and_send('consume_potion', [1])

def get_nearby_port_index(self):
    # get x and y in tile position
    x_tile = self.my_role.x / c.PIXELS_COVERED_EACH_MOVE
    y_tile = self.my_role.y / c.PIXELS_COVERED_EACH_MOVE

    # iterate each port
    for i in range(1,131):
        if abs(x_tile - hash_ports_meta_data[i]['x']) <= 2 \
                and abs(y_tile - hash_ports_meta_data[i]['y']) <= 2:
            port_id = i - 1
            return port_id

    return None

def move_right_and_then_back(self):
    self.change_and_send('start_move', [self.my_role.x, self.my_role.y, 'right'])
    reactor.callLater(2, send_stop_moving, self)
    reactor.callLater(2.5, start_moving_left, self)
    reactor.callLater(4.5, send_stop_moving, self)

def send_stop_moving(self):
    self.change_and_send('stop_move', [self.my_role.x, self.my_role.y])

def start_moving_left(self):
    self.change_and_send('start_move', [self.my_role.x, self.my_role.y, 'left'])

def key_up(self, event):
    key = chr(event.key)

    # stop moving
    if key in ['w', 's', 'a', 'd', 'e', 'q', 'z', 'x']:
        try:
            self.change_and_send('stop_move', [self.my_role.x, self.my_role.y])
        except:
            pass

def user_event_move(self, event):
    if self.my_role:
        if self.move_direction == 1:
            self.change_and_send('move', ['right'])
        else:
            self.change_and_send('move', ['left'])

        self.move_count += 1

        if self.move_count >= 15:
            self.move_count = 0
            self.move_direction *= -1