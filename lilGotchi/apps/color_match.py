import display, touch, buttons, buzzer, system, time, gc

W = display.WIDTH
H = display.HEIGHT
c = display.color

BK = c(0, 0, 0); WH = c(255, 255, 255); GR = c(60, 60, 70)
DG = c(30, 30, 40)

# 4 colors mapped to 4 buttons
GAME_COLORS = [
    c(255, 60, 60),   # B1 = Red
    c(60, 200, 60),   # B2 = Green
    c(60, 100, 255),  # B3 = Blue
    c(255, 220, 50),  # B4 = Yellow
]
COLOR_NAMES = ['RED', 'GREEN', 'BLUE', 'YELLOW']
BTN_LABELS = ['B1', 'B2', 'B3', 'B4']

_rs = time.ticks_us()
def _rn():
    global _rs; _rs = (_rs * 1103515245 + 12345) & 0x7FFFFFFF; return _rs
def ri(a, b): return a + _rn() % (b - a + 1)

score = 0; best = 0; alive = True; streak = 0; max_streak = 0
round_t = 0; time_limit = 2000  # ms to respond
target = 0; shown_at = 0
result_msg = ''; result_t = 0; result_col = GR
mode = 0  # 0=show color, 1=wait input, 2=result flash

# trick mode: sometimes show color NAME in different color
trick = False; trick_name = 0

s = system.readfile('/littlefs/config/cmatch_best.txt')
if s:
    try: best = int(s.strip())
    except: pass

def new_round():
    global target, shown_at, mode, trick, trick_name, time_limit
    target = ri(0, 3)
    shown_at = time.ticks_ms()
    mode = 1
    # 30% chance of trick round after score 5
    trick = score > 5 and ri(0, 99) < 30
    if trick:
        # show a WRONG color name in the TARGET color
        trick_name = (target + ri(1, 3)) % 4
    # speed up over time
    time_limit = max(600, 2000 - score * 50)

def reset():
    global score, alive, streak, max_streak, mode
    score = 0; alive = True; streak = 0; max_streak = 0; mode = 0

reset()

_bp = [False] * 4
def be(n):
    cu = buttons.pressed(n); h = cu and not _bp[n - 1]; _bp[n - 1] = cu; return h

fr = 0
start_t = 0

while True:
    g = touch.gesture()
    if g == 'swipe_left' or g == 'long_press': system.exit()
    now = time.ticks_ms()
    b1 = be(1); b2 = be(2); b3 = be(3); b4 = be(4)

    if not alive:
        display.clear(BK)
        display.text(W // 2 - 50, 40, "GAME OVER", 2, c(255, 60, 60))
        display.text(W // 2 - 40, 85, "Score: " + str(score), 1, WH)
        display.text(W // 2 - 35, 110, "Best: " + str(best), 1, c(255, 220, 50))
        display.text(W // 2 - 45, 135, "Streak: " + str(max_streak), 1, c(0, 200, 255))

        # reaction time average would be nice but keep it simple
        display.text(W // 2 - 45, 180, "Tap to retry", 1, GR)
        display.flush()
        if touch.touching() or buttons.any():
            time.sleep_ms(250); reset()
        time.sleep_ms(33); continue

    # mode 0: pre-round (show instructions or countdown)
    if mode == 0:
        display.clear(BK)
        display.text(W // 2 - 55, 30, "COLOR MATCH", 1, WH)
        display.text(W // 2 - 60, 60, "Match the COLOR", 0, GR)
        display.text(W // 2 - 60, 75, "not the word!", 0, GR)

        # show button mappings
        for i in range(4):
            bx = 30 + i * 58
            display.rect_filled(bx, 110, 45, 30, GAME_COLORS[i])
            display.text(bx + 10, 118, BTN_LABELS[i], 0, BK)
            display.text(bx + 2, 145, COLOR_NAMES[i][:3], 0, GAME_COLORS[i])

        display.text(W // 2 - 50, 185, "Press any button", 0, WH)
        display.flush()
        if buttons.any() or touch.touching():
            time.sleep_ms(300)
            new_round()
        time.sleep_ms(33); continue

    # mode 1: showing color, waiting for input
    if mode == 1:
        elapsed = time.ticks_diff(now, shown_at)

        # timeout
        if elapsed > time_limit:
            alive = False
            if score > best:
                best = score
                system.writefile('/littlefs/config/cmatch_best.txt', str(best))
            buzzer.tone(150, 300)
            continue

        # check input
        pressed = -1
        if b1: pressed = 0
        elif b2: pressed = 1
        elif b3: pressed = 2
        elif b4: pressed = 3

        if pressed >= 0:
            if pressed == target:
                # correct!
                streak += 1
                if streak > max_streak: max_streak = streak
                pts = 1
                if streak >= 3: pts = 2
                if streak >= 6: pts = 3
                if streak >= 10: pts = 5
                # bonus for fast response
                if elapsed < 400: pts += 2
                elif elapsed < 700: pts += 1
                score += pts
                result_msg = '+' + str(pts)
                if streak >= 3: result_msg += ' x' + str(streak)
                result_col = c(0, 230, 80)
                result_t = now
                mode = 2
                buzzer.tone(600 + streak * 30, 40)
            else:
                # wrong!
                alive = False
                if score > best:
                    best = score
                    system.writefile('/littlefs/config/cmatch_best.txt', str(best))
                buzzer.tone(150, 300)
                continue

        # draw color screen
        display.clear(BK)

        # time bar (shrinking)
        bar_w = W * (time_limit - elapsed) // time_limit
        bar_col = c(0, 200, 80) if elapsed < time_limit // 2 else (
                  c(255, 200, 0) if elapsed < time_limit * 3 // 4 else c(255, 60, 60))
        display.rect_filled(0, 0, bar_w, 4, bar_col)

        # big color circle
        display.circle_filled(W // 2, H // 2 - 10, 60, GAME_COLORS[target])

        # trick: show wrong word in correct color
        if trick:
            txt = COLOR_NAMES[trick_name]
            display.text(W // 2 - len(txt) * 6, H // 2 - 15, txt, 1, BK)
        else:
            txt = COLOR_NAMES[target]
            display.text(W // 2 - len(txt) * 6, H // 2 - 15, txt, 1, BK)

        # score
        display.text(4, 8, str(score), 1, WH)
        if streak >= 3:
            display.text(W - 40, 8, 'x' + str(streak), 0, c(255, 220, 50))

        # button hints at bottom
        for i in range(4):
            bx = 20 + i * 62
            display.rect_filled(bx, H - 22, 40, 16, GAME_COLORS[i])
            display.text(bx + 10, H - 19, BTN_LABELS[i], 0, BK)

        display.flush()

    # mode 2: result flash
    if mode == 2:
        elapsed = time.ticks_diff(now, result_t)
        if elapsed < 400:
            display.clear(BK)
            display.text(W // 2 - len(result_msg) * 6, H // 2 - 10,
                        result_msg, 1, result_col)
            display.flush()
        else:
            new_round()

    fr += 1
    if fr % 60 == 0: gc.collect()
    time.sleep_ms(16)
