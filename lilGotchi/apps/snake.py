import display, touch, buttons, buzzer, system, time, gc, imu

W = display.WIDTH
H = display.HEIGHT
c = display.color

# Nokia 3310 palette
BG = c(130, 150, 90)
FG = c(40, 50, 20)
HD = c(20, 30, 10)
FD = c(10, 15, 5)
# powerup colors (darker variants for LCD look)
PC_S = c(80, 100, 40)   # slow - lighter green
PC_X = c(60, 75, 25)    # shrink
PC_D = c(50, 65, 20)    # double pts
PC_G = c(35, 45, 10)    # ghost
PC_B = c(90, 110, 50)   # bonus food

G = 8
GW = W // G
GH = (H - 14) // G
OY = 14

_rs = time.ticks_us()
def _rn():
    global _rs
    _rs = (_rs * 1103515245 + 12345) & 0x7FFFFFFF
    return _rs
def ri(a, b): return a + _rn() % (b - a + 1)

snake = []
dx = 1; dy = 0
ndx = 1; ndy = 0
fx = 0; fy = 0

def init_snake():
    global snake, dx, dy, ndx, ndy
    mx = GW // 2; my = GH // 2
    snake = [(mx, my), (mx-1, my), (mx-2, my), (mx-3, my)]
    dx = 1; dy = 0; ndx = 1; ndy = 0

def rand_empty():
    for _ in range(200):
        rx = ri(0, GW - 1)
        ry = ri(0, GH - 1)
        ok = True
        for s in snake:
            if s[0] == rx and s[1] == ry: ok = False; break
        if ok: return rx, ry
    return ri(0, GW-1), ri(0, GH-1)

def place_food():
    global fx, fy
    fx, fy = rand_empty()

init_snake()
place_food()
score = 0; best = 0; alive = True; level = 1
spd = 150; combo = 0; combo_t = 0
foods_eaten = 0

s = system.readfile('/littlefs/config/snake_best.txt')
if s:
    try: best = int(s.strip())
    except: pass

# powerups on field: [x, y, type, spawn_time]
# types: 0=slow, 1=shrink, 2=double, 3=ghost, 4=bonus
pups = []
PU_SYM = ['S', 'X', '2', 'G', '$']
PU_COL = [PC_S, PC_X, PC_D, PC_G, PC_B]

# active effects
slow_t = 0; double_t = 0; ghost_t = 0
msg = ''; msg_t = 0

# bonus food (second food that appears temporarily)
bfx = -1; bfy = -1; bf_t = 0

_bp = [False] * 4
def be(n):
    cu = buttons.pressed(n)
    h = cu and not _bp[n - 1]
    _bp[n - 1] = cu
    return h

last_step = time.ticks_ms()
next_pup = time.ticks_ms() + ri(8000, 15000)
fr = 0

