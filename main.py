import pygame
import random
import time

WINDOW_WIDTH = 1680
WINDOW_HEIGHT = 1050
P1_WIDTH = 840
P2_width = 1680

FPS = 60

rocks = pygame.sprite.Group()

class Fighter(pygame.sprite.Sprite):
    def __init__(self, border_left, border_right):
        super(Fighter, self).__init__()
        self.image = pygame.image.load('src/fighter.png')
        self.border_left = border_left
        self.border_right = border_right
        self.rect = self.image.get_rect()
        self.rect.x = int((self.border_right + self.border_left) / 2)
        self.rect.y = WINDOW_HEIGHT - self.rect.height
        self.dx = 0
        self.dy = 0
    
    def update(self):
        self.rect.x += self.dx
        self.rect.y += self.dy

        if self.rect.x < self.border_left or self.rect.x + self.rect.width > self.border_right:
            self.rect.x -= self.dx
        
        if self.rect.y < 0 or self.rect.y + self.rect.height > WINDOW_HEIGHT:
            self.rect.y -= self.dy
    
    def draw(self, screen):
        screen.blit(self.image, self.rect)

    def collide(self, sprites):
        for sprite in sprites:
            if pygame.sprite.collide_rect(self, sprite) :
                return sprite
    
class Missile(pygame.sprite.Sprite):
    def __init__(self, xpos, ypos, speed):
        super(Missile, self).__init__()
        self.image = pygame.image.load('src/missile.png')
        self.rect = self.image.get_rect()
        self.rect.x = xpos
        self.rect.y = ypos
        self.speed = speed
        self.sound = pygame.mixer.Sound('src/missile.wav')

    def launch(self):
        self.sound.play()

    def update(self):
        self.rect.y -= self.speed

        if self.rect.y + self.rect.height < 0:
            self.kill()

    def collide(self, sprites):
        for sprite in sprites:
            if pygame.sprite.collide_rect(self, sprite):
                return sprite
            
class Rock(pygame.sprite.Sprite):
    def __init__(self, xpos, ypos, speed):
        super(Rock, self).__init__()
        rock_images = [f'src/rock{i:02d}.png' for i in range(1, 31)]

        self.image = pygame.image.load(random.choice(rock_images))
        self.rect = self.image.get_rect()
        self.rect = self.image.get_rect()
        self.rect.x = xpos
        self.rect.y = ypos
        self.speed = speed

    def update(self):
        self.rect.y += self.speed

    def out_of_screen(self):
        if self.rect.y > WINDOW_HEIGHT:
            return True

class DefaultRock(Rock):
    def __init__(self, xpos, ypos, speed):
        super().__init__(xpos, ypos, speed)

class SplitRock(Rock):
    def __init__(self, xpos, ypos, speed):
        super().__init__(xpos, ypos, speed)

    def split(self):
        speed = self.speed + 10
        rock1 = DefaultRock(self.rect.x - 50, self.rect.y + 5, speed)
        rock2 = DefaultRock(self.rect.x + 50, self.rect.y + 5, speed)
        rocks.add(rock1)
        rocks.add(rock2)

def draw_text(text, font, surface, x, y, main_color):
    text_obj = font.render(text, True, main_color)
    text_rect = text_obj.get_rect()
    text_rect.centerx = x
    text_rect.centery = y
    surface.blit(text_obj, text_rect)


def occur_explosion(surface, x, y):
    explosion_image = pygame.image.load('src/explosion.png')
    explosion_rect = explosion_image.get_rect()
    explosion_rect.x = x
    explosion_rect.y = y
    surface.blit(explosion_image, explosion_rect)
    
    # explosion_sounds = [f'src/explosion{i:02d}.wav' for i in range(1, 4)]
    # explosion_sound = pygame.mixer.Sound(random.choice(explosion_sounds))
    # explosion_sound.play()

