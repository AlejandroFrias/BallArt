import pygame
import colorsys
from models import Vector, Ball


pygame.init()
clock = pygame.time.Clock()
font = pygame.font.SysFont(None, 25)

WHITE = (255, 255, 255)
BLACK = (0, 0, 0)

RED = (255, 0, 0)
GREEN = (0, 255, 0)
BLUE = (0, 0, 255)

FRAME_RATE = 60
WIDTH = 1000
HEIGHT = 800
FRICTION = 0
ELASTICITY = 1.0
GRAVITY = Vector(0, 0)
BALL_SIZE = 50
INITIAL_VELOCITY_SCALAR = 5

GAME_DISPLAY = pygame.display.set_mode((WIDTH, HEIGHT))
GAME_DISPLAY.fill(BLACK)

mouse_pos = None
modify_type = None
modify_up = False
modify_down = False
balls = []


def update_balls(balls):
    updated_balls = []
    # Check for ball collisions
    active_balls = [ball for ball in balls if ball.vel]
    if len(active_balls) > 1:
        x_points = []
        for ball in active_balls:
            x_points.append((ball.pos.x - ball.size, True, ball))
            x_points.append((ball.pos.x + ball.size, False, ball))
        x_points.sort(key=lambda t: (t[0], t[1]))
        entered = 0
        potential_collisions = set()
        for x_point in x_points:
            _, entered, ball = x_point
            if entered:
                potential_collisions.add(ball)
            else:
                potential_collisions.remove(ball)
                for other in potential_collisions:
                    if (ball.pos - other.pos).mag <= ball.size + other.size:
                        Ball.separate_balls(ball, other)
                        Ball.change_velocities(ball, other)
    # Wall collisions, update position, apply friction
    for ball in balls:
        ball.size = BALL_SIZE
        if ball.vel:
            # wall collision checks
            if (ball.pos.x <= 0 and ball.vel.x < 0) or (ball.pos.x >= WIDTH and ball.vel.x > 0):
                ball.vel.x *= -ELASTICITY
                ball.vel.y *= ELASTICITY
            if (ball.pos.y <= 0 and ball.vel.y < 0) or (ball.pos.y >= HEIGHT and ball.vel.y > 0):
                ball.vel.y *= ELASTICITY
                ball.vel.y *= -ELASTICITY
            # apply friction
            ball.vel -= ball.vel.norm * FRICTION * ball.size
            # let balls move themselves according to velocity and acceleration vectors
            ball.update(FRAME_RATE)

            # remove ball if it's all the way off screen
            if (
                ball.pos.x < -50
                or ball.pos.x > WIDTH + 50
                or ball.pos.y < -50
                or ball.pos.y > HEIGHT + 50
            ):
                continue
        updated_balls.append(ball)
    return updated_balls


