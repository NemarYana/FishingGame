import pygame
import random
from abc import ABC, abstractmethod
from pygame.sprite import Sprite

SCREEN_WIDTH = 1208
SCREEN_HEIGHT = 690
PLAYER_X = 478
PLAYER_Y = 307
PLAYER_WIDTH = 178
PLAYER_HEIGHT = 227

MINIGAME_WIDTH = 440
MINIGAME_HEIGHT = 218

FONT_PATH = 'minecraft.ttf'
TITLE_SIZE = 40
PROGRESS_SIZE = 32
HINT_SIZE = 16
HINT2_SIZE = 24
MINIGAME_SIZE = 24
MINIGAME_HINT_SIZE = 16

from pygame.locals import (
    K_SPACE,
    K_p,
    K_TAB,
    K_ESCAPE,
    KEYDOWN,
    QUIT
)

class Fish(ABC):
    def __init__(self, name):
        self.name = name
        self.caught = False

    @abstractmethod
    def get_difficulty(self):
        pass

class CommonFish(Fish):
    def get_difficulty(self):
        return 35

class RareFish(Fish):
    def get_difficulty(self):
        return 25

class LegendaryFish(Fish):
    def get_difficulty(self):
        return 15

class Album:
    def __init__(self):
        self.all_fish = [
            CommonFish("Старый ботинок"), CommonFish("Окунь"), CommonFish("Щука"), CommonFish("Лещ"),
            RareFish("Сом"), RareFish("Форель"), RareFish("Судак"), RareFish("Лосось"), RareFish("Осётр"),
            LegendaryFish("Хариус"), LegendaryFish("Голец"), LegendaryFish("Золотая рыбка")
        ]
        
        self.fish_icons = []
        for fish in self.all_fish:
            icon_path = f'icons/{fish.name}.png'
            icon = pygame.image.load(icon_path).convert_alpha()
            icon.set_colorkey((0, 0, 0))
            self.fish_icons.append(icon)
            
        self.closed_icon = pygame.image.load('icons/closed.png').convert_alpha()
        self.closed_icon.set_colorkey((0, 0, 0))

    def catch_fish(self, fish_index):
        fish = self.all_fish[fish_index]
        if not fish.caught:
            fish.caught = True
            return True, fish
        return False, fish

    def get_caught_count(self):
        return sum(1 for fish in self.all_fish if fish.caught)

    def get_total_fish(self):
        return len(self.all_fish)

    def draw(self, screen):
        overlay = pygame.Surface((SCREEN_WIDTH, SCREEN_HEIGHT))
        overlay.set_alpha(200)
        overlay.fill((0, 0, 0))
        screen.blit(overlay, (0, 0))

        big_font = pygame.font.Font(FONT_PATH, TITLE_SIZE)
        font = pygame.font.Font(FONT_PATH, PROGRESS_SIZE)

        title = big_font.render("АЛЬБОМ РЫБ", True, (255, 255, 255))
        screen.blit(title, (SCREEN_WIDTH//2 - title.get_width()//2, 91))

        progress = font.render(f"Прогресс: {self.get_caught_count()}/{self.get_total_fish()}", True, (255, 255, 0))
        screen.blit(progress, (SCREEN_WIDTH//2 - progress.get_width()//2, 150))

        progress_percent = self.get_caught_count() / len(self.all_fish)
        bar_width = 1020
        bar_height = 40
        bar_x = SCREEN_WIDTH//2 - bar_width//2
        bar_y = 202

        pygame.draw.rect(screen, (73, 73, 73), (bar_x, bar_y, bar_width, bar_height))
        pygame.draw.rect(screen, (76, 191, 90), (bar_x, bar_y, int(bar_width * progress_percent), bar_height))

        padding = 12
        cell_size = 160
        cols = 6
        rows = 2

        total_width = cols * cell_size + (cols - 1) * padding
        total_height = rows * cell_size + (rows - 1) * padding

        start_x = (SCREEN_WIDTH - total_width) // 2
        start_y = 266

        for i, fish in enumerate(self.all_fish):
            row = i // cols
            col = i % cols

            x = start_x + col * (cell_size + padding)
            y = start_y + row * (cell_size + padding)

            if fish.caught:
                icon = self.fish_icons[i]
            else:
                icon = self.closed_icon

            screen.blit(icon, (x, y))

class FishingMiniGame:
    def __init__(self):
        self.active = False
        self.current_fish = None
        self.bar_position = 30
        self.direction = 1
        self.target_start = 0
        self.target_end = 0
        self.bar_speed = 2
        self.fish_index = None
        self.required_hits = 0
        self.hits_made = 0

    def start(self, fish, fish_index):
        self.active = True
        self.current_fish = fish
        self.fish_index = fish_index
        self.bar_position = random.randint(20, 80)
        self.direction = random.choice([-1, 1])
        self.hits_made = 0

        target_width = fish.get_difficulty()
        self.target_start = random.randint(20, 80 - target_width)
        self.target_end = self.target_start + target_width

        if isinstance(fish, LegendaryFish):
            self.required_hits = 5
        elif isinstance(fish, RareFish):
            self.required_hits = 3
        else:
            self.required_hits = 1

    def update(self, space_pressed):
        if not self.active:
            return False, None

        self.bar_position += self.bar_speed * self.direction

        if self.bar_position >= 95:
            self.bar_position = 95
            self.direction = -1
        elif self.bar_position <= 5:
            self.bar_position = 5
            self.direction = 1

        if space_pressed:
            if self.target_start <= self.bar_position <= self.target_end:
                self.hits_made += 1
                if self.hits_made >= self.required_hits:
                    self.active = False
                    return True, True
                else:
                    self.bar_position = random.randint(20, 80)
            else:
                self.active = False
                return True, False

        return False, None

    def draw(self, screen):
        if not self.active:
            return

        window_w = MINIGAME_WIDTH
        window_h = MINIGAME_HEIGHT
        window_x = 674
        window_y = SCREEN_HEIGHT//2 - window_h//2

        back = pygame.Surface((window_w, window_h))
        back.fill((0,0,0))
        back.set_alpha(180)
        screen.blit(back, (window_x, window_y))

        big_font = pygame.font.Font(FONT_PATH, MINIGAME_SIZE)
        font = pygame.font.Font(FONT_PATH, MINIGAME_HINT_SIZE)
        
        title = big_font.render(f"Ловим рыбу", True, (255, 255, 255))
        screen.blit(title, (window_x + window_w//2 - title.get_width()//2, window_y + 20))
        
        if self.required_hits > 1:
            progress = big_font.render(f"Попаданий: {self.hits_made}/{self.required_hits}", True, (255, 215, 0))
            screen.blit(progress, (window_x + window_w//2 - progress.get_width()//2, window_y + 55))
        
        bar_y = window_y + 100
        bar_h = 50
        bar_w = 400
        bar_x = window_x + (window_w - bar_w)//2

        pygame.draw.rect(screen, (73, 73, 73), (bar_x, bar_y, bar_w, bar_h))
        
        target_x = bar_x + (self.target_start * bar_w // 100)
        target_w = (self.target_end - self.target_start) * bar_w // 100
        pygame.draw.rect(screen, (76, 191, 90), (target_x, bar_y, target_w, bar_h))
        
        bar_pos = bar_x + (self.bar_position * bar_w // 100)
        pygame.draw.rect(screen, (255, 255, 255), (bar_pos - 3, bar_y, 6, bar_h))
               
        instr = font.render("Нажмите пробел в зелёной зоне!", True, (255, 255, 255))
        screen.blit(instr, (window_x + window_w//2 - instr.get_width()//2, window_y + 174))

class Player(Sprite):
    def __init__(self, album, mini_game):
        self.x = PLAYER_X
        self.y = PLAYER_Y

        self.sprites_cast = []
        sheet = pygame.image.load('images/player1.png').convert_alpha()
        sheet.set_colorkey((0, 0, 0))
        for i in range(3):
            self.sprites_cast.append(sheet.subsurface(
                pygame.Rect(i*PLAYER_WIDTH, 0, PLAYER_WIDTH, PLAYER_HEIGHT)
            ))

        self.sprites_retrieve = []
        sheet = pygame.image.load('images/player.png').convert_alpha()
        sheet.set_colorkey((0, 0, 0))
        for i in range(6):
            self.sprites_retrieve.append(sheet.subsurface(
                pygame.Rect(i*PLAYER_WIDTH, 0, PLAYER_WIDTH, PLAYER_HEIGHT)
            ))

        self.current_sprites = self.sprites_cast 
        self.current_frame = 0

        self.is_cast = False
        self.is_animating = False
        self.anim_speed = 0.1
        self.state = "IDLE"

        self.album = album
        self.mini_game = mini_game
        self.pending_fish = None
        self.pending_fish_index = None

        self.message = ""
        self.message_timer = 0
        
    def actions(self, event):
        if event.type == KEYDOWN:
            if event.key == K_SPACE and not self.is_animating and not self.mini_game.active:
                self.is_animating = True
                self.current_frame = 0
                if not self.is_cast:
                    self.current_sprites = self.sprites_cast
                    self.state = "CASTING"
                else:
                    self.current_sprites = self.sprites_retrieve
                    self.state = "RETRIEVING"
    
    def update(self):
        if self.message_timer > 0:
            self.message_timer -= 1
            if self.message_timer == 0:
                self.message = ""
                
        if self.is_animating:
            self.current_frame += self.anim_speed
            if self.current_frame >= len(self.current_sprites):
                if self.state == "CASTING":
                    self.current_frame = len(self.current_sprites) - 1
                    self.is_cast = True
                    self.is_animating = False

                    fish_index = random.randint(0, len(self.album.all_fish) - 1)
                    self.pending_fish = self.album.all_fish[fish_index]
                    self.pending_fish_index = fish_index

                    self.mini_game.start(self.pending_fish, self.pending_fish_index)
                    
                elif self.state == "RETRIEVING":
                    self.is_cast = False
                    self.is_animating = False
                    self.current_sprites = self.sprites_cast
                    self.current_frame = 0
                    self.state = "IDLE"

    def finish_fishing(self, success):
        if success:
            s_catch = pygame.mixer.Sound('sounds/catch.mp3')
            s_catch.set_volume(0.1)
            s_catch.play()
            is_new, fish = self.album.catch_fish(self.pending_fish_index)
            if fish.name == "Старый ботинок":
                self.message = f"Вы поймали {fish.name.lower()}!"
                self.message_timer = 100
            elif is_new:
                self.message = f"Новая рыба - {fish.name}!"
                self.message_timer = 120
            else:
                self.message = f"{fish.name}, уже есть в альбоме"
                self.message_timer = 100
                
        else:
            self.message = f"Рыба сорвалась с крючка!"
            self.message_timer = 100
            
        self.is_animating = True
        self.current_frame = 0
        self.current_sprites = self.sprites_retrieve
        self.state = "RETRIEVING"

        self.pending_fish = None
        self.pending_fish_index = None
    
    def draw(self, screen):
        idx = int(self.current_frame)
        if idx < len(self.current_sprites):
            img = self.current_sprites[idx]
            screen.blit(img, (self.x, self.y))

    def draw_message(self, screen):
        font = pygame.font.Font(FONT_PATH, MINIGAME_SIZE)
        if self.message:
            text = font.render(self.message, True, (255, 255, 255))
            screen.blit(text, (SCREEN_WIDTH//2 - text.get_width()//2, SCREEN_HEIGHT//2 - 80))

class GameField:
    def __init__(self, screen, player):
        self.screen = screen
        self.album = player.album
        self.mini_game = player.mini_game
        self.player = player

        self.background_img = pygame.image.load('images/background.png').convert()

        self.show_album = False
        
    def handle_events(self, event):
        if event.type == KEYDOWN:
            if event.key == K_TAB:
                if not self.mini_game.active:
                    self.show_album = not self.show_album

    def draw_background(self):
        self.screen.blit(self.background_img, (0, 0))

    def draw_interface(self):
        font = pygame.font.Font(FONT_PATH, HINT2_SIZE)
        
        progress_text = font.render(
            f"Альбом: {self.album.get_caught_count()}/{len(self.album.all_fish)}", 
            True, (255, 255, 255)
        )
        self.screen.blit(progress_text, (24, 24))
        
        hint1 = font.render(("TAB - альбом рыб"), True, (255, 255, 255))
        self.screen.blit(hint1, (SCREEN_WIDTH - hint1.get_width() - 24, 24))

        hint2 = font.render(("Пробел - забросить удочку"), True, (255, 255, 255))
        self.screen.blit(hint2, (SCREEN_WIDTH - hint2.get_width() - 24, 50))
        
        self.player.draw_message(self.screen)
        
        self.mini_game.draw(self.screen)

    def draw_album(self):
        if self.show_album:
            self.album.draw(self.screen)

    def is_album_open(self):
        return self.show_album
    
    def close_album(self):
        self.show_album = False
    
    def draw(self):
        self.draw_background()
        self.player.draw(self.screen)
        self.draw_interface()
        self.draw_album()

pygame.init()
screen = pygame.display.set_mode((SCREEN_WIDTH, SCREEN_HEIGHT))
pygame.display.set_caption("Рыбалка")
clock = pygame.time.Clock()
pygame.mixer.music.load("sounds/music.mp3")
pygame.mixer.music.play(-1)
pygame.mixer.music.set_volume(0.1)
isPause = False

album = Album()
mini_game = FishingMiniGame() 
player = Player(album, mini_game)
game_field = GameField(screen, player)
    
isRun = True
    
while isRun:
    space_pressed = False
    for event in pygame.event.get():
        if event.type == QUIT:
            isRun = False
        if event.type == KEYDOWN:
            if event.key == K_ESCAPE:
                isRun = False
            elif event.key == K_p:
                isPause = not isPause
                if isPause:
                    pygame.mixer.music.pause()
                else:
                    pygame.mixer.music.unpause()
            elif event.key == K_SPACE:
                if not game_field.is_album_open():
                        space_pressed = True
                        if not mini_game.active and not player.is_animating:
                            player.actions(event)
            else:
                game_field.handle_events(event)

    if mini_game.active:
        finished, success = mini_game.update(space_pressed)
        if finished:
            player.finish_fishing(success)
        
    player.update()
        
    game_field.draw()
        
    pygame.display.flip()
    clock.tick(60)
    
pygame.quit()
