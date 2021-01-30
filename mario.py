import os
import sys

import pygame
from pygame.sprite import collide_rect, collide_mask            # Блок импорта библиотек
from random import randint, choice
import sqlite3
import pygame_gui

# -------------------------------------------------------------------

FPS = 50                                        # Колличество fps (используется только для началоного экрана ¯\_(ツ)_/¯)
WIDTH = 500                                     # Ширина окна
HEIGHT = 500                                    # Высота окна
STEP = 1                                        # Шаг персонажа
SPIKES_DAMAGE = 15                              # Колличество урона, наносимого шипами
SPIKES_SPEED = 2                                # Скорость(шаг) шипов
KILL_SCORE = 1                                  # Колличесто опыта получаемого после убийства врагв
KILL_BOSS_SCORE = 10                            # Колличесто опыта получаемого после убийства Босса

TIMER_SET = pygame.USEREVENT + 1          #
EMEMIES_MOVE = pygame.USEREVENT + 3       # Для работы set_timer()
BOSSES_MOVE = pygame.USEREVENT + 2        #

tile_width = tile_height = 64                   # Высота и ширина спрайтов карты

ENEMY_LIST = ['\Slime', '\AngryPig', '\Bat']                    # Список мобов
FRUITS_LIST = ['apple', 'bananas', 'cherries', 'kiwi',
               'melon', 'orange', 'pineapple', 'strawberry']    # Список фруктов
SPIKES = ['spik1', 'spik2', 'spik3', 'spik4', 'spik5']          # Список шипов

# -------------------------------------------------------------------

pygame.init()                                   #
size = WIDTH, HEIGHT                            #
screen = pygame.display.set_mode(size)          # Для созданиея окна приложения и ui элементов
clock = pygame.time.Clock()                     #
manager = pygame_gui.UIManager((800, 600))      #

player_direction = 'right'                      # Напровление Игрока
kills_number = 0                                # Счётчик количества убийств
spawn = 1

spawn_boss = False                              #
damage_take = True                              #
over = False                                    # Логические переменные
spikes_move = False                             #
result = False                                  #

player = None                   # Основной персонаж
boss = None                     # Основной Босс

all_sprites = pygame.sprite.Group()             # Группа всех спрайтов
tiles_group = pygame.sprite.Group()             # Группа спрайтов окружения карты
player_group = pygame.sprite.Group()            # Группа спрайтов для персонажа
enemy_group = pygame.sprite.Group()             # Группа спрайтов для мобов
fireBoll_group = pygame.sprite.Group()          # Группа спрайтов для снарядов персонажа
countKills_group = pygame.sprite.Group()        # Группа спрайтов для счётчика убийств до Босса
boss_enemy_group = pygame.sprite.Group()        # Группа спрайтов для Босса
fruit_group = pygame.sprite.Group()             # Группа спрайтов для фруктов
spikes_group = pygame.sprite.Group()            # Группа спрайтов для шипов

# ------------------------------------------------------------------


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
# Функция для загрузка спрайтов/картинок


fruits = {  # Словарь с тегами и спрайтами для фруктов
    'apple': load_image('sprites\Fruits', 'apple_one.png', colorkey=-1),
    'bananas': load_image('sprites\Fruits', 'bananas_one.png', colorkey=-1),
    'cherries': load_image('sprites\Fruits', 'cherries_one.png', colorkey=-1),
    'kiwi': load_image('sprites\Fruits', 'kiwi_one.png', colorkey=-1),
    'melon': load_image('sprites\Fruits', 'melon_one.png', colorkey=-1),
    'orange': load_image('sprites\Fruits', 'orange_one.png', colorkey=-1),
    'pineapple': load_image('sprites\Fruits', 'pineapple_one.png', colorkey=-1),
    'strawberry': load_image('sprites\Fruits', 'strawberry_one.png', colorkey=-1),
}

tile_images = {  # Словарь с тегами и спрайтами для окружения карты
    'grass': load_image('sprites', 'Green.png'),
    'spawn_plase': load_image('sprites', 'Green.png'),
    'spawn_boss_plase': load_image('sprites', 'Green.png'),
    'spawn_player_plase': load_image('sprites', 'Green.png'),
    'wall': load_image('sprites', 'wall.png')
}

