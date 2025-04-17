import pygame
import random
import sys
import psycopg2
from datetime import datetime
from tabulate import tabulate


conn = psycopg2.connect(
    dbname = 'snake',
    user = 'postgres',
    password = '',
    host = 'localhost',
    port = 5432
)
cur = conn.cursor()

cur.execute("""
    CREATE TABLE IF NOT EXISTS game_user (
        user_id SERIAL PRIMARY KEY,
        username VARCHAR(100) UNIQUE NOT NULL
    );
""")
cur.execute("""
    CREATE TABLE IF NOT EXISTS game_score (
        id SERIAL PRIMARY KEY,
        user_id INTEGER REFERENCES game_user(user_id),
        score INTEGER DEFAULT 0,
        level INTEGER DEFAULT 1,
        saved_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
    );
""")
conn.commit()

username = input("Enter your username: ")
cur.execute("SELECT user_id FROM game_user WHERE username = %s", (username,))
user = cur.fetchone()
if user is None:
    cur.execute("INSERT INTO game_user (username) VALUES (%s) RETURNING user_id", (username,))
    user_id = cur.fetchone()[0]
    conn.commit()
else:
    user_id = user[0]

cur.execute('''
        SELECT score, level FROM game_score WHERE user_id = %s ORDER BY saved_at DESC LIMIT 1;
''', (user_id,))
last_game = cur.fetchone()

if last_game :
    print(f"Last session - Score : {last_game[0]}, Level : {last_game[1]}")
else :
    print("No previous game found. Starting fresh.")

print(f"\n Welcome, {username} (user_id: {user_id})\n")

pygame.init()
width, height = 600, 400
cell_size = 20
FPS = 15
speed = 10
clock = pygame.time.Clock()

white = (255, 255, 255)
green = (0, 255, 0)
dark_green = (0, 155, 0)
red = (255, 0, 0)
black = (0, 0, 0)

screen = pygame.display.set_mode((width, height))
pygame.display.set_caption("Snake")
font = pygame.font.SysFont("Verdana", 20)

snake = [(100, 100), (80, 100), (60, 100)]
direction = 'RIGHT'
score = 0
level = 1
move_counter = FPS // speed

walls = []
for x in range(0, width, cell_size):
    walls.append((x, 0))
    walls.append((x, height - cell_size))
for y in range(0, height, cell_size):
    walls.append((0, y))
    walls.append((width - cell_size, y))

def generate_food():
    while True:
        x = random.randint(1, (width // cell_size) - 2) * cell_size
        y = random.randint(1, (height // cell_size) - 2) * cell_size
        if (x, y) not in snake and (x, y) not in walls:
            return (x, y)

food = generate_food()

def draw():
    screen.fill(white)
    for wall in walls:
        pygame.draw.rect(screen, black, (wall[0], wall[1], cell_size, cell_size))
    for part in snake:
        pygame.draw.rect(screen, green, (part[0], part[1], cell_size, cell_size))
    pygame.draw.rect(screen, red, (food[0], food[1], cell_size, cell_size))
    score_text = font.render(f"Score: {score}  Level: {level}", True, dark_green)
    screen.blit(score_text, (10, 10))
    pygame.display.update()

running = True
paused = False
while running:
    clock.tick(FPS)
    if not paused:
        move_counter += 1

    for event in pygame.event.get():
        if event.type == pygame.QUIT:
            running = False
            break
        elif event.type == pygame.KEYDOWN:
            if event.key == pygame.K_SPACE:
                paused = not paused
                if paused:
                    cur.execute("INSERT INTO game_score (user_id, score, level) VALUES (%s, %s, %s)", (user_id, score, level))
                    conn.commit()
                    print("Game paused and saved.")
            if not paused:
                if event.key == pygame.K_UP and direction != 'DOWN':
                    direction = 'UP'
                elif event.key == pygame.K_DOWN and direction != 'UP':
                    direction = 'DOWN'
                elif event.key == pygame.K_LEFT and direction != 'RIGHT':
                    direction = 'LEFT'
                elif event.key == pygame.K_RIGHT and direction != 'LEFT':
                    direction = 'RIGHT'

    if not paused and move_counter >= FPS // speed:
        move_counter = 0
        head_x, head_y = snake[0]
        if direction == 'UP': head_y -= cell_size
        elif direction == 'DOWN': head_y += cell_size
        elif direction == 'LEFT': head_x -= cell_size
        elif direction == 'RIGHT': head_x += cell_size

        new_head = (head_x, head_y)
        if new_head in walls or new_head in snake or head_x < 0 or head_x >= width or head_y < 0 or head_y >= height:
            cur.execute("INSERT INTO game_score (user_id, score, level) VALUES (%s, %s, %s)", (user_id, score, level))
            conn.commit()
            print("Game saved!")
            pygame.time.delay(1000)
            print("Game Over :( ")
            running = False
            break

        snake.insert(0, new_head)
        if new_head == food:
            score += 1
            food = generate_food()
        else:
            snake.pop()
        draw()

pygame.quit()
cur.close()
conn.close()