import os
import sys

import pygame
from pygame.sprite import collide_rect
from random import randint, choice

FPS = 50
WIDTH = 500
HEIGHT = 500
STEP = 1
KILL_SCORE = 1
KILL_BOSS_SCORE = 10
ENEMY_LIST = ['\Slime', '\AngryPig', '\Bat']

pygame.init()
size = WIDTH, HEIGHT
screen = pygame.display.set_mode(size)
clock = pygame.time.Clock()
player_direction = 'right'
kills_number = 49
spawn_boss = False
# основной персонаж
player = None
boss = None
# группы спрайтов
all_sprites = pygame.sprite.Group()
tiles_group = pygame.sprite.Group()
player_group = pygame.sprite.Group()
enemy_group = pygame.sprite.Group()
fireBoll_group = pygame.sprite.Group()
countKills_group = pygame.sprite.Group()
boss_enemy_group = pygame.sprite.Group()





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
    'spawn_boss_plase': load_image('sprites', 'Green.png'),
    'wall': load_image('sprites', 'wall.png')

}
player_image = load_image('sprites', 's_r.png', colorkey=-1)
fireBoll_image = load_image('sprites', 'fire_boll.png', colorkey=-1)
countKills_image = load_image('sprites\chisla', '0.png', colorkey=-1)
score_image = pygame.transform.scale(load_image('sprites', 'score_w.png', colorkey=-1), (84, 16))

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


class Score:
    def __init__(self):
        self.score = 0
        self.font = pygame.font.Font(None, 30)
        self.text = None

    def change(self):
        self.text = self.font.render(str(self.score), True, (255, 255, 255))


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


class Tile(pygame.sprite.Sprite):
    def __init__(self, tile_type, pos_x, pos_y):
        super().__init__(tiles_group, all_sprites)
        self.image = tile_images[tile_type]
        self.type = tile_type
        self.rect = self.image.get_rect().move(
            tile_width * pos_x, tile_height * pos_y)


class EnemysBoss(pygame.sprite.Sprite):
    def __init__(self, pos_x, pos_y):
        super().__init__(boss_enemy_group, all_sprites)
        self.health = 100
        self.hit_count = 0
        self.x = pos_x
        self.y = pos_y
        self.image = pygame.transform.scale(load_image('sprites\Enemies\Bosses', 'spikes_boss_l.png', colorkey=-1),
                                            (123, 78))
        self.rect = self.image.get_rect().move(pos_x, pos_y)

    def updete(self):
        global kills_number, spawn_boss, score
        if self.health == 0:
            self.kill()
            score.score += KILL_BOSS_SCORE
            kills_number = 0
            kills.load_number(0)
            spawn_boss = False
        self.boss_health()

    def boss_health(self):
        pygame.draw.rect(screen, (0, 0, 0), (self.rect.x + 10, self.rect.y - 16,
                                               self.health + 1, 11), 3)
        pygame.draw.rect(screen, (255, 0, 0), (self.rect.x + 11, self.rect.y - 15,
                                               self.health, 10))


class Enemys(pygame.sprite.Sprite):
    def __init__(self, pos_x, pos_y, who):
        super().__init__(enemy_group, all_sprites)
        self.image = load_image('sprites\Enemies' + who, 'stay_r.png', colorkey=-1)
        self.rect = self.image.get_rect().move(pos_x, pos_y)


def spawn_enemis():
    for pos in tiles_group:
        if pos.type == 'spawn_plase':
            Enemys(pos.rect.x, pos.rect.y, choice(ENEMY_LIST))


class CountKills(pygame.sprite.Sprite):
    def __init__(self):
        super().__init__(countKills_group, all_sprites)
        self.image = pygame.transform.scale(countKills_image, (32, 31))
        self.rect = self.image.get_rect()

    def change(self):
        global kills, countKills_image, kills_number
        if kills_number < 50:
            kills_number += 1
        kills.kill()
        self.load_number(kills_number)

    def load_number(self, chislo):
        global countKills_image, kills
        countKills_image = load_image('sprites\chisla', str(chislo) + '.png', colorkey=-1)
        kills = CountKills()


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
        self.direction = None
        self.image = fireBoll_image
        self.rect = self.image.get_rect().move(player.rect.x + 11,
                                               player.rect.y + 11)
        if player.rect.y - 20 <= direction[1] <= player.rect.y + 45:
            if direction[0] < player.rect.x:
                self.direction = 'left'
            elif direction[0] > player.rect.x:
                self.direction = 'right'
        elif player.rect.x - 20 <= direction[0] <= player.rect.x + 42:
            if direction[1] < player.rect.x:
                self.direction = 'up'
            elif direction[1] > player.rect.x:
                self.direction = 'down'

    def update(self):
        global spawn_boss, score
        for el in tiles_group:
            if collide_rect(self, el) and el.type in ['wall', 'box']:
                self.kill()
        for en in enemy_group:
            if collide_rect(self, en):
                self.kill()
                en.kill()
                kills.change()
                score.score += KILL_SCORE
        for boss in boss_enemy_group:
            if collide_rect(self, boss) and spawn_boss:
                self.kill()
                boss.hit_count += 1
                boss.health -= 5

        for boll in fireBoll_group:
            if boll.direction == 'right':
                boll.rect.x += 1
            elif boll.direction == 'left':
                boll.rect.x -= 1
            elif boll.direction == 'up':
                boll.rect.y -= 1
            elif boll.direction == 'down':
                boll.rect.y += 1
            else:
                boll.kill()


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
            elif level[y][x] == 'B':
                Tile('spawn_boss_plase', x, y)
            elif level[y][x] == '@':
                Tile('grass', x, y)
                new_player = Player(x, y)
                # new_player = AnimatedSprite(load_image('sprites\Main Characters\Virtual Guy', 'Idle (32x32).png', colorkey=-1), 11, 1, x, y)
    # вернем игрока, а также размер поля в клетках
    return new_player, x, y


player, level_x, level_y = generate_level(load_level('map.txt'))
spawn_enemis()
print('Количество спрайтов:', len(all_sprites))
print('Кол-во страйтов игрока:', len(player_group))
print('Кол-во спрайтов окружения:', len(tiles_group))
print('Кол-во спрайтов врагов:', len(enemy_group))
kills = CountKills()
score = Score()
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
                FireBoll(event.pos)
    screen.fill((33, 31, 100))
    tiles_group.draw(screen)
    enemy_group.draw(screen)
    fireBoll_group.draw(screen)
    player_group.draw(screen)
    if kills_number >= 50:
        for pos in tiles_group:
            if pos.type == 'spawn_boss_plase':
                boss = EnemysBoss(pos.rect.x, pos.rect.y)
        spawn_boss = True
    if spawn_boss:
        kills_number = 49
        boss_enemy_group.draw(screen)
        boss.updete()
    screen.blit(kills.image, (0, 0))
    screen.blit(score_image, (350, 4))
    score.change()
    screen.blit(score.text, (450, 3))
    if len(enemy_group) == 0:
        spawn_enemis()
    fireBoll_group.update()
    camera.update(player)
    # обновляем положение всех спрайтов
    for sprite in all_sprites:
        camera.apply(sprite)
    pygame.display.flip()
    # clock.tick(FPS)
terminate()