# Переменные со спрайтами, картинками надписей и кнопок
player_image = load_image('sprites', 's_r.png', colorkey=-1)
fireBoll_image = load_image('sprites', 'fire_boll.png', colorkey=-1)
countKills_image = load_image('sprites\chisla', '0.png', colorkey=-1)
# score_image = pygame.transform.scale(load_image('sprites', 'score.png', colorkey=-1), (84, 16))
# heart = pygame.transform.scale(load_image('sprites', 'heart.png', colorkey=-1), (33, 33))
heart_and_score_fon = load_image('sprites', 'heart_and_score.png', colorkey=-1)
# gameover = pygame.transform.scale(load_image('sprites', 'game over.png', colorkey=-1), (280, 180))
# restart = pygame.transform.scale(load_image('sprites', 'to_restart.png', colorkey=-1), (370, 27))
# save_result = pygame.transform.scale(load_image('sprites', 'save_result.png', colorkey=-1), (246, 12))
game_over_fon = load_image('sprites', 'gameover.png', colorkey=-1)
# for_save = pygame.transform.scale(load_image('sprites', 'fs.png', colorkey=-1), (286, 58))
# enter_your_name = pygame.transform.scale(load_image('sprites', 'eyn.png', colorkey=-1), (230, 16))
# click_button = pygame.transform.scale(load_image('sprites', 'tcotb.png', colorkey=-1), (300, 14))
# restart_button = pygame.transform.scale(load_image('sprites', 'Restart.png', colorkey=-1), (42, 43))
save_menu_fon = load_image('sprites', 'save_menu.png', colorkey=-1)

# ------------------------------------------------------------------

line = pygame_gui.elements.UITextEntryLine(
    relative_rect=pygame.Rect((330, 145), (155, 10)),   # Переменная с полем ввода из pygame_gui
    manager=manager)

btn_save = pygame_gui.elements.UIButton(
    relative_rect=pygame.Rect((330, 292), (155, 30)),   # Переменная с кнапкой из pygame_gui
    text="Save",
    manager=manager)

# ------------------------------------------------------------------


def terminate():
    pygame.quit()
    sys.exit()
# Функция для завершения работы окна


def start_screen():
    # title = pygame.transform.scale(load_image('sprites', 'title.png', colorkey=-1), (380, 110))
    # play = pygame.transform.scale(load_image('sprites', 'Play.png', colorkey=-1), (84, 85))
    # leaderboard = pygame.transform.scale(load_image('sprites', 'Leaderboard.png', colorkey=-1), (42, 43))
    # settings = pygame.transform.scale(load_image('sprites', 'Settings.png', colorkey=-1), (42, 43))
    screen.blit(load_image('sprites', 'start_screen.png'), (0, 0))

    while True:
        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                terminate()
            elif event.type == pygame.MOUSEBUTTONDOWN:
                if 292 > event.pos[0] > 208 and 335 > event.pos[1] > 250:
                    pygame.key.set_repeat(1, 1)
                    return
                if 43 > event.pos[0] > 0 and 500 > event.pos[1] > 457:
                    con = sqlite3.connect("save_result.db")
                    cur = con.cursor()
                    result = cur.execute("""SELECT * FROM result""").fetchall()
                    print('')
                    for elem in result:
                        print(elem[1].capitalize() + ':', elem[2])

                    con.close()
        pygame.display.flip()
        clock.tick(FPS)
start_screen()
# Отображение начального экрана


def load_level(filename):
    filename = "map/" + filename
    # читаем уровень, убирая символы перевода строки
    with open(filename, 'r') as mapFile:
        level_map = [line.strip() for line in mapFile]

    # и подсчитываем максимальную длину
    max_width = max(map(len, level_map))

    # дополняем каждую строку пустыми клетками ('.')
    return list(map(lambda x: x.ljust(max_width, '.'), level_map))
# Функция для загрузки карты


