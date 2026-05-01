import display, touch, buttons, buzzer, system, time, gc, math

W = display.WIDTH
H = display.HEIGHT
c = display.color

BG = c(5, 5, 15)
WHITE = c(255, 255, 255)
DIM = c(80, 80, 100)
DARK = c(20, 20, 35)

def tc(y, txt, sz, col):
    cw = [5, 10, 15][min(sz, 2)]
    display.text(W // 2 - (len(txt) * cw) // 2, y, txt, sz, col)

def lerp(a, b, t):
    return int(a + (b - a) * t)

def mix(c1, c2, t):
    r1, g1, b1 = c1
    r2, g2, b2 = c2
    return c(lerp(r1, r2, t), lerp(g1, g2, t), lerp(b1, b2, t))

# Phase colors (r,g,b tuples for mixing)
C_IN = (0, 200, 255)
C_HOLD = (160, 80, 255)
C_OUT = (0, 220, 140)

# Modes: name, [(label, duration_s, color_tuple), ...]
MODES = [
    ("Box 4-4-4-4", [("Breathe In", 4, C_IN), ("Hold", 4, C_HOLD),
                      ("Breathe Out", 4, C_OUT), ("Hold", 4, C_HOLD)]),
    ("4-7-8 Calm", [("Breathe In", 4, C_IN), ("Hold", 7, C_HOLD),
                     ("Breathe Out", 8, C_OUT)]),
    ("Relaxing", [("Breathe In", 4, C_IN), ("Breathe Out", 6, C_OUT)]),
]

mode = 0
phase = 0
pt = time.ticks_ms()
cycles = 0
fr = 0

_prev1 = False

while True:
    g = touch.gesture()
    if g == 'swipe_left' or g == 'long_press':
        system.exit()

    b1 = buttons.pressed(1)
    sw = g == 'swipe_right'
    if (b1 and not _prev1) or sw:
        mode = (mode + 1) % len(MODES)
        phase = 0
        pt = time.ticks_ms()
        cycles = 0
        buzzer.click()
    _prev1 = b1

    mn, phases = MODES[mode]
    ph = phases[phase]
    label, dur, pcol = ph
    now = time.ticks_ms()
    elapsed = time.ticks_diff(now, pt) / 1000.0
    t = min(elapsed / dur, 1.0)

    if t >= 1.0:
        phase = (phase + 1) % len(phases)
        if phase == 0:
            cycles += 1
        pt = now
        t = 0.0
        # Buzzer feedback per phase type
        nl = phases[phase][0]
        if nl == "Breathe In":
            buzzer.tone(600, 60)
        elif nl == "Hold":
            buzzer.tone(400, 40)
        else:
            buzzer.tone(300, 80)
        ph = phases[phase]
        label, dur, pcol = ph

    # Smooth easing with sin
    ease = math.sin(t * math.pi / 2)

    # Circle radius based on phase
    R_MIN = 30
    R_MAX = 75
    if label == "Breathe In":
        r = R_MIN + int((R_MAX - R_MIN) * ease)
    elif label == "Breathe Out":
        r = R_MAX - int((R_MAX - R_MIN) * ease)
    else:
        # Hold: gentle pulse
        pulse = math.sin(t * math.pi * 4) * 4
        r = (R_MAX if phase > 0 else R_MIN) + int(pulse)
        if r < R_MIN:
            r = R_MIN

    # Color: current phase color with slight shift
    col = c(pcol[0], pcol[1], pcol[2])
    # Dimmer version for outer ring
    dcol = c(pcol[0] // 3, pcol[1] // 3, pcol[2] // 3)

    cx = W // 2
    cy = H // 2 + 10

    # --- Draw ---
    display.clear(BG)

    # Outer glow rings
    for i in range(3):
        display.circle(cx, cy, r + 6 + i * 4, dcol)

    # Main filled circle
    display.circle_filled(cx, cy, r, col)

    # Inner highlight
    hcol = c(min(pcol[0] + 60, 255), min(pcol[1] + 60, 255), min(pcol[2] + 60, 255))
    display.circle_filled(cx, cy, r // 3, hcol)

    # Phase label
    tc(cy - 8, label, 1, WHITE)

    # Mode name at top
    tc(4, mn, 0, DIM)

    # Cycle count
    display.text(4, 4, str(cycles), 0, DIM)

    # Progress bar at bottom
    bw = 200
    bx = (W - bw) // 2
    by = H - 18
    display.rect(bx, by, bw, 6, DARK)
    pw = int(bw * t)
    if pw > 0:
        display.rect_filled(bx, by, pw, 6, col)

    # Phase dots indicator
    np = len(phases)
    dx = W // 2 - (np * 12) // 2
    for i in range(np):
        if i == phase:
            display.circle_filled(dx + i * 12 + 4, H - 8, 3, WHITE)
        else:
            display.circle(dx + i * 12 + 4, H - 8, 2, DIM)

    display.flush()

    fr += 1
    if fr % 60 == 0:
        gc.collect()
    time.sleep_ms(33)
