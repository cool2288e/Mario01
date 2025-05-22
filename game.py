from pygame import *
from random import randint
from time import time as timer # ⬅️

# нам потрібні такі картинки:
img_back = "location1.jpg"  # фон гри
img_hero = "images/right_1.png"  # герой

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
    def __init__(self, player_image, player_x, player_y, size_x, size_y, player_speed, right_images_paths, left_images_paths):
        super().__init__(player_image, player_x, player_y, size_x, size_y, player_speed)
        self.is_jumping = False
        self.jump_height = 12
        self.jump_count = self.jump_height
        self.is_moving_right = False
        self.is_moving_left = False
        self.frame_index = 0
        self.animation_delay = 3
        self.delay_count = 0
        self.direction = "right"
        self.default_image = self.image.copy()
        self.images_right = [transform.scale(image.load(path), (size_x, size_y)) for path in right_images_paths]
        self.images_left = [transform.scale(image.load(path), (size_x, size_y)) for path in left_images_paths]
        self.ground_y = player_y  # запам'ятовуємо базову підлогу




    def animate(self):
        self.delay_count += 1
        if self.delay_count >= self.animation_delay:
            self.delay_count = 0
            self.frame_index = (self.frame_index + 1) % len(self.images_right)

            if self.direction == "right":
                self.image = self.images_right[self.frame_index]
            elif self.direction == "left":
                self.image = self.images_left[self.frame_index]


    def update(self, bgs):
        moved = False
        if self.is_moving_right:
            self.direction = "right"
            if not self.is_jumping:
                self.animate()
            for bg in bgs:
                bg.update(-1)
            moved = True
        if self.is_moving_left:
            self.direction = "left"
            if not self.is_jumping:
                self.animate()
            for bg in bgs:
                bg.update(1)
            moved = True

        if not moved:
            # якщо гравець стоїть — повертаємо стандартну картинку
            self.image = self.default_image
            self.frame_index = 0
            self.delay_count = 0


    def jump(self):
        if self.is_jumping:
            if self.jump_count == self.jump_height:
                jump_sound.play()
                self.image = transform.scale(  # один рядок
                    image.load("images/right_4.png"), (self.rect.width, self.rect.height))
            if self.jump_count >= -self.jump_height:
                direction = 1
                if self.jump_count < 0:
                    direction = -1
                self.rect.y -= (self.jump_count ** 2) * 0.3 * direction
                if self.rect.y > self.ground_y:
                    self.rect.y = self.ground_y

                self.jump_count -= 1
            else:
                self.is_jumping = False
                self.jump_count = self.jump_height
                self.rect.y = self.ground_y  # повертаємо строго на підлогу
                self.image = transform.scale(  # один рядок
                    image.load("images/right_1.png"), (self.rect.width, self.rect.height))

    def short_jump(self):
        # робимо короткий стрибок, без збивання ground_y
        self.is_jumping = True
        self.jump_count = self.jump_height // 2


class Platform(sprite.Sprite):
    def __init__(self, x, y, num_blocks):
        super().__init__()
        self.blocks = []
        self.special_block_index = randint(0, num_blocks - 1)
        self.width = num_blocks * 50

        for i in range(num_blocks):
            if i == self.special_block_index:
                img = transform.scale(image.load("blok1.png"), (50, 50))
                is_special = True
            else:
                img = transform.scale(image.load("blok2.png"), (50, 50))
                is_special = False

            block = {
                "image": img,
                "rect": img.get_rect(topleft=(x + i * 50, y)),
                "is_special": is_special,
                "used": False
            }
            self.blocks.append(block)

    def draw(self, surface):
        for block in self.blocks:
            surface.blit(block["image"], block["rect"])

    def update(self, direction):
        for block in self.blocks:
            block["rect"].x += direction * 10  # рух разом з фоном