class Score:
    def __init__(self):
        self.score = 0
        self.font = pygame.font.Font(None, 30)
        self.text = None
        self.text_b = None

    def change(self):
        self.text = self.font.render(str(self.score), True, (255, 255, 255))
        self.text_b = self.font.render(str(self.score), True, (0, 0, 0))
# Класс счёта


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
# Класс камеры


class Tile(pygame.sprite.Sprite):
    def __init__(self, tile_type, pos_x, pos_y):
        super().__init__(tiles_group, all_sprites)
        self.image = tile_images[tile_type]
        self.type = tile_type
        self.rect = self.image.get_rect().move(
            tile_width * pos_x, tile_height * pos_y)
# Класс окружения


class EnemysBoss(pygame.sprite.Sprite):
    def __init__(self, pos_x, pos_y):
        super().__init__(boss_enemy_group, all_sprites)
        self.direction = 'l'
        self.health = 100
        self.hit_count = 0
        self.image = pygame.transform.scale(load_image('sprites\Enemies\Bosses', 'spikes_boss_l.png', colorkey=-1),
                                            (123, 78))
        self.mack = pygame.mask.from_surface(self.image)
        self.rect = self.image.get_rect().move(pos_x, pos_y)
        pygame.time.set_timer(TIMER_SET, 500)
        pygame.time.set_timer(BOSSES_MOVE, 1)

    def updete(self):  # Функция проверки количества здоровья Босса
        global kills_number, spawn_boss, score, spawn_fruits, over
        if self.health <= 0:
            spawn_fruits(boss.rect.x, boss.rect.y, boss.rect.w, boss.rect.h)
            self.kill()
            for s in spikes_group:
                s.kill()
            spikes_group.empty()
            score.score += KILL_BOSS_SCORE
            kills_number = 0
            kills.load_number(0)
            spawn_boss = False
        self.boss_health()

    def rotation(self):  # Функция поворота Босса
        if player.rect.x < self.rect.x and self.rect.x - player.rect.x <= 20 and self.direction == 'r':
            self.image = pygame.transform.scale(load_image('sprites\Enemies\Bosses', 'spikes_boss_l.png', colorkey=-1),
                                                (123, 78))
            self.direction = 'l'
        if player.rect.x > self.rect.x + self.rect.w \
                and self.direction == 'l':
            self.image = pygame.transform.scale(load_image('sprites\Enemies\Bosses', 'spikes_boss_r.png', colorkey=-1),
                                                (123, 78))
            self.direction = 'r'

    def spawn_spikes(self):  # Функция появления шипов
        global boss
        for s in SPIKES:
            if s == 'spik1':
                BossSpikes(self.rect.x, self.rect.y + (self.rect.h - 27), s, (18, 21))
            elif s == 'spik2':
                BossSpikes(self.rect.x + 15, self.rect.y + 15, s, (18, 18))
            elif s == 'spik3':
                BossSpikes(self.rect.x + 48, self.rect.y + 20, s, (21, 21))
            elif s == 'spik4':
                BossSpikes(self.rect.x + (self.rect.w - 36), self.rect.y + 16, s, (21, 21))
            elif s == 'spik5':
                BossSpikes(self.rect.x + (self.rect.w - 20), self.rect.y + (self.rect.h - 27), s, (21, 21))

    def boss_health(self):  # Функция полосы здоровья Босса
        pygame.draw.rect(screen, (0, 0, 0), (self.rect.x + 10, self.rect.y - 16,
                                             self.health + 1, 11), 3)
        pygame.draw.rect(screen, (255, 0, 0), (self.rect.x + 11, self.rect.y - 15,
                                               self.health, 10))

    def move(self):  # Функция перемещения Босса
        global player
        if not self.rect.x + self.rect.w // 2 + 10 > player.rect.x + player.rect.w // 2 > self.rect.x + self.rect.w // 2 - 10:
            if self.direction == 'l':
                self.rect.x -= 2
            else:
                self.rect.x += 2
        if player.rect.y < self.rect.y:
            self.rect.y -= 2
        if player.rect.y > self.rect.y:
            self.rect.y += 2
# Класс Босса


