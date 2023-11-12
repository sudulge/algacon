# TODO: 점수 추가, 각 플레이어 영역에서 운석 등장하게 변경, 점수기준으로 운석 많이 나오게 할건지 시간 기준으로 할건지 변경,
#       아이템 추가, ;
#       게임 오버화면 - p1, p2 각각 승리화면

import pygame
import random
import time

# 게임 화면 세팅
WINDOW_WIDTH = 1680
WINDOW_HEIGHT = 1050
P1_WIDTH = 840
P2_WIDTH = 1680

# 프레임 설정
FPS = 60

# 화면상에 존재하는 운석 그룹
rocks = pygame.sprite.Group()

# 전투기 클래스 정의
class Fighter(pygame.sprite.Sprite):
    def __init__(self, border_left, border_right, name):
        super(Fighter, self).__init__()
        self.name = name
        self.image = pygame.image.load(f'src/{name}.png')
        self.border_left = border_left
        self.border_right = border_right
        self.rect = self.image.get_rect()
        self.rect.x = int((self.border_right + self.border_left) / 2)
        self.rect.y = WINDOW_HEIGHT - self.rect.height
        self.dx = 0
        self.dy = 0
        self.life = 5
        self.invincible = False
        self.invincible_time = None
    
    # 움직임
    def update(self):
        self.rect.x += self.dx
        self.rect.y += self.dy

        if self.rect.x < self.border_left or self.rect.x + self.rect.width > self.border_right:
            self.rect.x -= self.dx
        
        if self.rect.y < 0 or self.rect.y + self.rect.height > WINDOW_HEIGHT:
            self.rect.y -= self.dy
    
    def draw(self, screen):
        screen.blit(self.image, self.rect)

    # 충돌 판정
    def collide(self, sprites):
        for sprite in sprites:
            if pygame.sprite.collide_rect(self, sprite) :
                return sprite
    
# 미사일 클래스 정의
class Missile(pygame.sprite.Sprite):
    def __init__(self, xpos, ypos, speed):
        super(Missile, self).__init__()
        self.image = pygame.image.load('src/missile1.png')
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

# 운석 클래스 정의            
class Rock(pygame.sprite.Sprite):
    def __init__(self, xpos, ypos, speed):
        super(Rock, self).__init__()
        rock_images = [f'src/rock{i:02d}.png' for i in range(1, 5)]

        self.image = pygame.image.load(random.choice(rock_images))
        self.rect = self.image.get_rect()
        self.rect = self.image.get_rect()
        self.rect.x = xpos
        self.rect.y = ypos
        self.speed = speed
        self.life = 2

    def update(self):
        self.rect.y += self.speed

    def out_of_screen(self):
        if self.rect.y > WINDOW_HEIGHT:
            return True

# 기본 운석
class DefaultRock(Rock):
    def __init__(self, xpos, ypos, speed):
        super().__init__(xpos, ypos, speed)

# 분할 운석
class SplitRock(Rock):
    def __init__(self, xpos, ypos, speed):
        super().__init__(xpos, ypos, speed)
        self.image = pygame.image.load('src/splitrock.png')

    def split(self):
        speed = self.speed + 10
        rock1 = DefaultRock(self.rect.x - 50, self.rect.y + 5, speed)
        rock1.image = pygame.image.load('src/splitedrock_l.png')
        rock2 = DefaultRock(self.rect.x + 50, self.rect.y + 5, speed)
        rock2.image = pygame.image.load('src/splitedrock_r.png')
        rocks.add(rock1)
        rocks.add(rock2)

# 부서지지 않는 운석
class UnbreakableRock(Rock):
    def __init__(self, xpos, ypos, speed):
        super().__init__(xpos, ypos, speed)
        self.image = pygame.image.load('src/unbreakablerock.png')

# 텍스트 보여주는 함수
def draw_text(text, font, surface, x, y, main_color):
    text_obj = font.render(text, True, main_color)
    text_rect = text_obj.get_rect()
    text_rect.centerx = x
    text_rect.centery = y
    surface.blit(text_obj, text_rect)

