import sys

import pygame
import random, time
import os
import numpy as np

#### Constants

width, height = 288, 512
fps = 60

pygame.init()
screen = pygame.display.set_mode((width, height))
pygame.display.set_caption('Fucking bird')
clock = pygame.time.Clock()
icon = pygame.image.load('assets/sprites/icon.png')
pygame.display.set_icon(icon)

#### Materials
Images = {}
for image in os.listdir('assets/sprites'):
    name, extension = os.path.splitext(image)
    if extension == '.png':
        path = os.path.join('assets/sprites', image)
        Images[name] = pygame.image.load(path)

#### Sound
Sound = {}
for sound in os.listdir('assets/audio'):
    name, extension = os.path.splitext(sound)
    path = os.path.join('assets/audio', sound)
    if extension == '.wav' or '.mp3' or 'ogg':
        Sound[name] = pygame.mixer.Sound(path)

bg_list = ['day', 'night', 'ocean', 'space']
weapon_list = ['rifle', 'tripod_rifle', 'chaser', 'shotgun', ]
weapon_price = [20, 40, 60]
potion_list = ['drink1', 'drink2']
potion_price = [1, 5]
enermy_number_list =[22, 32, 50, 80]
shop_price = weapon_price + potion_price

font_en = pygame.font.SysFont('Times New Roman', 30, bold=True)
font_en_20 = pygame.font.SysFont('Times New Roman', 20, bold=True)
font_en_15 = pygame.font.SysFont('Times New Roman', 15, bold=True)
font_en_Gothic = pygame.font.SysFont('MS Gothic', 20, bold=True)


class Bird(pygame.sprite.Sprite):
    def __init__(self, x, y):
        pygame.sprite.Sprite.__init__(self)
        self.frames = [0]*5 + [1]*5 + [2]*5 + [1]*5
        self.idx = 0
        self.image = Images['birds'][self.frames[self.idx]]
        self.rect = self.image.get_rect()
        self.rect.x = x
        self.rect.y = y
        self.y_v = -10
        self.max_y_v = 10
        self.die_y_v = 2
        self.gravity = 1
        self.angle = 25
        self.max_angle = -20
        self.rotate_v = -1
        self.rotate_v_ini = -1
        self.y_v_ini = -10
        self.angle_ini = 25
        self.hp = 10
        self.hp_full = 10

    def update(self, flap, damage):
        if flap:
            self.y_v = self.y_v_ini
            self.rotate_v = 15
        if flap == False: self.rotate_v = self.rotate_v_ini
            # self.angle = self.angle_ini

        self.y_v = min(self.y_v+self.gravity, self.max_y_v)
        self.rect.y += self.y_v
        if self.rect.y <0: self.rect.y = 0
        if self.rect.y >height-Images['base'].get_height()-20: self.rect.y = height-Images['base'].get_height()-20

        if self.angle+self.rotate_v > 25: self.angle = 25
        elif self.angle+self.rotate_v < -25: self.angle = -25
        else: self.angle = self.angle+self.rotate_v

        self.idx += 1
        self.idx %= len(self.frames)
        self.image = Images['birds'][self.frames[self.idx]]
        self.image = pygame.transform.rotate(self.image, self.angle)
        self.hp -= damage
        if self.hp >= 10: self.hp = 10

    def die(self):
        if self.rect.y < height-Images['base'].get_height()-20:

            self.rect.y += self.die_y_v
            self.angle = -90
            self.image = Images['birds'][self.frames[self.idx]]
            self.image = pygame.transform.rotate(self.image, self.angle)


class Bullet(pygame.sprite.Sprite):
    def __init__(self, x, y, angle):
        pygame.sprite.Sprite.__init__(self)
        self.damage = 1
        self.image = Images['RegAttack']
        self.rect = self.image.get_rect()
        self.rect.x = x
        self.rect.y = y
        self.angle = angle
        self.v_x = 5
        self.image = pygame.transform.rotate(self.image, self.angle)


    def update(self):
        self.rect.x += self.v_x * np.cos(self.angle*np.pi/180)
        self.rect.y -= self.v_x * np.sin(self.angle*np.pi/180)

