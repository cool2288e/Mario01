from pygame import *
from random import randint
from time import time as timer # ⬅️

# нам потрібні такі картинки:
img_back = "location1.jpg"  # фон гри
img_hero = "Mario1.png"  # герой

img_enemy = "mashroom1.png"  # ворог
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
        self.is_moving_right = False
        self.is_moving_left = False
        self.ground_y = player_y  # запам'ятовуємо базову підлогу

    def update(self, bgs):
        if self.is_moving_right:
            for bg in bgs:
                bg.update(-1)  # рухаємо вліво
        if self.is_moving_left:
            for bg in bgs:
                bg.update(1)  # рухаємо вправо

    def jump(self):
        if self.is_jumping:
            if self.jump_count == self.jump_height:
                jump_sound.play()
                self.image = transform.scale(  # один рядок
                    image.load("mariojump.png"), (self.rect.width+20, self.rect.height-20))
            if self.jump_count >= -self.jump_height:
                direction = 1
                if self.jump_count < 0:
                    direction = -1
                self.rect.y -= (self.jump_count ** 2) * 0.3 * direction
                self.jump_count -= 1
            else:
                self.is_jumping = False
                self.jump_count = self.jump_height
                self.rect.y = self.ground_y  # повертаємо строго на підлогу
                self.image = transform.scale(  # один рядок
                    image.load("Mario1.png"), (self.rect.width, self.rect.height))

    def short_jump(self):
        # робимо короткий стрибок, без збивання ground_y
        self.is_jumping = True
        self.jump_count = self.jump_height // 2



class Background(GameSprite):
    def update(self, direction):
        self.rect.x += self.speed * direction
        # Якщо фон пішов занадто вліво — переносимо вправо
        if self.rect.right <= 0:
            self.rect.x = win_width
        # Якщо фон пішов занадто вправо — переносимо вліво
        elif self.rect.left >= win_width:
            self.rect.x = -win_width

class Enemy(GameSprite):
    def __init__(self, player_image, player_x, player_y, size_x, size_y, player_speed):
        super().__init__(player_image, player_x, player_y, size_x, size_y, player_speed)
        self.start_x = player_x
        self.direction = 1  # 1 = вправо, -1 = вліво
        self.movement_range = 200

    def update(self, player):
        # Базовий рух ворога
        self.rect.x += self.speed * self.direction

        # Зміна напрямку при досягненні межі руху
        if self.rect.x > self.start_x + self.movement_range:
            self.direction = -1
        elif self.rect.x < self.start_x - self.movement_range:
            self.direction = 1

        # Адаптація до руху гравця (ефект паралакса)
        if player.is_moving_right:
            self.rect.x -= 10  # ворог відносно гравця рухається лівіше швидше
        elif player.is_moving_left:
            self.rect.x += 10  # ворог рухається вправо швидше

    def respawn_right(self):
        # Телепортація ворога за межі екрану праворуч
        self.rect.x = win_width + randint(100, 300)


# клас спрайта-ворога




# створюємо спрайти
mario = Player(img_hero, 5, win_height - 167, 70, 100, 10)
background1 = Background(img_back, 0,0,win_width,win_height,mario.speed)
background2 = Background(img_back, win_width,0,win_width,win_height,mario.speed)
enemy1 = Enemy(img_enemy, 300, win_height - 118, 60, 50, 5)


while run:
    # подія натискання на кнопку Закрити
    for e in event.get():
        if e.type == QUIT:
            run = False
        # подія натискання на пробіл - спрайт стріляє
        elif e.type == KEYDOWN:
            if e.key == K_SPACE:
                mario.is_jumping =  True
            if e.key == K_d:
                mario.is_moving_right = True
            if e.key == K_a:
                mario.is_moving_left = True
        elif e.type == KEYUP:

            if e.key == K_d:
                mario.is_moving_right = False
            if e.key == K_a:
                mario.is_moving_left = False



    if not finish:
        pressed_keys = key.get_pressed()
        background1.reset()
        background2.reset()
        mario.update([background1, background2])
        mario.reset()
        mario.jump()
        enemy1.update(mario)
        enemy1.reset()

        # --- Взаємодія Mario та ворога ---
        if mario.rect.colliderect(enemy1.rect):
            if mario.rect.bottom <= enemy1.rect.centery:
                enemy1.respawn_right()
                mario.short_jump()  # тепер викликаємо окремий метод короткого стрибка
            else:
                finish = True
                print("Game Over!")
        display.update()

    # цикл спрацьовує кожні 0.05 секунд
    time.delay(50)
