# Cops and Robbers Game by Ryan Dominguez
# 3/17/26
# CSIT 114 Midterm
# This game is a game where the player is the "Robber"
# The Goal is to evade the Police and make it to the exit.
# Stay out of the cops vision cones and reach the green exit to win.
# You can hide in the shield area to avoid detection
# Each level gets harder with more cops and faster speeds.
# Escape all 5 levels and you win!!!!!

import pygame
import sys
import math
import time
import random
import asyncio

# Screen settings
WIDTH, HEIGHT = 800, 600
FPS = 60

# Colors
WHITE = (255, 255, 255)
BLACK = (0, 0, 0)
BLUE = (50, 100, 255)
ORANGE = (255, 150, 50)
RED = (255, 80, 80)
GREEN = (100, 255, 100)


class Player:
    def __init__(self):
        self.x = 100
        self.y = 300
        self.radius = 12
        self.speed = 4

    def move(self, keys):
        if keys[pygame.K_w]: self.y -= self.speed
        if keys[pygame.K_s]: self.y += self.speed
        if keys[pygame.K_a]: self.x -= self.speed
        if keys[pygame.K_d]: self.x += self.speed
        self.x = max(self.radius, min(WIDTH - self.radius, self.x))
        self.y = max(self.radius, min(HEIGHT - self.radius, self.y))

    def draw(self, screen):
        pygame.draw.circle(screen, ORANGE, (int(self.x), int(self.y)), self.radius)


class Cop:
    def __init__(self, x, y):
        self.x = x
        self.y = y
        self.radius = 15
        self.vision_length = 120
        self.angle = random.uniform(0, 2 * math.pi)
        self.rotation_speed = 0.04
        self.move_angle = random.uniform(0, 2 * math.pi)
        self.move_speed = 1.8
        self.turn_rate = 0.15

    def update(self):
        self.move_angle += random.uniform(-self.turn_rate, self.turn_rate)
        self.x += math.cos(self.move_angle) * self.move_speed
        self.y += math.sin(self.move_angle) * self.move_speed

        if self.x < self.radius or self.x > WIDTH - self.radius:
            self.move_angle = math.pi - self.move_angle
            self.x = max(self.radius, min(WIDTH - self.radius, self.x))
        if self.y < self.radius or self.y > HEIGHT - self.radius:
            self.move_angle = -self.move_angle
            self.y = max(self.radius, min(HEIGHT - self.radius, self.y))

        self.angle += self.rotation_speed

    def draw(self, screen):
        left_angle = self.angle - 0.5
        right_angle = self.angle + 0.5
        p1 = (self.x, self.y)
        p2 = (self.x + math.cos(left_angle) * self.vision_length,
              self.y + math.sin(left_angle) * self.vision_length)
        p3 = (self.x + math.cos(right_angle) * self.vision_length,
              self.y + math.sin(right_angle) * self.vision_length)
        pygame.draw.polygon(screen, RED, [p1, p2, p3], 1)
        pygame.draw.circle(screen, BLUE, (int(self.x), int(self.y)), self.radius)

    def detect_player(self, player):
        dx = player.x - self.x
        dy = player.y - self.y
        distance = math.sqrt(dx * dx + dy * dy)
        if distance > self.vision_length:
            return False
        angle_to_player = math.atan2(dy, dx)
        diff = abs((angle_to_player - self.angle + math.pi) % (2 * math.pi) - math.pi)
        return diff < 0.5