class Chaser(pygame.sprite.Sprite):
    def __init__(self, x, y, angle):
        pygame.sprite.Sprite.__init__(self)
        self.damage = 2
        loop_time = 5
        self.idx = 0
        self.frames = [0]*loop_time + [1]*loop_time
        Images['chaser'] = [Images['Ammo_chaser1'], Images['Ammo_chaser2']]
        self.image = Images['chaser'][self.frames[self.idx]]
        self.rect = self.image.get_rect()
        self.rect.x = x
        self.rect.y = y
        self.angle = angle
        self.v_x = 5
        self.image = pygame.transform.rotate(self.image, self.angle)

    def update(self, target):
        if target == None:
            distance_x = 1000
            distance_y = 0
        else:
            distance_x = target.rect.x - self.rect.x
            distance_y = target.rect.y - self.rect.y
        if distance_x > 0: self.rect.x += self.v_x
        elif distance_x < 0: self.rect.x -= self.v_x

        if distance_y < 0: self.rect.y -= self.v_x
        elif distance_y > 0: self.rect.y += self.v_x

        if distance_x == 0:
            target_angle = 90
        elif distance_x > 0: target_angle = np.arctan(-distance_y/distance_x)*180/np.pi
        elif distance_x < 0: target_angle = 180 + np.arctan(-distance_y/distance_x)*180/np.pi

        # print(distance_x, -distance_y)
        # print(target_angle)
        # breakpoint()

        self.idx += 1
        self.idx %= len(self.frames)
        self.image = Images['chaser'][self.frames[self.idx]]
        self.image = pygame.transform.rotate(self.image, target_angle)


class Shotgun(pygame.sprite.Sprite):
    def __init__(self, x, y, angle):
        pygame.sprite.Sprite.__init__(self)
        self.damage = 3
        loop_time = 3
        self.idx = 0
        self.frames = []
        for i in range(4): self.frames += [i] * loop_time
        Images['shotgun'] = [Images['Ammo_shootgun3'], Images['Ammo_shootgun4'], Images['Ammo_shootgun5'], Images['Ammo_shootgun7']]
        # Images['shotgun'] = [Images['Ammo_shootgun'+str(i+1)] for i in range(8)]
        self.image = Images['shotgun'][self.frames[self.idx]]
        self.rect = self.image.get_rect()
        self.rect.x = x
        self.rect.y = y
        self.angle = angle
        self.v_x = 5
        self.image = pygame.transform.rotate(self.image, self.angle)
        self.neglect_obj = []

    def update(self, obj):
        # self.rect.x += self.v_x * np.cos(self.angle * np.pi / 180)
        # self.rect.y -= self.v_x * np.sin(self.angle * np.pi / 180)
        self.idx += 1
        self.idx %= len(self.frames)
        if self.idx == 0: self.kill()
        self.image = Images['shotgun'][self.frames[self.idx]]
        self.image = pygame.transform.rotate(self.image, self.angle)
        self.neglect_obj.append(obj)


class Item(pygame.sprite.Sprite):
    def __init__(self, x, y):
        pygame.sprite.Sprite.__init__(self)
        rand = random.uniform(0, 1)
        if rand < 0.2:
            self.image = Images['drink2']
            self.hp_plus = -4
        else:
            self.image = Images['drink1']
            self.hp_plus = -1
        self.rect = self.image.get_rect()
        self.rect.x = x
        self.rect.y = y
        self.v_x = -1

    def update(self):
        self.rect.x += self.v_x


class Slime_green(pygame.sprite.Sprite):
    def __init__(self, x, y):
        pygame.sprite.Sprite.__init__(self)
        self.hp = 1
        self.v_x = -1
        loop_time = 20
        self.idx = 0
        self.frames = [0]*loop_time + [1]*loop_time

        Images['slime_green'] = [Images['slime_green1'], Images['slime_green2']]
        self.image = Images['slime_green'][self.frames[self.idx]]
        self.rect = self.image.get_rect()
        self.rect.x = x
        self.rect.y = y

    def update(self, damage):
        self.rect.x += self.v_x
        self.idx += 1
        self.idx %= len(self.frames)
        self.image = Images['slime_green'][self.frames[self.idx]]
        self.hp -= damage

class Slime_red(Slime_green):
    def update(self, damage):
        self.rect.x += self.v_x
        self.idx += 1
        self.idx %= len(self.frames)
        Images['slime_red'] = [Images['slime_red1'], Images['slime_red2']]
        self.image = Images['slime_red'][self.frames[self.idx]]
        self.hp -= damage

class Slime_king(Slime_green):
    def __init__(self, x, y):
        super().__init__(x, y)
        self.hp = 3
    def update(self, damage):
        self.rect.x += self.v_x
        self.idx += 1
        self.idx %= len(self.frames)
        Images['slime_king'] = [Images['slime_king1'], Images['slime_king2']]
        self.image = Images['slime_king'][self.frames[self.idx]]
        self.hp -= damage

class Bat_blue(Slime_green):
    def __init__(self, x, y):
        super().__init__(x, y)
        self.hp = 2
    def update(self, damage):
        self.rect.x += self.v_x
        self.idx += 1
        self.idx %= len(self.frames)
        Images['bat_blue'] = [Images['bat_blue1'], Images['bat_blue2']]
        self.image = Images['bat_blue'][self.frames[self.idx]]
        self.hp -= damage

