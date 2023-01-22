import os
import sys
from random import choice, randint

import pygame

pygame.init()
size = width, height = 500, 500
screen = pygame.display.set_mode(size)
clock = pygame.time.Clock()
FPS = 50


def load_image(name, colorkey=None):
    fullname = os.path.join('data', name)
    # если файл не существует, то выходим
    if not os.path.isfile(fullname):
        print(f"Файл с изображением '{fullname}' не найден")
        sys.exit()
    image = pygame.image.load(fullname)
    if colorkey is not None:
        image = image.convert()
        if colorkey == -1:
            colorkey = image.get_at((0, 0))
        image.set_colorkey(colorkey)
    else:
        image = image.convert_alpha()
    return image


def load_level(filename):
    filename = "maps/" + filename
    # читаем уровень, убирая символы перевода строки
    with open(filename, 'r') as mapFile:
        level_map = [line.strip() for line in mapFile]

    max_width = max(map(len, level_map))

    return list(map(lambda x: x.ljust(max_width, '*'), level_map))


def load_room(filename):
    filename = "rooms/" + filename
    with open(filename, 'r') as mapFile:
        room_map = [line.strip() for line in mapFile]

    max_width = max(map(len, room_map))
    return list(map(lambda x: x.ljust(max_width, '*'), room_map))


def terminate():
    pygame.quit()
    sys.exit()


def start_screen():
    intro_text = ["ЗАСТАВКА", "",
                  "Правила игры",
                  "Если в правилах несколько строк,",
                  "приходится выводить их построчно"]

    fon = pygame.transform.scale(load_image('fon.jpg'), (width, height))
    screen.blit(fon, (0, 0))
    font = pygame.font.Font(None, 30)
    text_coord = 50
    for line in intro_text:
        string_rendered = font.render(line, 1, pygame.Color('white'))
        intro_rect = string_rendered.get_rect()
        text_coord += 10
        intro_rect.top = text_coord
        intro_rect.x = 10
        text_coord += intro_rect.height
        screen.blit(string_rendered, intro_rect)
    while True:
        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                terminate()
            elif event.type == pygame.KEYDOWN or \
                    event.type == pygame.MOUSEBUTTONDOWN:
                return True
        pygame.display.flip()
        clock.tick(FPS)


tile_images = {
    'wall': load_image('box.png'),
    'floor': load_image('grass.png'),
    'empty': load_image('niger.png')
}
player_image = load_image('mar.png', -1)

enemy_images = {
    'en_1': load_image('en_1.png'),
    'en_2': load_image('en_2.png'),
    'en_3': load_image('en_3.png'),
    'en_4': load_image('en_4.png'),
    'en_5': load_image('en_5.png')
}

fight_screen = load_image('fight_screen.png')

error_screen = load_image('error_screen.png')

tile_width = tile_height = 50

class Tile(pygame.sprite.Sprite):
    def __init__(self, tile_type, pos_x, pos_y):
        super().__init__(tiles_group, all_sprites)
        self.image = tile_images[tile_type]
        self.rect = self.image.get_rect().move(
            tile_width * pos_x, tile_height * pos_y)


class Player(pygame.sprite.Sprite):
    def __init__(self, pos_x, pos_y):
        super().__init__(player_group, all_sprites)
        self.pos_x = pos_x
        self.pos_y = pos_y
        self.image = player_image
        self.rect = self.image.get_rect().move(
            tile_width * self.pos_x + 15, tile_height * self.pos_y + 5)

        self.is_moving_up = False
        self.is_moving_down = False
        self.is_moving_left = False
        self.is_moving_right = False

        self.is_fighting = False
        self.is_dead_inside = False

    def move(self):
        try:
            if self.is_moving_up and room_map[int(self.pos_y)][int(self.pos_x)] != '#':
                self.rect = self.rect.move(0, -5)
            if self.is_moving_down and room_map[int(self.pos_y + 1)][int(self.pos_x)] != '#':
                self.rect = self.rect.move(0, 5)
            if self.is_moving_right and room_map[int(self.pos_y)][int(self.pos_x + 1)] != '#':
                self.rect = self.rect.move(5, 0)
            if self.is_moving_left and room_map[int(self.pos_y)][int(self.pos_x)] != '#':
                self.rect = self.rect.move(-5, 0)
        except IndexError:
            self.is_dead_inside = True

    def update(self):
        self.pos_x = self.rect[0] / 50
        self.pos_y = self.rect[1] / 50
        for enemy in pygame.sprite.spritecollide(self, enemy_group, False):
            print(enemy)
        # if pygame.sprite.spritecollideany(self, enemy_group):
        #     self.is_fighting = True


