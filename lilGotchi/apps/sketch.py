import display, touch, buttons, system, time, gc, buzzer

W = display.WIDTH
H = display.HEIGHT
c = display.color

BLACK = c(0, 0, 0)
WHITE = c(255, 255, 255)
DGRAY = c(30, 30, 30)
GRAY = c(80, 80, 80)

TB = 18
colors = [WHITE, c(255, 0, 0), c(0, 255, 0), c(0, 80, 255),
          c(255, 255, 0), c(0, 255, 255), c(255, 0, 255)]
cnames = ["WHT", "RED", "GRN", "BLU", "YEL", "CYN", "MAG"]
sizes = [1, 3, 5]
ci = 0
si = 0

_bp = [False] * 4
def be(n):
    cur = buttons.pressed(n)
    hit = cur and not _bp[n - 1]
    _bp[n - 1] = cur
    return hit

lx = -1
ly = -1
was = False

def toolbar():
    display.rect_filled(0, 0, W, TB, DGRAY)
    display.rect_filled(2, 2, 14, 14, colors[ci])
    display.text(20, 3, cnames[ci], 0, WHITE)
    r = sizes[si]
    display.text(60, 3, "Sz:" + str(r), 0, WHITE)
    display.circle_filled(100, 9, r, colors[ci])
    display.text(130, 3, "B2:Clr", 0, GRAY)

def draw_pt(x, y, col, r):
    if r <= 1:
        display.pixel(x, y, col)
    else:
        display.circle_filled(x, y, r, col)

display.clear(BLACK)
toolbar()
display.flush()

fr = 0
while True:
    g = touch.gesture()
    if g == 'swipe_left' or g == 'long_press':
        system.exit()

    dirty = False

    if be(1):
        ci = (ci + 1) % len(colors)
        buzzer.click()
        dirty = True

    if be(2):
        display.clear(BLACK)
        buzzer.click()
        dirty = True

    if be(4):
        si = (si + 1) % len(sizes)
        buzzer.click()
        dirty = True

    if touch.touching():
        p = touch.pos()
        if p:
            tx, ty = p
            if ty > TB:
                col = colors[ci]
                r = sizes[si]
                if was and lx >= 0:
                    display.line(lx, ly, tx, ty, col)
                    if r > 1:
                        draw_pt(lx, ly, col, r)
                        draw_pt(tx, ty, col, r)
                else:
                    draw_pt(tx, ty, col, r)
                lx = tx
                ly = ty
                was = True
                dirty = True
    else:
        if was:
            was = False
            lx = -1
            ly = -1

    if dirty:
        toolbar()
        display.flush()

    fr += 1
    if fr % 60 == 0:
        gc.collect()
    time.sleep_ms(16)
