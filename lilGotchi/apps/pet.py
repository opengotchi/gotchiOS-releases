import display as D,touch,buttons as B,system,time,gc,buzzer as Z,imu,math
_rs=time.ticks_us()
def _rn():
 global _rs;_rs=(_rs*1103515245+12345)&0x7FFFFFFF;return _rs
def ri(a,b):return a+_rn()%(b-a+1)
C=D.color;cf=D.circle_filled;rf=D.rect_filled;dl=D.line;dt=D.text
BG=C(30,30,50);SK=C(255,220,180);W=C(255,255,255);K=C(0,0,0)
PK=C(255,150,180);G=C(80,220,80);Y=C(255,220,0);R=C(255,60,60)
BL=C(100,150,255)
hu=50;ha=50;en=50;st=0;bk=0;fr=0;sl=False;ex=0;lt=time.ticks_ms()
P='/littlefs/config/pet.txt'
def load():
 global hu,ha,en
 d=system.readfile(P)
 if d:
  p=d.strip().split(',')
  if len(p)==3:hu=int(p[0]);ha=int(p[1]);en=int(p[2])
def save():system.writefile(P,'%d,%d,%d'%(hu,ha,en))
def cl(v):return max(0,min(100,v))
def mood():
 if sl:return 0
 a=(hu+ha+en)//3
 if ex>0:return 4
 if a>70:return 3
 if a>35:return 2
 return 1
def bar(x,y,w,h,v):
 rf(x,y,w,h,K);c=G if v>60 else Y if v>30 else R
 rf(x+1,y+1,max(1,(w-2)*v//100),h-2,c)
def eyes_closed(cx,cy):dl(cx-15,cy-8,cx-7,cy-8,K);dl(cx+7,cy-8,cx+15,cy-8,K)
def eyes_open(cx,cy):cf(cx-12,cy-8,4,K);cf(cx+12,cy-8,4,K)
def face(cx,cy,m):
 cf(cx,cy,40,SK)
 cf(cx-25,cy+10,8,PK);cf(cx+25,cy+10,8,PK)
 cf(cx-35,cy-30,10,SK);cf(cx+35,cy-30,10,SK)
 cf(cx-35,cy-30,5,PK);cf(cx+35,cy-30,5,PK)
 if m==0:
  eyes_closed(cx,cy)
  dt(cx+30,cy-35,'Z',2,W);dt(cx+42,cy-50,'z',1,W)
  dl(cx-5,cy+15,cx+5,cy+15,K)
 elif m==4:
  cf(cx-12,cy-8,5,W);cf(cx+12,cy-8,5,W)
  cf(cx-12,cy-8,2,K);cf(cx+12,cy-8,2,K)
  dl(cx-12,cy+12,cx,cy+20,K);dl(cx,cy+20,cx+12,cy+12,K)
 elif m==3:
  if bk>0:eyes_closed(cx,cy)
  else:eyes_open(cx,cy);cf(cx-10,cy-9,1,W);cf(cx+14,cy-9,1,W)
  for i in range(-10,11):rf(cx+i,cy+14+abs(i)//3,1,1,K)
 elif m==1:
  eyes_open(cx,cy);cf(cx-12,cy+2,2,BL)
  for i in range(-8,9):rf(cx+i,cy+20-abs(i)//3,1,1,K)
 else:
  if bk>0:eyes_closed(cx,cy)
  else:eyes_open(cx,cy)
  dl(cx-6,cy+15,cx+6,cy+15,K)
load()
while True:
 lt=time.ticks_ms()
 sw=touch.swipe()
 if sw=='left' or B.pressed(4):save();system.exit()
 if B.pressed(1):hu=cl(hu+15);Z.beep();save()
 if B.pressed(2):ha=cl(ha+15);en=cl(en-5);Z.click();save()
 if B.pressed(3):sl=True;st=0;Z.click();save()
 try:
  ax,ay,az=imu.accel();mg=math.sqrt(ax*ax+ay*ay+az*az)
  if mg>2.0 and not sl:ex=30;ha=cl(ha+5);Z.tone(800,50)
 except:pass
 if sl:
  if fr%10==0:en=cl(en+1)
  st+=1
  if en>=100 or st>300:sl=False;st=0
 if fr%120==0 and not sl:hu=cl(hu-2);ha=cl(ha-1);en=cl(en-1)
 if fr%60==0 and ri(0,3)==0:bk=8
 if bk>0:bk-=1
 if ex>0:ex-=1
 by=int(math.sin(fr*0.08)*3)if not sl else 0
 D.clear(BG);dt(90,5,'My Gotchi',2,W)
 face(140,90+by,mood())
 dt(15,195,'HNG',1,W);bar(50,195,60,12,hu)
 dt(120,195,'HAP',1,W);bar(155,195,60,12,ha)
 dt(225,195,'NRG',1,W);bar(225,208,45,12,en)
 dt(5,225,'B1:Feed',1,G);dt(95,225,'B2:Play',1,Y)
 dt(185,225,'B3:Nap',1,BL)
 D.flush();fr+=1
 if fr%60==0:gc.collect()
 time.sleep_ms(33)
