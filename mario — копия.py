import os
import sys

import pygame
from pygame.sprite import collide_rect
from random import randint, choice

FPS = 50
WIDTH = 500
HEIGHT = 500
STEP = 1
ENEMY_LIST = ['\Slime', '\AngryPig', '\Bat']

pygame.init()
size = WIDTH, HEIGHT
screen = pygame.display.set_mode(size)
clock = pygame.time.Clock()
player_direction = 'right'


# основной персонаж
player = None

# группы спрайтов
all_sprites = pygame.sprite.Group()
tiles_group = pygame.sprite.Group()
player_group = pygame.sprite.Group()
enemy_group = pygame.sprite.Group()
fireBoll_group = pygame.sprite.Group()




def load_image(folder, name, colorkey=None):
    fullname = os.path.join(folder, name)
    # если файл не существует, то выходим
    if not os.path.isfile(fullname):
        print(f"Файл с изображением '{fullname}' не найден")
        sys.exit()
    image = pygame.image.load(fullname)

    if colorkey is None:
        image = image.convert()
        if colorkey == -1:
            colorkey = image.get_at((0, 0))
        image.set_colorkey(colorkey)
    else:
        image = image.convert_alpha()
    return image


tile_images = {
    'grass': load_image('sprites', 'Green.png'),
    'spawn_plase': load_image('sprites', 'Green.png'),
    'wall': load_image('sprites', 'wall.png')

}
player_image = load_image('sprites', 's_r.png', colorkey=-1)
fireBoll_image = load_image('sprites', 'fire_boll.png', colorkey=-1)

tile_width = tile_height = 64


def terminate():
    pygame.quit()
    sys.exit()


def start_screen():
    intro_text = ["ЗАСТАВКА", "",
                  "Правила игры",
                  "Если в правилах несколько строк,",
                  "приходится выводить их построчно"]

    fon = pygame.transform.scale(load_image('sprites', 'fajrbackground.png'), (WIDTH, HEIGHT))
    screen.blit(fon, (0, 0))
    font = pygame.font.Font(None, 30)
    text_coord = 50
    for line in intro_text:
        string_rendered = font.render(line, 1, pygame.Color('black'))
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
                return  # начинаем игру
        pygame.display.flip()
        clock.tick(FPS)

start_screen()


def load_level(filename):
    filename = "map/" + filename
    # читаем уровень, убирая символы перевода строки
    with open(filename, 'r') as mapFile:
        level_map = [line.strip() for line in mapFile]

    # и подсчитываем максимальную длину
    max_width = max(map(len, level_map))

    # дополняем каждую строку пустыми клетками ('.')
    return list(map(lambda x: x.ljust(max_width, '.'), level_map))


