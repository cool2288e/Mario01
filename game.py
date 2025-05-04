from pygame import *
from random import randint
from time import time as timer # ⬅️

# нам потрібні такі картинки:
img_back = "location1.jpg"  # фон гри
img_hero = "Mario1.png"  # герой

img_enemy = "ufo.png"  # ворог
img_bullet = "bullet.png" # куля
img_ast = "asteroid.png" # астероїд ⬅️


# створюємо віконце
win_width = 700
win_height = 500
display.set_caption("")
window = display.set_mode((win_width, win_height))


finish = False
run = True



score = 0  # збито кораблів
mixer.init()
mixer.music.load("muzyka-super-mario.mp3")
mixer.music.play(-1)
jump_sound = mixer.Sound("pryjok-mario.mp3")


class GameSprite(sprite.Sprite):
    def __init__(self, player_image, player_x, player_y,  # один рядок
                 size_x, size_y, player_speed):
        sprite.Sprite.__init__(self)
        self.image = transform.scale(  # один рядок
            image.load(player_image), (size_x, size_y))
        self.speed = player_speed
        self.rect = self.image.get_rect()
        self.rect.x = player_x
        self.rect.y = player_y

    def reset(self):
        window.blit(self.image, (self.rect.x, self.rect.y))


# клас головного гравця
class Player(GameSprite):
    def __init__(self, player_image, player_x, player_y, size_x, size_y, player_speed):
        super().__init__(player_image, player_x, player_y, size_x, size_y, player_speed)
        self.is_jumping = False
        self.jump_height = 12
        self.jump_count = self.jump_height

    def update(self, bgs):
        if pressed_keys[K_RIGHT]:
            for bg in bgs:
                bg.update()


    def jump(self):
        if self.is_jumping:
            if self.jump_count == self.jump_height:
                jump_sound.play()
            if self.jump_count >= -self.jump_height:
                direction = 1
                if self.jump_count < 0:
                    direction = -1
                self.rect.y -= (self.jump_count ** 2) * 0.3 * direction
                self.jump_count -= 1
            else:
                self.is_jumping = False
                self.jump_count = self.jump_height



class Background(GameSprite):
    def update(self):
        self.rect.x -= self.speed
        if self.rect.x < win_width:
            self.rect.x = win_width





# клас спрайта-ворога
class Enemy(GameSprite):
    # рух ворога
    def update(self):
        pass



# створюємо спрайти
mario = Player(img_hero, 5, win_height - 167, 80, 100, 10)
background1 = Background(img_back, 0,0,win_width,win_height,mario.speed)
background2 = Background(img_back, win_width,0,win_width,win_height,mario.speed)

while run:
    # подія натискання на кнопку Закрити
    for e in event.get():
        if e.type == QUIT:
            run = False
        # подія натискання на пробіл - спрайт стріляє
        elif e.type == KEYDOWN:
            if e.key == K_SPACE:
                mario.is_jumping =  True

    if not finish:
        pressed_keys = key.get_pressed()
        background1.reset()
        background2.reset()
        mario.update([background1, background2])
        mario.reset()
        mario.jump()
        display.update()

    # цикл спрацьовує кожні 0.05 секунд
    time.delay(50)
