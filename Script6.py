import pygame
pygame.init()

# Load Simba image
player_image = pygame.image.load("Photos/Simba_First_Game.jpg")

screen = pygame.display.set_mode((800, 600))
clock = pygame.time.Clock()

# Red square (obstacle)
surface = pygame.Surface((100, 100))
surface.fill((255, 0, 0))  # Fill the surface with red color
square_rect = surface.get_rect(center=(600, 300))

# Simba position and rect
player_pos = pygame.Vector2(50, 50)
scaled_player = pygame.transform.scale(player_image, (80, 80))
player_rect = scaled_player.get_rect(topleft=player_pos)

running = True
dt = 0

while running:
    dt = clock.tick(60) / 1000  # Delta time in seconds
    
    for event in pygame.event.get():
        if event.type == pygame.QUIT:
            running = False
    
    screen.fill("skyblue")  # Fill the screen with blue 
    
    # Draw red square
    screen.blit(surface, square_rect)
    
    # Draw Simba
    scaled_player = pygame.transform.scale(player_image, (80, 80))
    player_rect = scaled_player.get_rect(topleft=player_pos)
    screen.blit(scaled_player, player_pos)
    
    # Player controls
    keys = pygame.key.get_pressed()
    if keys[pygame.K_UP]:
        player_pos.y -= 300 * dt
    if keys[pygame.K_DOWN]:
        player_pos.y += 300 * dt
    if keys[pygame.K_LEFT]:
        player_pos.x -= 300 * dt
    if keys[pygame.K_RIGHT]:
        player_pos.x += 300 * dt
    
    player_rect = scaled_player.get_rect(topleft=player_pos)
    
    # Collision detection
    if player_rect.colliderect(square_rect):
        print("Collision detected! Simba hit the red square!")
    
    pygame.display.flip()

pygame.quit()