class Bat_red(Slime_green):
    def __init__(self, x, y):
        super().__init__(x, y)
        self.hp = 3
    def update(self, damage):
        self.rect.x += self.v_x
        self.idx += 1
        self.idx %= len(self.frames)
        Images['bat_red'] = [Images['bat_red1'], Images['bat_red2']]
        self.image = Images['bat_red'][self.frames[self.idx]]
        self.hp -= damage

class Bat_little(Slime_green):
    def __init__(self, x, y):
        super().__init__(x, y)
        self.hp = 1
    def update(self, damage):
        self.rect.x += self.v_x
        self.idx += 1
        self.idx %= len(self.frames)
        Images['bat_little'] = [Images['bat_little1'], Images['bat_little2']]
        self.image = Images['bat_little'][self.frames[self.idx]]
        self.hp -= damage

class Elve(Slime_green):
    def __init__(self, x, y):
        super().__init__(x, y)
        self.hp = 4
    def update(self, damage):
        self.rect.x += self.v_x
        self.idx += 1
        self.idx %= len(self.frames)
        Images['elve'] = [Images['elve1'], Images['elve2']]
        self.image = Images['elve'][self.frames[self.idx]]
        self.hp -= damage

class Devil_blue(Slime_green):
    def __init__(self, x, y):
        super().__init__(x, y)
        self.hp = 4
    def update(self, damage):
        self.rect.x += self.v_x
        self.idx += 1
        self.idx %= len(self.frames)
        Images['devil_blue'] = [Images['devil_blue1'], Images['devil_blue2']]
        self.image = Images['devil_blue'][self.frames[self.idx]]
        self.hp -= damage

class Devil_red(Slime_green):
    def __init__(self, x, y):
        super().__init__(x, y)
        self.hp = 5
    def update(self, damage):
        self.rect.x += self.v_x
        self.idx += 1
        self.idx %= len(self.frames)
        Images['devil_red'] = [Images['devil_red1'], Images['devil_red2']]
        self.image = Images['devil_red'][self.frames[self.idx]]
        self.hp -= damage

class Boss_attack(pygame.sprite.Sprite):
    def __init__(self, x, y, angle, level):
        pygame.sprite.Sprite.__init__(self)
        self.boss_attack_type = [random.choice(('slime_green', 'slime_red')), random.choice(('bat_little', 'bat_blue')),
                                 random.choice(('bat_red', 'slime_king')), random.choice(('devil_red', 'devil_blue', 'elve', 'fuckingbird'))][level]
        self.idx = 0
        loop_time = 20
        self.frames = [0]*loop_time + [1]*loop_time
        Images['bossattack'] = [Images[self.boss_attack_type+'1'], Images[self.boss_attack_type+'2']]
        self.image = Images['bossattack'][self.frames[self.idx]]
        self.rect = self.image.get_rect()
        self.rect.x = x
        self.rect.y = y
        self.angle = angle
        self.v_x = 5
        self.image = pygame.transform.rotate(self.image, self.angle)

    def update(self, damage):
        self.idx += 1
        self.idx %= len(self.frames)
        self.image = Images['bossattack'][self.frames[self.idx]]

        self.rect.x += self.v_x * np.cos(self.angle*np.pi/180)
        self.rect.y += self.v_x * np.sin(self.angle*np.pi/180)


class Boss(pygame.sprite.Sprite):
    def __init__(self, x, y, level):
        pygame.sprite.Sprite.__init__(self)
        self.boss_type = ['slime_king', 'bat_red', 'elve', 'witch'][level]
        boss_hp = [30, 60, 120, 200]
        Images['boss'] = [Images[self.boss_type+'1'], Images[self.boss_type+'2']]
        loop_time = 20
        self.idx = 0
        self.frames = [0]*loop_time + [1]*loop_time
        self.image = Images['boss'][self.frames[self.idx]]
        self.image = pygame.transform.scale(self.image, (100, 100))
        self.rect = self.image.get_rect()
        self.rect.x = x
        self.rect.y = y
        self.hp = boss_hp[level]
        self.rush_v = 20
        self.move_v = 5
        self.initial_location = (width-100+self.rect.width/2, (height-100)/2+self.rect.height/2)

    def update(self, damage, rush, rush_location, is_rused):
        self.idx += 1
        self.idx %= len(self.frames)
        self.image = Images['boss'][self.frames[self.idx]]
        self.image = pygame.transform.scale(self.image, (100, 100))
        self.hp -= damage

        if self.boss_type != 'slime_king':
            if self.boss_type == 'elve' or self.boss_type == 'witch':
                if rush == False and is_rused == False:
                    if self.rect.y >= 300: self.move_v /= -1
                    if self.rect.y <= 100: self.move_v /= -1
                    self.rect.y += self.move_v

                elif rush == True and is_rused == False:
                    self.rect.x += (rush_location[0] - self.rect.center[0])/self.rush_v
                    self.rect.y += (rush_location[1] - self.rect.center[1])/self.rush_v

            elif self.boss_type == 'bat_red':
                if rush == True and is_rused == False:
                    self.rect.x += (rush_location[0] - self.rect.center[0]) / self.rush_v
                    self.rect.y += (rush_location[1] - self.rect.center[1]) / self.rush_v