async def main():
    pygame.init()
    screen = pygame.display.set_mode((WIDTH, HEIGHT))
    pygame.display.set_caption("Cops & Prisoners")
    clock = pygame.time.Clock()
    font = pygame.font.SysFont(None, 36)

    def create_level(level):
        player = Player()
        if level == 1:
            player.x, player.y = 100, 300
            player.speed = 4
            cops = [Cop(400, 200), Cop(600, 400), Cop(300, 450)]
            for c in cops:
                c.vision_length = 120
                c.rotation_speed = 0.04
                c.move_speed = 1.7
                c.turn_rate = 0.15
            goal = pygame.Rect(700, 250, 50, 100)
            shield = pygame.Rect(80, 280, 60, 60)
        elif level == 2:
            player.x, player.y = 750, 550
            player.speed = 4.3
            cops = [Cop(400, 150), Cop(600, 350), Cop(500, 500), Cop(250, 300)]
            for c in cops:
                c.vision_length = 110
                c.rotation_speed = 0.045
                c.move_speed = 1.9
                c.turn_rate = 0.17
            goal = pygame.Rect(40, 250, 45, 90)
            shield = pygame.Rect(730, 530, 60, 60)
        elif level == 3:
            player.x, player.y = 100, 500
            player.speed = 4.7
            cops = [Cop(350, 170), Cop(640, 120), Cop(200, 420), Cop(520, 360), Cop(680, 500)]
            for c in cops:
                c.vision_length = 120
                c.rotation_speed = 0.06
                c.move_speed = 2.1
                c.turn_rate = 0.23
            goal = pygame.Rect(740, 20, 35, 85)
            shield = pygame.Rect(80, 480, 50, 50)
        elif level == 4:
            player.x, player.y = 100, 80
            player.speed = 5
            cops = [Cop(400, 130), Cop(650, 250), Cop(520, 420), Cop(220, 340), Cop(660, 520)]
            for c in cops:
                c.vision_length = 115
                c.rotation_speed = 0.07
                c.move_speed = 2.3
                c.turn_rate = 0.25
            goal = pygame.Rect(740, 500, 45, 80)
            shield = pygame.Rect(80, 50, 50, 50)
        else:
            player.x, player.y = 750, 50
            player.speed = 5.2
            cops = [Cop(240, 150), Cop(570, 100), Cop(360, 330),
                    Cop(620, 450), Cop(490, 530), Cop(720, 330)]
            for c in cops:
                c.vision_length = 125
                c.rotation_speed = 0.08
                c.move_speed = 2.5
                c.turn_rate = 0.3
            goal = pygame.Rect(40, 520, 35, 70)
            shield = pygame.Rect(720, 30, 60, 60)
        return player, cops, goal, shield

    level = 1
    player, cops, goal, shield = create_level(level)
    game_state = "playing"
    start_time = time.time()
    final_time = 0

    def reset_level():
        nonlocal player, cops, goal, shield, game_state, start_time, final_time
        player, cops, goal, shield = create_level(level)
        game_state = "playing"
        start_time = time.time()
        final_time = 0

    def restart_game():
        nonlocal level
        level = 1
        reset_level()

    while True:
        await asyncio.sleep(0)  # Required for pygbag
        clock.tick(FPS)

        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                pygame.quit()
                sys.exit()
            if event.type == pygame.KEYDOWN:
                if event.key == pygame.K_r and game_state != "playing":
                    restart_game()
                if event.key == pygame.K_n and game_state == "level_complete":
                    if level < 5:
                        level += 1
                    reset_level()

        keys = pygame.key.get_pressed()

        if game_state == "playing":
            player.move(keys)
            for cop in cops:
                cop.update()
                if shield.collidepoint(player.x, player.y):
                    continue
                if cop.detect_player(player):
                    game_state = "lose"
                    final_time = time.time() - start_time

            player_rect = pygame.Rect(player.x - player.radius,
                                      player.y - player.radius,
                                      player.radius * 2, player.radius * 2)
            if player_rect.colliderect(goal):
                if level < 5:
                    game_state = "level_complete"
                else:
                    game_state = "win"
                final_time = time.time() - start_time

        screen.fill(BLACK)
        pygame.draw.rect(screen, GREEN, goal)
        pygame.draw.rect(screen, (50, 150, 50), shield)
        player.draw(screen)
        for cop in cops:
            cop.draw(screen)

        level_text = font.render(f"Level: {level}", True, WHITE)
        screen.blit(level_text, (10, 40))

        if game_state == "playing":
            current_time = time.time() - start_time
            timer_text = font.render(f"Time: {current_time:.1f}", True, WHITE)
            screen.blit(timer_text, (10, 10))
        else:
            timer_text = font.render(f"Time: {final_time:.1f}", True, WHITE)
            screen.blit(timer_text, (10, 10))

        if game_state == "lose":
            text = font.render("CAUGHT! Press R to restart", True, WHITE)
            screen.blit(text, (180, 260))
            stats = font.render(f"Time: {final_time:.1f}s Levels: {level}", True, WHITE)
            screen.blit(stats, (180, 300))
        elif game_state == "level_complete":
            text = font.render("LEVEL COMPLETE! Press N for next level", True, WHITE)
            screen.blit(text, (80, 280))
        elif game_state == "win":
            text = font.render("YOU ESCAPED ALL LEVELS! Press R", True, WHITE)
            screen.blit(text, (120, 260))
            stats = font.render(f"Time: {final_time:.1f}s Levels: {level}", True, WHITE)
            screen.blit(stats, (120, 300))

        pygame.display.flip()


if __name__ == "__main__":
    asyncio.run(main())