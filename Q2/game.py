import pygame
import random

# Initialize Pygame
pygame.init()

# Screen dimensions
screen_width = 1280
screen_height = 720
screen = pygame.display.set_mode((screen_width, screen_height))
pygame.display.set_caption("Tank Battle")

# Colors
white = (255, 255, 255)
black = (0, 0, 0)
red = (255, 0, 0)
green = (0, 255, 0)
gray = (128, 128, 128)  # For the tank body

# Clock for controlling frame rate
clock = pygame.time.Clock()

# --- Classes ---

class Player(pygame.sprite.Sprite):
    def __init__(self, x, y):
        super().__init__()
        self.image = pygame.Surface((50, 30))  # Create a surface for the tank
        self.image.fill(gray)  # Fill with gray color
        pygame.draw.rect(self.image, black, (10, 10, 30, 10))  # Draw the turret
        self.rect = self.image.get_rect()
        self.rect.x = x
        self.rect.y = y
        self.speed = 5
        self.health = 100
        self.lives = 3

    def update(self):
        keys = pygame.key.get_pressed()
        if keys[pygame.K_LEFT]:
            self.rect.x -= self.speed
        if keys[pygame.K_RIGHT]:
            self.rect.x += self.speed
        # Keep player within screen bounds
        if self.rect.left < 0:
            self.rect.left = 0
        elif self.rect.right > screen_width:
            self.rect.right = screen_width

    def shoot(self):
        projectile = Projectile(self.rect.centerx, self.rect.top)
        all_sprites.add(projectile)
        projectiles.add(projectile)

class Projectile(pygame.sprite.Sprite):
    def __init__(self, x, y, speed=-10, color=black):
        super().__init__()
        self.image = pygame.Surface((10, 20))  # Simple projectile image
        self.image.fill(color)
        self.rect = self.image.get_rect()
        self.rect.centerx = x
        self.rect.bottom = y
        self.speed = speed  # Moving upwards or downwards

    def update(self):
        self.rect.y += self.speed
        if self.rect.bottom < 0 or self.rect.top > screen_height:
            self.kill()  # Remove projectile when off-screen

class Enemy(pygame.sprite.Sprite):
    def __init__(self, x, y):
        super().__init__()
        self.image = pygame.Surface((50, 30))  # Create a surface for the enemy tank
        self.image.fill(gray)
        pygame.draw.rect(self.image, black, (10, 10, 30, 10))  # Draw the turret
        self.rect = self.image.get_rect()
        self.rect.x = x
        self.rect.y = y
        self.speed = 3
        self.health = 50
        self.shoot_delay = 1500  # Time between shots (milliseconds)
        self.last_shot_time = pygame.time.get_ticks()

    def update(self):
        self.rect.x += self.speed
        # Basic enemy movement: bounce off screen edges
        if self.rect.left < 0 or self.rect.right > screen_width:
            self.speed *= -1

        # Shooting logic for enemies
        current_time = pygame.time.get_ticks()
        if current_time - self.last_shot_time > self.shoot_delay:
            self.shoot()
            self.last_shot_time = current_time

    def shoot(self):
        projectile = Projectile(self.rect.centerx, self.rect.bottom, speed=5, color=red)
        all_sprites.add(projectile)
        enemy_projectiles.add(projectile)

