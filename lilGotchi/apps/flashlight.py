import display, touch, buttons, buzzer, system, time, gc

W = display.WIDTH
H = display.HEIGHT
c = display.color

WHITE = c(255, 255, 255)
BLACK = c(0, 0, 0)
RED = c(255, 0, 0)
DRED = c(80, 0, 0)
GRAY = c(40, 40, 40)

# Button edge detection
_prev = [False] * 4
def be(n):
    cur = buttons.pressed(n)
    hit = cur and not _prev[n - 1]
    _prev[n - 1] = cur
    return hit

# State
mode = 0        # 0=white, 1=red, 2=strobe
sos = False
bright = 255
bl = [255, 191, 127, 64]
bi = 0
strobe_on = True
msg = ""
msg_t = 0

# SOS pattern: dot=1, dash=3, gap between=1, letter gap=3, word gap=7
# S=...  O=---  S=...
# Units: dot dash gap lgap (between letters) wgap (end repeat)
SOS_PAT = [1,0,1,0,1, 9, 3,0,3,0,3, 9, 1,0,1,0,1, 21]
# 1=dot on, 3=dash on, 0=inter-element gap(1 unit), 9=letter gap(3 units), 21=word gap(7 units)
sos_idx = 0
sos_timer = 0
SOS_UNIT = 150  # ms per unit

def show_msg(s):
    global msg, msg_t
    msg = s
    msg_t = time.ticks_ms()

def get_sos_state():
    """Returns (on, duration_units) for current SOS element"""
    v = SOS_PAT[sos_idx]
    if v == 0:
        return (False, 1)
    elif v == 9:
        return (False, 3)
    elif v == 21:
        return (False, 7)
    else:
        return (True, v)

fr = 0
display.backlight(bright)

while True:
    g = touch.gesture()
    if g == 'swipe_left' or g == 'long_press':
        display.backlight(128)
        system.exit()

    now = time.ticks_ms()

    # B1: cycle mode
    if be(1):
        mode = (mode + 1) % 3
        names = ["WHITE", "RED", "STROBE"]
        show_msg(names[mode])
        buzzer.click()
        strobe_on = True

    # B2: toggle SOS
    if be(2):
        sos = not sos
        show_msg("SOS ON" if sos else "SOS OFF")
        buzzer.click()
        sos_idx = 0
        sos_timer = now

    # B3: brightness cycle
    if be(3):
        bi = (bi + 1) % 4
        bright = bl[bi]
        display.backlight(bright)
        show_msg(str((4 - bi) * 25) + "%")
        buzzer.click()

    # SOS logic
    sos_on = False
    if sos:
        on, dur = get_sos_state()
        elapsed = time.ticks_diff(now, sos_timer)
        if elapsed >= dur * SOS_UNIT:
            sos_idx = (sos_idx + 1) % len(SOS_PAT)
            sos_timer = now
            on, dur = get_sos_state()
        sos_on = on
        if sos_on:
            buzzer.tone(800, 10)

    # Determine screen color
    if sos:
        if sos_on:
            col = WHITE
            display.backlight(bright)
        else:
            col = BLACK
            display.backlight(0)
    elif mode == 0:
        col = WHITE
        display.backlight(bright)
    elif mode == 1:
        col = RED
        display.backlight(bright)
    elif mode == 2:
        strobe_on = not strobe_on
        if strobe_on:
            col = WHITE
            display.backlight(bright)
        else:
            col = BLACK
            display.backlight(0)

    # Draw
    display.clear(col)

    # Show message overlay briefly
    if msg and time.ticks_diff(now, msg_t) < 800:
        tw = len(msg) * 10
        bx = W // 2 - tw // 2 - 4
        display.rect_filled(bx, H // 2 - 12, tw + 8, 28, GRAY)
        display.text(W // 2 - tw // 2, H // 2 - 7, msg, 1, WHITE)
    elif msg:
        msg = ""

    # Small mode indicator at bottom
    if not sos and mode != 2:
        ind = "B1:Mode B2:SOS B3:Dim"
        display.text(4, H - 10, ind, 0, DRED if mode == 0 else GRAY)

    display.flush()

    fr += 1
    if fr % 60 == 0:
        gc.collect()

    if mode == 2 and not sos:
        time.sleep_ms(50)
    else:
        time.sleep_ms(33)