while True:
    g = touch.gesture()
    if g == 'swipe_left' or g == 'long_press':
        system.exit()

    now = time.ticks_ms()

    if not alive:
        display.clear(BG)
        display.rect_filled(W//2-65, 40, 130, 140, FG)
        display.rect_filled(W//2-63, 42, 126, 136, BG)
        display.text(W//2-45, 50, "GAME OVER", 1, FG)
        display.text(W//2-30, 78, "Score:" + str(score), 0, FG)
        display.text(W//2-28, 93, "Best:" + str(best), 0, FG)
        display.text(W//2-28, 108, "Level:" + str(level), 0, FG)
        display.text(W//2-28, 123, "Eaten:" + str(foods_eaten), 0, FG)
        display.text(W//2-35, 150, "Tap retry", 0, FG)
        display.flush()
        if touch.touching() or buttons.any():
            time.sleep_ms(200)
            init_snake(); place_food()
            score = 0; spd = 150; alive = True; level = 1
            combo = 0; foods_eaten = 0
            pups = []; slow_t = 0; double_t = 0; ghost_t = 0
            bfx = -1; bfy = -1; bf_t = 0
            next_pup = now + ri(8000, 15000)
        time.sleep_ms(33); continue

    # Buttons
    if be(1) and dx != 1: ndx = -1; ndy = 0
    if be(4) and dx != -1: ndx = 1; ndy = 0
    if be(2) and dy != 1: ndx = 0; ndy = -1
    if be(3) and dy != -1: ndx = 0; ndy = 1

    # Swipe
    if g == 'swipe_up' and dy != 1: ndx = 0; ndy = -1
    if g == 'swipe_down' and dy != -1: ndx = 0; ndy = 1
    if g == 'swipe_right' and dx != -1: ndx = 1; ndy = 0

    # Gyro tilt
    try:
        ax, ay, _ = imu.accel()
    except:
        ax, ay, _ = 0.0, 0.0, 0.0
    if abs(ax) > 0.55 or abs(ay) > 0.55:
        if abs(ax) > abs(ay):
            if ax > 0.55 and dx != -1: ndx = 1; ndy = 0
            elif ax < -0.55 and dx != 1: ndx = -1; ndy = 0
        else:
            if ay > 0.55 and dy != -1: ndx = 0; ndy = 1
            elif ay < -0.55 and dy != 1: ndx = 0; ndy = -1

    # spawn powerup periodically
    if time.ticks_diff(now, next_pup) > 0 and len(pups) < 2:
        px, py = rand_empty()
        pups.append([px, py, ri(0, 4), now])
        next_pup = now + ri(10000, 20000)

    # expire powerups after 8 seconds
    pups = [p for p in pups if time.ticks_diff(now, p[3]) < 8000]

    # expire bonus food
    if bfx >= 0 and time.ticks_diff(now, bf_t) > 6000:
        bfx = -1; bfy = -1

    # expire effects
    if slow_t and now > slow_t: slow_t = 0
    if double_t and now > double_t: double_t = 0
    if ghost_t and now > ghost_t: ghost_t = 0

    # current speed (slow powerup)
    cur_spd = spd * 2 if slow_t and now < slow_t else spd

    # step
    if time.ticks_diff(now, last_step) >= cur_spd:
        last_step = now
        dx = ndx; dy = ndy

        hx = (snake[0][0] + dx) % GW
        hy = (snake[0][1] + dy) % GH

        # self collision (skip if ghost mode)
        if not (ghost_t and now < ghost_t):
            for s in snake:
                if s[0] == hx and s[1] == hy:
                    alive = False
                    if score > best:
                        best = score
                        system.writefile('/littlefs/config/snake_best.txt', str(best))
                    buzzer.tone(200, 200)
                    break

        if alive:
            snake.insert(0, (hx, hy))
            ate = False

            # main food
            if hx == fx and hy == fy:
                ate = True
                foods_eaten += 1
                # combo scoring
                if time.ticks_diff(now, combo_t) < 3000:
                    combo += 1
                else:
                    combo = 1
                combo_t = now
                pts = combo * level
                if double_t and now < double_t: pts *= 2
                score += pts
                if combo > 1:
                    msg = str(combo) + 'x COMBO! +' + str(pts)
                    msg_t = now
                place_food()
                buzzer.click()
                if spd > 60: spd -= 3

                # level up every 8 foods
                if foods_eaten % 8 == 0:
                    level += 1
                    msg = 'LEVEL ' + str(level) + '!'
                    msg_t = now
                    buzzer.tone(600, 50)
                    time.sleep_ms(50)
                    buzzer.tone(800, 100)

                # spawn bonus food occasionally
                if ri(0, 99) < 25 and bfx < 0:
                    bfx, bfy = rand_empty()
                    bf_t = now

            # bonus food
            elif bfx >= 0 and hx == bfx and hy == bfy:
                ate = True
                pts = 5 * level
                if double_t and now < double_t: pts *= 2
                score += pts
                msg = 'BONUS +' + str(pts)
                msg_t = now
                bfx = -1; bfy = -1
                buzzer.tone(500, 40)

            if not ate:
                snake.pop()

            # check powerup pickup
            np = []
            for p in pups:
                if p[0] == hx and p[1] == hy:
                    pt = p[2]
                    if pt == 0:  # slow
                        slow_t = now + 6000
                        msg = 'SLOW MODE'; msg_t = now
                    elif pt == 1:  # shrink
                        if len(snake) > 4:
                            for _ in range(3):
                                if len(snake) > 4: snake.pop()
                        msg = 'SHRINK!'; msg_t = now
                    elif pt == 2:  # double points
                        double_t = now + 10000
                        msg = '2X POINTS'; msg_t = now
                    elif pt == 3:  # ghost
                        ghost_t = now + 5000
                        msg = 'GHOST MODE'; msg_t = now
                    elif pt == 4:  # bonus score
                        pts = 10 * level
                        score += pts
                        msg = '+' + str(pts) + ' PTS'; msg_t = now
                    buzzer.tone(500, 40)
                else:
                    np.append(p)
            pups = np

    # draw
    display.clear(BG)

    # HUD
    display.text(2, 2, str(score), 0, FG)
    display.text(W//2 - 8, 2, 'L' + str(level), 0, FG)
    display.text(W - 40, 2, "HI:" + str(best), 0, FG)

    # active effect indicators
    ix = 50
    if slow_t and now < slow_t:
        display.text(ix, 2, 'S', 0, FG); ix += 8
    if double_t and now < double_t:
        display.text(ix, 2, '2', 0, FG); ix += 8
    if ghost_t and now < ghost_t:
        display.text(ix, 2, 'G', 0, FG); ix += 8

    display.line(0, OY - 2, W, OY - 2, FG)

    # main food — blinking
    if (now // 300) % 2 == 0:
        display.rect_filled(fx * G + 1, OY + fy * G + 1, G - 2, G - 2, FD)
    else:
        display.rect_filled(fx * G + 2, OY + fy * G + 2, G - 4, G - 4, FD)

    # bonus food — fast blink
    if bfx >= 0:
        if (now // 150) % 2 == 0:
            display.rect_filled(bfx * G, OY + bfy * G, G, G, FD)

    # powerups on field
    for p in pups:
        px = p[0] * G; py = OY + p[1] * G
        # blink when about to expire (last 2s)
        age = time.ticks_diff(now, p[3])
        if age > 6000 and (now // 200) % 2 == 0:
            continue
        display.rect_filled(px, py, G, G, PU_COL[p[2]])
        display.text(px + 1, py, PU_SYM[p[2]], 0, BG)

    # snake
    is_ghost = ghost_t and now < ghost_t
    for i in range(len(snake)):
        sx = snake[i][0] * G
        sy = OY + snake[i][1] * G
        if i == 0:
            display.rect_filled(sx, sy, G, G, HD)
        elif is_ghost and (now // 100) % 2 == 0:
            display.rect(sx, sy, G, G, FG)  # outline only in ghost
        else:
            display.rect_filled(sx, sy, G, G, FG)

    # combo/message popup
    if msg and time.ticks_diff(now, msg_t) < 1500:
        mx = W // 2 - len(msg) * 3
        display.text(mx, OY + 4, msg, 0, HD)
    elif msg:
        msg = ''

    display.flush()
    fr += 1
    if fr % 60 == 0: gc.collect()
    time.sleep_ms(16)
