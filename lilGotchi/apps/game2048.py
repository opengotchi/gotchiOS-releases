import display,touch,buttons,buzzer,system,time,gc,imu
W=display.WIDTH;H=display.HEIGHT;c=display.color
BK=c(0,0,0);WH=c(255,255,255);GR=c(80,80,90);DG=c(30,30,40)
YL=c(255,220,0);RD=c(255,60,60);SH=c(20,20,30)
TC={0:c(50,50,62),2:c(90,195,235),4:c(60,215,175),8:c(255,190,70),16:c(255,150,55),32:c(255,110,85),64:c(255,65,65),128:c(190,130,255),256:c(160,90,255),512:c(255,90,190),1024:c(255,55,140),2048:c(255,225,55)}
TX={0:DG,2:BK,4:BK,8:WH,16:WH,32:WH,64:WH,128:WH,256:WH,512:WH,1024:WH,2048:BK}
_rs=time.ticks_us()
def _rn():
 global _rs;_rs=(_rs*1103515245+12345)&0x7FFFFFFF;return _rs
def ri(a,b):return a+_rn()%(b-a+1)
GS=4;PD=5;CS=(H-30-PD*(GS+1))//GS;OY=28;OX=(W-GS*CS-PD*(GS+1))//2
bd=[];sc=0;bs=0;ok=True;won=False
s=system.readfile('/littlefs/config/2048_best.txt')
if s:
 try:bs=int(s.strip())
 except:pass
def nb():
 global bd,sc,ok,won;bd=[]
 for i in range(16):bd.append(0)
 sc=0;ok=True;won=False;spawn();spawn()
def spawn():
 e=[]
 for i in range(16):
  if bd[i]==0:e.append(i)
 if e:bd[e[ri(0,len(e)-1)]]=2 if ri(0,9)<9 else 4
def gg(x,y):return bd[y*GS+x]
def ss(x,y,v):bd[y*GS+x]=v
def mv(dx,dy):
 global sc;moved=False
 rng=range(GS-1,-1,-1) if dx==1 or dy==1 else range(GS)
 for _ in range(GS):
  for y in rng:
   for x in rng:
    v=gg(x,y)
    if v==0:continue
    nx=x+dx;ny=y+dy
    if 0<=nx<GS and 0<=ny<GS:
     if gg(nx,ny)==0:ss(nx,ny,v);ss(x,y,0);moved=True
     elif gg(nx,ny)==v:ss(nx,ny,v*2);ss(x,y,0);sc+=v*2;moved=True
 return moved
def can_mv():
 for i in range(16):
  if bd[i]==0:return True
 for y in range(GS):
  for x in range(GS):
   v=gg(x,y)
   if x+1<GS and gg(x+1,y)==v:return True
   if y+1<GS and gg(x,y+1)==v:return True
 return False
nb()
bp=[False]*4
def be(n):
 cu=buttons.pressed(n);h=cu and not bp[n-1];bp[n-1]=cu;return h
fr=0;twas=0;tcd=0;TH=0.55;BB=c(58,58,72)
while True:
 g=touch.gesture()
 if g=='swipe_left'or g=='long_press':system.exit()
 b1=be(1);b2=be(2);b3=be(3);b4=be(4)
 nw=time.ticks_ms()
 try:ax,ay,_=imu.accel()
 except:ax=0.0;ay=0.0
 td=0
 if abs(ax)>abs(ay):
  if ax>TH:td=4
  elif ax<-TH:td=3
 else:
  if ay>TH:td=1
  elif ay<-TH:td=2
 tf=False
 if td>0 and td!=twas and time.ticks_diff(nw,tcd)>300:tf=True;tcd=nw
 if abs(ax)<0.25 and abs(ay)<0.25:twas=0
 elif td>0:twas=td
 if not ok:
  display.clear(BK)
  display.rect_filled(W//2-68,44,136,124,c(40,40,55))
  display.rect(W//2-68,44,136,124,GR)
  display.text(W//2-50,55,"GAME OVER",2,RD)
  display.text(W//2-len(str(sc))*5,95,str(sc),1,WH)
  display.text(W//2-len(str(bs))*5,120,str(bs),1,YL)
  display.flush()
  if touch.touching()or buttons.any():time.sleep_ms(200);nb()
  time.sleep_ms(33);continue
 moved=False
 if b1:moved=mv(-1,0)
 elif b4:moved=mv(1,0)
 elif b2 or b3:moved=mv(0,-1)
 elif tf:
  if td==1:moved=mv(0,1)
  elif td==2:moved=mv(0,-1)
  elif td==3:moved=mv(-1,0)
  elif td==4:moved=mv(1,0)
 if moved:
  spawn();buzzer.click()
  if sc>bs:bs=sc;system.writefile('/littlefs/config/2048_best.txt',str(bs))
  if not can_mv():ok=False;buzzer.tone(150,200)
  if not won:
   for i in range(16):
    if bd[i]>=2048:won=True;buzzer.tone(800,100);break
 display.clear(c(35,35,48))
 display.rect_filled(0,0,W,24,c(45,45,60))
 display.line(0,24,W,24,c(70,70,90))
 display.text(4,4,"2048",1,c(90,200,240))
 display.text(70,4,str(sc),1,YL)
 ht="HI:"+str(bs)
 display.text(W-len(ht)*5-4,6,ht,0,c(120,120,140))
 bw=GS*CS+PD*(GS+1)
 display.rect_filled(OX,OY,bw,bw,BB)
 display.rect(OX,OY,bw,bw,c(75,75,95))
 for y in range(GS):
  for x in range(GS):
   v=gg(x,y);cx=OX+PD+x*(CS+PD);cy=OY+PD+y*(CS+PD)
   bg=TC.get(v,c(200,80,200))
   display.rect_filled(cx,cy,CS,CS,bg)
   if v>0:
    display.line(cx,cy,cx+CS-1,cy,WH)
    display.line(cx,cy,cx,cy+CS-1,WH)
    display.line(cx+1,cy+CS-1,cx+CS-1,cy+CS-1,SH)
    display.line(cx+CS-1,cy+1,cx+CS-1,cy+CS-1,SH)
    display.rect_filled(cx+1,cy+1,CS-2,CS-2,bg)
    t=str(v);fg=TX.get(v,WH)
    if v<100:display.text(cx+CS//2-len(t)*5,cy+CS//2-7,t,1,fg)
    elif v<1000:display.text(cx+CS//2-len(t)*4,cy+CS//2-5,t,0,fg)
    else:display.text(cx+2,cy+CS//2-4,t,0,fg)
 display.flush();fr+=1
 if fr%60==0:gc.collect()
 time.sleep_ms(33)