class Enemy(pygame.sprite.Sprite):
    def __init__(self, room_x, room_y):
        super().__init__(enemy_group, all_sprites)
        self.pos_x = randint(2, 7)
        self.pos_y = randint(2, 7)
        self.room_pos_x = room_x
        self.room_pos_y = room_y
        self.image = choice(list(enemy_images.values()))
        self.rect = self.image.get_rect().move(
            tile_width * self.pos_x + 15, tile_height * self.pos_y + 5)

all_sprites = pygame.sprite.Group()
tiles_group = pygame.sprite.Group()

player_group = pygame.sprite.Group()
enemy_group = pygame.sprite.Group()


def generate_start_level(level):
    start_room_pos_x, start_room_pos_y = None, None
    for y in range(len(level)):
        for x in range(len(level[y])):
            if level[y][x] == 'S':
                new_player, room_map = generate_room('S')
                start_room_pos_x = x
                start_room_pos_y = y
    # вернем игрока, а также размер поля в клетках
    return new_player, start_room_pos_x, start_room_pos_y, room_map


def generate_room(type):
    tiles_group.empty()
    enemy_group.empty()
    print(enemy_group)

    new_player = None
    if type == 'S':
        room = load_room('start_room.txt')
    elif type == 'B':
        room = load_room('bonus_room.txt')
        Enemy(room_pos_x, room_pos_y)
        Enemy(room_pos_x, room_pos_y)
    elif type == '#':
        room = load_room('bonus_room.txt')
        Enemy(room_pos_x, room_pos_y)
        Enemy(room_pos_x, room_pos_y)
    elif type == '*':
        room = load_room('empty.txt')
    else:
        room = load_room('bonus_room.txt')
        Enemy(room_pos_x, room_pos_y)
        Enemy(room_pos_x, room_pos_y)

    print(room)

    for y in range(len(room)):
        for x in range(len(room[y])):
            if room[y][x] == '.':
                Tile('floor', x, y)
            elif room[y][x] == '#':
                Tile('wall', x, y)
            elif room[y][x] == '@':
                Tile('floor', x, y)
                if player_group:
                    new_player = None
                else:
                    new_player = Player(x, y)
            elif room[y][x] == 'D':
                Tile('floor', x, y)

    return new_player, room

def switch_room(x, y):
    room_map = None
    try:
        room_map = generate_room(level_map[room_pos_y][room_pos_x])
    except IndexError:
        player.is_dead_inside = True
    return room_map

level_map = load_level('test_map.txt')

player, room_pos_x, room_pos_y, room_map = generate_start_level(level_map)
print(room_pos_x, room_pos_y)
running = start_screen()

while running:
    clock.tick(FPS)
    screen.fill((255, 255, 255))
    for event in pygame.event.get():
        if event.type == pygame.QUIT:
            running = False
        if event.type == pygame.KEYDOWN:
            if event.key == 119:
                player.is_moving_up = True
                # player.move_up()
            if event.key == 115:
                player.is_moving_down = True
                # player.move_down()
            if event.key == 97:
                player.is_moving_left = True
                # player.move_left()
            if event.key == 100:
                player.is_moving_right = True
                # player.move_right()

        if event.type == pygame.KEYUP:
            if event.key == 119:
                player.is_moving_up = False
            if event.key == 115:
                player.is_moving_down = False
            if event.key == 97:
                player.is_moving_left = False
            if event.key == 100:
                player.is_moving_right = False

    if player.pos_x == 8.5:
        room_pos_x += 1
        player.pos_x = 1
        player.rect = player.rect.move(-400, 0)
        switch_room(room_pos_x, room_pos_y)
    elif player.pos_x == 0.5:
        room_pos_x -= 1
        player.pos_x = 8
        player.rect = player.rect.move(400, 0)
        switch_room(room_pos_x, room_pos_y)
    elif player.pos_y == 8.5:
        room_pos_y += 1
        player.pos_y = 1
        player.rect = player.rect.move(0, -400)
        switch_room(room_pos_x, room_pos_y)
    elif player.pos_y == 0.5:
        room_pos_y -= 1
        player.pos_y = 8
        player.rect = player.rect.move(0, 400)
        switch_room(room_pos_x, room_pos_y)

    player.move()
    player.update()

    all_sprites.update()
    all_sprites.draw(screen)
    player_group.draw(screen)
    # for sprite in enemy_group:
    #     if sprite.room_pos_x == room_pos_x and sprite.room_pos_y == room_pos_y:
    #         sprite.draw(screen)
    enemy_group.draw(screen)

    if player.is_fighting:
        fon = pygame.transform.scale(load_image('fight_screen.png'), (width, height))
        screen.blit(fon, (0, 0))
    elif player.is_dead_inside:
        fon = pygame.transform.scale(load_image('error_screen.png'), (width, height))
        screen.blit(fon, (0, 0))
    pygame.display.flip()
pygame.quit()