class Info(pygame.sprite.Sprite):
    def __init__(self, x, y, scale):
        pygame.sprite.Sprite.__init__(self)
        loop_time = 10
        self.frames = [0]*loop_time + [1]*loop_time + [2]*loop_time + [3]*loop_time
        self.idx = 0
        self.image = Images['coin'][self.frames[self.idx]]

        self.rect = self.image.get_rect()
        self.rect.x = x
        self.rect.y = y
        self.scale_f = scale

    def update(self):
        self.idx += 1
        self.idx %= len(self.frames)
        self.image = Images['coin'][self.frames[self.idx]]
        self.image = pygame.transform.scale(self.image, (self.scale_f, self.scale_f))

class Shop(pygame.sprite.Sprite):
    def __init__(self, x, y):
        pygame.sprite.Sprite.__init__(self)
        Images['shop'] = [Images['shop1'], Images['shop2']]
        loop_time = 40
        self.frames = [0]*loop_time + [1]*loop_time
        self.idx = 0
        self.image = Images['shop'][self.frames[self.idx]]

        self.rect = self.image.get_rect()
        self.rect.x = x
        self.rect.y = y

    def update(self):
        self.idx += 1
        self.idx %= len(self.frames)
        self.image = Images['shop'][self.frames[self.idx]]

def check_out_screen(group, chaser_list):
    for spr in group.sprites():
        if spr.rect.center[0] < 0 or spr.rect.center[0] > width or spr.rect.center[1] < 0 or spr.rect.center[1] > height:
            spr.kill()
            for i in range(len(chaser_list)):
                if chaser_list[i][1] == spr:
                    chaser_list[i][0].kill()

def main():
    while True:
        bird_color = random.choice(['red', 'yellow', 'blue'])
        Images['birds'] = [Images[bird_color+'bird-upflap'], Images[bird_color+'bird-midflap'], Images[bird_color+'bird-downflap']]
        Images['coin'] = [Images['coin1'], Images['coin2'], Images['coin3'], Images['coin4']]

        menu_window()

        end_bird, end_level, score = game_window()
        end_window(end_bird, end_level, score)

def menu_window():

    idx = 0
    repeat = 5
    frames = [0]*repeat + [1]*repeat + [2]*repeat + [1]*repeat
    bird_x, bird_y = (width - Images['birds'][frames[idx]].get_width()) / 3, (height - Images['birds'][frames[idx]].get_height()) / 2
    bird_y_v = 1
    bird_yrange = [bird_y-4, bird_y+4]
    Sound['bgm_sum'].play(-1)


    while True:
        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                pygame.display.quit()
                sys.exit()
            if event.type == pygame.KEYDOWN and event.key == pygame.K_SPACE:
                Sound['swoosh'].play()
                return

        idx += 1
        idx %= len(frames)
        bird_y += bird_y_v
        if bird_y < bird_yrange[0] or bird_y > bird_yrange[1]: bird_y_v/=-1


        screen.blit(Images['background-'+'day'], (0, 0))
        screen.blit(Images['base'], (0, (height-Images['base'].get_height())))
        screen.blit(Images['message'], ((width-Images['message'].get_width())/2, (height-Images['message'].get_height())/3))
        screen.blit(Images['birds'][frames[idx]], (bird_x, bird_y))
        pygame.display.update()
        clock.tick(fps)



