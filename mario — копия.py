import os
import sys

import pygame
from pygame.sprite import collide_rect, collide_mask
from random import randint, choice

FPS = 50
WIDTH = 500
HEIGHT = 500
STEP = 1
KILL_SCORE = 1
KILL_BOSS_SCORE = 10
ENEMY_LIST = ['\Slime', '\AngryPig', '\Bat']
FRUITS_LIST = ['apple', 'bananas', 'cherries', 'kiwi',
               'melon', 'orange', 'pineapple', 'strawberry']

pygame.init()
size = WIDTH, HEIGHT
screen = pygame.display.set_mode(size)
clock = pygame.time.Clock()
player_direction = 'right'
kills_number = 49
spawn_boss = False
damage_take = True
over = False
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
fruit_group = pygame.sprite.Group()





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


fruits = {
    'apple': load_image('sprites\Fruits', 'apple_one.png', colorkey=-1),
    'bananas': load_image('sprites\Fruits', 'bananas_one.png', colorkey=-1),
    'cherries': load_image('sprites\Fruits', 'cherries_one.png', colorkey=-1),
    'kiwi': load_image('sprites\Fruits', 'kiwi_one.png', colorkey=-1),
    'melon': load_image('sprites\Fruits', 'melon_one.png', colorkey=-1),
    'orange': load_image('sprites\Fruits', 'orange_one.png', colorkey=-1),
    'pineapple': load_image('sprites\Fruits', 'pineapple_one.png', colorkey=-1),
    'strawberry': load_image('sprites\Fruits', 'strawberry_one.png', colorkey=-1),

}


tile_images = {
    'grass': load_image('sprites', 'Green.png'),
    'spawn_plase': load_image('sprites', 'Green.png'),
    'spawn_boss_plase': load_image('sprites', 'Green.png'),
    'wall': load_image('sprites', 'wall.png')

}
player_image = load_image('sprites', 's_r.png', colorkey=-1)
fireBoll_image = load_image('sprites', 'fire_boll.png', colorkey=-1)
countKills_image = load_image('sprites\chisla', '0.png', colorkey=-1)
score_image = pygame.transform.scale(load_image('sprites', 'score.png', colorkey=-1), (84, 16))
heart = pygame.transform.scale(load_image('sprites', 'heart.png', colorkey=-1), (33, 33))
gameover = pygame.transform.scale(load_image('sprites', 'game over.png', colorkey=-1), (280, 180))

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
        self.text_b = None

    def change(self):
        self.text = self.font.render(str(self.score), True, (255, 255, 255))
        self.text_b = self.font.render(str(self.score), True, (0, 0, 0))


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
        self.direction = 'l'
        self.health = 100
        self.hit_count = 0
        self.image = pygame.transform.scale(load_image('sprites\Enemies\Bosses', 'spikes_boss_l.png', colorkey=-1),
                                            (123, 78))
        self.mack = pygame.mask.from_surface(self.image)
        self.rect = self.image.get_rect().move(pos_x, pos_y)

    def updete(self):
        global kills_number, spawn_boss, score, spawn_fruits
        if self.health <= 0:
            spawn_fruits(boss.rect.x, boss.rect.y, boss.rect.w, boss.rect.h)
            self.kill()
            score.score += KILL_BOSS_SCORE
            kills_number = 0
            kills.load_number(0)
            spawn_boss = False
        self.boss_health()

    def rotation(self):
        if player.rect.x < self.rect.x and self.rect.x - player.rect.x <= 20 and self.direction == 'r':
            self.image = pygame.transform.scale(load_image('sprites\Enemies\Bosses', 'spikes_boss_l.png', colorkey=-1),
                                                (123, 78))
            self.direction = 'l'
        if player.rect.x > self.rect.x + self.rect.w \
                and self.direction == 'l':
            self.image = pygame.transform.scale(load_image('sprites\Enemies\Bosses', 'spikes_boss_r.png', colorkey=-1),
                                                (123, 78))
            self.direction = 'r'

    def boss_health(self):
        pygame.draw.rect(screen, (0, 0, 0), (self.rect.x + 10, self.rect.y - 16,
                                             self.health + 1, 11), 3)
        pygame.draw.rect(screen, (255, 0, 0), (self.rect.x + 11, self.rect.y - 15,
                                               self.health, 10))


class Enemys(pygame.sprite.Sprite):
    def __init__(self, pos_x, pos_y, who, direction):
        super().__init__(enemy_group, all_sprites)
        self.who = who
        self.direction = direction
        self.image = load_image('sprites\Enemies' + who, 'stay_r.png', colorkey=-1)
        self.rect = self.image.get_rect().move(pos_x, pos_y)

    def update(self):
        for en in enemy_group:
            if player.rect.x < en.rect.x and en.rect.x - player.rect.x <= 20 and en.direction == 'r':
                en.image = load_image('sprites\Enemies' + en.who, 'stay_l.png', colorkey=-1)
                en.direction = 'l'
            elif player.rect.x > en.rect.x + en.rect.w and player.rect.x - en.rect.x <= 50 \
                    and en.direction == 'l':
                en.image = load_image('sprites\Enemies' + en.who, 'stay_r.png', colorkey=-1)
                en.direction = 'r'