class BossSpikes(pygame.sprite.Sprite):
    def __init__(self, pos_x, pos_y, who, size):
        super().__init__(spikes_group, all_sprites)
        self.who = who
        self.image = pygame.transform.scale(load_image('sprites\Enemies\Bosses', self.who + '.png', colorkey=-1),
                                            size)
        self.mask = pygame.mask.from_surface(self.image)
        self.rect = self.image.get_rect().move(pos_x, pos_y)

    def move(self):  # Функция перемещения шипов
        if self.who == 'spik1':
            self.rect.x -= SPIKES_SPEED
        elif self.who == 'spik2':
            self.rect.x -= SPIKES_SPEED
            self.rect.y -= SPIKES_SPEED
        elif self.who == 'spik3':
            self.rect.y -= SPIKES_SPEED
        elif self.who == 'spik4':
            self.rect.x += SPIKES_SPEED
            self.rect.y -= SPIKES_SPEED
        elif self.who == 'spik5':
            self.rect.x += SPIKES_SPEED
        self.check()

    def check(self):  # Функция проверки столкновения шипов
        global player, spikes_move
        for t in tiles_group:
            if t.type == 'wall' and collide_rect(self, t):
                self.kill()
                spikes_move = False
            elif collide_rect(self, player):
                spikes_move = False
                self.kill()
                player.health -= SPIKES_DAMAGE
                break
# Класс шипов


class Enemys(pygame.sprite.Sprite):
    def __init__(self, pos_x, pos_y, who, direction):
        super().__init__(enemy_group, all_sprites)
        self.who = who
        self.direction = direction
        self.image = load_image('sprites\Enemies' + who, 'stay_' + self.direction + '.png', colorkey=-1)
        self.rect = self.image.get_rect().move(pos_x, pos_y)
        pygame.time.set_timer(EMEMIES_MOVE, 1)
        self.center = self.rect.x + self.rect.w // 2

    def update(self):  # Функция поворота мобов
        global player
        if player.rect.x + player.rect.w < self.rect.x and self.direction == 'r':
            self.image = pygame.transform.flip(self.image, True, False)
            self.direction = 'l'
        elif player.rect.x > self.rect.x + self.rect.w and self.direction == 'l':
            self.image = pygame.transform.flip(self.image, True, False)
            self.direction = 'r'

    def move(self):  # Функция перемешения мобов
        global player
        for t in tiles_group:
            if collide_rect(self, t) and t.type == "wall":
                pass
        if self.direction == 'l':
            self.rect.x -= 2
        else:
            self.rect.x += 2
        if player.rect.y < self.rect.y:
            self.rect.y -= 2
        if player.rect.y > self.rect.y:
            self.rect.y += 2
# Класс мобов


def spawn_enemis():
    global player, spawn
    direction = ''
    for i in range(spawn):
        for pos in tiles_group:
            if pos.type == 'spawn_plase':
                if player.rect.x > pos.rect.x:
                    direction = 'r'
                elif player.rect.x < pos.rect.x:
                    direction = 'l'
                Enemys(pos.rect.x + randint(-20, 20), pos.rect.y + randint(-20, 20), choice(ENEMY_LIST), direction)
# Функция появления мобов


class Fruits(pygame.sprite.Sprite):
    def __init__(self, fruit, pos_x, pos_y):
        super().__init__(fruit_group, all_sprites)
        self.image = fruits[fruit]
        self.rect = self.image.get_rect().move(pos_x, pos_y)
# Класс фруктов


def spawn_fruits(pos_x, pos_y, w, h):
    for f in range(5):
        x = pos_x + w // 2 + randint(-100, 100)
        y = pos_y + h // 2 + randint(-100, 100)
        Fruits(choice(FRUITS_LIST), x, y)
# Функция появления фруктов


class CountKills(pygame.sprite.Sprite):
    def __init__(self):
        super().__init__(countKills_group, all_sprites)
        self.image = pygame.transform.scale(countKills_image, (32, 31))
        self.rect = self.image.get_rect()

    def change(self):  # Функция увеличения числа убийств
        global kills, countKills_image, kills_number
        if kills_number < 50:
            kills_number += 1
        kills.kill()
        self.load_number(kills_number)

    def load_number(self, chislo):  # Функция исменения картинуи числа
        self.image = pygame.transform.scale(load_image('sprites\chisla', str(chislo) + '.png', colorkey=-1), (32, 31))