class Boss(Enemy):  # Inheriting from Enemy class
    def __init__(self, x, y):
        super().__init__(x, y)
        self.image = pygame.Surface((100, 60))  # Bigger image for the boss
        self.image.fill(gray)
        pygame.draw.rect(self.image, black, (25, 20, 50, 20))  # Turret
        self.rect = self.image.get_rect()
        self.rect.x = x
        self.rect.y = y
        self.speed = 2  # Slower speed
        self.health = 1000  # Boss with more health
        self.max_health = 1000  # Track max health for the health bar
        self.shoot_delay = 1500  # Time between shots (milliseconds)
        self.last_shot_time = pygame.time.get_ticks()
        self.invincible = False  # Flag for invincibility after being hit
        self.invincibility_duration = 500  # 500 ms of invincibility
        self.last_hit_time = 0  # Time when the boss was last hit

    def update(self):
        # Move boss left and right like regular enemies
        self.rect.x += self.speed
        if self.rect.left < 0 or self.rect.right > screen_width:
            self.speed *= -1  # Reverse direction when it hits the screen edge

        # Shooting logic for the boss
        current_time = pygame.time.get_ticks()
        if current_time - self.last_shot_time > self.shoot_delay:
            self.shoot()
            self.last_shot_time = current_time

        # Check if boss was hit recently and prevent further damage during invincibility period
        if self.invincible and current_time - self.last_hit_time > self.invincibility_duration:
            self.invincible = False  # End invincibility after the duration

    def shoot(self):
        # Boss shoots 5 projectiles in different directions
        for i in range(-2, 3):  # Create 5 projectiles in total
            offset = i * 20  # Spread the projectiles apart horizontally
            projectile = Projectile(self.rect.centerx + offset, self.rect.bottom, speed=5, color=red)
            all_sprites.add(projectile)
            enemy_projectiles.add(projectile)

    def take_damage(self, amount):
        """Handles taking damage, ensuring boss stays invincible for a short time after getting hit"""
        if not self.invincible:
            self.health -= amount
            if self.health < 0:
                self.health = 0  # Prevent health from going negative
            self.invincible = True  # Activate invincibility after being hit
            self.last_hit_time = pygame.time.get_ticks()  # Update the time of the last hit

    def draw_health_bar(self, surface):
        # Boss health bar
        health_percentage = self.health / self.max_health  # Normalize health
        pygame.draw.rect(surface, red, (screen_width - 250, 40, 200, 20))  # Background bar
        pygame.draw.rect(surface, green, (screen_width - 250, 40, 200 * health_percentage, 20))  # Foreground bar
        font = pygame.font.Font(None, 30)
        health_text = font.render(f"Boss Health: {self.health}", True, black)
        surface.blit(health_text, (screen_width - 250, 10))

    def special_attack(self):
        # Fires a burst of projectiles every 5 seconds
        current_time = pygame.time.get_ticks()
        if current_time - self.last_shot_time > 5000:  # Burst every 5 seconds
            for _ in range(5):
                offset = random.choice([-30, 0, 30])  # Random spread
                projectile = Projectile(self.rect.centerx + offset, self.rect.bottom, speed=5, color=red)
                all_sprites.add(projectile)
                enemy_projectiles.add(projectile)
            self.last_shot_time = current_time

            
class Collectible(pygame.sprite.Sprite):
    def __init__(self, x, y, type):
        super().__init__()
        self.type = type
        if self.type == "health":
            self.image = pygame.Surface((20, 20))  # Simple collectible image
            self.image.fill(green)
        elif self.type == "life":
            self.image = pygame.Surface((20, 20))
            self.image.fill(red)  
        self.rect = self.image.get_rect()
        self.rect.centerx = x
        self.rect.bottom = y

# --- Game Variables ---
all_sprites = pygame.sprite.Group()
projectiles = pygame.sprite.Group()
enemies = pygame.sprite.Group()
enemy_projectiles = pygame.sprite.Group()
collectibles = pygame.sprite.Group()

player = Player(100, 500)
all_sprites.add(player)

score = 0

# --- Level Design ---
def create_level_1():
    for i in range(5):
        enemy = Enemy(100 + i * 150, 400)
        all_sprites.add(enemy)
        enemies.add(enemy)

    # Add collectibles
    health_boost = Collectible(300, 400, "health")
    all_sprites.add(health_boost)
    collectibles.add(health_boost)

def create_level_2(): 
    # More enemies, different positions
    for i in range(8):
        enemy = Enemy(50 + i * 100, 300)
        all_sprites.add(enemy)
        enemies.add(enemy)

    # Add collectibles
    life_boost = Collectible(600, 300, "life")
    all_sprites.add(life_boost)
    collectibles.add(life_boost)

def create_level_3():
    # Even more enemies, challenging positions
    for i in range(12):
        enemy = Enemy(20 + i * 70, 200)
        all_sprites.add(enemy)
        enemies.add(enemy)

    # Add collectibles
    health_boost = Collectible(400, 200, "health")
    all_sprites.add(health_boost)
    collectibles.add(health_boost)
    life_boost = Collectible(700, 200, "life")
    all_sprites.add(life_boost)
    collectibles.add(life_boost)

