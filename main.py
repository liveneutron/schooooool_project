import pygame
import random
import math

# ---------- INITIALISE ----------
pygame.init()
WIDTH, HEIGHT = 800, 600
screen = pygame.display.set_mode((WIDTH, HEIGHT))
pygame.display.set_caption("Circle Shooter")
clock = pygame.time.Clock()

# ---------- COLOURS ----------
BLACK = (0, 0, 0)
WHITE = (255, 255, 255)
RED   = (255, 0, 0)
YELLOW= (255, 255, 0)
BLUE  = (0, 100, 255)
GRAY  = (50, 50, 50)

# ---------- FONTS ----------
font_large = pygame.font.SysFont("Arial", 60, bold=True)
font_medium = pygame.font.SysFont("Arial", 36)
font_small = pygame.font.SysFont("Arial", 28)

# ---------- HIGH SCORE ----------
HIGHSCORE_FILE = "highscore.txt"

def load_highscore():
    try:
        with open(HIGHSCORE_FILE, "r") as f:
            return int(f.read().strip())
    except:
        return 0

def save_highscore(score):
    with open(HIGHSCORE_FILE, "w") as f:
        f.write(str(score))

highscore = load_highscore()

# ---------- GAME VARIABLES ----------
player_pos = [WIDTH // 2, HEIGHT // 2]
PLAYER_RADIUS = 20
PLAYER_SPEED = 5

bullets = []          # [x, y, dx, dy]
BULLET_SPEED = 12
BULLET_RADIUS = 5

enemies = []          # [x, y]
ENEMY_SIZE = 30
ENEMY_SPEED = 2

score = 0
spawn_timer = 0
SPAWN_INTERVAL = 40

# Checkered background
CELL_SIZE = 50

def draw_checkerboard():
    for y in range(0, HEIGHT, CELL_SIZE):
        for x in range(0, WIDTH, CELL_SIZE):
            color = GRAY if (x // CELL_SIZE + y // CELL_SIZE) % 2 == 0 else BLACK
            pygame.draw.rect(screen, color, (x, y, CELL_SIZE, CELL_SIZE))

# Game states
state = "title"  # "title", "playing", "game_over"

# --------------------------------------------------------------
# Helper: draw centred text
# --------------------------------------------------------------
def draw_centered_text(text, font, color, y_offset=0):
    surf = font.render(text, True, color)
    rect = surf.get_rect(center=(WIDTH // 2, HEIGHT // 2 + y_offset))
    screen.blit(surf, rect)

# --------------------------------------------------------------
# Reset game
# --------------------------------------------------------------
def reset_game():
    global player_pos, bullets, enemies, score, spawn_timer
    player_pos = [WIDTH // 2, HEIGHT // 2]
    bullets.clear()
    enemies.clear()
    score = 0
    spawn_timer = 0

# --------------------------------------------------------------
# Main Game Loop
# --------------------------------------------------------------
running = True

while running:
    screen.fill(BLACK)

    # ---------- EVENT HANDLING ----------
    for event in pygame.event.get():
        if event.type == pygame.QUIT:
            running = False

        elif event.type == pygame.KEYDOWN:
            # Start from title
            if state == "title" and event.key == pygame.K_SPACE:
                state = "playing"
                reset_game()

            # Restart from game over
            elif state == "game_over" and event.key == pygame.K_r:
                state = "playing"
                reset_game()

        elif event.type == pygame.MOUSEBUTTONDOWN and state == "playing":
            # Shoot bullet
            mx, my = pygame.mouse.get_pos()
            dx = mx - player_pos[0]
            dy = my - player_pos[1]
            dist = math.hypot(dx, dy)
            if dist > 0:
                dir_x = dx / dist
                dir_y = dy / dist
                bullets.append([player_pos[0], player_pos[1], dir_x, dir_y])

    # ==========================================================
    # TITLE SCREEN (No checkerboard)
    # ==========================================================
    if state == "title":
        draw_centered_text("CIRCLE SHOOTER", font_large, BLUE, -100)
        draw_centered_text(f"HIGH SCORE: {highscore}", font_medium, YELLOW, -30)
        draw_centered_text("PRESS SPACE TO PLAY", font_small, WHITE, 50)
        draw_centered_text("WASD = Move | Click = Shoot", font_small, WHITE, 100)

    # ==========================================================
    # PLAYING STATE (With checkerboard)
    # ==========================================================
    elif state == "playing":
        draw_checkerboard()

        # ----- Player Movement -----
        keys = pygame.key.get_pressed()
        if keys[pygame.K_w] and player_pos[1] > PLAYER_RADIUS:
            player_pos[1] -= PLAYER_SPEED
        if keys[pygame.K_s] and player_pos[1] < HEIGHT - PLAYER_RADIUS:
            player_pos[1] += PLAYER_SPEED
        if keys[pygame.K_a] and player_pos[0] > PLAYER_RADIUS:
            player_pos[0] -= PLAYER_SPEED
        if keys[pygame.K_d] and player_pos[0] < WIDTH - PLAYER_RADIUS:
            player_pos[0] += PLAYER_SPEED

        # ----- Spawn Enemies -----
        spawn_timer += 1
        if spawn_timer >= SPAWN_INTERVAL:
            side = random.choice(['top', 'bottom', 'left', 'right'])
            if side == 'top':
                ex, ey = random.randint(0, WIDTH), -ENEMY_SIZE
            elif side == 'bottom':
                ex, ey = random.randint(0, WIDTH), HEIGHT + ENEMY_SIZE
            elif side == 'left':
                ex, ey = -ENEMY_SIZE, random.randint(0, HEIGHT)
            else:
                ex, ey = WIDTH + ENEMY_SIZE, random.randint(0, HEIGHT)
            enemies.append([ex, ey])
            spawn_timer = 0

        # ----- Update Bullets -----
        for b in bullets[:]:
            b[0] += b[2] * BULLET_SPEED
            b[1] += b[3] * BULLET_SPEED
            if not (0 < b[0] < WIDTH and 0 < b[1] < HEIGHT):
                bullets.remove(b)
                continue
            pygame.draw.circle(screen, WHITE, (int(b[0]), int(b[1])), BULLET_RADIUS)

        # ----- Update Enemies -----
        for e in enemies[:]:
            # Move toward player
            dx = player_pos[0] - e[0]
            dy = player_pos[1] - e[1]
            dist = math.hypot(dx, dy)
            if dist > 0:
                e[0] += (dx / dist) * ENEMY_SPEED
                e[1] += (dy / dist) * ENEMY_SPEED

            # Draw enemy
            pygame.draw.rect(screen, RED, (e[0], e[1], ENEMY_SIZE, ENEMY_SIZE))

            # ----- Collision: Enemy hits Player → GAME OVER -----
            if (abs(player_pos[0] - (e[0] + ENEMY_SIZE/2)) < PLAYER_RADIUS + ENEMY_SIZE/2 and
                abs(player_pos[1] - (e[1] + ENEMY_SIZE/2)) < PLAYER_RADIUS + ENEMY_SIZE/2):
                enemies.remove(e)
                if score > highscore:
                    highscore = score
                    save_highscore(highscore)
                state = "game_over"
                break

            # ----- Collision: Bullet hits Enemy -----
            for b in bullets[:]:
                if (abs(b[0] - (e[0] + ENEMY_SIZE/2)) < ENEMY_SIZE/2 + BULLET_RADIUS and
                    abs(b[1] - (e[1] + ENEMY_SIZE/2)) < ENEMY_SIZE/2 + BULLET_RADIUS):
                    enemies.remove(e)
                    bullets.remove(b)
                    score += 1
                    break

        # ----- Draw Player -----
        pygame.draw.circle(screen, YELLOW, (int(player_pos[0]), int(player_pos[1])), PLAYER_RADIUS)

        # ----- UI -----
        ui = font_small.render(f"Score: {score}", True, WHITE)
        screen.blit(ui, (10, 10))

    # ==========================================================
    # GAME OVER SCREEN
    # ==========================================================
    elif state == "game_over":
        draw_centered_text("GAME OVER", font_large, RED, -100)
        draw_centered_text(f"Final Score: {score}", font_medium, WHITE, -40)
        if score == highscore:
            draw_centered_text("NEW HIGH SCORE!", font_medium, YELLOW, 10)
        draw_centered_text(f"High Score: {highscore}", font_medium, YELLOW, 60)
        draw_centered_text("Press R to Restart", font_small, WHITE, 120)

    # Update display
    pygame.display.flip()

    # Delta time | making physics independent of time
    dt = clock.tick(60) / 1000

pygame.quit()
