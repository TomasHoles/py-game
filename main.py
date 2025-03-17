import pygame
import random
import math

# Inicializace Pygame
pygame.init()

# Nastavení okna
WIDTH, HEIGHT = 800, 600
WIN = pygame.display.set_mode((WIDTH, HEIGHT))

# Barvy
WHITE = (255, 255, 255)
RED = (255, 0, 0, 128)
YELLOW = (255, 255, 0, 128)
BLUE = (0, 0, 255)
MAGENTA = (255, 0, 255)
BLACK = (0, 0, 0)
GREEN = (0, 255, 0)
ORANGE = (255, 165, 0)
CYAN = (0, 255, 255)

# Hráč
PLAYER_SIZE = 30
BASE_PLAYER_SPEED = 5
BASE_JUMP_FORCE = -12
GRAVITY = 0.6

class Player:
    def __init__(self):
        self.rect = pygame.Rect(WIDTH//2, HEIGHT//2, PLAYER_SIZE, PLAYER_SIZE)
        self.velocity_y = 0
        self.jumps_left = 2
        self.lives = 3
        self.speed = BASE_PLAYER_SPEED
        self.jump_force = BASE_JUMP_FORCE
        self.invincible = False
        self.invincible_timer = 0
        self.speed_timer = 0
        self.jump_boost_timer = 0

    def jump(self):
        if self.jumps_left > 0:
            self.velocity_y = self.jump_force
            self.jumps_left -= 1

    def update(self):
        self.velocity_y += GRAVITY
        self.rect.y += self.velocity_y

        if self.rect.bottom >= HEIGHT:
            self.rect.bottom = HEIGHT
            self.velocity_y = 0
            self.jumps_left = 2

        # Timery power-upů
        if self.invincible:
            self.invincible_timer -= 1
            if self.invincible_timer <= 0:
                self.invincible = False

        if self.speed_timer > 0:
            self.speed_timer -= 1
            if self.speed_timer == 0:
                self.speed = BASE_PLAYER_SPEED

        if self.jump_boost_timer > 0:
            self.jump_boost_timer -= 1
            if self.jump_boost_timer == 0:
                self.jump_force = BASE_JUMP_FORCE

class Projectile:
    def __init__(self, target_pos):
        self.size = random.randint(15, 25)
        start_side = random.choice(["top", "left", "right"])
        
        if start_side == "top":
            self.x = random.randint(0, WIDTH)
            self.y = -self.size
        elif start_side == "left":
            self.x = -self.size
            self.y = random.randint(0, HEIGHT)
        else:
            self.x = WIDTH + self.size
            self.y = random.randint(0, HEIGHT)

        self.rect = pygame.Rect(self.x, self.y, self.size, self.size)
        self.color = BLUE
        
        dx = target_pos[0] - self.x
        dy = target_pos[1] - self.y
        distance = math.hypot(dx, dy)
        self.speed = 4 + random.random() * 2
        self.dx = dx/distance * self.speed
        self.dy = dy/distance * self.speed

    def update(self):
        self.rect.x += self.dx
        self.rect.y += self.dy

class GroundObstacle:
    def __init__(self):
        self.width = 100
        self.height = 20
        self.direction = random.choice(["left", "right"])
        
        if self.direction == "left":
            self.rect = pygame.Rect(-self.width, HEIGHT - self.height - 10, self.width, self.height)
            self.speed = 7
        else:
            self.rect = pygame.Rect(WIDTH, HEIGHT - self.height - 10, self.width, self.height)
            self.speed = -7
        
        self.color = MAGENTA

    def update(self):
        self.rect.x += self.speed

class PowerUp:
    TYPES = ['life', 'invincibility', 'speed', 'jump']
    COLORS = {
        'life': GREEN,
        'invincibility': YELLOW,
        'speed': ORANGE,
        'jump': CYAN
    }

    def __init__(self):
        self.type = random.choice(self.TYPES)
        self.size = 25
        self.rect = pygame.Rect(random.randint(0, WIDTH - self.size), random.randint(0, HEIGHT - self.size), self.size, self.size)
        self.color = self.COLORS[self.type]



class VerticalDangerZone:
    def __init__(self):
        self.width = WIDTH // 5  # 1/5 šířky
        self.x = random.randint(0, WIDTH - self.width)  # náhodná pozice při aktivaci
        self.rect = pygame.Rect(self.x, 0, self.width, HEIGHT)
        self.warning = False
        self.active = False
        self.timer = 0
        self.cooldown = 600
        self.current_cooldown = self.cooldown

    def activate(self):
        self.x = random.randint(0, WIDTH - self.width)
        self.rect = pygame.Rect(self.x, 0, self.width, HEIGHT)
        self.warning = True
        self.active = False
        self.timer = 90  # 1.5s varování

    def update(self):
        if self.warning or self.active:
            self.timer -= 1
            if self.warning and self.timer <= 0:
                self.warning = False
                self.active = True
                self.timer = 120  # 2s aktivní fáze
            elif self.active and self.timer <= 0:
                self.active = False
                self.current_cooldown = self.cooldown
        else:
            self.current_cooldown -= 1
            if self.current_cooldown <= 0:
                self.activate()

    def draw(self, window):
        if self.warning or self.active:
            color = YELLOW if self.warning else RED
            surface = pygame.Surface((self.width, HEIGHT), pygame.SRCALPHA)
            surface.fill(color)
            window.blit(surface, (self.x, 0))

    def check_collision(self, player_rect):
        return self.active and self.rect.colliderect(player_rect)

# Implementace do hry
def main():
    clock = pygame.time.Clock()
    player = Player()
    projectiles = []
    ground_obstacles = []
    powerups = []
    danger_zone = VerticalDangerZone()
    score = 0
    score_timer = 0
    font = pygame.font.Font(None, 36)
    game_active = True

    while True:
        clock.tick(60)
        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                pygame.quit()
                return
            if event.type == pygame.KEYDOWN:
                if event.key == pygame.K_SPACE and game_active:
                    player.jump()
                if event.key == pygame.K_r and not game_active:
                    main()

        if game_active:
            keys = pygame.key.get_pressed()
            player.rect.x += (keys[pygame.K_RIGHT] - keys[pygame.K_LEFT]) * player.speed
            player.update()

            # Skóre rychlejší: každých 30 ticků = +1 bod
            score_timer += 1
            if score_timer % 30 == 0:
                score += 1

            # Projektily
            difficulty = score // 50
            if random.random() < 0.03 + difficulty * 0.01:
                projectiles.append(Projectile(player.rect.center))

            # Zemní překážky
            if random.random() < 0.005 + difficulty * 0.002:
                ground_obstacles.append(GroundObstacle())

            # Power-upy (nízko u země)
            if random.random() < 0.002:
                pu = PowerUp()
                pu.rect.y = random.randint(HEIGHT - 100, HEIGHT - 50)
                powerups.append(pu)

            # Danger zone update
            danger_zone.update()

            # Kolize
            for projectile in projectiles[:]:
                projectile.update()
                if projectile.rect.colliderect(player.rect):
                    if not player.invincible:
                        player.lives -= 1
                    projectiles.remove(projectile)
                    if player.lives <= 0:
                        game_active = False
                elif not pygame.Rect(-100, -100, WIDTH+200, HEIGHT+200).colliderect(projectile.rect):
                    projectiles.remove(projectile)

            for obstacle in ground_obstacles[:]:
                obstacle.update()
                if obstacle.rect.colliderect(player.rect):
                    if not player.invincible:
                        player.lives -= 1
                    ground_obstacles.remove(obstacle)
                    if player.lives <= 0:
                        game_active = False
                if (obstacle.direction == "left" and obstacle.rect.left > WIDTH) or \
                   (obstacle.direction == "right" and obstacle.rect.right < 0):
                    ground_obstacles.remove(obstacle)

            for powerup in powerups[:]:
                if powerup.rect.colliderect(player.rect):
                    if powerup.type == 'life':
                        player.lives += 1
                    elif powerup.type == 'invincibility':
                        player.invincible = True
                        player.invincible_timer = 300
                    elif powerup.type == 'speed':
                        player.speed = 8
                        player.speed_timer = 300
                    elif powerup.type == 'jump':
                        player.jump_force = -16
                        player.jump_boost_timer = 300
                    powerups.remove(powerup)

            # Kontrola zóny nebezpečí
            if danger_zone.check_collision(player.rect) and not player.invincible:
                player.lives -= 1
                if player.lives <= 0:
                    game_active = False

            player.rect.clamp_ip(pygame.Rect(0, 0, WIDTH, HEIGHT))

            # Kreslení
            WIN.fill(BLACK)
            pygame.draw.rect(WIN, WHITE if not player.invincible else YELLOW, player.rect)

            for p in projectiles:
                pygame.draw.rect(WIN, p.color, p.rect)
            for go in ground_obstacles:
                pygame.draw.rect(WIN, go.color, go.rect)
            for pu in powerups:
                pygame.draw.rect(WIN, pu.color, pu.rect)

            # Danger zóna vykreslení
            danger_zone.draw(WIN)

            # HUD
            WIN.blit(font.render(f"Životy: {player.lives}", True, WHITE), (10, 10))
            WIN.blit(font.render(f"Skóre: {score}", True, WHITE), (10, 40))
            if player.invincible:
                WIN.blit(font.render("Nesmrtelnost!", True, YELLOW), (10, 70))
            if player.speed_timer > 0:
                WIN.blit(font.render("Rychlost ↑", True, ORANGE), (10, 100))
            if player.jump_boost_timer > 0:
                WIN.blit(font.render("Doskok ↑", True, CYAN), (10, 130))

        else:
            WIN.fill(BLACK)
            WIN.blit(font.render("Game Over! R - restart", True, WHITE), (WIDTH//2-120, HEIGHT//2-20))
            WIN.blit(font.render(f"Skóre: {score}", True, WHITE), (WIDTH//2-50, HEIGHT//2+20))

        pygame.display.update()


if __name__ == "__main__":
    main()
