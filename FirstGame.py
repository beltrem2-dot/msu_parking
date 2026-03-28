## Fist PyGame Program, just a simpple program!!
import pygame
pygame.init()
player_image = pygame.image.load("Photos/Simba_First_Game.jpg")
screen = pygame.display.set_mode((1080, 720))
clock = pygame.time.Clock()
dt = clock.tick(60)/500 #delta time
player_pos = pygame.Vector2(screen.get_width()/2, screen.get_height()/2)
running = True
dt = 0 
while running:
    for event in pygame.event.get():
        if event.type == pygame.QUIT:
            running = False
    screen.fill("skyblue") #fills screen with blue color
    scaled_player = pygame.transform.scale(player_image, (100, 100))
    screen.blit(scaled_player, player_pos) #includes picture of my dog instead 
    # player controls
    keys = pygame.key.get_pressed()
    if keys[pygame.K_UP]:
        player_pos.y -= 300 * dt
    if keys[pygame.K_DOWN]:
         player_pos.y += 300 * dt
    if keys[pygame.K_LEFT]:
        player_pos.x -= 300 * dt
    if keys[pygame.K_RIGHT]:
        player_pos.x += 300 * dt
    pygame.display.flip()     
    clock.tick(60)   #makes game run at 60 fps
pygame.quit()