class Coin(sprite.Sprite):
    def __init__(self, x, y):
        super().__init__()
        self.image = transform.scale(image.load("coin.png"), (30, 30))
        self.rect = self.image.get_rect(center=(x, y))
        self.vel_y = -5  # вилітає вгору
        self.lifetime = 30  # кадри життя

    def update(self):
        self.rect.y += self.vel_y
        self.lifetime -= 1
        if self.lifetime <= 0:
            self.kill()



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
mario = Player(
    img_hero,
    5,
    win_height - 168,
    70,
    100,
    10,
    [f"images/right_{i}.png" for i in range(1, 5)],
    [f"images/left_{i}.png" for i in range(1, 5)]
)

background1 = Background(img_back, 0,0,win_width,win_height,mario.speed)
background2 = Background(img_back, win_width,0,win_width,win_height,mario.speed)
enemy1 = Enemy(img_enemy, 300, win_height - 118, 60, 50, 5)

platforms = []
current_platform = Platform(win_width + 100, 300, randint(2, 4))
platforms.append(current_platform)
coins = sprite.Group()

while run:
    # подія натискання на кнопку Закрити
    for e in event.get():
        if e.type == QUIT:
            run = False
        # подія натискання на пробіл - спрайт стріляє
        elif e.type == KEYDOWN:
            if e.key == K_SPACE:
                if not mario.is_jumping and abs(mario.rect.y - mario.ground_y) < 5:
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


        # Рух платформ
        for platform in platforms:
            if mario.is_moving_right:
                platform.update(-1)  # рухаємо платформу вліво

            platform.draw(window)

        # Перевірка — якщо Mario пройшов попередню платформу
        last_platform = platforms[-1]
        right_edge = max(block["rect"].right for block in last_platform.blocks)
        if mario.rect.x > right_edge - 200 and len(platforms) < 3:  # обмеження кількості
            new_platform = Platform(win_width + randint(100, 200), randint(100, 250), randint(2, 4))
            platforms.append(new_platform)

        for platform in platforms:
            for block in platform.blocks:
                if mario.rect.colliderect(block["rect"]):
                    # Стрибок вгору, удар знизу
                    if mario.jump_count > 0 and mario.rect.bottom > block["rect"].top:
                        mario.jump_count = -1  # розворот стрибка
                        mario.rect.bottom = block["rect"].top + 1

                        if block["is_special"] and not block["used"]:
                            coin = Coin(block["rect"].centerx, block["rect"].top)
                            coins.add(coin)
                            block["used"] = True

                    # Приземлення на платформу
                    elif mario.jump_count < 0 and abs(mario.rect.bottom - block["rect"].top) < 10 and mario.rect.centerx in range(block["rect"].left, block["rect"].right):

                        mario.ground_y = block["rect"].top - mario.rect.height
                        mario.rect.y = mario.ground_y

        platforms = [p for p in platforms if any(block["rect"].right > 0 for block in p.blocks)]

        mario_on_platform = False
        for platform in platforms:
            for block in platform.blocks:
                if mario.rect.colliderect(block["rect"]):
                    # координати для зручності
                    player_bottom = mario.rect.bottom
                    player_top = mario.rect.top
                    block_top = block["rect"].top
                    block_bottom = block["rect"].bottom

                    # УДАР ЗНИЗУ
                    if mario.jump_count > 0 and player_bottom <= block_top + 10:
                        mario.jump_count = -1
                        mario.rect.bottom = block_top + 1

                        if block["is_special"] and not block["used"]:
                            coin = Coin(block["rect"].centerx, block["rect"].top)
                            coins.add(coin)
                            block["used"] = True

                    # ПРИЗЕМЛЕННЯ
                    elif mario.jump_count < 0 and player_top < block_bottom and abs(player_bottom - block_top) < 10:
                        mario.ground_y = block_top - mario.rect.height
                        mario.rect.y = mario.ground_y
                        mario_on_platform = True

        if not mario_on_platform:
            mario.ground_y = win_height - 168

        display.update()

    # цикл спрацьовує кожні 0.05 секунд
    time.delay(50)