# 폭발 함수
def occur_explosion(surface, x, y):
    explosion_image = pygame.image.load('src/explosion.png')
    explosion_rect = explosion_image.get_rect()
    explosion_rect.x = x
    explosion_rect.y = y
    surface.blit(explosion_image, explosion_rect)
    
    # explosion_sounds = [f'src/explosion{i:02d}.wav' for i in range(1, 4)]
    # explosion_sound = pygame.mixer.Sound(random.choice(explosion_sounds))
    # explosion_sound.play()

# 게임 진행 루프
def game_loop():
    default_font = pygame.font.Font('src/NanumGothic.ttf', 28)
    background_image = pygame.image.load('src/background_ingame.png')
    gameover_sound = pygame.mixer.Sound('src/gameover.wav')
    # pygame.mixer.music.load('src/music.wav')
    # pygame.mixer.music.play(-1)
    fps_clock = pygame.time.Clock()

    missiles = pygame.sprite.Group()
    fighters = pygame.sprite.Group()
    p1_fighter = Fighter(0, 840, 'fighter1')
    p2_fighter = Fighter(840, 1680, 'fighter2')
    fighters.add(p1_fighter, p2_fighter)
    # rocks = pygame.sprite.Group()

    # occur_prob = 40
    shot_count = 0
    count_missed = 0

    # 타이머 설정
    start_ticks = pygame.time.get_ticks()

    running = True

    while running:
        # 게임 시작 후 경과 시간 
        elapsed_time = int((pygame.time.get_ticks() - start_ticks) / 1000)

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
                elif event.key == pygame.K_SPACE:
                    missile = Missile(p1_fighter.rect.centerx, p1_fighter.rect.y, 10)
                    missile.launch()
                    missiles.add(missile)

                elif event.key == pygame.K_LEFT:
                    p2_fighter.dx -= 10
                elif event.key == pygame.K_RIGHT:
                    p2_fighter.dx += 10
                elif event.key == pygame.K_UP:
                    p2_fighter.dy -= 10
                elif event.key == pygame.K_DOWN:
                    p2_fighter.dy += 10
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

        # 운석 등장 횟수(확률) 조정 
        occur_of_default_rocks = 3 + int(shot_count / 10)
        occur_of_split_rocks = occur_of_default_rocks - 1
        occur_of_unbreakable_rocks = occur_of_default_rocks - 2
        min_rock_speed = 1 + int(shot_count / 200)
        max_rock_speed = 1 + int(shot_count / 100)

        probablity_num = random.randint(1, 200)

        if probablity_num > 198:
            for i in range(occur_of_default_rocks):
                speed = random.randint(min_rock_speed, max_rock_speed)
                rock = DefaultRock(random.randint(0, WINDOW_WIDTH - 30), 0, speed)
                rocks.add(rock)
        elif probablity_num > 197:
            for i in range(occur_of_split_rocks):
                speed = random.randint(min_rock_speed, max_rock_speed)
                rock = SplitRock(random.randint(0, WINDOW_WIDTH - 30), 0, speed)
                rocks.add(rock)
        elif probablity_num > 196:
            for i in range(occur_of_unbreakable_rocks):
                speed = random.randint(min_rock_speed, max_rock_speed)
                rock = UnbreakableRock(random.randint(0, WINDOW_WIDTH - 30), 0, speed)
                rocks.add(rock)
        
        draw_text(f'파괴한 운석: {shot_count}', default_font, screen, 100, 20, (255, 255, 255))
        draw_text(f'놓친 운석: {count_missed}', default_font, screen, 400, 20, (255, 0, 0))
        draw_text(f'{180 - elapsed_time}', pygame.font.Font('src/NanumGothic.ttf', 60), screen, 840, 30, (255, 255, 255))

        for missile in missiles:
            rock = missile.collide(rocks)
            if rock:
                if type(rock).__name__ == 'UnbreakableRock':
                    continue
                rock.life -= 1
                missile.kill()
                if rock.life <= 0:
                    if type(rock).__name__ == 'SplitRock':
                        rock.split()
                    rock.kill()
                    occur_explosion(screen, rock.rect.x, rock.rect.y)
                    shot_count += 1

        for rock in rocks:
            if rock.out_of_screen():
                rock.kill()
                count_missed += 1
        
        for fighter in fighters:

            if fighter.invincible:
                if (pygame.time.get_ticks() - fighter.invincible_time) / 1000 >= 2:
                    fighter.invincible = False
                    fighter.invincible_time = None
                    fighter.image = pygame.image.load(f'src/{fighter.name}.png')

            rock = fighter.collide(rocks)
            if rock:
                rock.kill()
                occur_explosion(screen, fighter.rect.x, fighter.rect.y)

                if not fighter.invincible:
                    fighter.life -= 1
                    fighter.invincible = True
                    fighter.invincible_time = pygame.time.get_ticks()
                    fighter.image = pygame.image.load('src/invincible.png')
                
        for i in range(1, 6):
            if p1_fighter.life >= i:
                heart = pygame.image.load('src/heart.png')
                screen.blit(heart, ((i-1)*50 + 10, WINDOW_HEIGHT - 50))
            elif p1_fighter.life < i:
                brokenheart = pygame.image.load('src/brokenheart.png')
                screen.blit(brokenheart, ((i-1)*50 + 10, WINDOW_HEIGHT - 50))

            if p2_fighter.life >= i:
                heart = pygame.image.load('src/heart.png')
                screen.blit(heart, (WINDOW_WIDTH - (i)*50, WINDOW_HEIGHT - 50))
            elif p2_fighter.life < i:
                brokenheart = pygame.image.load('src/brokenheart.png')
                screen.blit(brokenheart, (WINDOW_WIDTH - (i)*50, WINDOW_HEIGHT - 50))

        # 충돌시 life가 0개면 하트 이미지가 업데이트 안돼서 나눠놓음
        for fighter in fighters:
            if fighter.life <= 0:
                pygame.mixer_music.stop()
                pygame.display.update()
                # gameover_sound.play()
                rocks.empty()
                fighters.empty()
                missiles.empty()
                time.sleep(1)
                running = False

        rocks.update()
        rocks.draw(screen)
        missiles.update()
        missiles.draw(screen)
        p1_fighter.update()
        p2_fighter.update()
        p1_fighter.draw(screen)
        p2_fighter.draw(screen)
        pygame.display.flip()

        # 게임 오버 조건

        if elapsed_time >= 180:
            running = False
            return 'time_end'
        
        fps_clock.tick(FPS)

    return 'game_menu'

