"""
gotchiOS Tilt Ball
Tilt the watch to move the ball. It bounces off walls!
"""
import display, imu, time, touch, system

BLACK = display.color(0, 0, 0)
WHITE = display.color(255, 255, 255)
GOLD  = display.color(255, 200, 0)
CYAN  = display.color(0, 200, 255)
DIM   = display.color(40, 40, 40)

W, H = display.WIDTH, display.HEIGHT
R = 8  # ball radius

# Ball state
x, y = W // 2, H // 2
vx, vy = 0.0, 0.0
GRAVITY = 0.3
BOUNCE = 0.7
FRICTION = 0.98

while True:
    g = touch.gesture()
    if g == 'long_press' or g == 'swipe_left':
        system.exit()

    display.clear(BLACK)

    # Border
    display.rect(0, 0, W, H, DIM)

    # Get tilt
    ax, ay, az = imu.accel()

    # Apply tilt as acceleration
    vx += ax * GRAVITY
    vy += ay * GRAVITY

    # Friction
    vx *= FRICTION
    vy *= FRICTION

    # Move
    x += vx
    y += vy

    # Bounce off walls
    if x - R < 1:
        x = R + 1
        vx = -vx * BOUNCE
    if x + R > W - 2:
        x = W - R - 2
        vx = -vx * BOUNCE
    if y - R < 1:
        y = R + 1
        vy = -vy * BOUNCE
    if y + R > H - 2:
        y = H - R - 2
        vy = -vy * BOUNCE

    # Draw ball with shadow
    display.circle_filled(int(x) + 2, int(y) + 2, R, DIM)
    display.circle_filled(int(x), int(y), R, GOLD)
    display.circle(int(x), int(y), R, WHITE)

    # Crosshair at center
    display.line(W // 2 - 5, H // 2, W // 2 + 5, H // 2, DIM)
    display.line(W // 2, H // 2 - 5, W // 2, H // 2 + 5, DIM)

    # Info
    display.text(4, 4, f'Tilt to move!', 0, CYAN)

    display.flush()
    time.sleep_ms(16)  # ~60fps
