# TODO: 게임방법이미지 변경, 전투기선택, 게임 오버화면 - p1, p2 각각 승리화면, 점수시스템
# TODO: multiplay.: 서버 안열려 잇으면 안열려있다고 표시

import pygame
import random
import time
import socket
import threading

# 게임 화면 세팅
WINDOW_WIDTH = 1680
WINDOW_HEIGHT = 1050
P1_WIDTH = 840
P2_WIDTH = 1680

# 프레임 설정
FPS = 60

# 화면상에 존재하는 운석 그룹
rocks = pygame.sprite.Group()
rock_images = [f'rock{i:02d}' for i in range(1, 5)]

items = pygame.sprite.Group()

selected_menu = 1

connect_trying = False

playing = False 

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
        self.speed = 1
        self.speedup_time = None
        self.power = 1
        self.powerup_time = None
    
    # 움직임
    def update(self):
        self.rect.x += self.dx * self.speed
        self.rect.y += self.dy * self.speed

        if self.rect.x < self.border_left or self.rect.x + self.rect.width > self.border_right:
            self.rect.x -= self.dx * self.speed
        
        if self.rect.y < 0 or self.rect.y + self.rect.height > WINDOW_HEIGHT:
            self.rect.y -= self.dy * self.speed
    
    def draw(self, screen):
        screen.blit(self.image, self.rect)

    # 충돌 판정
    def collide(self, sprites):
        for sprite in sprites:
            if pygame.sprite.collide_rect(self, sprite) :
                return sprite
    
# 미사일 클래스 정의
class Missile(pygame.sprite.Sprite):
    def __init__(self, xpos, ypos, fighter):
        super(Missile, self).__init__()
        self.sound = pygame.mixer.Sound('src/missile.wav')
        self.sound.set_volume(0.2)
        self.fighter = fighter
        self.image = pygame.image.load(f'src/missile{self.fighter.power}.png')
        self.rect = self.image.get_rect()
        self.rect.centerx = xpos
        self.rect.centery = ypos
        self.speed = self.fighter.power * 10

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
    def __init__(self, xpos, ypos, speed, image):
        super(Rock, self).__init__()

        self.image = pygame.image.load(f'src/{image}.png')
        self.rect = self.image.get_rect()
        self.rect.centerx = xpos
        self.rect.centery = ypos
        self.speed = speed
        self.life = 2

    def update(self):
        self.rect.y += self.speed

    def out_of_screen(self):
        if self.rect.y > WINDOW_HEIGHT:
            return True

# 분할 운석
class SplitRock(Rock):
    def __init__(self, xpos, ypos, speed):
        super().__init__(xpos, ypos, speed, 'splitrock')

    def split(self):
        speed = self.speed + 10
        rock1 = Rock(self.rect.centerx - 50, self.rect.y + 5, speed, 'splitedrock_l')
        rock2 = Rock(self.rect.centerx + 50, self.rect.y + 5, speed, 'splitedrock_r')
        rocks.add(rock1)
        rocks.add(rock2)

# 부서지지 않는 운석
class UnbreakableRock(Rock):
    def __init__(self, xpos, ypos, speed):
        super().__init__(xpos, ypos, speed, 'unbreakablerock')

# 아이템 클래스 정의
class Item(pygame.sprite.Sprite):
    def __init__(self, xpos, ypos, speed, image):
        super(Item, self).__init__()

        self.image = pygame.image.load(f'src/{image}.png')
        self.sound = pygame.mixer.Sound('src/item.mp3')
        self.sound.set_volume(0.7)
        self.rect = self.image.get_rect()
        self.rect.centerx = xpos
        self.rect.centery = ypos
        self.speed = speed
    
    def update(self):
        self.rect.y += self.speed
    
    def out_of_screen(self):
        if self.rect.y > WINDOW_HEIGHT:
            return True
        
class Heal(Item):
    def __init__(self, xpos, ypos, speed):
        super().__init__(xpos, ypos, speed, 'heart')

class SpeedUp(Item):
    def __init__(self, xpos, ypos, speed):
        super().__init__(xpos, ypos, speed, 'speedup')

