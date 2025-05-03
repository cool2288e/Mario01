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
background = transform.scale(image.load(img_back),(win_width, win_height))

finish = False
run = True



score = 0  # збито кораблів



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

    # метод для керування спрайтом стрілками клавіатури
    def update(self):
        pass

    def jump(self):
        if self.rect.y < win_height - 250:
            self.rect.y += 1


# клас спрайта-ворога
class Enemy(GameSprite):
    # рух ворога
    def update(self):
        pass



# створюємо спрайти
mario = Player(img_hero, 5, win_height - 167, 80, 100, 10)


while run:
    # подія натискання на кнопку Закрити
    for e in event.get():
        if e.type == QUIT:
            run = False
        # подія натискання на пробіл - спрайт стріляє
        elif e.type == KEYDOWN:
            if e.key == K_SPACE:
                mario.jump()




    if not finish:
        window.blit(background,(0,0))
        mario.reset()

        display.update()
    # цикл спрацьовує кожні 0.05 секунд
    time.delay(50)