import pygame
from pygame.locals import *
import os
import sys
import math
import random

pygame.font.init()
pygame.mixer.init()

W, H = 750,750
win = pygame.display.set_mode((W,H))
pygame.display.set_caption('Space Shooter')

red_plane=pygame.image.load(os.path.join("assets","pixel_ship_red_small.png"))
green_plane=pygame.image.load(os.path.join("assets","pixel_ship_green_small.png"))
blue_plane=pygame.image.load(os.path.join("assets","pixel_ship_blue_small.png"))

yellow_plane=pygame.image.load(os.path.join("assets","pixel_ship_yellow.png"))

red_laser=pygame.image.load(os.path.join("assets","pixel_laser_red.png"))
green_laser=pygame.image.load(os.path.join("assets","pixel_laser_green.png"))
blue_laser=pygame.image.load(os.path.join("assets","pixel_laser_blue.png"))
yellow_laser=pygame.image.load(os.path.join("assets","pixel_laser_yellow.png"))

bg=pygame.transform.scale(pygame.image.load(os.path.join("assets","bg.png")),(W,H))

music=pygame.mixer.music.load('SkyFire.ogg')
pygame.mixer.music.play(-1)

class Plane:
    cool_down=30
    def __init__(self,x,y,health=100):
        self.x=x
        self.y=y
        self.health=health
        self.plane_img=None
        self.laser_img=None
        self.lasers=[]
        self.counter=0

    def draw(self,surface):
        surface.blit(self.plane_img,(self.x,self.y))
        for laser in self.lasers:
            laser.draw(surface)

    def move_laser(self,vel,obj):
        self.cooldown()
        for laser in self.lasers:
            laser.move(vel)
            if laser.off_screen(H):
                self.lasers.remove(laser)
            elif laser.collision(obj):
                obj.health-=10
                self.lasers.remove(laser)
                    
    def cooldown(self):
        if self.counter>=self.cool_down:
            self.counter=0
        elif self.counter>0:
            self.counter+=1

    def shoot(self):
        if self.counter==0:
            laser=Laser(self.x,self.y,self.laser_img)
            self.lasers.append(laser)
            self.counter=1
            
    def get_width(self):
        return self.plane_img.get_width()
    def get_height(self):
        return self.plane_img.get_height()

class Player(Plane):
    def __init__(self,x,y,health=100):
        super().__init__(x,y,health)
        self.plane_img=yellow_plane
        self.laser_img=yellow_laser
        self.mask=pygame.mask.from_surface(self.plane_img)
        self.max_health=health
        vel=5

    def move_laser(self,vel,objs):
        self.cooldown()
        for laser in self.lasers:
            laser.move(vel)
            if laser.off_screen(H):
                self.lasers.remove(laser)
            else:
                for obj in objs:
                    if laser.collision(obj):
                        objs.remove(obj)
                        self.lasers.remove(laser)
    def draw(self,window):
        super().draw(window)
        self.healthbar(window)
    def healthbar(self,window):
        pygame.draw.rect(window,(255,0,0),(self.x,self.y+self.plane_img.get_height()+10,self.plane_img.get_width(),10))
        pygame.draw.rect(window,(0,255,0),(self.x,self.y+self.plane_img.get_height()+10,self.plane_img.get_width()*((self.health)/self.max_health),10))


         
class Enemy(Plane):
    c_map={
        "red":(red_plane,red_laser),
        "green":(green_plane,green_laser),
        "blue":(blue_plane,blue_laser)
        }
    def __init__(self,x,y,color,health=100):
        super().__init__(x,y,health)
        self.plane_img,self.laser_img=self.c_map[color]
        self.mask=pygame.mask.from_surface(self.plane_img)

    def shoot(self):
        if self.counter==0:
            laser=Laser(self.x-25,self.y,self.laser_img)
            self.lasers.append(laser)
            self.counter=1
    
    def move(self,vel):
        self.y+=vel