# 게임 메뉴(시작) 화면
def game_menu():
    start_image = pygame.image.load('src/background_menu.png')
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
            if event.key == pygame.K_RETURN:
                return 'play'
            
        if event.type == pygame.QUIT:
            return 'quit'
        
    return 'game_menu'

# 시간초과 화면
def time_end():
    start_image = pygame.image.load('src/background_menu.png')
    screen.blit(start_image, [0, 0])
    draw_x = int(WINDOW_WIDTH / 2)
    draw_y = int(WINDOW_HEIGHT / 4)
    font_70 = pygame.font.Font('src/NanumGothic.ttf', 70)
    font_40 = pygame.font.Font('src/NanumGothic.ttf', 40)

    draw_text("게임 오버", font_70, screen, draw_x, draw_y, (0, 255, 255))

    pygame.display.update()

    for event in pygame.event.get():
        if event.type == pygame.KEYDOWN:
            if event.key == pygame.K_RETURN:
                return 'game_menu'
            
        if event.type == pygame.QUIT:
            return 'quit'

    return 'time_end'

# 메인 루프
def main():
    global screen

    pygame.init()
    
    screen = pygame.display.set_mode((WINDOW_WIDTH, WINDOW_HEIGHT))
    pygame.display.set_caption('PyShooting')

    # 현재 action 에 따라서 게임 화면 구성
    # 메인 메뉴 화면으로 시작
    action = 'game_menu'

    while action != 'quit':
        if action == 'game_menu':
            action = game_menu()
        elif action == 'play':
            action = game_loop()
        elif action == 'time_end':
            action = time_end()

    pygame.quit()

if __name__ == "__main__":
    main()