def create_boss_level():
    global boss  # Declare the boss as global if it's being updated in the main game loop
    boss = Boss(screen_width // 2 - 50, 50)  # Position boss on screen
    enemies.add(boss)  # Add the boss to the enemies group
    all_sprites.add(boss)  # Add the boss to the main sprite group

# --- Functions ---
def game_over():
    font = pygame.font.Font(None, 74)
    text = font.render("GAME OVER", True, red)
    text_rect = text.get_rect(center=(screen_width/2, screen_height/2 - 50))
    screen.blit(text, text_rect)

    restart_font = pygame.font.Font(None, 40)
    restart_text = restart_font.render("Press R to restart", True, white)
    restart_rect = restart_text.get_rect(center=(screen_width/2, screen_height/2 + 50))
    screen.blit(restart_text, restart_rect)

    pygame.display.flip()
    waiting = True
    while waiting:
        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                pygame.quit()
                quit()
            if event.type == pygame.KEYDOWN:
                if event.key == pygame.K_r:
                    waiting = False

    # Reset game state
    player.rect.x = 100
    player.rect.y = 500
    player.health = 100
    player.lives = 3
    score = 0 # Reset the score
    for sprite in all_sprites:
        sprite.kill()  # Clear all sprites
    create_level_1()  # Start from level 1 again

def victory():
    font = pygame.font.Font(None, 74)  # Use a large font size
    text = font.render("YOU WON!", True, red)  # Set the text color to red
    text_rect = text.get_rect(center=(screen_width/2, screen_height/2 - 50))
    screen.blit(text, text_rect)

    pygame.display.flip()
    pygame.time.wait(3000)  
    pygame.quit()
    quit()

# Main Game Loop
running = True
current_level = 1
create_level_1()

while running:
    for event in pygame.event.get():
        if event.type == pygame.QUIT:
            running = False
        elif event.type == pygame.KEYDOWN:
            if event.key == pygame.K_SPACE:
                player.shoot()

    # Update all sprites
    all_sprites.update()

    # Check for collisions (projectiles hit enemies)
    hits = pygame.sprite.groupcollide(enemies, projectiles, True, True)
    for hit in hits:
        score += 10

    # Check for collisions (player hits enemies)
    enemy_hits = pygame.sprite.spritecollide(player, enemies, True)
    for hit in enemy_hits:
        player.health -= 20
        if player.health <= 0:
            player.lives -= 1
            player.health = 100
            if player.lives == 0:
                game_over()

    # Check for collisions (player hits enemy projectiles)
    enemy_projectile_hits = pygame.sprite.spritecollide(player, enemy_projectiles, True)
    for hit in enemy_projectile_hits:
        player.health -= 20
        if player.health <= 0:
            player.lives -= 1
            player.health = 100
            if player.lives == 0:
                game_over()

    # Check for collisions (player hits collectibles)
    collectible_hits = pygame.sprite.spritecollide(player, collectibles, True)
    for hit in collectible_hits:
        if hit.type == "health":
            player.health += 20
            if player.health > 100:
                player.health = 100
        elif hit.type == "life":
            player.lives += 1
    
    
    # In the main game loop
        if current_level == 4:
            if enemies:  # Ensure the boss exists in the enemies group
                boss = enemies.sprites()[0]  # Get the boss object
                boss.draw_health_bar(screen)  # Draw the health bar

    
    # Level progression and victory check
    if not enemies:  # If no enemies are left
        if current_level == 4:  # Check for victory at boss level
            victory()
        else:
            current_level += 1
            if current_level == 2:
                create_level_2()
            elif current_level == 3:
                create_level_3()
            elif current_level == 4:
                create_boss_level()


    # Draw / Render
    screen.fill(white)
    all_sprites.draw(screen)

    # Display score
    font = pygame.font.Font(None, 30)
    score_text = font.render("Score: " + str(score), True, black)
    screen.blit(score_text, (10, 10))

    # Display health
    pygame.draw.rect(screen, green, (10, 40, player.health, 15))
    pygame.draw.rect(screen, red, (10 + player.health, 40, 100 - player.health, 15))

    # Display lives
    lives_text = font.render("Lives: " + str(player.lives), True, black)
    screen.blit(lives_text, (10, 60))

    # Display Boss Health
    if current_level == 4:
        boss_health_text = font.render("Boss Health: " + str(enemies.sprites()[0].health), True, black)
        screen.blit(boss_health_text, (screen_width - 200, 10))

    pygame.display.flip()
    clock.tick(60)
    
def game_over():
    font = pygame.font.Font(None, 74)
    text = font.render("GAME OVER", True, red)
    text_rect = text.get_rect(center=(screen_width/2, screen_height/2 - 50))
    screen.blit(text, text_rect)

    restart_font = pygame.font.Font(None, 40)
    restart_text = restart_font.render("Press R to restart", True, white)
    restart_rect = restart_text.get_rect(center=(screen_width/2, screen_height/2 + 50))
    screen.blit(restart_text, restart_rect)

    pygame.display.flip()
    waiting = True
    while waiting:
        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                pygame.quit()
                quit()
            if event.type == pygame.KEYDOWN:
                if event.key == pygame.K_r:
                    waiting = False
                    reset_game()  # Function to reset the game

def reset_game():
    global score, current_level
    score = 0
    current_level = 1
    player.rect.x = 100
    player.rect.y = 500
    player.health = 100
    player.lives = 3
    for sprite in all_sprites:
        sprite.kill()
    create_level_1()  # Restart from level 1

    
    # --- Victory Function ---
def victory():
    font = pygame.font.Font(None, 74)
    text = font.render("YOU WON!", True, red)
    text_rect = text.get_rect(center=(screen_width/2, screen_height/2 - 50))
    screen.blit(text, text_rect)

    pygame.display.flip()
    pygame.time.wait(3000)  # Show victory message for 3 seconds
    pygame.quit()
    quit()

pygame.quit()
