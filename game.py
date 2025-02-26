import pygame

pygame.init()
screen = pygame.display.set_mode((800, 600))

# Load the background image
background_image = pygame.image.load("background.png")  # Replace with your background image file
background_image = pygame.transform.scale(background_image, (800, 600))  # Scale to fit the screen

# Load player images for Player 1 (arrow keys)
player1_image = pygame.image.load("player1.png")  # Image for moving right
player1_image = pygame.transform.scale(player1_image, (90, 90))  # Resize if needed
player2_image = pygame.image.load("player2.png")  # Image for moving left
player2_image = pygame.transform.scale(player2_image, (90, 90))  # Resize if needed
player1_jump_right = pygame.image.load("player1_jump_right.png")  # Jumping sprite when moving right
player1_jump_right = pygame.transform.scale(player1_jump_right, (90, 90))
player1_jump_left = pygame.image.load("player1_jump_left.png")  # Jumping sprite when moving left
player1_jump_left = pygame.transform.scale(player1_jump_left, (90, 90))

# Load player images for Player 2 (WASD keys)
player3_image = pygame.image.load("player3.png")  # Image for moving right
player3_image = pygame.transform.scale(player3_image, (90, 90))  # Resize if needed
player4_image = pygame.image.load("player4.png")  # Image for moving left
player4_image = pygame.transform.scale(player4_image, (90, 90))  # Resize if needed
player2_jump_right = pygame.image.load("player2_jump_right.png")  # Jumping sprite when moving right
player2_jump_right = pygame.transform.scale(player2_jump_right, (90, 90))
player2_jump_left = pygame.image.load("player2_jump_left.png")  # Jumping sprite when moving left
player2_jump_left = pygame.transform.scale(player2_jump_left, (90, 90))

# Load tile image
tile_image = pygame.image.load("tile.png")  # Replace with your tile image file
tile_image = pygame.transform.scale(tile_image, (50, 50))  # Resize if needed

# Tile settings
TILE_SIZE = 50  # Size of each tile
FLOOR_HEIGHT = 500  # Y-coordinate where the floor starts

# Player 1 (controlled with arrow keys)
current_player1_image = player1_image  # Default image for Player 1
player1_rect = current_player1_image.get_rect(topleft=(400, FLOOR_HEIGHT - 90))  # Initial position for Player 1
player1_velocity_y = 0  # Vertical velocity for Player 1
player1_jumping = False  # Jump state for Player 1
player1_facing_right = True  # Track direction

# Player 2 (controlled with WASD keys)
current_player2_image = player3_image  # Default image for Player 2
player2_rect = current_player2_image.get_rect(topleft=(50, FLOOR_HEIGHT - 90))  # Initial position for Player 2
player2_velocity_y = 0  # Vertical velocity for Player 2
player2_jumping = False  # Jump state for Player 2
player2_facing_right = True  # Track direction

# Physics settings
GRAVITY = 0.5  # Strength of gravity
JUMP_STRENGTH = -15  # Strength of the jump (negative because y increases downward)

# Speed variable
speed = 5  # Adjust this value to control speed

# Clock for frame rate control
clock = pygame.time.Clock()
FPS = 60  # Frames per second

# Function to draw the floor tiles
def draw_floor():
    for x in range(0, 800, TILE_SIZE):
        for y in range(FLOOR_HEIGHT, 600, TILE_SIZE):
            screen.blit(tile_image, (x, y))

running = True
while running:
    # Limit the frame rate
    clock.tick(FPS)

    # Check if player wants to quit
    for event in pygame.event.get():
        if event.type == pygame.QUIT:
            running = False

    # Move Player 1 (arrow keys) and change the sprite based on direction
    keys = pygame.key.get_pressed()
    if keys[pygame.K_RIGHT]:
        player1_rect.x += speed
        player1_facing_right = True
        if not player1_jumping:
            current_player1_image = player1_image
    if keys[pygame.K_LEFT]:
        player1_rect.x -= speed
        player1_facing_right = False
        if not player1_jumping:
            current_player1_image = player2_image

    # Jump for Player 1 (UP arrow key)
    if keys[pygame.K_UP] and not player1_jumping:
        player1_velocity_y = JUMP_STRENGTH
        player1_jumping = True
        current_player1_image = player1_jump_right if player1_facing_right else player1_jump_left

    # Move Player 2 (WASD keys) and change the sprite based on direction
    if keys[pygame.K_d]:
        player2_rect.x += speed
        player2_facing_right = True
        if not player2_jumping:
            current_player2_image = player3_image
    if keys[pygame.K_a]:
        player2_rect.x -= speed
        player2_facing_right = False
        if not player2_jumping:
            current_player2_image = player4_image

    # Jump for Player 2 (W key)
    if keys[pygame.K_w] and not player2_jumping:
        player2_velocity_y = JUMP_STRENGTH
        player2_jumping = True
        current_player2_image = player2_jump_right if player2_facing_right else player2_jump_left

    # Apply gravity to Player 1
    player1_velocity_y += GRAVITY
    player1_rect.y += player1_velocity_y

    # Apply gravity to Player 2
    player2_velocity_y += GRAVITY
    player2_rect.y += player2_velocity_y

    # Reset Player 1 when landing
    if player1_rect.bottom >= FLOOR_HEIGHT:
        player1_rect.bottom = FLOOR_HEIGHT
        player1_velocity_y = 0
        player1_jumping = False
        current_player1_image = player1_image if player1_facing_right else player2_image

    # Reset Player 2 when landing
    if player2_rect.bottom >= FLOOR_HEIGHT:
        player2_rect.bottom = FLOOR_HEIGHT
        player2_velocity_y = 0
        player2_jumping = False
        current_player2_image = player3_image if player2_facing_right else player4_image

    # Draw the background
    screen.blit(background_image, (0, 0))

    # Draw the floor tiles
    draw_floor()

    # Draw both players on the screen
    screen.blit(current_player1_image, player1_rect.topleft)
    screen.blit(current_player2_image, player2_rect.topleft)

    # Update the display
    pygame.display.flip()

pygame.quit()