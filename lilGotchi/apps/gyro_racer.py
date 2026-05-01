import display,touch,buttons,system,time,gc,buzzer,imu,math
W=display.WIDTH;H=display.HEIGHT;c=display.color
_rs=time.ticks_us()
def _rn():
    global _rs;_rs=(_rs*1103515245+12345)&0x7FFFFFFF;return _rs
def ri(a,b):return a+_rn()%(b-a+1)
BG=c(32,130,60);RD=c(60,60,65);WH=c(255,255,255);YL=c(255,220,0)
RE=c(220,40,30);CY=c(0,220,200);DK=c(40,40,44)
OR=c(255,140,0);GR=c(20,100,40);CC=c(200,30,20)
px=140;spd=3;sc=0;fu=100;fc=0
rcx=140;rw=120;cv=0;cvt=0
obs=[];my=0
def dcar(x,y,cl,w=18,h=28):
    display.rect_filled(x-w//2,y-h//2,w,h,cl)
    display.rect_filled(x-w//2+2,y-h//2+4,w-4,10,c(60,60,80))
    display.rect_filled(x-w//2,y+h//2-6,4,4,YL)
    display.rect_filled(x+w//2-4,y+h//2-6,4,4,YL)
def gover():
    buzzer.tone(200,300)
    display.rect_filled(40,80,200,80,DK)
    display.rect_filled(42,82,196,76,c(20,20,24))
    display.text(72,90,"GAME OVER",2,RE)
    display.text(80,115,"Score: "+str(sc),2,WH)
    display.text(68,138,"Tap to restart",1,CY)
    display.flush()
    while True:
        g=touch.gesture()
        if g=="swipe_left" or g=="long_press":system.exit()
        if g=="tap" or buttons.pressed(1):return
        time.sleep_ms(50)
def rst():
    global px,spd,sc,fu,fc,obs,rcx,rw,cv,cvt,my
    px=140;spd=3;sc=0;fu=100;fc=0
    rcx=140;rw=120;cv=0;cvt=0;obs=[];my=0
rst()
while True:
    g=touch.gesture()
    if g=="swipe_left" or g=="long_press":system.exit()
    ax,ay,az=imu.accel()
    px=int(px+ax*8)
    fc+=1;cvt+=1
    if cvt>60:cvt=0;cv=ri(-3,3)
    rcx=int(rcx+cv*0.3)
    if rcx<80:rcx=80;cv=abs(cv)
    if rcx>200:rcx=200;cv=-abs(cv)
    if fc%120==0 and spd<10:spd+=1
    rw=max(70,120-(spd-3)*5)
    rl=rcx-rw;rr=rcx+rw
    if px<rl+14:px=rl+14
    if px>rr-14:px=rr-14
    if fc%max(18,35-spd*2)==0:
        ot=0 if ri(0,5)>0 else 1
        obs.append([ri(rl+16,rr-16),-30,ot])
    i=len(obs)-1
    while i>=0:
        obs[i][1]+=spd+2
        if obs[i][1]>260:obs.pop(i)
        i-=1
    hit=False
    for o in obs:
        if o[1]>180 and o[1]<220 and abs(o[0]-px)<16:
            if o[2]==1:
                fu=min(100,fu+25);sc+=50
                buzzer.tone(800,60);o[1]=999
            else:hit=True;break
    if hit:gover();rst();continue
    if fc%30==0:fu-=1
    if fu<=0:gover();rst();continue
    sc+=spd
    display.clear(GR)
    display.rect_filled(rl,0,rw*2,H,RD)
    display.rect_filled(rl-3,0,3,H,WH)
    display.rect_filled(rr,0,3,H,WH)
    my=(my+(spd+2))%40;y=my-40
    while y<H:
        display.rect_filled(rcx-1,y,3,20,YL);y+=40
    ry=my-40
    while ry<H:
        display.rect_filled(rl-8,ry,5,8,WH)
        display.rect_filled(rr+3,ry,5,8,WH);ry+=40
    for o in obs:
        if o[1]<-30 or o[1]>250:continue
        if o[2]==0:
            dcar(o[0],o[1],c(ri(60,180),ri(60,180),ri(60,200)))
        else:
            display.circle_filled(o[0],o[1],8,CY)
            display.text(o[0]-4,o[1]-4,"F",1,DK)
    dcar(px,200,CC,20,30)
    if fc%4<2:
        display.circle_filled(px-4,218,2,c(180,180,180))
        display.circle_filled(px+4,220,2,c(150,150,150))
    display.rect_filled(0,0,W,18,c(0,0,0))
    display.text(4,2,"SPD:"+str(spd),1,OR)
    display.text(80,2,"SC:"+str(sc),1,WH)
    fb=max(0,fu);fcc=CY if fb>30 else RE
    display.text(180,2,"F:"+str(fb)+"%",1,fcc)
    bw=int(40*fb//100)
    display.rect_filled(230,4,42,10,DK)
    display.rect_filled(231,5,bw,8,fcc)
    display.flush()
    if fc%60==0:gc.collect()
    time.sleep_ms(33)