while True:
    for event in pygame.event.get():
        if event.type == pygame.QUIT:
            pygame.quit()
            quit()
        if event.type == pygame.MOUSEBUTTONDOWN:
            mouse_down = True
            mouse_pos = Vector(*event.pos)
            balls.append(Ball(mouse_pos, start_vel=None, start_acc=GRAVITY, size=BALL_SIZE))
        if event.type == pygame.MOUSEBUTTONUP:
            if not balls:
                continue
            mouse_pos = Vector(*event.pos)
            ball = balls[-1]
            ball.vel = (ball.pos - mouse_pos) * INITIAL_VELOCITY_SCALAR
            mouse_down = False
        if event.type == pygame.MOUSEMOTION:
            mouse_pos = Vector(*event.pos)
        if event.type == pygame.KEYDOWN:
            if event.key in {pygame.K_ESCAPE, pygame.K_q}:
                pygame.quit()
                quit()
            if event.key == pygame.K_r:  # reset
                balls = []
                GRAVITY = Vector(0, 0)
                ELASTICITY = 1.0
                FRICTION = 0.0
                BALL_SIZE = 50
                FRAME_RATE = 60
                INITIAL_VELOCITY_SCALAR = 5
                modify_type = None
                modify_down = modify_up = False
            if event.key == pygame.K_s:
                modify_type = "S" if modify_type != "S" else None
            if event.key == pygame.K_g:
                modify_type = "G" if modify_type != "G" else None
            if event.key == pygame.K_e:
                modify_type = "E" if modify_type != "E" else None
            if event.key == pygame.K_u:
                modify_type = "FRICTION" if modify_type != "FRICTION" else None
            if event.key == pygame.K_v:
                modify_type = "V" if modify_type != "V" else None
            if event.key == pygame.K_f:
                modify_type = "FRAME_RATE" if modify_type != "FRAME_RATE" else None
            if event.key in {pygame.K_k, pygame.K_l, pygame.K_UP, pygame.K_RIGHT}:
                modify_up = True
                modify_down = False
            if event.key in {pygame.K_j, pygame.K_h, pygame.K_DOWN, pygame.K_LEFT}:
                modify_down = True
                modify_up = False
        if event.type == pygame.KEYUP:
            if event.key in {pygame.K_j, pygame.K_h, pygame.K_DOWN, pygame.K_LEFT}:
                modify_down = False
            if event.key in {pygame.K_k, pygame.K_l, pygame.K_UP, pygame.K_RIGHT}:
                modify_up = False

    if modify_up or modify_down:
        if modify_type == "G":
            if modify_up:
                GRAVITY.y = min(100, GRAVITY.y + 1)
            else:
                GRAVITY.y = max(0, GRAVITY.y - 1)
        if modify_type == "E":
            if modify_up:
                ELASTICITY = min(1.0, ELASTICITY + 0.001)
            else:
                ELASTICITY = max(0, ELASTICITY - 0.001)
        if modify_type == "FRICTION":
            if modify_up:
                FRICTION = min(1.0, FRICTION + 0.0001)
            else:
                FRICTION = max(0, FRICTION - 0.0001)
        if modify_type == "S":
            if modify_up:
                BALL_SIZE = min(100, BALL_SIZE + 1)
            else:
                BALL_SIZE = max(1, BALL_SIZE - 1)
        if modify_type == "V":
            if modify_up:
                INITIAL_VELOCITY_SCALAR = min(100, INITIAL_VELOCITY_SCALAR + 1)
            else:
                INITIAL_VELOCITY_SCALAR = max(0, INITIAL_VELOCITY_SCALAR - 1)
        if modify_type == "FRAME_RATE":
            if modify_up:
                FRAME_RATE = min(120, FRAME_RATE + 1)
            else:
                FRAME_RATE = max(1, FRAME_RATE - 1)
    balls = update_balls(balls)
    if len(balls) > 2:
        n = len(balls) # of balls
        area = 0.0
        for i in range(n):
            j = (i + 1) % n
            area += balls[i].pos.x * balls[j].pos.y
            area -= balls[j].pos.x * balls[i].pos.y
        area = abs(area) / 2.0
        color = colorsys.hsv_to_rgb(area/(WIDTH*HEIGHT), 1, 255)
    else:
        color = BLACK
    GAME_DISPLAY.fill(color)
    gravity_text = font.render(
        f"Gravity (g): {GRAVITY.y}", True, RED if modify_type == "G" else BLACK
    )
    elasticity_text = font.render(
        f"Elasticity (e): {ELASTICITY * 100}%", True, RED if modify_type == "E" else BLACK
    )
    friction_text = font.render(
        f"Friction (u): {FRICTION * 100}%", True, RED if modify_type == "FRICTION" else BLACK
    )
    size_text = font.render(
        f"Ball Size (s): {BALL_SIZE}", True, RED if modify_type == "S" else BLACK
    )
    initial_velocity_text = font.render(
        f"Initial Velocity (v): {INITIAL_VELOCITY_SCALAR}",
        True,
        RED if modify_type == "V" else BLACK,
    )
    frame_rate_text = font.render(
        f"Frame Rate (f): {FRAME_RATE}", True, RED if modify_type == "FRAME_RATE" else BLACK
    )
    position_text = font.render(f"Mouse Pos: {mouse_pos}", True, BLACK)
    GAME_DISPLAY.blit(gravity_text, (0, 0))
    GAME_DISPLAY.blit(elasticity_text, (0, 30))
    GAME_DISPLAY.blit(friction_text, (0, 60))
    GAME_DISPLAY.blit(size_text, (0, 90))
    GAME_DISPLAY.blit(initial_velocity_text, (0, 120))
    GAME_DISPLAY.blit(frame_rate_text, (0, 150))
    GAME_DISPLAY.blit(position_text, (0, 180))

    if len(balls) > 2:
        pygame.draw.polygon(GAME_DISPLAY, BLACK, [ball.point for ball in balls])
    for ball in balls:
        pygame.draw.circle(GAME_DISPLAY, ball.color, ball.point, ball.size)
    if balls and mouse_pos and mouse_down:
        pygame.draw.line(GAME_DISPLAY, RED, balls[-1].point, mouse_pos.point, 5)

    pygame.display.update()
    clock.tick(FRAME_RATE)