class Laser:
    def __init__(self,x,y,img):
        self.x=x
        self.y=y
        self.img=img
        self.mask=pygame.mask.from_surface(self.img)

    def draw(self,window):
        window.blit(self.img,(self.x,self.y))

    def move(self,vel):
        self.y+=vel

    def off_screen(self,height):
        return not(self.y<=height and self.y>=0)

    def collision(self,obj):
        return collide(self,obj)

def collide(obj1,obj2):
    os_x=obj2.x-obj1.x
    os_y=obj2.y-obj1.y
    return obj1.mask.overlap(obj2.mask,(os_x,os_y))!=None
        
def main():
    run=True
    level=0
    lives=3
    font=pygame.font.SysFont("comicsans",50)
    lost_f=pygame.font.SysFont("comicsans",150)
    e1=[]
    wave_l=5
    e_vel=1
    p_vel=5
    l_vel=5
    lost=False
    lost_count=0
    bgx=bg.get_height()
    bgx1=0
    clock=pygame.time.Clock()
    p1=Player(300,630)
    def redraw_win():
        win.blit(bg,(0,bgx))
        win.blit(bg,(0,bgx1))
        live_label=font.render("Lives: "+str(lives),1,(255,255,255))
        level_label=font.render("Level: "+str(level),1,(255,255,255))
        win.blit(live_label,(10,10))
        win.blit(level_label,(W-level_label.get_width()-10,10))
        for en in e1:
            en.draw(win)
        p1.draw(win)

        if lost:
            lost_l=lost_f.render("You Lost!!!",1,(255,255,255))
            win.blit(lost_l,(W/2-lost_l.get_width()/2,350))
            
        pygame.display.update()
    while run:
        clock.tick(60)
        bgx-=1.6
        bgx1-=1.6
        if bgx<bg.get_height()*-1:
            bgx=bg.get_height()
        if bgx1<bg.get_height()*-1:
            bgx1=bg.get_height()
        redraw_win()
        
        if lives!=0:
            if p1.health<=0:
                lives-=1
        if lives<=0:
            lost=True
            lost_count+=1
        if lost:
            if lost_count>180:
                run=False
            else:
                continue
        
        if len(e1)==0:
            level+=1
            wave_l+=5
            for i in range(wave_l):
                en=Enemy(random.randrange(50,W-100),random.randrange(-1500,-100),random.choice(["red", "blue", "green"]))
                e1.append(en)
        for e in pygame.event.get():
            if e.type==pygame.QUIT:
                quit()
        k=pygame.key.get_pressed()
        if k[pygame.K_LEFT] and p1.x-p_vel>0:
            p1.x-=p_vel
        if k[pygame.K_RIGHT] and p1.x+p_vel+p1.get_width()<W:
            p1.x+=p_vel
        if k[pygame.K_UP] and p1.y-p_vel>0:
            p1.y-=p_vel
        if k[pygame.K_DOWN] and p1.y+p_vel+p1.get_height()+20<H:
            p1.y+=p_vel
        if k[pygame.K_SPACE]:
            p1.shoot()

        for en in e1[:]:
            en.move(e_vel)
            en.move_laser(l_vel,p1)
            if random.randrange(0,2*60)==1:
                en.shoot()
            if collide(en,p1):
                p1.health-=10
                e1.remove(en)
            elif en.y+en.get_height()>H:
                lives-=1
                e1.remove(en)
            
        p1.move_laser(-l_vel,e1)
def main_menu():
    title_font=pygame.font.SysFont("comicsans",70)
    run=True
    while run:
        win.blit(bg,(0,bgx))
        win.blit(bg,(0,bgx1))
        tit_label=title_font.render("Press the mouse to begin..",1,(255,255,255))
        win.blit(tit_label,(W/2-tit_label.get_width()/2,350))
        for e in pygame.event.get():
            if e.type==pygame.QUIT:
                run=False
            if e.type==pygame.MOUSEBUTTONDOWN:
                main()
    pygame.quit()
main()
