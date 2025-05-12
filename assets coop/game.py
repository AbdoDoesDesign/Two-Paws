import pygame
from pygame.locals import *
from pygame import mixer
import pickle
from os import path

# ----- Initialization -----
pygame.mixer.pre_init(44100, -16, 2, 512)
mixer.init()
pygame.init()

clock = pygame.time.Clock()
fps = 60

screen_width = 1000
screen_height = 1000
screen = pygame.display.set_mode((screen_width, screen_height))
pygame.display.set_caption('Platformer')

# ----- Fonts -----
font = pygame.font.SysFont('Bauhaus 93', 70)
font_score = pygame.font.SysFont('Bauhaus 93', 30)

# ----- Game variables -----
tile_size = 50
game_over = 0
main_menu = True
level = 3
max_levels = 7
score_p1 = 0  # Player 1 score
score_p2 = 0  # Player 2 score

# ----- Colours -----
white = (255, 255, 255)
blue  = (0, 0, 255)
red   = (255, 0, 0)

# ----- Load images -----
sun_img     = pygame.image.load('sun.png')
bg_img      = pygame.image.load('sky.png')
restart_img = pygame.image.load('restart_btn.png')
start_img   = pygame.image.load('start_btn.png')
exit_img    = pygame.image.load('exit_btn.png')
menu_logo_i = pygame.image.load('menu_logo.png')

# ----- Load sounds -----
pygame.mixer.music.load('music.wav')
pygame.mixer.music.play(-1, 0.0, 5000)
coin_fx      = pygame.mixer.Sound('coin.wav');     coin_fx.set_volume(0.5)
jump_fx      = pygame.mixer.Sound('jump.wav');     jump_fx.set_volume(0.5)
game_over_fx = pygame.mixer.Sound('game_over.wav');game_over_fx.set_volume(0.5)

# ----- Utility -----
def draw_text(text, font, text_col, x, y):
    img = font.render(text, True, text_col)
    screen.blit(img, (x, y))

