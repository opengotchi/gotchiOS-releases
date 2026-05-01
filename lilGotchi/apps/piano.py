import display, touch, buttons, buzzer, system, time, gc

W = display.WIDTH
H = display.HEIGHT
c = display.color

BG = c(30, 30, 40)
WHITE = c(255, 255, 255)
BLACK = c(0, 0, 0)
GRAY = c(180, 180, 180)
HIT_W = c(200, 220, 255)
HIT_B = c(80, 80, 120)
CYAN = c(0, 200, 255)
DKGRAY = c(50, 50, 60)

NAMES = ['C','C#','D','D#','E','F','F#','G','G#','A','A#','B']
BASE = [262,277,294,311,330,349,370,392,415,440,466,494]

octave = 0
WI = [0,2,4,5,7,9,11]
BI = [1,3,6,8,10]

NW = 8
KW = W // NW
KH = 160
KY = H - KH
BKW = 22
BKH = 100

BKX = [KW-BKW//2, 2*KW-BKW//2, 4*KW-BKW//2, 5*KW-BKW//2, 6*KW-BKW//2]

_prev = [False]*4
def btn_edge(n):
    cur = buttons.pressed(n)
    hit = cur and not _prev[n-1]
    _prev[n-1] = cur
    return hit

def freq(semi):
    f = BASE[semi % 12] if semi < 12 else BASE[0] * 2
    o = octave
    if semi == 12: o += 1
    if o > 0:
        for _ in range(o): f *= 2
    elif o < 0:
        for _ in range(-o): f //= 2
    return f

def get_note(tx, ty):
    if ty < KY or ty > H:
        return -1
    if ty < KY + BKH:
        for i in range(5):
            bx = BKX[i]
            if bx <= tx < bx + BKW:
                return BI[i]
    ki = tx // KW
    if ki > 7: ki = 7
    if ki < NW:
        return WI[ki] if ki < 7 else 12
    return -1

played = -1
note_name = ""
fr = 0

while True:
    g = touch.gesture()
    if g == 'swipe_left' or g == 'long_press':
        system.exit()

    if btn_edge(3):
        octave = min(2, octave + 1)
    if btn_edge(2):
        octave = max(-2, octave - 1)

    cur = -1
    if touch.touching():
        p = touch.pos()
        if p:
            cur = get_note(p[0], p[1])
            if cur >= 0 and cur != played:
                f = freq(cur)
                buzzer.tone(f, 200)
                if cur < 12:
                    note_name = NAMES[cur]
                else:
                    note_name = "C"
            played = cur
    else:
        played = -1

    display.clear(BG)

    oname = "C" + str(4 + octave)
    display.text(5, 5, "Piano", 1, WHITE)
    display.text(W - 80, 5, "Oct:" + oname, 1, CYAN)

    if note_name:
        display.text(W//2 - 15, 30, note_name, 2, WHITE)

    display.text(5, 55, "B2:Oct-", 0, GRAY)
    display.text(W-60, 55, "B3:Oct+", 0, GRAY)

    for i in range(NW):
        x = i * KW
        semi = WI[i] if i < 7 else 12
        hit = (cur == semi)
        col = HIT_W if hit else WHITE
        display.rect_filled(x + 1, KY, KW - 2, KH, col)
        display.rect(x, KY, KW, KH, DKGRAY)
        nm = NAMES[semi % 12]
        display.text(x + KW//2 - 5, KY + KH - 18, nm, 0, BLACK)

    for i in range(5):
        bx = BKX[i]
        semi = BI[i]
        hit = (cur == semi)
        col = HIT_B if hit else BLACK
        display.rect_filled(bx, KY, BKW, BKH, col)
        display.rect(bx, KY, BKW, BKH, DKGRAY)

    display.flush()

    fr += 1
    if fr % 60 == 0:
        gc.collect()
    time.sleep_ms(33)