# Класс убийств до Босса


class Player(pygame.sprite.Sprite):
    def __init__(self, pos_x, pos_y):
        super().__init__(player_group, all_sprites)
        self.health = 100
        self.image = player_image
        self.mack = pygame.mask.from_surface(self.image)
        self.rect = self.image.get_rect().move(
            tile_width * pos_x + 15, tile_height * pos_y + 5)
        self.center = self.rect.x + self.rect.w // 2

    def updete(self):  # Функция проверки столкновений
        global damage_take, boss, spawn_boss
        for el in tiles_group:
            if collide_rect(self, el) and el.type in ['wall', 'box']:
                self.rect.x = beforex
                self.rect.y = beforey
        for en in enemy_group:
            if collide_rect(self, en):
                if self.health > 0:
                    self.health -= 1

                break
        if spawn_boss:
            if collide_mask(self, boss):
                if self.health > 0 and damage_take:
                    self.health -= 5
                damage_take = False
            else:
                self.take_damage(boss, 60)

        for f in fruit_group:
            if collide_rect(self, f):
                if self.health < 100:
                    self.health += 5
                f.kill()

    def rotation(self):  # Фцнкция поворота игрока
        global player_direction
        if player_direction == "left":
            self.image = load_image('sprites', 's_l.png', colorkey=-1)
        elif player_direction == 'right':
            self.image = load_image('sprites', 's_r.png', colorkey=-1)

    def player_health(self):  # Функция отображения полоски здоровья игрока
        global over
        if self.health > 0:
            pygame.draw.rect(screen, (0, 0, 0), (38, 7, self.health + 2, 17), 2)
            pygame.draw.rect(screen, (255, 0, 0), (39, 8, self.health, 15))
        else:
            pygame.mouse.set_visible(False)
            over = True

    def take_damage(self, take, renge):
        global damage_take
        x = take.rect.x + take.rect.w // 2
        y = take.rect.y + take.rect.h // 2
        if self.rect.x <= x - renge or self.rect.x >= x + renge \
                or self.rect.y <= y - renge or self.rect.y >= y + renge and not damage_take:
            damage_take = True
# Класс игрока(персонажа)


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

    def update(self):  # Функция для перемешения и столкновения
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
# Класс снарядов


def generate_level(level):
    global start_x, start_y
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
                Tile('spawn_player_plase', x, y)
                new_player = Player(x, y)
                start_x, start_y = x, y
    # вернем игрока, а также размер поля в клетках
    return new_player, x, y
# Функция для создания уровня(окружения карты)


def game_draw():
    global kills_number, spawn_boss, boss
    tiles_group.draw(screen)
    fireBoll_group.draw(screen)
    enemy_group.draw(screen)
    if len(fruit_group) > 0:
        fruit_group.draw(screen)
    player_group.draw(screen)
    if kills_number >= 50 and not spawn_boss:
        for pos in tiles_group:
            if pos.type == 'spawn_boss_plase':
                boss = EnemysBoss(pos.rect.x + randint(-30, 30), pos.rect.y + randint(-40, 40))
        spawn_boss = True
    spikes_group.draw(screen)
    if spawn_boss:
        kills_number = 49
        if len(spikes_group) == 0:
            boss.spawn_spikes()
        spikes_group.draw(screen)
        boss_enemy_group.draw(screen)
        for s in spikes_group:
            s.move()
        boss.updete()
        boss.rotation()
    # screen.blit(heart, (0, 0))
    # screen.blit(score_image, (350, 4))
    screen.blit(heart_and_score_fon, (0, 0))
    screen.blit(kills.image, (0, 33))
    score.change()
    screen.blit(score.text_b, (451, 4))
    screen.blit(score.text, (450, 3))
    if len(enemy_group) == 0:
        spawn_enemis()
    player.player_health()
    # player.updete()
    fireBoll_group.update()
    enemy_group.update()