class PowerUp(Item):
    def __init__(self, xpos, ypos, speed):
        super().__init__(xpos, ypos, speed, 'powerup')
        
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
    explosion_rect.centerx = x
    explosion_rect.centery = y
    surface.blit(explosion_image, explosion_rect)
    
    # explosion_sounds = [f'src/explosion{i:02d}.wav' for i in range(1, 4)]
    # explosion_sound = pygame.mixer.Sound(random.choice(explosion_sounds))
    # explosion_sound.play()

# 게임 진행 루프
def game_loop():
    global selected_menu, p1_fighter, p2_fighter, missiles
    default_font = pygame.font.Font('src/NanumGothic.ttf', 28)
    background_image = pygame.image.load('src/background_ingame.png')
    gameover_sound = pygame.mixer.Sound('src/gameover.wav')
    pygame.mixer.music.load('src/background_music.mp3')
    pygame.mixer.music.set_volume(0.3)
    pygame.mixer.music.play(-1)
    fps_clock = pygame.time.Clock()

    missiles = pygame.sprite.Group()
    fighters = pygame.sprite.Group()
    p1_fighter = Fighter(0, 840, 'fighter1')
    p2_fighter = Fighter(840, 1680, 'fighter2')
    fighters.add(p1_fighter, p2_fighter)


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
                    missile = Missile(p1_fighter.rect.centerx, p1_fighter.rect.y, p1_fighter)
                    missile.launch()
                    missiles.add(missile)

                elif event.key == pygame.K_LEFT:
                    p2_fighter.dx -= 10
                    client.sendall('left'.encode())
                elif event.key == pygame.K_RIGHT:
                    p2_fighter.dx += 10
                    client.sendall('right'.encode())
                elif event.key == pygame.K_UP:
                    p2_fighter.dy -= 10
                    client.sendall('up'.encode())
                elif event.key == pygame.K_DOWN:
                    p2_fighter.dy += 10
                    client.sendall('down'.encode())
                elif event.key == pygame.K_RCTRL:
                    client.sendall('launch'.encode())
                    missile = Missile(p2_fighter.rect.centerx, p2_fighter.rect.y, p2_fighter)
                    missile.launch()
                    missiles.add(missile)

            if event.type == pygame.KEYUP:
                if event.key == pygame.K_a:
                    p1_fighter.dx += 10
                elif event.key == pygame.K_d:
                    p1_fighter.dx -= 10
                elif event.key == pygame.K_w:
                    p1_fighter.dy += 10
                elif event.key == pygame.K_s:
                    p1_fighter.dy -= 10

                elif event.key == pygame.K_LEFT:
                    p2_fighter.dx += 10
                    client.sendall('_left'.encode())
                elif event.key == pygame.K_RIGHT:
                    p2_fighter.dx -= 10
                    client.sendall('_right'.encode())
                elif event.key == pygame.K_UP:
                    p2_fighter.dy += 10
                    client.sendall('_up'.encode())
                elif event.key == pygame.K_DOWN:
                    p2_fighter.dy -= 10
                    client.sendall('_down'.encode())

        screen.blit(background_image, background_image.get_rect())

        # 한번에 등장하는 운석 개수
        occur_of_default_rocks = 3 + int(elapsed_time // 20)
        occur_of_split_rocks = occur_of_default_rocks - 1
        occur_of_unbreakable_rocks = occur_of_default_rocks - 2
        min_rock_speed = 3 + int(elapsed_time // 20)
        max_rock_speed = 3 + int(elapsed_time // 10)

        probablity_num = random.randint(1, 1000)
        # 운석, 아이템 등장 확률 조정

        if probablity_num > 990:  # 10 / 1000  1%
            for i in range(2):
                for j in range(occur_of_default_rocks):
                    speed = random.randint(min_rock_speed, max_rock_speed)
                    rock = Rock(random.randint(i*840, (i+1)*840), 0, speed, random.choice(rock_images))
                    rocks.add(rock)
        elif probablity_num > 985:  # 5 / 1000  0.5%
            for i in range(2):
                for j in range(occur_of_split_rocks):
                    speed = random.randint(min_rock_speed, max_rock_speed)
                    rock = SplitRock(random.randint(i*840, (i+1)*840), 0, speed)
                    rocks.add(rock)
        elif probablity_num > 980:  # 5 / 1000  0.5%
            for i in range(2):
                for j in range(occur_of_unbreakable_rocks):
                    speed = random.randint(min_rock_speed, max_rock_speed)
                    rock = UnbreakableRock(random.randint(i*840, (i+1)*840), 0, speed)
                    rocks.add(rock)
        elif probablity_num > 978:  # 2 / 1000  0.2%
            for i in range(2):
                heal = Heal(random.randint(i*840, (i+1)*840), 0, 20)
                heal.add(items)
        elif probablity_num > 973:  # 5 / 1000  0.5% 
            for i in range(2):
                speedup = SpeedUp(random.randint(i*840, (i+1)*840), 0, 20)
                speedup.add(items)
        elif probablity_num > 970:
            for i in range(2):
                powerup = PowerUp(random.randint(i*840, (i+1)*840), 0, 20)
                powerup.add(items)
        
        draw_text(f'{180 - elapsed_time}', pygame.font.Font('src/NanumGothic.ttf', 60), screen, 840, 30, (255, 255, 255))

        for missile in missiles:
            rock = missile.collide(rocks)
            if rock:
                if type(rock).__name__ == 'UnbreakableRock':
                    continue
                rock.life -= missile.fighter.power
                missile.kill()
                if rock.life <= 0:
                    if type(rock).__name__ == 'SplitRock':
                        rock.split()
                    rock.kill()
                    occur_explosion(screen, rock.rect.centerx, rock.rect.centery)

        for rock in rocks:
            if rock.out_of_screen():
                rock.kill()
        
        for item in items:
            if item.out_of_screen():
                item.kill()
        
        for fighter in fighters:
            if fighter.invincible:
                if (pygame.time.get_ticks() - fighter.invincible_time) / 1000 >= 2:
                    fighter.invincible = False
                    fighter.invincible_time = None
                    fighter.image = pygame.image.load(f'src/{fighter.name}.png')
            
            if fighter.speed > 1:
                if (pygame.time.get_ticks() - fighter.speedup_time) / 1000 >= 10:
                    fighter.speed = 1
                    fighter.speedup_time = None
                    fighter.image = pygame.image.load(f'src/{fighter.name}.png')
            
            if fighter.power > 1:
                if (pygame.time.get_ticks() - fighter.powerup_time) / 1000 >= 10:
                    fighter.power = 1
                    fighter.powerup_time = None

            rock = fighter.collide(rocks)
            if rock:
                rock.kill()
                occur_explosion(screen, fighter.rect.centerx, fighter.rect.centery)

                if not fighter.invincible:
                    fighter.life -= 1
                    fighter.invincible = True
                    fighter.invincible_time = pygame.time.get_ticks()
                    fighter.image = pygame.image.load(f'src/{fighter.name}_invincible.png')

            item = fighter.collide(items)
            if item:
                item.sound.play()
                item.kill()
                if type(item).__name__ == 'Heal':
                    if fighter.life < 5:
                        fighter.life += 1
                elif type(item).__name__ == 'SpeedUp':
                    fighter.speed = 1.6
                    fighter.speedup_time = pygame.time.get_ticks()
                    fighter.image = pygame.image.load(f'src/{fighter.name}_speedup.png')
                elif type(item).__name__ == 'PowerUp':
                    fighter.power = 2
                    fighter.powerup_time = pygame.time.get_ticks()
            
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
                items.empty()
                time.sleep(1)
                running = False

        rocks.update()
        rocks.draw(screen)
        missiles.update()
        missiles.draw(screen)
        fighters.update()
        fighters.draw(screen)
        items.update()
        items.draw(screen)
        pygame.display.flip()

        # 게임 오버 조건

        if elapsed_time >= 180:
            running = False
            return 'time_end'
        
        fps_clock.tick(FPS)

    pygame.mixer_music.stop()
    pygame.display.update()
    # gameover_sound.play()
    rocks.empty()
    fighters.empty()
    missiles.empty()
    items.empty()
    selected_menu = 1
    return 'game_menu'

# 게임 메뉴(시작) 화면
def game_menu():
    global selected_menu
    background_menu = pygame.image.load(f'src/menu{selected_menu}.png')
    screen.blit(background_menu, [0, 0])

    pygame.display.update()

    for event in pygame.event.get():
        if event.type == pygame.KEYDOWN:
            if event.key == pygame.K_RETURN:
                if selected_menu == 1:
                    return 'waiting'
                elif selected_menu == 2:
                    return 'how_to_play'
                elif selected_menu == 3:
                    return 'quit'
            
            # 메뉴이동
            elif event.key == pygame.K_UP:
                if selected_menu > 1:
                    selected_menu -= 1
            elif event.key == pygame.K_DOWN:
                if selected_menu < 3:
                    selected_menu += 1

        if event.type == pygame.QUIT:
            return 'quit'
    
    return 'game_menu'

# 게임방법 화면
def how_to_play():
    how_to_play_image = pygame.image.load('src/howtoplay.png')
    screen.blit(how_to_play_image, [0, 0])

    pygame.display.update()

    for event in pygame.event.get():
        if event.type == pygame.KEYDOWN:
            if event.key == pygame.K_RETURN:
                return 'waiting'
            
        if event.type == pygame.QUIT:
            return 'quit'
    
    return 'how_to_play'

# 시간초과 화면
def time_end():
    background_image = pygame.image.load('src/background_menu.png')
    screen.blit(background_image, [0, 0])
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

# 연결 대기 화면
def waiting():
    global connect_trying
    background_image = pygame.image.load('src/background_waiting.png')
    screen.blit(background_image, [0, 0])

    pygame.display.update()

    if not connect_trying:
        acceptC()
        connect_trying = True

    for event in pygame.event.get():
        if event.type == pygame.QUIT:
            return 'quit'
    
    return 'waiting'

# 메인 루프
def main():
    global screen, action

    pygame.init()
    
    screen = pygame.display.set_mode((WINDOW_WIDTH, WINDOW_HEIGHT))
    pygame.display.set_caption('~ 운석 뿌셔뿌셔 ~')

    # 현재 action 에 따라서 게임 화면 구성
    # 메인 메뉴 화면으로 시작
    action = 'game_menu'

    while action != 'quit':
        if action == 'game_menu':
            action = game_menu()
        elif action == 'how_to_play':
            action = how_to_play()
        elif action == 'play':
            action = game_loop()
        elif action == 'time_end':
            action = time_end()
        elif action == 'waiting':
            if not playing:
                action = waiting()
            elif playing:
                action = game_loop()

    pygame.quit()

HOST = 'localhost'
PORT = 50007

def acceptC():
    global client
    client = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
    client.connect((HOST, PORT))

    thread = threading.Thread(target=consoles, args=())
    thread.daemon = True
    thread.start()

def consoles():
    global p1_fighter, p2_fighter, missiles, playing
    while True:
        msg = client.recv(1024)
        if msg.decode() == 'left':
            p1_fighter.dx -= 10
        elif msg.decode() == 'right':
            p1_fighter.dx += 10
        elif msg.decode() == 'up':
            p1_fighter.dy -= 10
        elif msg.decode() == 'down':
            p1_fighter.dy += 10
        elif msg.decode() == 'launch':
            missile = Missile(p1_fighter.rect.centerx, p1_fighter.rect.y, p1_fighter)
            missile.launch()
            missiles.add(missile)

        elif msg.decode() == '_left':
            p1_fighter.dx += 10
        elif msg.decode() == '_right':
            p1_fighter.dx -= 10
        elif msg.decode() == '_up':
            p1_fighter.dy += 10
        elif msg.decode() == '_down':
            p1_fighter.dy -= 10

        elif msg.decode() == 'GAMESTART':
            playing = True


if __name__ == "__main__":
    main()