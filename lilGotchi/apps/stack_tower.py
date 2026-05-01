import display, touch, buttons, buzzer, system, time, gc

W = display.WIDTH
H = display.HEIGHT
c = display.color
BK=c(0,0,0); WH=c(255,255,255); GR=c(50,50,60)
DG=c(25,25,35); YL=c(255,220,0); RD=c(255,50,50)

_rs=time.ticks_us()
def _rn():
    global _rs
    _rs=(_rs*1103515245+12345)&0x7FFFFFFF
    return _rs
def ri(a,b): return a+_rn()%(b-a+1)

def hue(n):
    h = (n * 37) % 360
    s = 0.8; v = 0.9
    hi = int(h/60) % 6
    f = h/60 - int(h/60)
    p = v*(1-s); q = v*(1-f*s); t = v*(1-(1-f)*s)
    r,g,b = [(v,t,p),(q,v,p),(p,v,t),(p,q,v),(t,p,v),(v,p,q)][hi]
    return c(int(r*255),int(g*255),int(b*255))

# game state
BH = 12  # block height
base_w = 120
blocks = []  # (x, w, color)
cur_x = 0.0
cur_w = base_w
cur_dir = 1
spd = 2.0
score = 0
best = 0
alive = True
cam_y = 0.0
perfect = 0

s = system.readfile('/littlefs/config/stack_best.txt')
if s:
    try: best = int(s.strip())
    except: pass

# base block
blocks.append((W//2 - base_w//2, base_w, hue(0)))
cur_x = 0.0
cur_w = base_w

_bp=[False]*4
def be(n):
    cu=buttons.pressed(n); h=cu and not _bp[n-1]; _bp[n-1]=cu; return h

def reset():
    global blocks, cur_x, cur_w, cur_dir, spd, score, alive, cam_y, perfect
    blocks = [(W//2-base_w//2, base_w, hue(0))]
    cur_x = 0.0; cur_w = base_w; cur_dir = 1
    spd = 2.0; score = 0; alive = True; cam_y = 0.0; perfect = 0

tp = False
fr = 0

while True:
    g = touch.gesture()
    if g == 'swipe_left' or g == 'long_press':
        system.exit()

    t = touch.touching() or buttons.any()
    te = t and not tp
    tp = t

    if not alive:
        display.clear(BK)
        display.text(W//2-50, 50, "GAME OVER", 2, RD)
        display.text(W//2-40, 90, "score: "+str(score), 1, WH)
        display.text(W//2-35, 115, "best: "+str(best), 1, YL)
        display.text(W//2-45, 160, "tap to retry", 1, GR)
        display.flush()
        if te: reset()
        time.sleep_ms(33)
        continue

    # move current block
    cur_x += spd * cur_dir
    if cur_x + cur_w > W:
        cur_dir = -1
    elif cur_x < 0:
        cur_dir = 1

    # drop
    if te:
        prev = blocks[-1]
        px = prev[0]; pw = prev[1]
        cx = int(cur_x)

        # calc overlap
        ol = max(0, min(cx+cur_w, px+pw) - max(cx, px))

        if ol <= 0:
            alive = False
            if score > best:
                best = score
                system.writefile('/littlefs/config/stack_best.txt', str(best))
            buzzer.tone(150, 200)
        else:
            nx = max(cx, px)
            # perfect detection
            if abs(ol - cur_w) < 3:
                ol = cur_w
                nx = px
                perfect += 1
                if perfect > 1:
                    buzzer.tone(500 + perfect*50, 60)
                else:
                    buzzer.click()
            else:
                perfect = 0
                buzzer.click()

            col = hue(len(blocks))
            blocks.append((nx, ol, col))
            score += 1
            cur_w = ol
            cur_x = 0.0 if cur_dir > 0 else float(W - ol)
            spd = min(5.0, 2.0 + score * 0.12)

            # camera follows
            target = max(0, len(blocks) * BH - (H - 60))
            cam_y = target

    # --- draw ---
    display.clear(BK)

    # draw blocks
    for i in range(len(blocks)):
        bx, bw, bc = blocks[i]
        by = H - 20 - (i+1)*BH + int(cam_y)
        if -BH < by < H:
            display.rect_filled(int(bx), by, int(bw), BH-1, bc)

    # draw moving block
    if alive:
        my = H - 20 - (len(blocks)+1)*BH + int(cam_y)
        col = hue(len(blocks))
        display.rect_filled(int(cur_x), my, int(cur_w), BH-1, col)

    # ground
    gy = H - 20 + int(cam_y)
    if gy < H:
        display.rect_filled(0, gy, W, 2, GR)

    # HUD
    display.rect_filled(0, 0, W, 16, DG)
    display.text(4, 2, str(score), 1, WH)
    if perfect > 1:
        display.text(W//2-20, 2, "x"+str(perfect)+"!", 1, YL)
    display.text(W-55, 2, "HI:"+str(best), 0, YL)

    display.flush()
    fr += 1
    if fr % 60 == 0: gc.collect()
    time.sleep_ms(16)
