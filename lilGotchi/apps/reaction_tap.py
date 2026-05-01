import display, touch, buttons, buzzer, system, time, gc

W = display.WIDTH
H = display.HEIGHT
c = display.color
BK = c(0,0,0)
WH = c(255,255,255)
RD = c(255,40,40)
GN = c(0,255,80)
YL = c(255,220,0)
GR = c(60,60,70)
DG = c(30,30,40)
PK = c(255,100,180)

IDLE=0; WAIT=1; GO=2; SHOW=3; EARLY=4
st = IDLE
best = 0
res = 0
w_start = 0
g_start = 0
w_dur = 0
rnd = 0
streak = 0

s = system.readfile('/littlefs/config/react_best.txt')
if s:
    try: best = int(s.strip())
    except: pass

import math
_rs=time.ticks_us()
def _rn():
    global _rs
    _rs=(_rs*1103515245+12345)&0x7FFFFFFF
    return _rs
def ri(a,b): return a+_rn()%(b-a+1)

def tc(y, t, sz, co):
    cw = [5,10,15][min(sz,2)]
    display.text(W//2 - (len(t)*cw)//2, y, t, sz, co)

fr = 0
tp = False

while True:
    g = touch.gesture()
    if g == 'swipe_left' or g == 'long_press':
        system.exit()
    t = touch.touching() or buttons.any()
    te = t and not tp
    tp = t
    now = time.ticks_ms()

    if st == IDLE:
        display.clear(DG)
        tc(50, "REACTION", 2, WH)
        tc(80, "TAP", 2, WH)
        if best > 0:
            tc(120, "BEST: " + str(best) + "ms", 1, YL)
        tc(160, "tap to start", 1, GR)
        display.flush()
        if te:
            st = WAIT; w_start = now
            w_dur = ri(1500, 5000)
            buzzer.click()

    elif st == WAIT:
        el = time.ticks_diff(now, w_start)
        display.clear(RD)
        tc(90, "WAIT...", 2, WH)
        tc(130, "don't tap yet", 1, WH)
        display.flush()
        if te:
            st = EARLY; streak = 0
            buzzer.tone(200, 100)
        if el >= w_dur:
            st = GO; g_start = now

    elif st == GO:
        el = time.ticks_diff(now, g_start)
        display.clear(GN)
        tc(70, "TAP!", 2, BK)
        tc(100, "NOW!", 2, BK)
        tc(150, str(el) + "ms", 1, BK)
        display.flush()
        if te:
            res = el; rnd += 1; streak += 1
            if best == 0 or res < best:
                best = res
                system.writefile('/littlefs/config/react_best.txt', str(best))
            st = SHOW; buzzer.beep()
        if el > 3000:
            res = 3000; streak = 0; st = SHOW

    elif st == SHOW:
        display.clear(DG)
        if res < 200: bg = GN; msg = "INSANE!"
        elif res < 300: bg = YL; msg = "FAST!"
        elif res < 500: bg = PK; msg = "OK"
        else: bg = RD; msg = "SLOW"
        tc(30, msg, 2, bg)
        tc(70, str(res) + "ms", 2, WH)
        tc(110, "best: " + str(best) + "ms", 1, YL)
        if streak > 1: tc(140, "streak: " + str(streak), 1, GN)
        tc(180, "round " + str(rnd), 0, GR)
        tc(200, "tap again", 1, GR)
        display.flush()
        if te:
            st = WAIT; w_start = now
            w_dur = ri(1500, 5000)
            buzzer.click()

    elif st == EARLY:
        display.clear(DG)
        tc(60, "TOO", 2, RD)
        tc(90, "EARLY!", 2, RD)
        tc(140, "wait for green", 1, GR)
        tc(175, "tap to retry", 1, GR)
        display.flush()
        if te:
            st = WAIT; w_start = now
            w_dur = ri(1500, 5000)
            buzzer.click()

    fr += 1
    if fr % 60 == 0: gc.collect()
    time.sleep_ms(16)