def game_window():
    time_start_ini = pygame.time.get_ticks()
    level = 0
    weapon = weapon_list[0]
    machinegun_ammo = 1

    floor_gap = Images['base'].get_width() - width
    floor_x = 0
    bird = Bird(0.1*width, 0.4*height)
    bird_group = pygame.sprite.Group()
    bird_group.add(bird)
    bullet_group = pygame.sprite.Group()
    shotgun_group = pygame.sprite.Group()
    chaser_group = pygame.sprite.Group()
    item_group = pygame.sprite.Group()
    enermy_group = pygame.sprite.Group()
    boss_attack_group = pygame.sprite.Group()
    boss_group = pygame.sprite.Group()
    coin_group = pygame.sprite.Group()
    menu_shop_group = pygame.sprite.Group()
    time_start = pygame.time.get_ticks()
    boss_attack_frequency = random.randint(1000, 2000)
    boss_rush_frequency = random.randint(1000, 5000)
    in_shop_menu = False

    selected_option = 0
    menu_options = ['Machinegun', 'Chaser', 'Shotgun', 'HP+1', 'HP+4']
    owned_weapon = [False, False, False, False, False]
    chaser_list = []

    score_record = 0
    coin_record = 0

    coin_group.add(Info(0, 0, 30))
    menu_shop_group.add(Info(55, 162, 18))
    menu_shop_group.add(Info(55, 192, 18))
    menu_shop_group.add(Info(55, 222, 18))
    menu_shop_group.add(Info(55, 252, 18))
    menu_shop_group.add(Info(55, 282, 18))
    menu_shop_group.add(Shop(100, 90))


    while True:
        end_less_mode = False
        boss_showup = False
        boss_rush = False
        is_rushed = False
        rush_location=[0, 0]
        no_fucking_money = False
        enermy_showed = 0
        if end_less_mode == False:
            enermy_showup_frequency = random.randint(int(2000/(level+1)), int(5000/(level+1)))
        else:
            enermy_showup_frequency = random.randint(int(2000/(8)), int(5000/(8)))
        while True:
            enermy_number = enermy_number_list[level]
            flap = False
            bg_color = bg_list[level]
            screen.blit(Images['background-'+bg_color], (0, 0))
            screen.blit(Images['base'], (floor_x, (height-Images['base'].get_height())))
            screen.blit(bird.image, bird.rect)
            screen.blit(font_en.render(str(coin_record), True, (255, 255, 255)), (35, 0))
            screen.blit(font_en_20.render('Score: '+str(score_record), True, (255, 255, 255)), (int(width/2), 0))

            # screen.blit(bullet.image, bullet.rect)
            for event in pygame.event.get():
                if event.type == pygame.QUIT:
                    pygame.display.quit()
                    sys.exit()
                    # quit()

                if event.type == pygame.KEYDOWN and event.key == pygame.K_SPACE:
                    Sound['wing'].play()
                    flap = True
                    if weapon == weapon_list[0]:
                        bullet_group.add(Bullet(bird.rect.x, bird.rect.y, bird.angle))
                    elif weapon == weapon_list[1]:
                        for i in range(machinegun_ammo):
                            bullet_group.add(Bullet(random.uniform(bird.rect.center[0], bird.rect.right), random.uniform(bird.rect.y, bird.rect.y+bird.rect.height), bird.angle+random.uniform(-20, 20)))
                    elif weapon == weapon_list[2]:
                        chaseri = Chaser(bird.rect.x, bird.rect.y, bird.angle)
                        chaser_group.add(chaseri)
                        if enermy_group.sprites()!= []:
                            targeti = random.choice(enermy_group.sprites())
                        elif boss_group.sprites()!= []:
                            targeti = random.choice(boss_group.sprites())
                        else: targeti = None
                        chaser_list.append([chaseri, targeti])

                    elif weapon == weapon_list[3]:
                        shotgun_group.add(Shotgun(bird.rect.right, (bird.rect.y)-bird.rect.height*(np.cos(bird.angle*np.pi/180)), bird.angle))

                if event.type == pygame.KEYDOWN and event.key == pygame.K_ESCAPE:
                    selected_option = 0
                    in_shop_menu = not in_shop_menu
                    no_fucking_money = False

                if in_shop_menu == True:
                    Sound['bgm_sum'].set_volume(0.2)
                    if event.type == pygame.KEYDOWN:
                        if event.key == pygame.K_UP:
                            selected_option = (selected_option - 1) % len(menu_options)
                        elif event.key == pygame.K_DOWN:
                            selected_option = (selected_option + 1) % len(menu_options)
                        elif event.key == pygame.K_RETURN:
                            if owned_weapon[selected_option] == False:
                                if coin_record >= shop_price[selected_option]:
                                    if selected_option == 0:
                                        coin_record -= shop_price[selected_option] + (machinegun_ammo-1)*30
                                        weapon = weapon_list[selected_option+1]
                                        machinegun_ammo += 1
                                        if machinegun_ammo >= 5:
                                            owned_weapon[selected_option] = True
                                        Sound['Reload'].play()
                                    elif selected_option < 3:
                                        coin_record -= shop_price[selected_option]
                                        owned_weapon[selected_option] = True
                                        weapon = weapon_list[selected_option + 1]
                                        Sound['Reload'].play()
                                    elif selected_option == 3:
                                        coin_record -= shop_price[selected_option]
                                        bird.update(False, -1)
                                        Sound['resume'].play()
                                    elif selected_option == 4:
                                        coin_record -= shop_price[selected_option]
                                        bird.update(False, -4)
                                        Sound['resume'].play()
                                else:
                                    no_fucking_money = True
                                    Sound['error'].play()
                            else:
                                if selected_option < 3:
                                    owned_weapon[selected_option] = True
                                    weapon = weapon_list[selected_option + 1]
                                    Sound['Reload'].play()

            if in_shop_menu == True:
                if no_fucking_money == True:
                    screen.blit(font_en_20.render('No fucking money!', True, (255, 0, 0)), (60, 450))
                screen.blit(font_en_20.render('↑↓ to choose,    to buy', True, (220, 220, 220)), (50, 130))
                screen.blit(font_en_Gothic.render('↵', True, (220, 220, 220)), (162, 130))
                screen.blit(font_en_20.render('HP:', True, (0, 0, 0)), (0, 425))
                pygame.draw.rect(screen, (255, 255, 255), (37, 431, 100, 12))
                pygame.draw.rect(screen, (255, 0, 0), (37, 431, 100*bird.hp/bird.hp_full, 12))
                screen.blit(font_en_15.render(str(bird.hp)+'/'+str(bird.hp_full), True, (0, 0, 0)), (70, 428))
                for i in range(len(weapon_price)):
                    if owned_weapon[i] == True:
                        screen.blit(font_en_20.render('0:', True, (220, 220, 220)), (84, 160+30*i))
                    else:
                        if i == 0:
                            screen.blit(font_en_20.render(str(weapon_price[i]+ (machinegun_ammo-1) * 30) + ':', True, (220, 220, 220)), (75, 160 + 30 * i))
                        else:
                            screen.blit(font_en_20.render(str(weapon_price[i]) + ':', True, (220, 220, 220)), (75, 160 + 30 * i))
                for i in range(len(potion_price)):
                    screen.blit(font_en_20.render(str(potion_price[i])+':', True, (220, 220, 220)), (84, 250+30*i))
                for i in range(len(menu_options)):
                    color = (255, 255, 255) if i == selected_option else (220, 220, 220)
                    if i == 0:
                        screen.blit(font_en_20.render(menu_options[i]+'+'+str(machinegun_ammo), True, color), (110, 160+30*i))
                    else: screen.blit(font_en_20.render(menu_options[i], True, color), (110, 160+30*i))
                screen.blit(Images['drink1'], (170, 245))
                screen.blit(Images['drink2'], (170, 275))

                menu_shop_group.draw(screen)
                menu_shop_group.update()

            if in_shop_menu == False:
                Sound['bgm_sum'].set_volume(1)

                current_time = pygame.time.get_ticks()
                # print(current_time, time_start)
                if current_time - time_start > enermy_showup_frequency:
                    enermy_showed += 1
                    if level == 0:
                        if random.choice([True, False]):
                            enermy_group.add(Slime_green(random.randint(int(width / 2), width), random.randint(0, height - 250)))
                        else:
                            enermy_group.add(Slime_red(random.randint(int(width / 2), width), random.randint(0, height - 250)))
                    if level == 1:
                        if random.choice([True, False]):
                            enermy_group.add(Bat_little(random.randint(int(width / 2), width), random.randint(0, height - 250)))
                        else:
                            enermy_group.add(Bat_blue(random.randint(int(width / 2), width), random.randint(0, height - 250)))
                    if level == 2:
                        if random.choice([True, False]):
                            enermy_group.add(Slime_king(random.randint(int(width / 2), width), random.randint(0, height - 250)))
                        else:
                            enermy_group.add(Bat_red(random.randint(int(width / 2), width), random.randint(0, height - 250)))
                    if level == 3:
                        choose = random.uniform(0, 1)
                        if choose <= 0.4:
                            enermy_group.add(Devil_blue(random.randint(int(width / 2), width), random.randint(0, height - 250)))
                        elif 0.4 < choose <= 0.6:
                            enermy_group.add(Devil_red(random.randint(int(width / 2), width), random.randint(0, height - 250)))
                        elif choose > 0.6:
                            enermy_group.add(Devil_red(random.randint(int(width / 2), width), random.randint(0, height - 250)))



                    # item_group.add(Item(random.randint(int(width/2), width), random.randint(0, height-250)))
                    time_start = current_time

                colli_list_bull_enermy = pygame.sprite.groupcollide(bullet_group, enermy_group, True, False)
                colli_list_shotgun_enermy = pygame.sprite.groupcollide(shotgun_group, enermy_group, False, False)
                colli_list_chaser_enermy = pygame.sprite.groupcollide(chaser_group, enermy_group, True, False)
                if len(colli_list_bull_enermy) != 0:
                    hurted_ammo = list(colli_list_bull_enermy.keys())[0]
                    hurted_sprite = list(colli_list_bull_enermy.values())[0][0]
                    hurted_sprite.update(hurted_ammo.damage)
                    Sound['point'].play()
                    score_record += 1
                    coin_record += 1
                    if hurted_sprite.hp <= 0:
                        hurted_sprite.kill()
                        if 0 < random.uniform(0, 1) < 0.1:
                            item_group.add(Item(random.randint(int(width / 2), width), random.randint(0, height - 250)))
                if len(colli_list_chaser_enermy) != 0:
                    hurted_ammo = list(colli_list_chaser_enermy.keys())[0]
                    hurted_sprite = list(colli_list_chaser_enermy.values())[0][0]
                    hurted_sprite.update(hurted_ammo.damage)
                    Sound['point'].play()
                    score_record += 1
                    coin_record += 1
                    if hurted_sprite.hp <= 0:
                        hurted_sprite.kill()
                        if 0 < random.uniform(0, 1) < 0.1:
                            item_group.add(Item(random.randint(int(width / 2), width), random.randint(0, height - 250)))
                        for i in range(len(chaser_list)):
                            if chaser_list[i][1] == hurted_sprite:
                                chaser_list[i][0].kill()
                if len(colli_list_shotgun_enermy) != 0:
                    shot_obj = list(colli_list_shotgun_enermy.values())[0]
                    shot_ammo = list(colli_list_shotgun_enermy.keys())[0]
                    if shot_obj in shot_ammo.neglect_obj:
                        pass
                    else:
                        shotgun_group.update(shot_obj)
                        hurted_sprite = list(colli_list_shotgun_enermy.values())[0][0]
                        hurted_sprite.update(shot_ammo.damage)
                        Sound['point'].play()
                        score_record += 1
                        coin_record += 1
                        if hurted_sprite.hp <= 0:
                            hurted_sprite.kill()
                            if 0 < random.uniform(0, 1) < 0.1:
                                item_group.add(Item(random.randint(int(width / 2), width), random.randint(0, height - 250)))

                colli_list_bird_item = pygame.sprite.groupcollide(bird_group, item_group, False, True)
                if len(colli_list_bird_item) != 0:
                    Sound['resume'].play()
                    bird_group.update(False, list(colli_list_bird_item.values())[0][0].hp_plus)



                colli_list_bird_enermy = pygame.sprite.groupcollide(bird_group, enermy_group, False, True)
                colli_list_bird_bossattack = pygame.sprite.groupcollide(bird_group, boss_attack_group, False, True)
                colli_list_bird_bossrush = pygame.sprite.groupcollide(bird_group, boss_group, False, False)
                if len(colli_list_bird_enermy) != 0 or len(colli_list_bird_bossattack) != 0:
                    Sound['hit'].play()
                    bird_group.update(False, 1)
                    if bird.hp <= 0:
                        Sound['bgm_sum'].stop()
                        return bird, level, score_record

                    if list(colli_list_bird_enermy.values()) != []:
                        hurted_sprite = list(colli_list_bird_enermy.values())[0][0]
                        for i in range(len(chaser_list)):
                            if chaser_list[i][1] == hurted_sprite:
                                chaser_list[i][0].kill()



                # print(enermy_showed, enermy_number)
                if enermy_showed >= enermy_number and boss_showup == False:
                    boss_showup = True
                    time_boss_attack = pygame.time.get_ticks()
                    time_boss_rush = pygame.time.get_ticks()

                    boss = Boss(width-100, (height-100)/2, level)
                    boss_group.add(boss)


                if boss_showup == True:
                    if list(colli_list_bird_bossrush.values()) != []:
                        is_rushed = True
                        Sound['hit'].play()
                        bird_group.update(False, 1)
                        if bird.hp <= 0:
                            Sound['bgm_sum'].stop()
                            return bird, level, score_record
                    elif boss.rect.x == 6:
                        is_rushed = True

                    if boss.rect.center[0] == 229:
                        boss_rush = False
                        is_rushed = False

                    diameter = 100
                    attack_x = []
                    attack_y = []
                    attack_angle = [random.randint(0, 360) for i in range(20)]
                    for i in range(len(attack_angle)):
                        attack_x.append(boss.rect.center[0] + diameter * np.cos(attack_angle[i] * np.pi / 180))
                        attack_y.append(boss.rect.center[0] + diameter * np.sin(attack_angle[i] * np.pi / 180))
                    if current_time - time_boss_attack > boss_attack_frequency:
                        [boss_attack_group.add(Boss_attack(attack_x[i], attack_y[i], attack_angle[i], level)) for i in range(len(attack_angle))]
                        boss_attack_group.draw(screen)
                        time_boss_attack = current_time
                    if current_time - time_boss_rush > boss_rush_frequency:
                        is_rushed == False
                        boss_rush = True
                        rush_location = bird.rect.center
                        boss_group.update(0, boss_rush, rush_location, is_rushed)
                        time_boss_rush = current_time


                    colli_list_bull_bossattack = pygame.sprite.groupcollide(bullet_group, boss_attack_group, True, True)
                    colli_list_chaser_bossattack = pygame.sprite.groupcollide(chaser_group, boss_attack_group, True, True)
                    colli_list_shotgun_bossattack = pygame.sprite.groupcollide(shotgun_group, boss_attack_group, False, True)
                    colli_list_bull_boss = pygame.sprite.groupcollide(bullet_group, boss_group, True, False)
                    colli_list_shotgun_boss = pygame.sprite.groupcollide(shotgun_group, boss_group, False, False)
                    colli_list_chaser_boss = pygame.sprite.groupcollide(chaser_group, boss_group, True, False)
                    if len(colli_list_bull_boss) != 0:
                        shot_obj = list(colli_list_bull_boss.values())[0]
                        shot_ammo = list(colli_list_bull_boss.keys())[0]
                        boss_group.update(shot_ammo.damage, False, None, False)
                        Sound['point'].play()
                        score_record += 1
                        if boss.hp <= 0:
                            boss.kill()
                            boss_showup == False
                            if level < 3:
                                level += 1
                                break
                            elif level == 3:
                                end_less_mode = True
                                break

                    if len(colli_list_chaser_boss) != 0:
                        shot_obj = list(colli_list_chaser_boss.values())[0]
                        shot_ammo = list(colli_list_chaser_boss.keys())[0]
                        boss_group.update(shot_ammo.damage, False, None, False)
                        Sound['point'].play()
                        score_record += 1
                        if boss.hp <= 0:
                            boss.kill()
                            boss_showup == False
                            if level < 3:
                                level += 1
                                break
                            elif level == 3:
                                end_less_mode = True
                                break

                    if len(colli_list_shotgun_boss) != 0:
                        shot_obj = list(colli_list_shotgun_boss.values())[0]
                        shot_ammo = list(colli_list_shotgun_boss.keys())[0]
                        if shot_obj in shot_ammo.neglect_obj:
                            pass
                        else:
                            shotgun_group.update(shot_obj)
                            boss_group.update(shot_ammo.damage, False, None, False)
                            Sound['point'].play()
                            score_record += 1
                            if boss.hp <= 0:
                                boss.kill()
                                boss_showup == False
                                if level < 3:
                                    level += 1
                                    break
                                elif level == 3:
                                    end_less_mode = True
                                    break

                floor_x -= 1
                if floor_x <= -floor_gap: floor_x = 0

                bullet_group.draw(screen)
                shotgun_group.draw(screen)
                chaser_group.draw(screen)
                item_group.draw(screen)
                enermy_group.draw(screen)
                boss_group.draw(screen)
                boss_attack_group.draw(screen)

                screen.blit(font_en_20.render('HP:', True, (0, 0, 0)), (0, 425))
                pygame.draw.rect(screen, (255, 255, 255), (37, 431, 100, 12))
                pygame.draw.rect(screen, (255, 0, 0), (37, 431, 100*bird.hp/bird.hp_full, 12))
                screen.blit(font_en_15.render(str(bird.hp)+'/'+str(bird.hp_full), True, (0, 0, 0)), (70, 428))
                screen.blit(font_en_20.render('Esc: open shop', True, (0, 0, 0)), (160, 425))

                bird.update(flap, 0)
                shotgun_group.update(None)
                item_group.update()
                boss_attack_group.update(0)
                if boss_rush == True and is_rushed == False:
                    boss_group.update(0, boss_rush, rush_location, is_rushed)
                elif boss_rush == True and is_rushed == True:
                    boss_group.update(0, True, boss.initial_location, False)
                else:
                    boss_group.update(0, False, None, False)
                enermy_group.update(0)
                bullet_group.update()
                for i in range(len(chaser_list)):
                    chaser_list[i][0].update(chaser_list[i][1])

            check_out_screen(bullet_group, chaser_list)
            check_out_screen(chaser_group, chaser_list)
            check_out_screen(item_group, chaser_list)
            check_out_screen(boss_attack_group, chaser_list)
            check_out_screen(enermy_group, chaser_list)


            coin_group.draw(screen)
            coin_group.update()
            pygame.display.update()
            clock.tick(fps)


def end_window(end_bird, end_level, score_record):
    Sound['game_over'].play()
    while True:
        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                pygame.display.quit()
                sys.exit()
            if event.type == pygame.KEYDOWN and event.key == pygame.K_RETURN:
                return
        bg_color = bg_list[end_level]
        screen.blit(Images['background-' + bg_color], (0, 0))
        screen.blit(Images['gameover'], ((width-Images['gameover'].get_width())/2, (height-Images['gameover'].get_height())/3.2))
        screen.blit(Images['enter'], ((width-Images['enter'].get_width())/2, 280))
        screen.blit(Images['base'], (0, (height-Images['base'].get_height())))
        screen.blit(font_en.render('Score: ', True, (0, 0, 0)), (70, 210))
        screen.blit(font_en.render(str(score_record), True, (255, 0, 0)), (160, 210))


        end_bird.die()
        screen.blit(end_bird.image, end_bird.rect)

        pygame.display.update()
        clock.tick(fps)



main()