def game_loop():
    default_font = pygame.font.Font('src/NanumGothic.ttf', 28)
    background_image = pygame.image.load('src/background.png')
    gameover_sound = pygame.mixer.Sound('src/gameover.wav')
    # pygame.mixer.music.load('src/music.wav')
    # pygame.mixer.music.play(-1)
    fps_clock = pygame.time.Clock()

    p1_fighter = Fighter(0, 840)
    p2_fighter = Fighter(840, 1680)
    missiles = pygame.sprite.Group()
    # rocks = pygame.sprite.Group()

    # occur_prob = 40
    shot_count = 0
    count_missed = 0

    running = True

    while running:
        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                running = False
            
            if event.type == pygame.KEYDOWN:
                if event.key == pygame.K_a:
                    p1_fighter.dx -= 10
                elif event.key == pygame.K_d:
                    p1_fighter.dx += 10
                elif event.key == pygame.K_w:
                    p1_fighter.dy -= 10
                elif event.key == pygame.K_s:
                    p1_fighter.dy += 10
                elif event.key == pygame.K_LEFT:
                    p2_fighter.dx -= 10
                elif event.key == pygame.K_RIGHT:
                    p2_fighter.dx += 10
                elif event.key == pygame.K_UP:
                    p2_fighter.dy -= 10
                elif event.key == pygame.K_DOWN:
                    p2_fighter.dy += 10
                elif event.key == pygame.K_SPACE:
                    missile = Missile(p1_fighter.rect.centerx, p1_fighter.rect.y, 10)
                    missile.launch()
                    missiles.add(missile)
                elif event.key == pygame.K_RCTRL:
                    missile = Missile(p2_fighter.rect.centerx, p2_fighter.rect.y, 10)
                    missile.launch()
                    missiles.add(missile)

            if event.type == pygame.KEYUP:
                if event.key == pygame.K_a or event.key == pygame.K_d:
                    p1_fighter.dx = 0
                elif event.key == pygame.K_w or event.key == pygame.K_s:
                    p1_fighter.dy = 0
                elif event.key == pygame.K_LEFT or event.key == pygame.K_RIGHT:
                    p2_fighter.dx = 0
                elif event.key == pygame.K_UP or event.key == pygame.K_DOWN:
                    p2_fighter.dy = 0

        screen.blit(background_image, background_image.get_rect())

        occur_of_default_rocks = 3 + int(shot_count / 10)
        occur_of_split_rocks = occur_of_default_rocks - 1
        min_rock_speed = 1 + int(shot_count / 200)
        max_rock_speed = 1 + int(shot_count / 100)

        probablity_num = random.randint(1, 100)

        if probablity_num > 99:
            for i in range(occur_of_default_rocks):
                speed = random.randint(min_rock_speed, max_rock_speed)
                rock = DefaultRock(random.randint(0, WINDOW_WIDTH - 30), 0, speed)
                rocks.add(rock)
        elif probablity_num > 98:
            for i in range(occur_of_split_rocks):
                speed = random.randint(min_rock_speed, max_rock_speed)
                rock = SplitRock(random.randint(0, WINDOW_WIDTH - 30), 0, speed)
                rocks.add(rock)
        
        draw_text(f'파괴한 운석: {shot_count}', default_font, screen, 100, 20, (255, 255, 255))
        draw_text(f'놓친 운석: {count_missed}', default_font, screen, 400, 20, (255, 0, 0))

        for missile in missiles:
            rock = missile.collide(rocks)
            if rock:
                if type(rock).__name__ == 'SplitRock':
                    rock.split()
                missile.kill()
                rock.kill()
                occur_explosion(screen, rock.rect.x, rock.rect.y)
                shot_count += 1

        for rock in rocks:
            if rock.out_of_screen():
                rock.kill()
                count_missed += 1

        rocks.update()
        rocks.draw(screen)
        missiles.update()
        missiles.draw(screen)
        p1_fighter.update()
        p2_fighter.update()
        p1_fighter.draw(screen)
        p2_fighter.draw(screen)
        pygame.display.flip()

        if p1_fighter.collide(rocks) or count_missed >= 3:
            pygame.mixer_music.stop()
            occur_explosion(screen, p1_fighter.rect.x, p1_fighter.rect.y)
            pygame.display.update()
            # gameover_sound.play()
            time.sleep(1)
            running = False

        if p2_fighter.collide(rocks) or count_missed >= 3:
            pygame.mixer_music.stop()
            occur_explosion(screen, p2_fighter.rect.x, p2_fighter.rect.y)
            pygame.display.update()
            # gameover_sound.play()
            time.sleep(1)
            running = False

        fps_clock.tick(FPS)

    return 'game_menu'

def game_menu():
    start_image = pygame.image.load('src/background.png')
    screen.blit(start_image, [0, 0])
    draw_x = int(WINDOW_WIDTH / 2)
    draw_y = int(WINDOW_HEIGHT / 4)
    font_70 = pygame.font.Font('src/NanumGothic.ttf', 70)
    font_40 = pygame.font.Font('src/NanumGothic.ttf', 40)

    draw_text('지구를 지켜라!', font_70, screen, draw_x, draw_y, (0, 255, 255))
    draw_text('엔터 키를 누르면', font_40, screen, draw_x, draw_y + 200, (255, 255, 255))
    draw_text('게임이 시작됩니다', font_40, screen, draw_x, draw_y + 250, (255, 255, 255))

    pygame.display.update()

    for event in pygame.event.get():
        if event.type == pygame.KEYDOWN:
            print(event.key)
            if event.key == pygame.K_RETURN:
                return 'play'
            
        if event.type == pygame.QUIT:
            return 'quit'
        
    return 'game_menu'

def main():
    global screen

    pygame.init()
    
    screen = pygame.display.set_mode((WINDOW_WIDTH, WINDOW_HEIGHT))
    pygame.display.set_caption('PyShooting')

    action = 'game_menu'

    while action != 'quit':
        if action == 'game_menu':
            action = game_menu()
        elif action == 'play':
            action = game_loop()

    pygame.quit()

if __name__ == "__main__":
    main()