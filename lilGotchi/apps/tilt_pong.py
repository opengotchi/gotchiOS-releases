import display, touch, buttons, system, time, gc, imu, buzzer

W = display.WIDTH
H = display.HEIGHT
c = display.color

BG = c(0, 0, 0)
WHITE = c(255, 255, 255)
GREEN = c(0, 230, 80)
RED = c(255, 50, 50)
CYAN = c(0, 200, 255)
GRAY = c(40, 40, 40)
DGRAY = c(80, 80, 80)

_rs = time.ticks_us()
def _rn():
    global _rs
    _rs = (_rs * 1103515245 + 12345) & 0x7FFFFFFF
    return _rs
def ri(a, b):
    return a + _rn() % (b - a + 1)

PW = 50
PH = 6
BR = 4
WIN = 7

def tc(y, txt, sz, col):
    cw = [5, 10, 15][min(sz, 2)]
    display.text(W // 2 - (len(txt) * cw) // 2, y, txt, sz, col)

def reset_ball():
    global bx, by, bvx, bvy, spd
    bx = W // 2
    by = H // 2
    spd = 3
    bvx = spd if ri(0, 1) == 0 else -spd
    bvy = spd if ri(0, 1) == 0 else -spd

def init():
    global px, aix, ps, ais, over
    px = W // 2
    aix = W // 2
    ps = 0
    ais = 0
    over = False
    reset_ball()

PY = H - 18
AY = 12

init()
fr = 0

while True:
    g = touch.gesture()
    if g == 'swipe_left' or g == 'long_press':
        system.exit()

    if over:
        if g == 'press' or g == 'release' or buttons.any():
            init()
            continue
        display.clear(BG)
        if ps >= WIN:
            tc(80, "YOU WIN!", 2, GREEN)
        else:
            tc(80, "YOU LOSE", 2, RED)
        tc(120, str(ps) + " - " + str(ais), 1, WHITE)
        tc(160, "Tap to play", 1, DGRAY)
        display.flush()
        time.sleep_ms(33)
        fr += 1
        if fr % 60 == 0:
            gc.collect()
        continue

    # Player tilt control
    ax, ay, az = imu.accel()
    px += int(ax * 12)
    if px < PW // 2:
        px = PW // 2
    if px > W - PW // 2:
        px = W - PW // 2

    # AI tracking with slight delay
    diff = bx - aix
    ai_spd = 3
    if diff > 2:
        aix += ai_spd
    elif diff < -2:
        aix -= ai_spd
    if aix < PW // 2:
        aix = PW // 2
    if aix > W - PW // 2:
        aix = W - PW // 2

    # Ball movement
    bx += bvx
    by += bvy

    # Wall bounce
    if bx <= BR:
        bx = BR
        bvx = -bvx
    if bx >= W - BR:
        bx = W - BR
        bvx = -bvx

    # Player paddle bounce (bottom)
    if bvy > 0 and by >= PY - BR and by < PY + PH:
        if bx >= px - PW // 2 - BR and bx <= px + PW // 2 + BR:
            bvy = -bvy
            by = PY - BR
            off = (bx - px) / (PW // 2)
            bvx = int(off * 5)
            if bvx == 0:
                bvx = 1 if ri(0, 1) == 0 else -1
            spd += 0.15
            buzzer.tone(800, 30)

    # AI paddle bounce (top)
    if bvy < 0 and by <= AY + PH + BR and by > AY:
        if bx >= aix - PW // 2 - BR and bx <= aix + PW // 2 + BR:
            bvy = -bvy
            by = AY + PH + BR
            off = (bx - aix) / (PW // 2)
            bvx = int(off * 5)
            if bvx == 0:
                bvx = 1 if ri(0, 1) == 0 else -1
            spd += 0.15
            buzzer.tone(600, 30)

    # Speed clamp
    if spd > 7:
        spd = 7

    # Scoring
    if by < -10:
        ps += 1
        buzzer.tone(1200, 100)
        if ps >= WIN:
            over = True
        else:
            reset_ball()
    if by > H + 10:
        ais += 1
        buzzer.tone(300, 150)
        if ais >= WIN:
            over = True
        else:
            reset_ball()

    # Draw
    display.clear(BG)

    # Center line
    for i in range(0, W, 12):
        display.rect_filled(i, H // 2 - 1, 6, 2, GRAY)

    # Scores
    display.text(W // 2 - 30, H // 2 - 10, str(ais), 1, RED)
    display.text(W // 2 + 20, H // 2 - 10, str(ps), 1, GREEN)

    # AI paddle (top)
    display.rect_filled(aix - PW // 2, AY, PW, PH, RED)

    # Player paddle (bottom)
    display.rect_filled(px - PW // 2, PY, PW, PH, GREEN)

    # Ball
    display.circle_filled(int(bx), int(by), BR, CYAN)

    display.flush()
    fr += 1
    if fr % 60 == 0:
        gc.collect()
    time.sleep_ms(25)