# Функция для отрисовки и обновления игры


def xz_kak_nazvet():
    global over, player, score, kills_number, kills, boss, spawn_boss, result
    screen.fill((33, 31, 100))
    pygame.mouse.set_visible(True)
    player.health = 100
    for p in tiles_group:
        if p.type == 'spawn_player_plase':
            player.rect.x, player.rect.y = p.rect.x, p.rect.y
            break
    kills_number = 0
    kills.load_number(kills_number)
    if spawn_boss:
        boss.kill()
        spawn_boss = False
    for s in spikes_group:
        s.kill()
    spikes_group.empty()
    fruit_group.empty()
    enemy_group.empty()
    over = False
# Хз_как_назвать


def restart_game():
    global result
    for event in pygame.event.get():
        if event.type == pygame.KEYDOWN:
            if event.key == pygame.K_f:
                xz_kak_nazvet()
                score.score = 0
            elif event.key == pygame.K_SPACE:
                result = True
                xz_kak_nazvet()
#  Функция для перезапуска игры


def save_menu():
    global result
    time_delta = 1000
    screen.blit(save_menu_fon, (0, 0))
    # screen.blit(restart_button, (229, 400))
    # screen.blit(for_save, (107, 20))
    # screen.blit(enter_your_name, (15, 150))
    # screen.blit(click_button, (15, 300))
    manager.update(time_delta)
    manager.draw_ui(screen)
# Функия для отрисовки меню сохранения


def save_result_in_bd():
    # Подключение к БД
    con = sqlite3.connect('save_result.db')
    # Создание курсора
    cur = con.cursor()
    cur.execute("""INSERT INTO result (nickname, score)
                                    VALUES (?, ?)""", (line.text, score.score)).fetchall()
    con.commit()
# Функция добавления результата в бд


player, level_x, level_y = generate_level(load_level('map.txt'))
spawn_enemis()
print('\n')
print('Количество спрайтов:', len(all_sprites))
print('Кол-во страйтов игрока:', len(player_group))
print('Кол-во спрайтов окружения:', len(tiles_group))
print('Кол-во спрайтов врагов:', len(enemy_group))
print('\n')
kills = CountKills()
score = Score()
beforex = 0
beforey = 0
running = True
pygame.key.set_repeat(1, 1)

while running:
        # внутри игрового цикла ещё один циклda
        # приема и обработки сообщений
    for event in pygame.event.get():
        manager.process_events(event)
            # при закрытии окна
        if event.type == pygame.QUIT:
            running = False
        if event.type == pygame.KEYDOWN and not over:
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
            if event.key == pygame.K_r:
                kills_number = 49
            player.updete()
        if event.type == pygame.MOUSEBUTTONDOWN:
            if len(fireBoll_group) < 5:
                FireBoll(event.pos)
        if spawn_boss:
            if event.type == TIMER_SET:
                spikes_move = True
            if event.type == BOSSES_MOVE:
                boss.move()
        if event.type == EMEMIES_MOVE:
            for en in enemy_group:
                en.move()
        if (event.type == pygame.USEREVENT and event.user_type == pygame_gui.UI_BUTTON_PRESSED and
                event.ui_element == btn_save):
            save_result_in_bd()
            score.score = 0
        if result:
            if event.type == pygame.MOUSEBUTTONDOWN:
                if 371 > event.pos[0] > 229 and 443 > event.pos[1] > 400:
                    result = False
                    score.score = 0
                    start_screen()

    screen.fill((33, 31, 100))
    if not over:
            game_draw()
    else:
            screen.blit(game_over_fon, (0, 0))
            # screen.blit(gameover, (110, 93))
            # screen.blit(restart, (65, 303))
            # screen.blit(save_result, (127, 340))
            restart_game()
    if result:
        pygame.mouse.set_visible(True)
        save_menu()

    camera.update(player)
    # обновляем положение всех спрайтов
    for sprite in all_sprites:
        camera.apply(sprite)
    pygame.display.flip()
    # clock.tick(FPS)

terminate()