def spawn_enemis():
    for pos in tiles_group:
        if pos.type == 'spawn_plase':
            Enemys(pos.rect.x + randint(-20, 20), pos.rect.y + randint(-20, 20), choice(ENEMY_LIST), choice(['r', 'l']))


class Fruits(pygame.sprite.Sprite):
    def __init__(self, fruit, pos_x, pos_y):
        super().__init__(fruit_group, all_sprites)
        self.image = fruits[fruit]
        self.rect = self.image.get_rect().move(pos_x, pos_y)


def spawn_fruits(pos_x, pos_y, w, h):
    for f in range(5):
        x = pos_x + w // 2 + randint(-100, 100)
        y = pos_y + h // 2 + randint(-100, 100)
        Fruits(choice(FRUITS_LIST), x, y)


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
        self.image = pygame.transform.scale(load_image('sprites\chisla', str(chislo) + '.png', colorkey=-1), (32, 31))


class Player(pygame.sprite.Sprite):
    def __init__(self, pos_x, pos_y):
        super().__init__(player_group, all_sprites)
        self.health = 100
        self.image = player_image
        self.mack = pygame.mask.from_surface(self.image)
        self.rect = self.image.get_rect().move(
            tile_width * pos_x + 15, tile_height * pos_y + 5)

    def updete(self):
        global damage_take
        for el in tiles_group:
            if collide_rect(self, el) and el.type in ['wall', 'box']:
                self.rect.x = beforex
                self.rect.y = beforey
        for en in enemy_group:
            if collide_rect(self, en):
                if self.health > 0:
                    self.health -= 1

                break
        for boss in boss_enemy_group:
            if collide_mask(self, boss):
                self.rect.x = beforex
                self.rect.y = beforey
                if self.health > 0 and damage_take:
                    self.health -= 10
                damage_take = False
            else:
                self.take_damage(boss, 60)

        for f in fruit_group:
            if collide_rect(self, f):
                if self.health < 100:
                    self.health += 5
                f.kill()

    def rotation(self):
        global player_direction
        if player_direction == "left":
            self.image = load_image('sprites', 's_l.png', colorkey=-1)
        elif player_direction == 'right':
            self.image = load_image('sprites', 's_r.png', colorkey=-1)

    def player_health(self):
        global over
        if self.health > 0:
            pygame.draw.rect(screen, (0, 0, 0), (38, 7, self.health + 1, 16), 3)
            pygame.draw.rect(screen, (255, 0, 0), (39, 8, self.health, 15))
        else:
            player.kill()
            over = True

    def take_damage(self, take, renge):
        global damage_take
        x = take.rect.x + take.rect.w // 2
        y = take.rect.y + take.rect.h // 2
        if self.rect.x <= x - renge or self.rect.x >= x + renge \
                or self.rect.y <= y - renge or self.rect.y >= y + renge and not damage_take:
            damage_take = True


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


def game_draw():
    global kills_number, spawn_boss, boss
    tiles_group.draw(screen)
    enemy_group.draw(screen)
    fireBoll_group.draw(screen)
    if len(fruit_group) > 0:
        fruit_group.draw(screen)
    player_group.draw(screen)
    if kills_number >= 50 and not spawn_boss:
        for pos in tiles_group:
            if pos.type == 'spawn_boss_plase':
                boss = EnemysBoss(pos.rect.x + randint(-30, 30), pos.rect.y + randint(-40, 40))
        spawn_boss = True
    if spawn_boss:
        kills_number = 49
        boss_enemy_group.draw(screen)
        boss.updete()
        boss.rotation()
    screen.blit(heart, (0, 0))
    screen.blit(kills.image, (0, 33))
    screen.blit(score_image, (350, 4))
    score.change()
    screen.blit(score.text_b, (451, 4))
    screen.blit(score.text, (450, 3))
    if len(enemy_group) == 0:
        spawn_enemis()
    player.player_health()
    fireBoll_group.update()
    enemy_group.update()


player, level_x, level_y = generate_level(load_level('map.txt'))
spawn_enemis()
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
    if not over:
            game_draw()
    else:
            screen.blit(gameover, (110, 160))
            pygame.mouse.set_visible(False)
    camera.update(player)
    # обновляем положение всех спрайтов
    for sprite in all_sprites:
        camera.apply(sprite)
    pygame.display.flip()
    # clock.tick(FPS)
terminate()