# ----- Reset level -----
def reset_level(level):
    player1.reset(100, screen_height - 130)
    player2.reset(150, screen_height - 130)
    blob_group.empty()
    platform_group.empty()
    coin_group.empty()
    lava_group.empty()
    exit_group.empty()

    # load in level data
    if path.exists(f'level{level}_data'):
        with open(f'level{level}_data', 'rb') as f:
            world_data = pickle.load(f)
    world = World(world_data)

    # dummy coin for score display
    score_coin = Coin(tile_size // 2, tile_size // 2)
    coin_group.add(score_coin)

    return world

# ----- Button class -----
class Button():
    def __init__(self, x, y, image):
        self.image   = image
        self.rect    = self.image.get_rect(topleft=(x,y))
        self.clicked = False

    def draw(self):
        action = False
        pos    = pygame.mouse.get_pos()

        if self.rect.collidepoint(pos):
            if pygame.mouse.get_pressed()[0] and not self.clicked:
                action = True
                self.clicked = True
        if not pygame.mouse.get_pressed()[0]:
            self.clicked = False

        screen.blit(self.image, self.rect)
        return action

# ----- Player class -----
class Player():
    def __init__(self, x, y, player_num):
        # store player number, then set up sprites via reset
        self.player_num = player_num
        self.reset(x, y)

    def reset(self, x, y):
        # only x, y needed now
        self.images_right = []
        self.images_left  = []
        self.index        = 0
        self.counter      = 0

        # load walk sprites for each player
        for num in range(1, 5):
            if self.player_num == 1:
                img = pygame.image.load(f'guy{num}.png')
            else:
                img = pygame.image.load(f'guy2{num}.png')
            img = pygame.transform.scale(img, (40, 40))
            self.images_right.append(img)
            self.images_left.append(pygame.transform.flip(img, True, False))

        self.dead_image = pygame.image.load('ghost.png')
        self.image      = self.images_right[self.index]
        self.rect       = self.image.get_rect(topleft=(x, y))
        self.width      = self.image.get_width()
        self.height     = self.image.get_height()
        self.vel_y      = 0
        self.jumped     = False
        self.direction  = 0
        self.in_air     = True

    def update(self, game_over):
        dx, dy = 0, 0
        walk_cooldown = 5
        col_thresh    = 20

        if game_over == 0:
            key = pygame.key.get_pressed()

            # controls per player
            if self.player_num == 1:
                # jump
                if key[K_w] and not self.jumped and not self.in_air:
                    jump_fx.play()
                    self.vel_y = -11.5
                    self.jumped = True
                if not key[K_w]:
                    self.jumped = False
                # left/right
                if key[K_a]:
                    dx -= 5; self.counter += 1; self.direction = -1
                if key[K_d]:
                    dx += 5; self.counter += 1; self.direction =  1
            else:
                if key[K_UP] and not self.jumped and not self.in_air:
                    jump_fx.play()
                    self.vel_y = -11.5
                    self.jumped = True
                if not key[K_UP]:
                    self.jumped = False
                if key[K_LEFT]:
                    dx -= 5; self.counter += 1; self.direction = -1
                if key[K_RIGHT]:
                    dx += 5; self.counter += 1; self.direction =  1

            # idle animation reset
            if not (key[K_a] or key[K_d] or key[K_LEFT] or key[K_RIGHT]):
                self.counter = 0
                self.index   = 0
                self.image = (self.images_right if self.direction == 1 else self.images_left)[self.index]

            # walk animation
            if self.counter > walk_cooldown:
                self.counter = 0
                self.index  += 1
                if self.index >= len(self.images_right):
                    self.index = 0
                self.image = (self.images_right if self.direction == 1 else self.images_left)[self.index]

            # gravity
            self.vel_y += 0.5
            if self.vel_y > 10:
                self.vel_y = 10
            dy += self.vel_y

            # tile collisions
            self.in_air = True
            for tile in world.tile_list:
                # x collision
                if tile[1].colliderect(self.rect.x + dx, self.rect.y, self.width, self.height):
                    dx = 0
                # y collision
                if tile[1].colliderect(self.rect.x, self.rect.y + dy, self.width, self.height):
                    if self.vel_y < 0:
                        dy = tile[1].bottom - self.rect.top
                        self.vel_y = 0
                    else:
                        dy = tile[1].top - self.rect.bottom
                        self.vel_y = 0
                        self.in_air = False

            # enemy collision
            if pygame.sprite.spritecollide(self, blob_group, False):
                game_over = -1
                game_over_fx.play()

            # lava collision
            if pygame.sprite.spritecollide(self, lava_group, False):
                game_over = -1
                game_over_fx.play()

            # exit collision
            if pygame.sprite.spritecollide(self, exit_group, False):
                game_over = 1

            # moving platforms
            for platform in platform_group:
                # x
                if platform.rect.colliderect(self.rect.x + dx, self.rect.y, self.width, self.height):
                    dx = 0
                # y
                if platform.rect.colliderect(self.rect.x, self.rect.y + dy, self.width, self.height):
                    if abs((self.rect.top + dy) - platform.rect.bottom) < col_thresh:
                        self.vel_y = 0
                        dy = platform.rect.bottom - self.rect.top
                    elif abs((self.rect.bottom + dy) - platform.rect.top) < col_thresh:
                        self.rect.bottom = platform.rect.top - 1
                        self.in_air = False
                        dy = 0
                    if platform.move_x != 0:
                        self.rect.x += platform.move_direction

            # apply movement
            self.rect.x += dx
            self.rect.y += dy

        elif game_over == -1:
            # death animation
            self.image = self.dead_image
            draw_text('GAME OVER!', font, blue,
                      (screen_width // 2) - 200, screen_height // 2)
            if self.rect.y > 200:
                self.rect.y -= 5

        # draw player
        screen.blit(self.image, self.rect)

        # player indicator circle
        indicator_color = red if self.player_num == 1 else blue
        pygame.draw.circle(screen, indicator_color,
                           (self.rect.centerx, self.rect.top - 10), 5)

        return game_over

# ----- World class -----
class World():
    def __init__(self, data):
        self.tile_list = []
        dirt_img  = pygame.image.load('dirt.png')
        grass_img = pygame.image.load('grass.png')

        for row_idx, row in enumerate(data):
            for col_idx, tile in enumerate(row):
                x = col_idx * tile_size
                y = row_idx * tile_size

                if tile == 1:
                    img = pygame.transform.scale(dirt_img, (tile_size, tile_size))
                    rect = img.get_rect(topleft=(x, y))
                    self.tile_list.append((img, rect))
                if tile == 2:
                    img = pygame.transform.scale(grass_img, (tile_size, tile_size))
                    rect = img.get_rect(topleft=(x, y))
                    self.tile_list.append((img, rect))
                if tile == 3:
                    blob = Enemy(x, y + 15)
                    blob_group.add(blob)
                if tile == 4:
                    platform = Platform(x, y, 1, 0)
                    platform_group.add(platform)
                if tile == 5:
                    platform = Platform(x, y, 0, 1)
                    platform_group.add(platform)
                if tile == 6:
                    lava = Lava(x, y + (tile_size // 2))
                    lava_group.add(lava)
                if tile == 7:
                    coin = Coin(x + tile_size//2, y + tile_size//2)
                    coin_group.add(coin)
                if tile == 8:
                    exit = Exit(x, y - (tile_size//2))
                    exit_group.add(exit)

    def draw(self):
        for img, rect in self.tile_list:
            screen.blit(img, rect)

# ----- Other Sprites -----
class Enemy(pygame.sprite.Sprite):
    def __init__(self, x, y):
        super().__init__()
        self.image = pygame.image.load('blob.png')
        self.rect  = self.image.get_rect(topleft=(x, y))
        self.move_direction = 1
        self.move_counter   = 0

    def update(self):
        self.rect.x += self.move_direction
        self.move_counter += 1
        if abs(self.move_counter) > 50:
            self.move_direction *= -1
            self.move_counter *= -1

class Platform(pygame.sprite.Sprite):
    def __init__(self, x, y, move_x, move_y):
        super().__init__()
        img = pygame.image.load('platform.png')
        self.image = pygame.transform.scale(img, (tile_size, tile_size//2))
        self.rect  = self.image.get_rect(topleft=(x, y))
        self.move_x = move_x
        self.move_y = move_y
        self.move_counter   = 0
        self.move_direction = 1

    def update(self):
        self.rect.x += self.move_direction * self.move_x
        self.rect.y += self.move_direction * self.move_y
        self.move_counter += 1
        if abs(self.move_counter) > 50:
            self.move_direction *= -1
            self.move_counter *= -1

class Lava(pygame.sprite.Sprite):
    def __init__(self, x, y):
        super().__init__()
        img = pygame.image.load('lava.png')
        self.image = pygame.transform.scale(img, (tile_size, tile_size//2))
        self.rect  = self.image.get_rect(topleft=(x, y))

class Coin(pygame.sprite.Sprite):
    def __init__(self, x, y):
        super().__init__()
        img = pygame.image.load('coin.png')
        self.image = pygame.transform.scale(img, (tile_size//2, tile_size//2))
        self.rect  = self.image.get_rect(center=(x, y))

class Exit(pygame.sprite.Sprite):
    def __init__(self, x, y):
        super().__init__()
        img = pygame.image.load('exit.png')
        self.image = pygame.transform.scale(img, (tile_size, int(tile_size*1.5)))
        self.rect  = self.image.get_rect(topleft=(x, y))

# ----- Create players and groups -----
player1 = Player(100, screen_height - 130, 1)
player2 = Player(150, screen_height - 130, 2)

blob_group     = pygame.sprite.Group()
platform_group = pygame.sprite.Group()
lava_group     = pygame.sprite.Group()
coin_group     = pygame.sprite.Group()
exit_group     = pygame.sprite.Group()

# dummy coin for score
score_coin = Coin(tile_size//2, tile_size//2)
coin_group.add(score_coin)

# load initial world
if path.exists(f'level{level}_data'):
    with open(f'level{level}_data', 'rb') as f:
        world_data = pickle.load(f)
world = World(world_data)

# buttons
restart_button = Button(screen_width//2 - 50,  screen_height//2 + 100, restart_img)
start_button   = Button(screen_width//2 - 350, screen_height//2,       start_img)
exit_button    = Button(screen_width//2 + 150, screen_height//2,       exit_img)
menu_logo      = Button(screen_width//2 - 250, screen_height//10,      menu_logo_i)

# ----- Main loop -----
run = True
while run:
    clock.tick(fps)
    screen.blit(bg_img, (0,0))
    screen.blit(sun_img, (100,100))

    if main_menu:
        if exit_button.draw():  run = False
        if start_button.draw(): main_menu = False
        if menu_logo.draw():   main_menu = False
    else:
        world.draw()

        if game_over == 0:
            blob_group.update()
            platform_group.update()

            # collect coins
            if pygame.sprite.spritecollide(player1, coin_group, True):
                score_p1 += 1; coin_fx.play()
            if pygame.sprite.spritecollide(player2, coin_group, True):
                score_p2 += 1; coin_fx.play()

            # draw scores
            draw_text(f'P1: {score_p1}', font_score, red,  tile_size-10, 10)
            draw_text(f'P2: {score_p2}', font_score, blue, tile_size-10, 50)

        blob_group.draw(screen)
        platform_group.draw(screen)
        lava_group.draw(screen)
        coin_group.draw(screen)
        exit_group.draw(screen)

        # update players
        game_over_p1 = player1.update(game_over)
        game_over_p2 = player2.update(game_over)

        # game over if either dies
        if game_over_p1 == -1 or game_over_p2 == -1:
            game_over = -1
        # level complete if both exit
        if game_over_p1 == 1 and game_over_p2 == 1:
            game_over = 1

        if game_over == -1:
            if restart_button.draw():
                world = reset_level(level)
                game_over = 0
                score_p1 = score_p2 = 0

        if game_over == 1:
            level += 1
            if level <= max_levels:
                world = reset_level(level)
                game_over = 0
            else:
                draw_text('YOU WIN!', font, blue,
                          (screen_width//2) - 140, screen_height//2)
                if restart_button.draw():
                    level = 1
                    world = reset_level(level)
                    game_over = 0
                    score_p1 = score_p2 = 0

    for event in pygame.event.get():
        if event.type == QUIT:
            run = False

    pygame.display.update()

pygame.quit()