class Camera:
    # зададим начальный сдвиг камеры
    def __init__(self):
        self.dx = 0
        self.dy = 0

    # сдвинуть объект obj на смещение камеры
    def apply(self, obj):
        obj.rect.x += self.dx
        obj.rect.y += self.dy

    # позиционировать камеру на объекте target
    def update(self, target):
        self.dx = -(target.rect.x + target.rect.w // 2 - WIDTH // 2)
        self.dy = -(target.rect.y + target.rect.h // 2 - HEIGHT // 2)
camera = Camera()


class Enemys(pygame.sprite.Sprite):
    def __init__(self, pos_x, pos_y, who):
        super().__init__(enemy_group, all_sprites)
        self.image = load_image('sprites\Enemies' + who, 'stay_r.png', colorkey=-1)
        self.rect = self.image.get_rect().move(pos_x, pos_y)


def spawn_enemis():
    for pos in tiles_group:
        if pos.type == 'spawn_plase':
            Enemys(pos.rect.x, pos.rect.y, choice(ENEMY_LIST))


class Tile(pygame.sprite.Sprite):
    def __init__(self, tile_type, pos_x, pos_y):
        super().__init__(tiles_group, all_sprites)
        self.image = tile_images[tile_type]
        self.type = tile_type
        self.rect = self.image.get_rect().move(
            tile_width * pos_x, tile_height * pos_y)


class Player(pygame.sprite.Sprite):
    def __init__(self, pos_x, pos_y):
        super().__init__(player_group, all_sprites)
        self.image = player_image
        self.rect = self.image.get_rect().move(
            tile_width * pos_x + 15, tile_height * pos_y + 5)

    def updete(self):

        for el in tiles_group:
            if collide_rect(self, el) and el.type in ['wall', 'box']:
                self.rect.x = beforex
                self.rect.y = beforey

    def rotation(self):
        global player, player_image, player_direction
        if player_direction == "left":
            player.kill()
            player_image = load_image('sprites', 's_l.png', colorkey=-1)
            player = Player(player.rect.x, player.rect.y)
            player.rect.x, player.rect.y = beforex, beforey
        elif player_direction == 'right':
            player.kill()
            player_image = load_image('sprites', 's_r.png', colorkey=-1)
            player = Player(player.rect.x, player.rect.y)
            player.rect.x, player.rect.y = beforex, beforey


class FireBoll(pygame.sprite.Sprite):
    def __init__(self, direction):
        super().__init__(fireBoll_group, all_sprites)
        self.image = fireBoll_image
        self.rect = self.image.get_rect().move(player.rect.x + 11,
                                               player.rect.y + 11)
        self.direction = direction

    def update(self):
        for el in tiles_group:
            if collide_rect(self, el) and el.type in ['wall', 'box']:
                self.kill()
        for en in enemy_group:
            if collide_rect(self, en):
                self.kill()
                en.kill()


        for boll in fireBoll_group:
            if boll.direction == 'right':
                boll.rect.x += 1
            else:
                boll.rect.x -= 1


def generate_level(level):
    new_player, x, y = None, None, None
    for y in range(len(level)):
        for x in range(len(level[y])):
            if level[y][x] == '#':
                Tile('wall', x, y)
            elif level[y][x] == '.':
                Tile('grass', x, y)
            elif level[y][x] == '+':
                Tile('spawn_plase', x, y)
            elif level[y][x] == '@':
                Tile('grass', x, y)
                new_player = Player(x, y)
                # new_player = AnimatedSprite(load_image('sprites\Main Characters\Virtual Guy', 'Idle (32x32).png', colorkey=-1), 11, 1, x, y)
    # вернем игрока, а также размер поля в клетках
    return new_player, x, y


player, level_x, level_y = generate_level(load_level('map.txt'))
spawn_enemis()
print('Количество спрайтов:', len(all_sprites))
print('Кол-во страйтоп игрока:', len(player_group))
print('Кол-во спрайтов окружения:', len(tiles_group))
print('Кол-во спрайтов врагов:', len(enemy_group))
print('Кол-во огненый шаров:', len(fireBoll_group))

beforex = 0
beforey = 0
running = True
pygame.key.set_repeat(1, 1)
while running:
        # внутри игрового цикла ещё один цикл
        # приема и обработки сообщений
    for event in pygame.event.get():
            # при закрытии окна
        if event.type == pygame.QUIT:
            running = False
        if event.type == pygame.KEYDOWN:
            beforex = player.rect.x
            beforey = player.rect.y
            if event.key == pygame.K_LEFT or event.key == pygame.K_a:
                player_direction = 'left'
                player.rotation()
                player.rect.x -= STEP
            if event.key == pygame.K_RIGHT or event.key == pygame.K_d:
                player_direction = 'right'
                player.rotation()
                player.rect.x += STEP
            if event.key == pygame.K_UP or event.key == pygame.K_w:
                player.rect.y -= STEP
            if event.key == pygame.K_DOWN or event.key == pygame.K_s:
                player.rect.y += STEP
            player.updete()
        if event.type == pygame.MOUSEBUTTONDOWN:
            if len(fireBoll_group) < 5:
                FireBoll(player_direction)
    screen.fill((33, 31, 100))
    tiles_group.draw(screen)
    enemy_group.draw(screen)
    player_group.draw(screen)
    fireBoll_group.draw(screen)
    fireBoll_group.update()
    camera.update(player)
    # обновляем положение всех спрайтов
    for sprite in all_sprites:
        camera.apply(sprite)
    pygame.display.flip()
    # clock.tick(FPS)
terminate()