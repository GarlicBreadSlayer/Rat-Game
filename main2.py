import random
from math import atan2, degrees, sin, cos, pow
import pygame
import pygame.mixer

# Define some colors
BLACK = (0, 0, 0)
BLUE = (0, 0, 255)
GREEN = (0, 255, 0)
BLOOD_RED = (100, 0, 0)
WHITE = (255, 255, 255)
DARK_BLUE = (0, 9, 28)
DARK_GREY = (40,40,40)
DARK_RED = (150, 0, 0)

# Set the default size of the screen
DEFAULT_HEIGHT = 650
DEFAULT_WIDTH = 1100

# Other constants
MAX_BULLETS = 15
BULLETSPRITESPEED = 20
PLAYDOORPOSITION = 260
QUITDOORPOSITION = 760
SETTINGSDOORPOSITION = 510
DOOR_SPEED = 5
STARTING_LIVES = 5
WALKING_SPEED = 6
DOORHEIGHT = 188
DOORSPRITEHEIGHT = 108
SETTINGSHEIGHT = 250

def loadify(imgname):
  return pygame.image.load(imgname).convert_alpha()

def bubblesort(blitOrder):
  has_swapped = True
  num_of_iterations = 0
  while(has_swapped):
    has_swapped = False
    for i in range(len(blitOrder) - num_of_iterations - 1):
      if blitOrder[i].getRect().bottom > blitOrder[i+1].getRect().bottom:
        # Swap
        blitOrder[i], blitOrder[i+1] = blitOrder[i+1], blitOrder[i]
        has_swapped = True
    num_of_iterations += 1
  return blitOrder

class MasterSprite(pygame.sprite.Sprite):
  def __init__(self, imageFile, x=0, y=0):
    self.x = x
    self.y = y
    self.initialXY = (x,y)
    if str(imageFile) == imageFile:
      self.image = loadify(imageFile)
    else:
      self.image = imageFile
    self.rect=self.image.get_bounding_rect()
    self.rect.x=x
    self.rect.y=y
    self.displaySize=pygame.display.get_surface().get_size()
    self.width = self.rect.right - self.x
    self.height = self.rect.bottom - self.y

  def getHeight(self):
    return self.height

  def getRect(self):
    return self.rect

  def getSurface(self):
    return self.image

  def move(self):
    pass

  def setX(self, x):
    self.x = x
    self.rect.x = x

  def setXY(self,x,y):
    self.setX(x)
    self.setY(y)

  def setY(self, y):
    self.y = y
    self.rect.y = y

class Button(MasterSprite):
  def __init__(self,imageFile,x,y,l):
    super().__init__(imageFile,x,y)
    self.images = [self.image]
    self.images.append(loadify("data\door2.png"))
    self.images.append(loadify("data\door3.png"))
    self.images.append(loadify("data\door4.png"))
    self.imageToShow = 0
    self.counter = 0
    self.location = l
    self.initialXY = (x,y)
  
  def clicked(self,mousePos):
    if mousePos[0] >= self.rect.left and mousePos[0] <= self.rect.right:
      if mousePos[1] >= self.rect.top and mousePos[1] <= self.rect.bottom:
        return True
    return False

  def doorOpen(self):
    self.counter += 1
    if self.counter > DOOR_SPEED:
      self.imageToShow = (self.imageToShow + 1)
      self.counter = 0
      if self.imageToShow > 3:
        return True
      self.image = self.images[self.imageToShow]
    return False

  def getLocation(self):
    return self.location

class SettingsButton(Button):
  def __init__(self,x,y,l):
    super().__init__("data\door1.png",x,y,l)

class PlayButton(Button):
  def __init__(self,x,y,l):
    super().__init__("data\door1.png",x,y,l)

class QuitButton(Button):
  def __init__(self,x,y,l):
    super().__init__("data\door1.png",x,y,l)

class Slideswitchframe(MasterSprite):
  def __init__(self,x,y,l,handle,p):
    super().__init__("data\slideswitchframe.png",x,y)
    self.location = l
    self.position = int(p)
    self.handle = handle
    self.handle.setY(self.rect.bottom-self.position)

  def getLocation(self):
    return self.location

  def getPosition(self):
    return self.position

  def slide(self, s):
    self.position = self.position + int(s)
    if self.position > 92:
      self.position = 92
    if self.position < 18:
      self.position = 18
    self.handle.setY(self.rect.bottom-self.position)

  def getVolume(self):
    return round((self.position-18)/72,3)

class Slideswitchhandle(MasterSprite):
  def __init__(self,x,y,l):
    super().__init__("data\slideswitchhandle.png",x,y)
    self.location = l

  def getLocation(self):
    return self.location

class Player(MasterSprite):
  def __init__(self,x,y,hitboxtopleft,hitboxdimensions,weapon,location):
    super().__init__("data\character sprite front 1.png")
    self.images = [[self.image,loadify("data\character sprite front 2.png"),loadify("data\character sprite front 3.png")],[loadify("data\character sprite back 1.png"),loadify("data\character sprite back 2.png"), loadify("data\character sprite back 3.png")], [loadify("data\character sprite left 1.png"), loadify("data\character sprite left 2.png"), loadify("data\character sprite left 3.png")], [loadify("data\character sprite right 1.png"), loadify("data\character sprite right 2.png"), loadify("data\character sprite right 3.png")]]
    self.imageToShow1 = 0
    self.imageToShow2 = 0
    self.changeX = 0
    self.changeY = 0
    self.lives = STARTING_LIVES
    self.counter = 0
    self.location = location
    self.hitbox = pygame.Rect(hitboxtopleft,hitboxdimensions)
    self.hitboxposition = (x-self.hitbox.x,y-self.hitbox.y)
    self.setXY(x,y)
    self.initialXY = (x,y)
    self.weapon = weapon
    self.weaponPosition = (self.rect.centerx,self.rect.centery-20)
    self.bulletspeed = 10
    self.shootingPoint = (self.weaponPosition[0]+self.weapon.width,self.weaponPosition[1])
    self.shooting = False
    self.roomcount = 0

  def setLocation(self,l):
    pastLocation = self.location
    self.location = l
    if l.leftconnection == pastLocation:
      self.setXY(l.spawnFromLeft[0],l.spawnFromLeft[1])
    if l.rightconnection == pastLocation:
      self.setXY(l.spawnFromRight[0],l.spawnFromRight[1])
    if l.upconnection == pastLocation:
      self.setXY(l.spawnFromUp[0],l.spawnFromUp[1])
    else:
      self.setXY(l.spawnFromDown[0],l.spawnFromDown[1])

  def getLocation(self):
    return self.location

  def getHitbox(self):
    return self.hitbox

  def moveY(self, y):
    moveSize = 4
    self.changeY = y*moveSize

  def moveX(self, x):
    moveSize = 4
    self.changeX = x*moveSize

  def setXY(self, x, y):
    super().setXY(x,y)
    if self.rect.left < self.location.limits.left:
      self.setX(self.location.limits.left)
    if self.rect.right > self.location.limits.right:
      self.setX(self.location.limits.right-self.width)
    if self.rect.top < self.location.limits.top:
      self.setY(self.location.limits.top)
    if self.rect.bottom > self.location.limits.bottom:
      self.setY(self.location.limits.bottom-self.height)

  def update(self,objects,enemies):
    self.image = self.images[self.imageToShow1][self.imageToShow2]
    self.setXY(self.x+self.changeX, self.y+self.changeY)
    tempObjects = objects.copy()
    for enemy in enemies:
      if self.location in enemy.location:
        if enemy.playercollisions:
          tempObjects.append(enemy)
    for object in tempObjects:
      objectHitbox = object.getHitbox()
      if self.hitbox.colliderect(objectHitbox):
        if self.hitbox.top < objectHitbox.bottom and self.hitbox.bottom > objectHitbox.bottom and (objectHitbox.bottom - self.hitbox.top < 5): #moving up
          self.setY(objectHitbox.bottom+self.hitboxposition[1])
        if self.hitbox.bottom > objectHitbox.top and self.hitbox.top < objectHitbox.top and (self.hitbox.bottom - objectHitbox.top < 5): #moving down
          self.setY(objectHitbox.top-self.height)
        if self.hitbox.left < objectHitbox.right and self.hitbox.right > objectHitbox.right and (objectHitbox.right - self.hitbox.left < 5): #moving left
          self.setX(objectHitbox.right)
        if self.hitbox.right > objectHitbox.left and self.hitbox.left < objectHitbox.left and (self.hitbox.right - objectHitbox.left < 5): #moving right
          self.setX(objectHitbox.left-self.width)
    #set xy weapons
    mousePosition = pygame.mouse.get_pos()
    if self.weapon != "none":
      if mousePosition[0]-self.rect.centerx > 0:
        self.weaponPosition = (self.rect.centerx,self.rect.centery-20)
      elif mousePosition[0]-self.rect.centerx <= 0:
        self.weaponPosition = (self.rect.centerx-self.weapon.width,self.rect.centery-20)
      self.weapon.setXY(self.weaponPosition[0],self.weaponPosition[1])
      #rotate weapons
      self.weapon.angle = degrees(atan2(self.weapon.rect.centery- mousePosition[1], self.weapon.rect.centerx-mousePosition[0]))+180
      if mousePosition[0]-self.rect.centerx <= 0:
        self.weapon.imageToShow = 1
        self.weapon.angle += -180
      else:
        self.weapon.imageToShow = 0
      self.weapon.image = self.weapon.images[self.weapon.imageToShow]
      self.weapon.rect = (pygame.transform.rotate(self.weapon.image, -self.weapon.angle)).get_bounding_rect()
      self.weapon.rect.x = self.weapon.x
      if self.weapon.imageToShow == 1:
        if self.weapon.angle < 0:
          self.weapon.rect.y = self.weapon.y
          self.shootingPoint = (self.weapon.rect.bottomleft)
        else:
          self.weapon.rect.y = self.weapon.y + (18-self.weapon.rect.height)
          self.shootingPoint = (self.weapon.rect.topleft)
      elif self.weapon.imageToShow == 0:
        if self.weapon.angle < 180:
          self.weapon.rect.y = self.weapon.y
          self.shootingPoint = (self.weapon.rect.bottomright)
        else:
          self.weapon.rect.y = self.weapon.y + (18-self.weapon.rect.height)
          self.shootingPoint = (self.weapon.rect.topright)

  def reset(self):
    self.lives = STARTING_LIVES
    self.changeX = 0
    self.changeY = 0

  def resetRoom(self,room,components):
    room.setXY(room.initialXY[0],room.initialXY[1])
    for c in components:
      for o in c:
        if o.__class__.__name__ != "Bullet" and Bullet not in o.__class__.__bases__:
          if room in o.location:
            if o.__class__.__name__ == "Slideswitchhandle":
              o.setX(o.initialXY[0])
            elif o.__class__.__name__ == "Spikeball":
              o.pointReset()
              o.setXY(o.initialXY[0],o.initialXY[1])
            else:
              o.setXY(o.initialXY[0],o.initialXY[1])

  def movingright(self):
    self.imageToShow1 = 3

  def movingleft(self):
    self.imageToShow1 = 2

  def movingdown(self):
    self.imageToShow1 = 0

  def movingup(self):
    self.imageToShow1 = 1
    '''    
    if self.leftWeapon != "none":
      self.leftPosition = (self.rect.left+(self.leftWeapon.width/2)-5, self.rect.top+35-self.leftWeapon.height)
    if self.rightWeapon != "none":
      self.rightPosition = (self.rect.right-self.rightWeapon.width+(self.rightWeapon.width/2)-5, self.rect.top+35-self.rightWeapon.height)
    '''

  def moving(self):
    self.counter +=1
    if self.counter>4*WALKING_SPEED:
      self.counter = 0
    self.imageToShow2 = 0
    if self.counter > WALKING_SPEED:
      self.imageToShow2 = 1
    if self.counter > 2*WALKING_SPEED:
      self.imageToShow2 = 0
    if self.counter > 3*WALKING_SPEED:
      self.imageToShow2 = 2

  def setX(self,x):
    super().setX(x)
    self.hitbox.x = x - self.hitboxposition[0]

  def setY(self,y):
    super().setY(y)
    self.hitbox.y = y - self.hitboxposition[1]

  def Attack(self,mouseX,mouseY):
    self.weapon.attack(mouseX,mouseY,self.weaponPosition)

class Weapon(MasterSprite):
  def __init__(self,imageFile):
    super().__init__(imageFile)
    self.angle = 0
    self.reloadtime = 30
    self.reloadcount = 0
    self.attacktime = 20
    self.attackcount = 0
    self.images = [self.image,self.image]
    self.imageToShow = 0
    self.imageToShow = 0
    self.reloadtime = 30
    self.attacktime = 12

  def attack(self,lastbullet):
    print("x")
  
  def reloading(self):
    self.reloadcount = self.reloadcount + 1
    if self.reloadcount > self.reloadtime:
      return False
    return True

  def attacktimer(self):
    self.attackcount += 1
    if self.attackcount >= self.attacktime:
      self.attackcount = 0
      return True
    return False

class Pistol(Weapon):
  def __init__(self):
    super().__init__("data\\pistol1.png")
    self.images = [self.image, loadify("data\pistol2.png")]
    self.imageToShow = 0
    self.reloadtime = 30
    self.attacktime = 12

  def attack(self,lastbullet):
    self.reloadcount = 0
    if self.imageToShow == 1:
      lastbullet.angle = self.angle

class Monster(MasterSprite):
  def __init__(self, imageFile, x, y, h, l, playercollisions):
    super().__init__(imageFile,x,y)
    self.changeX = 0
    self.changeY = 0
    self.lives = h
    self.startingLives = h
    self.counter = 0
    self.location = l
    self.reloadcount = 0
    self.reloadtime = 60
    self.shootingpoint = self.rect.centerx, self.rect.centery
    self.bulletspeed = 2
    self.hitbox = self.rect
    self.hitboxposition = (x-self.hitbox.x,y-self.hitbox.y)
    self.setXY(x, y)
    self.initialXY = (x,y)
    self.startingXY = (x,y)
    self.playercollisions = playercollisions
    self.deadcount = -100

  def setLocation(self, l):
    self.location = l

  def getLocation(self):
    return self.location

  def getHitbox(self):
    return self.hitbox

  def moveY(self, y):
    moveSize = 4
    self.changeY = y * moveSize

  def moveX(self, x):
    moveSize = 4
    self.changeX = x * moveSize

  def update(self,playerx,background,objects,player):
    self.setXY(self.x + self.changeX, self.y + self.changeY)
    if self.rect.left < background.rect.left:
      self.setX(background.rect.left)
    if self.rect.right > background.rect.right:
      self.setX(background.rect.right - self.width)
    if self.rect.top < background.rect.top:
      self.setY(background.rect.top)
    if self.rect.bottom > background.rect.bottom:
      self.setY(background.rect.bottom- self.height)
    tempObjects = objects.copy()
    if self.playercollisions and self.deadcount>0:
      tempObjects.append(player)
    for object in tempObjects:
      objectHitbox = object.getHitbox()
      if self.hitbox.colliderect(objectHitbox):
        if self.hitbox.top < objectHitbox.bottom and self.hitbox.bottom > objectHitbox.bottom and (objectHitbox.bottom - self.hitbox.top < 5): #moving up
          self.setY(objectHitbox.bottom+self.hitboxposition[1])
        if self.hitbox.bottom > objectHitbox.top and self.hitbox.top < objectHitbox.top and (self.hitbox.bottom - objectHitbox.top < 5): #moving down
          self.setY(objectHitbox.top-self.height)
        if self.hitbox.left < objectHitbox.right and self.hitbox.right > objectHitbox.right and (objectHitbox.right - self.hitbox.left < 5): #moving left
          self.setX(objectHitbox.right)
        if self.hitbox.right > objectHitbox.left and self.hitbox.left < objectHitbox.left and (self.hitbox.right - objectHitbox.left < 5): #moving right
          self.setX(objectHitbox.left-self.width)

  def reloading(self):
    self.reloadcount = self.reloadcount + 1
    if self.reloadcount == 1:
      return False
    if self.reloadcount >= self.reloadtime:
      self.reloadcount = 0
    return True

  def move(self):
    pass

  def attack(self,lastbullet,playerx,playery):
    pass
  
  def setX(self,x):
    super().setX(x)
    self.hitbox.x = x - self.hitboxposition[0]

  def setY(self,y):
    super().setY(y)
    self.hitbox.y = y - self.hitboxposition[1]

class Spikeball(Monster):
  def __init__(self,l,point1,point2,speed):
    spikeballsurface = pygame.Surface((140,1544),pygame.SRCALPHA)
    spikeballsurface.blit(loadify("data\spikeball.png"),(0,1400))
    spikeballsurface.blit(loadify("data\spikeballchain.png"),(65,0))
    spikeballsurface.blit(loadify("data\spikeballchain.png"),(65,700))
    super().__init__(spikeballsurface,point1[0],point1[1]-1400,100,l,False)
    self.point1 = (point1[0],point1[1]-1400)
    self.point2 = (point2[0],point2[1]-1400)
    self.speed = speed
    self.forwards = True
    self.initialPoint1 = (point1[0],point1[1]-1400)
    self.initialPoint2 = (point2[0],point2[1]-1400)
    self.hitbox = pygame.Rect((point1[0]+10,point1[1]+44),(120,100))
    self.hitboxposition = (point1[0]-self.hitbox.x,point1[1]-1400-self.hitbox.y)
  
  def pointReset(self):
    self.point1,self.point2 = self.initialPoint1,self.initialPoint2
    self.forwards = True

  def changePoints(self,x,y):
    self.point1 = (self.point1[0]+x,self.point1[1]+y)
    self.point2 = (self.point2[0]+x,self.point2[1]+y)

  def update(self,playerx,background,objects,player):
    self.setXY(self.x + self.changeX, self.y + self.changeY)
      
  def move(self):
    if self.x < self.point1[0]+5 and self.x > self.point1[0]-5 and self.y < self.point1[1]+5 and self.y > self.point1[1]-5:
      if self.forwards == False:
        self.x,self.y = self.point1
      self.forwards = True
    if self.x < self.point2[0]+5 and self.x > self.point2[0]-5 and self.y < self.point2[1]+5 and self.y > self.point2[1]-5:
      if self.forwards:
        self.x,self.y = self.point2
      self.forwards = False
    if self.forwards:
      self.changeX = (self.point2[0] - self.point1[0])/self.speed
      self.changeY = (self.point2[1] - self.point1[1])/self.speed
    else:
      self.changeX = (self.point1[0] - self.point2[0])/self.speed
      self.changeY = (self.point1[1] - self.point2[1])/self.speed

class Turret(Monster):
  def __init__(self,x,y,l):
    super().__init__(loadify("data\\turretdownleft.png"),x,y,100,l,True)
    self.spritecount = 40
    self.hitbox = pygame.Rect((x,y+37),(69,40))
    self.hitboxposition = (x-self.hitbox.x,y-self.hitbox.y)
    self.images = [self.image,loadify("data\\turretdown.png"),loadify("data\\turretdownright.png"),loadify("data\\turretright.png"),loadify("data\\turretupright.png"),loadify("data\\turretup.png"),loadify("data\\turretupleft.png"),loadify("data\\turretleft.png")]
    self.shootingpoint = self.rect.bottomleft
    self.shootingpoints = [(self.rect.left,self.rect.bottom-50),(self.rect.centerx,self.rect.bottom),(self.rect.right,self.rect.bottom-50),(self.rect.right,self.rect.top+15),self.rect.topright,(self.rect.centerx,self.rect.top),self.rect.topleft,(self.rect.left,self.rect.top+15)]
    self.imageToShow = 0
    self.angle = -30
    self.bulletspeed = 4

  def update(self,playerx,background,objects,player):
    super().update(playerx,background,objects,player)
    self.spritecount -= 1
    self.shootingpoints = [(self.rect.left-24,self.rect.bottom-40),(self.rect.centerx,self.rect.bottom),(self.rect.right,self.rect.bottom-40),(self.rect.right,self.rect.top+8),(self.rect.right,self.rect.top-10),(self.rect.centerx,self.rect.top-20),(self.rect.left-24,self.rect.top-10),(self.rect.left-24,self.rect.top+8)]
    if self.spritecount <= 0:
      self.spritecount = 40
      self.imageToShow += 1
      if self.imageToShow == 1:
        self.angle = -90
      elif self.imageToShow == 2:
        self.angle = -150
      elif self.imageToShow == 3:
        self.angle = 180
      elif self.imageToShow == 4:
        self.angle = 155
      elif self.imageToShow == 5:
        self.angle = 90
      elif self.imageToShow == 6:
        self.angle = 25
      elif self.imageToShow == 7:
        self.angle = 0
      if self.imageToShow>len(self.images)-1:
        self.imageToShow = 0
        self.angle = -30
      self.image = self.images[self.imageToShow]
    self.shootingpoint = self.shootingpoints[self.imageToShow]

  def attack(self,lastbullet):
    lastbullet.angle = self.angle

class Rat(Monster):
  def __init__(self,x,y,h,l):
    super().__init__("data\\rat left.png",x,y,h,l,True)
    self.images = [self.image, loadify("data\\rat right.png"),loadify("data\\fallingratright.png"),loadify("data\\fallingratleft.png"),loadify("data\\deadratleft.png"),loadify("data\\deadratright.png")]
    self.reloadtime = 140
    self.reloadcount = random.randint(0,self.reloadtime)
    self.movecount = random.randint(0, 11)
    self.movetime = 12
    self.shootingpoint = self.rect.left,self.rect.top+32
    self.movespeed = 2
    self.direction1 = 0
    self.direction2 = 0
    self.accuracy = 20
    self.bulletspeed = 3
    self.hitbox = pygame.Rect((x,y+40),(48,30))
    self.hitboxposition = (x-self.hitbox.x,y-self.hitbox.y)
    self.deadcount = 10
    self.facingleft = True

  def update(self,playerx,background,objects,player):
    super().update(playerx,background,objects,player)
    if self.lives > 0:
      self.deadcount = 10
      if playerx < self.x:
        self.shootingpoint = self.rect.left, self.rect.top+32
        self.image = self.images[0]
        self.facingleft = True
      else:
        self.shootingpoint = self.rect.right, self.rect.top+32
        self.image = self.images[1]
        self.facingleft = False
    else:
      if self.deadcount > 0:
        if self.facingleft:
          self.image = self.images[3]
        else:
          self.image = self.images[2]
      else:
        if self.facingleft:
          self.image = self.images[4]
        else:
          self.image = self.images[5]
      self.deadcount -= 1
      if self.deadcount == -9:
        self.changeX = 0
        self.changeY = 0
      if self.deadcount == -10:
        self.initialXY = (self.x-background.rect.left,self.y-background.rect.top)

  def move(self):
    if self.reloadcount >= self.reloadtime - 5:
      self.direction1 = 0
      self.direction2 = 0
    elif self.reloadcount >= 5:
      self.movecount += 1
      if self.movecount >= self.movetime:
        self.movecount = 0
        self.direction1 = random.randint(-2,2)
        self.direction2 = random.randint(-2,2)
    self.changeX = self.direction1 * self.movespeed
    self.changeY = self.direction2 * self.movespeed

  def attack(self,lastbullet,playerx,playery):
    lastbullet.angle = degrees(atan2(self.shootingpoint[1]-playery, self.shootingpoint[0]-playerx))+random.randint(-self.accuracy,self.accuracy)

class FancyRat(Rat):
  def __init__(self,x,y,h,l):
   super().__init__(x,y,h,l)
   self.image = loadify("data\\fancy rat left.png")
   self.images = [self.image,loadify("data\\fancy rat right.png"),loadify("data\\fancy rat hatless left.png"),loadify("data\\fancy rat hatless right.png"),loadify("data\\fallingratright.png"),loadify("data\\fallingratleft.png"),loadify("data\\deadfancyratleft.png"),loadify("data\\deadfancyratright.png")]
   self.movetime = 50
   self.angryshootingpoint = self.rect.left,self.rect.top+5

  def move(self):
    if self.reloadcount >= self.reloadtime - 5:
      self.direction1 = 0
      self.direction2 = 0
    elif self.reloadcount >= 5:
      self.movecount += 1
      if self.movecount >= self.movetime:
        self.movecount = 0
        self.direction1 = random.randint(-1,1)
        self.direction2 = random.randint(-1,1)
    self.changeX = self.direction1 * self.movespeed
    self.changeY = self.direction2 * self.movespeed

  def update(self,playerx,background,objects,player):
    super().update(playerx,background,objects,player)
    if self.lives <= 0:
      if self.deadcount > 0:
        if self.facingleft:
          self.image = self.images[5]
        else:
          self.image = self.images[4]
      else:
        if self.facingleft:
          self.image = self.images[6]
        else:
          self.image = self.images[7]
    elif self.lives <= 2:
      self.reloadtime = 45
      if self.facingleft:
        self.image = self.images[2]
        self.angryshootingpoint = self.rect.left-6,self.rect.top+5
      else:
        self.image = self.images[3]
        self.angryshootingpoint = self.rect.right,self.rect.top+5
    elif self.lives > 2:
      self.reloadtime = 140

class Boss(Monster):
  def __init__(self,x,y,l):
    super().__init__("data\\bossfancyratleft2.png",x,y,40,l,True)
    self.images = [self.image,loadify("data\\bossfancyratright2.png"),loadify("data\\bossfancyratup.png")]
    self.movespeed = 3
    self.bulletspeed = 3
    self.accuracy = 40
    self.hitbox = pygame.Rect((x,y+80),(111,74))
    self.hitboxposition = (x-self.hitbox.x,y-self.hitbox.y)
    for location in self.location:
      self.fourpoints = [(location.x+300,location.y+300),(location.rect.right-300,location.y+300),(location.x+300,location.rect.bottom-300),(location.rect.right-300,location.rect.bottom-300)]
    self.aim = random.randint(0,3)
    self.vector = pygame.Vector2(-self.movespeed,0)
    self.reloadtime = 70
    self.hitbox = pygame.Rect((self.x+5,self.y+50),(101,104))
    self.hitboxposition = (x-self.hitbox.x,y-self.hitbox.y)
    self.minionspawned =  False
    self.pianoPosition = (self.x,self.y)
    self.shotguncount = 11

  def update(self,playerx,background,objects,player):
    super().update(playerx,background,objects,player)
    if self.lives > 30:
      self.image = self.images[2]
      self.pianoPosition = (background.x+540,background.y+40)
      self.hitbox = pygame.Rect((self.x+5,self.y+50),(101,104))
      self.hitboxposition = (self.x-self.hitbox.x,self.y-self.hitbox.y)
      self.minionspawned = False
    elif self.lives > 20 or (self.lives <= 10 and self.lives > 0):
      self.hitbox = pygame.Rect((self.x,self.y+50),(75,104))
      self.hitboxposition = (self.x-self.hitbox.x,self.y-self.hitbox.y)
      for location in self.location:
        self.fourpoints = [(location.x+300,location.y+300),(location.rect.right-300,location.y+300),(location.x+300,location.rect.bottom-300),(location.rect.right-300,location.rect.bottom-300)]
      if playerx < self.x:
        self.shootingpoint = self.rect.left, self.rect.top+50
        self.image = self.images[0]
      else:
        self.shootingpoint = self.rect.right, self.rect.top+50
        self.image = self.images[1]
      if self.lives > 20:
        self.shotguncount = 11
        self.reloadtime = 70
      else:
        self.shotguncount = 7
        self.reloadtime = 100
    elif self.lives > 10 or self.lives <= 0:
      self.pianoPosition = (background.x+540,background.y+40)
      self.image = self.images[2]
      self.hitbox = pygame.Rect((self.x,self.y+50),(75,104))
      self.hitboxposition = (self.x-self.hitbox.x,self.y-self.hitbox.y)

  def move(self):
    if self.lives > 30:
      if self.x < self.pianoPosition[0]+5 and self.x > self.pianoPosition[0]-5 and self.y < self.pianoPosition[1]+5 and self.y > self.pianoPosition[1]-5:
        self.changeX = 0
        self.changeY = 0
      else:
        self.angleToAim = degrees(atan2(self.y-self.pianoPosition[1], self.x-self.pianoPosition[0]))
        self.changeX = self.vector.rotate(self.angleToAim)[0]
        self.changeY = self.vector.rotate(self.angleToAim)[1]
    elif self.lives > 20 or (self.lives <= 10 and self.lives > 0):
      if self.x < self.fourpoints[self.aim][0]+5 and self.x > self.fourpoints[self.aim][0]-5 and self.y < self.fourpoints[self.aim][1]+5 and self.y > self.fourpoints[self.aim][1]-5:
        temp = self.aim
        while temp == self.aim:
          temp = random.randint(0,3)
        self.aim = temp
      self.angleToAim = degrees(atan2(self.y-self.fourpoints[self.aim][1], self.x-self.fourpoints[self.aim][0]))
      self.changeX = self.vector.rotate(self.angleToAim)[0]
      self.changeY = self.vector.rotate(self.angleToAim)[1]
    elif self.lives > 10:
      if self.x < self.pianoPosition[0]+5 and self.x > self.pianoPosition[0]-5 and self.y < self.pianoPosition[1]+5 and self.y > self.pianoPosition[1]-5:
        self.changeX = 0
        self.changeY = 0
      else:
        self.angleToAim = degrees(atan2(self.y-self.pianoPosition[1], self.x-self.pianoPosition[0]))
        self.changeX = self.vector.rotate(self.angleToAim)[0]
        self.changeY = self.vector.rotate(self.angleToAim)[1]

  def attack(self,lastbullet,playerx,playery):
    lastbullet.angle = degrees(atan2(self.shootingpoint[1]-playery, self.shootingpoint[0]-playerx))+random.randint(-self.accuracy,self.accuracy)

class WallGun(Monster):
  def __init__(self,x,y,l,facingdirection):
    super().__init__("data\\wallgunleft.png",x,y,100,l,False)
    self.facingdirection = facingdirection
    self.images = [self.image,loadify("data\\wallgunright.png"),loadify("data\\wallgunup.png"),loadify("data\\wallgundown.png")]
    self.image = self.images[self.facingdirection]
    self.bulletspeed = 2
    self.reloadcount = random.randint(1,1100)
    self.reloadtime = 1200
    self.shootingAngle = 0
    if self.facingdirection == 1:
      self.shootingAngle = 180
    elif self.facingdirection == 2:
      self.shootingAngle = 90
    elif self.facingdirection == 3:
      self.shootingAngle = -90

  def attack(self,lastbullet):
    lastbullet.angle = self.shootingAngle
    
class deadHat(Monster):
  def __init__(self,x,y,l,facingleft):
    super().__init__("data\\fancy rat hat left.png",x,y,0,l,False)
    self.images = [self.image,loadify("data\\fancy rat hat right.png")]
    self.deadcount = 60
    self.facingleft = facingleft

  def update(self,playerx,background,objects,player):
    super().update(playerx,background,objects,player)
    if self.deadcount == 30:
      self.facingleft = not self.facingleft
    if self.facingleft:
      self.image = self.images[0]
    else:
      self.image = self.images[1]
    if self.deadcount > 0:
      self.x = self.initialXY[0]+sin((self.deadcount/60)*3)*50
      self.y += 1
    self.deadcount -= 1
    if self.deadcount == -9:
      self.changeX = 0
      self.changeY = 0
    if self.deadcount == -10:
      self.initialXY = (self.x-background.rect.left,self.y-background.rect.top)

class Room(MasterSprite):
  #init   (0 surface,1 left,2 right,3 up,4 down,5-x,6-y,7 spawnFromLeft,8 spawnFromRight,9 spawnFromUp,10 spawnFromDown,11 limit topleft,12 limit dimensions)  -limit optional
  def __init__(self,*args):
    self.leftconnection = args[1]
    self.rightconnection = args[2]
    self.upconnection = args[3]
    self.downconnection = args[4]
    self.x = args[5]
    self.y = args[6]
    self.spawnFromDown = args[10] # spawn position when coming from downconnection
    self.spawnFromUp = args[9] 
    self.spawnFromLeft = args[7] # spawn position when coming from leftconnection
    self.spawnFromRight = args[8]
    self.image = args[0]
    self.rect=self.image.get_bounding_rect()
    self.rect.x=self.x
    self.rect.y=self.y
    self.width = self.rect.right - self.x
    self.height = self.rect.bottom - self.y
    self.initialXY = (self.x,self.y)
    if(len(args)>11):
      self.limits = pygame.Rect(args[11],args[12])
      self.limitposition = (args[11][0]-self.x,args[11][1]-self.y)
    else:
      self.limits = self.rect
      self.limitposition = (0,0)

  def addConnection(self,room,direction):
    if direction == "left":
      self.leftconnection = room
    if direction == "right":
      self.rightconnection = room
    if direction == "up":
      self.upconnection = room
    if direction == "down":
      self.downconnection = room

  def moveRoom(self,player,components,screen_width,screen_height):
    movedRoom = False
    if player.rect.right >= self.rect.right-5:
      if self.rightconnection != "none":
        player.resetRoom(self.rightconnection,components)
        player.setLocation(self.rightconnection)
        movedRoom = True
    if player.rect.left <= self.rect.left+5 and movedRoom == False:
      if self.leftconnection != "none":
        player.resetRoom(self.leftconnection,components)
        player.setLocation(self.leftconnection)
        movedRoom = True
    if player.rect.top <= self.rect.top+5 and movedRoom == False:
      if self.upconnection != "none":
        player.resetRoom(self.upconnection,components)
        player.setLocation(self.upconnection)
        movedRoom = True
    if player.rect.bottom >= self.rect.bottom-5 and movedRoom == False:
      if self.downconnection != "none":
        player.resetRoom(self.downconnection,components)
        player.setLocation(self.downconnection)
        movedRoom = True
    if movedRoom == True:
      if player.rect.right > screen_width:
        leftshift = player.x+player.width-screen_width
        player.setX(screen_width-(player.width+15))
        player.location.setX(player.location.x-leftshift)
        #player.location.limits.x = player.location.limits.x-leftshift
        for c in components:
          for o in c:
            if o.__class__.__name__ != "Bullet" and Bullet not in o.__class__.__bases__:
              if player.location in o.location:
                o.setX(o.x-leftshift)
                if o.__class__.__name__ == "Spikeball":
                  o.changePoints(-leftshift,0)
      if player.rect.bottom > screen_height:
        upshift = player.y+player.height-screen_height
        player.setY(screen_height-(player.height+15))
        player.location.setY(player.location.y-upshift)
        #player.location.limits.y = player.location.limits.y-upshift
        for c in components:
          for o in c:
            if o.__class__.__name__ != "Bullet" and Bullet not in o.__class__.__bases__:
              if player.location in o.location:
                if o.__class__.__name__ == "Spikeball":
                  o.changePoints(0,-upshift)
                o.setY(o.y-upshift)
    return movedRoom

  def setX(self,x):
    super().setX(x)
    self.limits.x = x + self.limitposition[0]

  def setY(self,y):
    super().setY(y)
    self.limits.y = y + self.limitposition[1]

  def __str__(self):
    return "Room"

class Trap(MasterSprite):
  def __init__(self,x,y,l):
    super().__init__("data\spiketrap1.png",x,y)
    self.location = l
    self.images = [self.image,loadify("data\spiketrap2.png")]
    self.reloadcount = 0
    self.reloadtime = 120
    self.attackcount = 0
    self.attacktime = 20
    self.imageToShow = 0
    self.reloading = False
    self.attacking = False
    self.setXY(x,y)
    self.initialXY = (x,y)
    self.playerDamaged = False

  def getLocation(self):
    return self.location

  def update(self,playerRect):
    playSound = False
    self.image = self.images[self.imageToShow]
    if self.getRect().colliderect(playerRect):
      self.attacking = True
    if self.attacking:
      self.attackcount += 1
      if self.attackcount >= self.attacktime:
        self.imageToShow = 1
        self.reloadcount = 0
        if not self.reloading:
          self.setY(self.y-5)
          playSound = True
        self.reloading = True
        self.attackcount = 0
        self.attacking = False
    if self.reloading:
      self.reloadcount += 1
      if self.reloadcount >= self.reloadtime:
        self.imageToShow = 0
        self.reloading = False
        self.playerDamaged = False
        self.setY(self.y+5)
    return playSound

class Object(MasterSprite):
  # init (self,x,y,imageFile,location,hitboxtopleft,hitboxdimensions) - hitbox optional
  def __init__(self,*args):
    super().__init__(args[2],args[0],args[1])
    self.location = args[3]
    if len(args)>4:
      self.hitbox = pygame.Rect(args[4],args[5])
    else:
      self.x = args[0]
      self.y = args[1]
      self.hitbox = self.getRect()
    self.hitboxposition = (args[0]-self.hitbox.x,args[1]-self.hitbox.y)
    self.setXY(args[0],args[1])
    self.initialXY = (args[0],args[1])

  def getHitbox(self):
    return self.hitbox

  def getLocation(self):
    return self.location

  def setX(self,x):
    super().setX(x)
    self.hitbox.x = x - self.hitboxposition[0]

  def setY(self,y):
    super().setY(y)
    self.hitbox.y = y - self.hitboxposition[1]

class Table(Object):
  def __init__(self,x,y,location):
    super().__init__(x,y,"data\\table.png",location,(x,y+32),(260,50))

class Chair(Object):
  def __init__(self,x,y,location,direction):
    super().__init__(x,y,"data\\chairleft.png",location,(x,y+60),(47,40))
    self.images = (self.image,loadify("data\\chairright.png"),loadify("data\\chairup.png"),loadify("data\\chairdown.png"))
    self.imageToShow = direction
    self.image = self.images[self.imageToShow]

class Wall(Object):
  def __init__(self,x,y,location):
    super().__init__(x,y,"data\wall2.png",location,(x,y+40),(100,100))

class HorizontalWall(Object):
  def __init__(self,x,y,location,length):
    super().__init__(x,y,"data\wall2.png",location,(x,y+40),(100,100))
    self.rect = pygame.Rect((x,y),(100*length,140))
    self.hitbox = pygame.Rect((x,y+40),(100*length,100))
    self.image = pygame.Surface(self.rect.size,pygame.SRCALPHA)
    for i in range(0,length):
      self.image.blit(loadify("data\wall2.png"),(99*i,0))

class VerticalWall(Object):
  def __init__(self,x,y,location,length):
    super().__init__(x,y,"data\wall2.png",location,(x,y+40),(100,100))
    self.rect = pygame.Rect((x,y),(100,140+(100*(length-1))))
    self.hitbox = pygame.Rect((x,y+40),(100,100*length))
    self.image = pygame.Surface(self.rect.size,pygame.SRCALPHA)
    for i in range(0,length):
      self.image.blit(loadify("data\wall2.png"),(0,(96*i)))

class MazeHorizontalWall(Object):
  def __init__(self,x,y,location,length):
    super().__init__(x,y,"data\cool rock.png",location,(x,y+40),(60,60))
    self.rect = pygame.Rect((x,y),(60*length,100))
    self.hitbox = pygame.Rect((x,y+40),(60*length,60))
    self.image = pygame.Surface(self.rect.size,pygame.SRCALPHA)
    for i in range(0,length):
      self.image.blit(loadify("data\cool rock.png"),(60*i,0))

class MazeVerticalWall(Object):
  def __init__(self,x,y,location,length):
    super().__init__(x,y,"data\cool rock.png",location,(x,y+40),(60,60))
    self.rect = pygame.Rect((x,y),(60,100+(60*(length-1))))
    self.hitbox = pygame.Rect((x,y+40),(60,60*length))
    self.image = pygame.Surface(self.rect.size,pygame.SRCALPHA)
    for i in range(0,length):
      self.image.blit(loadify("data\cool rock.png"),(0,(60*i)))
    
class Switch(Object):
  # init (self,state,x,y,location,hitboxtopleft,hitboxdimensions) - hitbox optional
  def __init__(self,state,*args):
    super().__init__(args[0],args[1],"data\switchon.png",args[2])
    self.state = state
    self.images = [self.image, loadify("data\switchoff.png")]

  def getState(self):
    return self.state

  def flipSwitch(self):
    self.state = not self.state
    if self.state == True:
      self.image = self.images[0]
    else:
      self.image = self.images[1]

  def getLocation(self):
    return self.location

class Bullet(MasterSprite):
  def __init__(self,imageFile,x,y,angle,bulletspeed,spritespeed,friendliness):
    super().__init__(imageFile,x,y)
    self.images = [self.image]
    self.images.append(loadify("data\pinkbullet2.png"))
    self.images.append(loadify("data\pinkbullet3.png"))
    self.images.append(loadify("data\pinkbullet4.png"))
    self.images.append(loadify("data\pinkbullet5.png"))
    self.images.append(loadify("data\\bluebullet1.png"))
    self.imageToShow = random.randint(0,len(self.images)-1)
    self.counter = 0
    self.setXY(x,y)
    self.initialXY = (x,y)
    self.speed = bulletspeed
    self.vector = pygame.Vector2(-bulletspeed, 0)
    self.changeX = -bulletspeed
    self.changeY = 0
    self.angle = angle
    self.friendly = friendliness
    self.spritespeed = spritespeed

  def update(self,background):
    self.changeX = self.vector.rotate(self.angle)[0]
    self.changeY = self.vector.rotate(self.angle)[1]
    self.rect = (pygame.transform.rotate(self.image, -self.angle)).get_bounding_rect()
    self.counter += 1
    if self.counter > self.spritespeed:
      self.imageToShow = (self.imageToShow + 1)
      if self.imageToShow>len(self.images)-1:
        self.imageToShow = 0
      self.image = self.images[self.imageToShow]
      self.counter = 0
    self.setXY(self.x+self.changeX,self.y+self.changeY)
    if self.rect.left < background.getRect().left or self.rect.top < background.getRect().top or self.rect.bottom > background.getRect().bottom or self.rect.right > background.getRect().right:
      return True
    return False

  def getAngle(self):
    return self.angle

class RatBullet(Bullet):
  def __init__(self,x,y,angle,bulletspeed):
    super().__init__("data\pinkbullet1.png",x,y,angle,bulletspeed,20,False)
    self.images = [self.image]
    self.images.append(loadify("data\pinkbullet2.png"))
    self.images.append(loadify("data\pinkbullet3.png"))
    self.images.append(loadify("data\pinkbullet4.png"))
    self.images.append(loadify("data\pinkbullet5.png"))
    self.imageToShow = random.randint(0,len(self.images)-1)

class PistolBullet(Bullet):
  def __init__(self,x,y,angle,bulletspeed):
    super().__init__("data\pistolbullet1.png",x,y,angle,bulletspeed,12,True)
    self.images = [self.image,loadify("data\pistolbullet2.png"),loadify("data\pistolbullet3.png")]
    self.imageToShow = random.randint(0,len(self.images)-1)

class TurretBullet(Bullet):
  def __init__(self,x,y,angle,bulletspeed):
    super().__init__("data\\bluebullet1.png",x,y,angle,bulletspeed,12,False)
    self.images = [self.image,loadify("data\\bluebullet2.png"),loadify("data\\bluebullet3.png"),loadify("data\\bluebullet4.png")]
    self.imageToShow = random.randint(0,len(self.images)-1)

class FancyBullet(Bullet):
  def __init__(self,x,y,angle,bulletspeed):
    super().__init__("data\\fancy rat bullet.png",x,y,angle,bulletspeed,12,False)
    self.images = [self.image,pygame.transform.rotate(self.image, -45),pygame.transform.rotate(self.image, -90),pygame.transform.rotate(self.image, -135),pygame.transform.rotate(self.image, -180),pygame.transform.rotate(self.image, -225),pygame.transform.rotate(self.image, -270),pygame.transform.rotate(self.image, -315)]
    self.imageToShow = 0

class AngryBullet(Bullet):
  def __init__(self,x,y,angle,bulletspeed):
    super().__init__("data\\angry man bullet.png",x,y,angle,bulletspeed,100,False)
    self.images = [self.image]

class WallGunBullet(Bullet):
  def __init__(self,x,y,angle,bulletspeed):
    super().__init__("data\\bigbullet1.png",x,y,angle,bulletspeed,15,False)
    self.images = [self.image,loadify("data\\bigbullet2.png"),loadify("data\\bigbullet3.png")]
    self.detonationTime = random.randint(120,800)

  def update(self,background):
    super().update(background)
    self.detonationTime -= 1

def main():
  #pre init music
  pygame.mixer.pre_init(44100,-16,2,2048)

  #start PyGame
  pygame.init()

  #open settings file to check fullscreen or not
  settingsfile = open("data\settings.txt","r")

  # Set the height and width of the screen
  screen_width,screen_height = DEFAULT_WIDTH,DEFAULT_HEIGHT
  size = [screen_width, screen_height]
  fullscreen = False
  if settingsfile.readline()[0:5]=="False":
    screen_width,screen_height = DEFAULT_WIDTH,DEFAULT_HEIGHT
    size = [screen_width, screen_height]
  else:
    screen_width,screen_height = pygame.display.Info().current_w, pygame.display.Info().current_h
    size = [screen_width, screen_height]
    fullscreen = True
  screen = pygame.display.set_mode(size)

  pygame.display.set_caption("Rat Game")

  icon = loadify("data\\rat icon 2.png")
  pygame.display.set_icon(icon)

  # Set up the fonts
  titleFont = pygame.font.Font("data\BleedingPixels.ttf", 30)
  deadFont = pygame.font.Font("data\BleedingPixels.ttf", 60)
  escapeFont = pygame.font.Font("data\BleedingPixels.ttf", 20)
  victoryFont = pygame.font.Font("data\CaslonAntique.ttf", 60)
  victoryFont2 = pygame.font.Font("data\CaslonAntique.ttf", 30)
  victoryFont3 = pygame.font.Font("data\CaslonAntique.ttf", 20)

  # Loop until the user clicks the close button.
  userQuit = False
  restart = False

  # highscore
  highscorefile = open("data\highscore.txt","r")
  highscore = int(highscorefile.read())
  score = 0

  #create the rooms
  #   menu rooms
  menubackground = pygame.Surface((2304,1422),pygame.SRCALPHA)
  menubackground.blit(loadify("data\\start screen background.png"),(0,0))
  menubackground.blit(loadify("data\\start screen background.png"),(1152,0))
  menubackground.blit(loadify("data\\woodfloor3.png"),(0,648))
  menubackground.blit(loadify("data\\woodfloor3.png"),(1152,648))
  startmenu = Room(menubackground,"none","none","none","none",0,0,(0,0),(0,0),(0,0),(370,480),(0,DOORHEIGHT+DOORSPRITEHEIGHT-70),(2304,1422-DOORHEIGHT-DOORSPRITEHEIGHT+70))
  settingsmenu = Room(menubackground,"none","none","none","none",0,0,(0,0),(0,0),(0,0),(370,480),(0,DOORHEIGHT+DOORSPRITEHEIGHT-70),(2304,1422-DOORHEIGHT-DOORSPRITEHEIGHT+70))
  #   trial start rooms
  trialstart = Room(loadify("data\\trialstart.png"),"none","none","none","none",0,0,(0,0),(0,0),(870,15),(570,480))
  trialstart2 = Room(loadify("data\\trialstart.png"),"none","none","none",trialstart,0,0,(0,0),(0,0),(870,15),(900,851))
  trialstart.addConnection(trialstart2,"up")
  trialstart3 = Room(loadify("data\\trialstart.png"),"none","none","none",trialstart2,0,0,(0,0),(0,0),(870,15),(900,851))
  trialstart2.addConnection(trialstart3,"up")
  #   trial corridor
  corridorbackground = pygame.Surface((200,1038),pygame.SRCALPHA)
  corridorbackground.blit(loadify("data\\trialcorridor.png"),(0,0))
  corridorbackground.blit(loadify("data\\trialcorridor.png"),(0,346))
  corridorbackground.blit(loadify("data\\trialcorridor.png"),(0,692))
  trialcorridor = Room(corridorbackground,"none","none","none",trialstart3,screen_width/2-100,0,(0,0),(0,0),(screen_width/2-10,15),(screen_width/2-10,953),(screen_width/2-83,0),(166,1038))
  trialstart3.addConnection(trialcorridor,"up")
  #   trial rat
  trialrat = Room(loadify("data\\trialstart.png"),"none","none","none",trialcorridor,0,0,(0,0),(0,0),(870,50),(900,851))
  trialcorridor.addConnection(trialrat,"up")
  #   trial spike trap rat room
  trialspikeratbackground = pygame.Surface((936,1900),pygame.SRCALPHA)
  trialspikeratbackground.blit(pygame.transform.rotate(loadify("data\\trialstart.png"),90),(0,0))
  trialspikerat = Room(trialspikeratbackground,"none","none","none",trialrat,screen_width/2-468,0,(0,0),(0,0),(screen_width/2-18,15),(screen_width/2-18,1815))
  trialrat.addConnection(trialspikerat,"up")
  #   spike ball corridor
  trialspikeballcorridor = Room(trialspikeratbackground,"none","none","none",trialspikerat,screen_width/2-468,0,(0,0),(0,0),(screen_width/2+301,15),(screen_width/2-418,1815))
  trialspikerat.addConnection(trialspikeballcorridor,"up")
  #   fancy rat room
  mazebackground = pygame.Surface((3800,1872),pygame.SRCALPHA)
  mazebackground.blit(loadify("data\\woodfloor3.png"),(0,0))
  mazebackground.blit(loadify("data\\woodfloor3.png"),(1499,0))
  mazebackground.blit(loadify("data\\woodfloor3.png"),(0,774))
  mazebackground.blit(loadify("data\\woodfloor3.png"),(1499,774))
  trialmaze = Room(mazebackground,"none","none","none",trialspikeballcorridor,0,0,(0,0),(0,0),(1850,50),(800,1790))
  trialspikeballcorridor.addConnection(trialmaze,"up")
  #    boss room
  bossbackground = pygame.Surface((1100,1100),pygame.SRCALPHA)
  for i in range(0,3):
    for j in range(0,3):
      bossbackground.blit(loadify("data\\bigbrickbackground.png"),(396*i,432*j))
  bossroom = Room(bossbackground,"none","none","none","none",screen_width/2-550,0,(0,0),(0,0),(screen_width/2-50,50),(screen_width/2-10,1015))
  trialmaze.addConnection(bossroom,"up")
  #   death room (mostly useless)
  deathroom = Room(loadify("data\start screen background.png"),"none","none","none","none",0,0,(0,0),(0,0),(0,0),(370,480))
  #   victory room (also mostly useless)
  victoryroom = Room(loadify("data\start screen background.png"),"none","none","none","none",0,0,(0,0),(0,0),(0,0),(370,480))

  #list of rooms where the player can attack and monsters are allowed
  gamerooms = (trialstart,trialstart2,trialstart3,trialcorridor,trialrat,trialmaze,trialspikerat,trialspikeballcorridor,bossroom)

  # Menu buttons
  playButton = PlayButton(PLAYDOORPOSITION,DOORHEIGHT,[startmenu])
  quitButton = QuitButton(QUITDOORPOSITION,DOORHEIGHT,[startmenu])
  settingsButton = SettingsButton(SETTINGSDOORPOSITION,DOORHEIGHT,[startmenu,settingsmenu])
  playDoorOpening = False
  quitDoorOpening = False
  settingsDoorOpening = False
  doors = [playButton,quitButton,settingsButton]

  #settings
  fullScreenSwitch = Switch(True,PLAYDOORPOSITION-200,SETTINGSHEIGHT,[settingsmenu])
  if not fullscreen:
    fullScreenSwitch.flipSwitch()
  musicSwitch = Switch(True,PLAYDOORPOSITION,SETTINGSHEIGHT,[settingsmenu])
  if settingsfile.readline()[0:5]=="False":
    musicSwitch.flipSwitch()

  volumeSwitchHandle = Slideswitchhandle(QUITDOORPOSITION-32,SETTINGSHEIGHT,[settingsmenu])
  volumeSwitch = Slideswitchframe(QUITDOORPOSITION-40,SETTINGSHEIGHT-80,[settingsmenu],volumeSwitchHandle,int(settingsfile.readline()[0:2]))

  soundVolumeSwitchHandle = Slideswitchhandle(QUITDOORPOSITION+78,SETTINGSHEIGHT,[settingsmenu])
  soundVolumeSwitch = Slideswitchframe(QUITDOORPOSITION+70,SETTINGSHEIGHT-80,[settingsmenu],soundVolumeSwitchHandle,int(settingsfile.readline()[0:2]))
  doorcreak = pygame.mixer.Sound("data\doorcreak.mp3")
  pistolshot = pygame.mixer.Sound("data\pistolshot.mp3")
  spiketrap = pygame.mixer.Sound("data\spiketrap.mp3")
  playerdamage = pygame.mixer.Sound("data\playerdamage.mp3")
  ratdamage = pygame.mixer.Sound("data\\ratdamage.mp3")
  ratdeath = pygame.mixer.Sound("data\\ratdeath.mp3")
  spikeballimpact = pygame.mixer.Sound("data\spikeballimpact.mp3")
  bossdeath = pygame.mixer.Sound("data\\bossdeath.mp3")
  sounds = [doorcreak,pistolshot,spiketrap,playerdamage,ratdamage,ratdeath,spikeballimpact,bossdeath]
  for s in sounds:
    pygame.mixer.Sound.set_volume(s,soundVolumeSwitch.getVolume())
  pygame.mixer.Sound.set_volume(pistolshot,soundVolumeSwitch.getVolume()/10)
  pygame.mixer.Sound.set_volume(spiketrap,soundVolumeSwitch.getVolume()/2)
  pygame.mixer.Sound.set_volume(ratdamage,soundVolumeSwitch.getVolume()/5)
  pygame.mixer.Sound.set_volume(ratdeath,soundVolumeSwitch.getVolume()/10)
  pygame.mixer.Sound.set_volume(spikeballimpact,soundVolumeSwitch.getVolume()/5)

  switches = [musicSwitch,volumeSwitch,soundVolumeSwitch,fullScreenSwitch]
  handles= [volumeSwitchHandle,soundVolumeSwitchHandle]
  settingsfile.close()

  #background music home screen
  pygame.mixer.init()
  pygame.mixer.music.load("data\\titlemusic.wav")
  pygame.mixer.music.set_volume(volumeSwitch.getVolume())
  if musicSwitch.getState():
    pygame.mixer.music.play(-1)

  # Used to manage how fast the screen updates
  clock = pygame.time.Clock()

  # Create the initial sprites for the player and weapons
  pistol = Pistol()
  player = Player(370,480,(370,525),(32,25),pistol,startmenu)
  bullets = []

  #create the enemies
  rat = Rat(trialrat.x+700,trialrat.y+300,2,[trialrat])
  rat2 = Rat(trialstart3.x+400,trialstart3.y+500,2,[trialstart3])
  ratboss = Boss(bossroom.x+540,bossroom.y+40,[bossroom])
  #   spike ball corridor
  spikeball1 = Spikeball([trialspikeballcorridor],(trialspikeballcorridor.rect.left+5,trialspikeballcorridor.rect.bottom-700),(trialspikeballcorridor.rect.right-145,trialspikeballcorridor.rect.bottom-700),80)
  spikeball2 = Spikeball([trialspikeballcorridor],(trialspikeballcorridor.rect.right-145,trialspikeballcorridor.rect.bottom-500),(trialspikeballcorridor.rect.left+5,trialspikeballcorridor.rect.bottom-300),80)
  spikeball3 = Spikeball([trialspikeballcorridor],(trialspikeballcorridor.rect.left+5,trialspikeballcorridor.rect.bottom-1200),(trialspikeballcorridor.rect.right-145,trialspikeballcorridor.rect.bottom-1200),100)
  spikeball4 = Spikeball([trialspikeballcorridor],(trialspikeballcorridor.rect.left+330,trialspikeballcorridor.rect.top+200),(trialspikeballcorridor.rect.right-145,trialspikeballcorridor.rect.top+200),90)
  spikeball5 = Spikeball([trialspikeballcorridor],(trialspikeballcorridor.rect.left+5,trialspikeballcorridor.rect.top+300),(trialspikeballcorridor.rect.right-300,trialspikeballcorridor.rect.top+800),120)
  turret1 = Turret(trialrat.rect.left+400,trialrat.rect.top+400,[trialrat,trialstart2])
  turret2 = Turret(trialrat.rect.right-400,trialrat.rect.bottom-400,[trialrat])
  turret3 = Turret(trialspikeballcorridor.rect.left+80,trialspikeballcorridor.rect.top+150,[trialspikeballcorridor])
  turret4 = Turret(trialspikeballcorridor.rect.right-150,trialspikeballcorridor.rect.centery,[trialspikeballcorridor])
  enemies = [rat,rat2,ratboss,spikeball1,spikeball2,spikeball3,spikeball4,spikeball5,turret1,turret2,turret3,turret4]
  for i in range(1,5):
    enemies.append(Rat(round(trialrat.x+700+(sin(i)*500),0),trialrat.y+300,2,[trialrat]))

  for i in range(1,25):
    enemies.append(Rat(round(trialspikerat.x+387+(sin(i)*420),0),round(trialspikerat.y+800+(cos(i)*600),0),1,[trialspikerat]))

  for i in range(1,11):
    enemies.append(WallGun(bossroom.rect.left,bossroom.rect.top+100*i,[bossroom],1))
    enemies.append(WallGun(bossroom.rect.right-27,bossroom.rect.top+100*i,[bossroom],0))
    enemies.append(WallGun(bossroom.rect.left+100*i,bossroom.rect.top,[bossroom],3))
    enemies.append(WallGun(bossroom.rect.left+100*i,bossroom.rect.bottom-27,[bossroom],2))

  deadEnemies = []

  topWall = HorizontalWall(trialstart.rect.left,trialstart.rect.top,[trialstart,trialstart2,trialstart3,trialrat],8)
  topWall2 = HorizontalWall(trialstart.rect.left+1000,trialstart.rect.top,[trialstart,trialstart2,trialstart3,trialrat],9)
  leftWall = VerticalWall(trialstart.rect.left,trialstart.rect.top,[trialstart,trialstart2,trialstart3,trialrat],10)
  rightWall = VerticalWall(trialstart.rect.right-100,trialstart.rect.top,[trialstart,trialstart2,trialstart3,trialrat],10)
  bottomWall = HorizontalWall(trialstart.rect.left,trialstart.rect.bottom-100,[trialstart,trialstart2,trialstart3,trialrat],8)
  bottomWall2 = HorizontalWall(trialstart.rect.left+1000,trialstart.rect.bottom-100,[trialstart,trialstart2,trialstart3,trialrat],9)

  #spikerat room obstacles
  rock1 = Object(trialspikerat.rect.left+200,trialspikerat.rect.bottom-400,"data\cool rock.png",[trialspikerat],(trialspikerat.rect.left+200,trialspikerat.rect.bottom-360),(60,60))
  rock2 = Object(trialspikerat.rect.right-260,trialspikerat.rect.bottom-800,"data\cool rock.png",[trialspikerat],(trialspikerat.rect.right-260,trialspikerat.rect.bottom-760),(60,60))
  rock3 = Object(trialspikerat.rect.left+200,trialspikerat.rect.bottom-1200,"data\cool rock.png",[trialspikerat],(trialspikerat.rect.left+200,trialspikerat.rect.bottom-1160),(60,60))
  rock4 = Object(trialspikerat.rect.right-260,trialspikerat.rect.bottom-1600,"data\cool rock.png",[trialspikerat],(trialspikerat.rect.right-260,trialspikerat.rect.bottom-1560),(60,60))
  rock5 = Object(trialspikerat.rect.left+400,trialspikerat.rect.bottom-950,"data\cool rock.png",[trialspikerat],(trialspikerat.rect.left+400,trialspikerat.rect.bottom-910),(60,60))
  rock6 = Object(trialspikerat.rect.left+340,trialspikerat.rect.bottom-950,"data\cool rock.png",[trialspikerat],(trialspikerat.rect.left+340,trialspikerat.rect.bottom-910),(60,60))
  rock7 = Object(trialspikerat.rect.left+460,trialspikerat.rect.bottom-950,"data\cool rock.png",[trialspikerat],(trialspikerat.rect.left+460,trialspikerat.rect.bottom-910),(60,60))
  rock8 = Object(trialspikerat.rect.left+520,trialspikerat.rect.bottom-950,"data\cool rock.png",[trialspikerat],(trialspikerat.rect.left+520,trialspikerat.rect.bottom-910),(60,60))
  rock9 = Object(trialspikerat.rect.left+580,trialspikerat.rect.bottom-950,"data\cool rock.png",[trialspikerat],(trialspikerat.rect.left+580,trialspikerat.rect.bottom-910),(60,60))

  #spikeballcorridor walls
  spikeballcorridorWall = MazeHorizontalWall(trialspikeballcorridor.rect.left,trialspikeballcorridor.rect.top-40,[trialspikeballcorridor],12)
  spikeballcorridorWall2 = MazeHorizontalWall(trialspikeballcorridor.rect.left+216,trialspikeballcorridor.rect.bottom-100,[trialspikeballcorridor],12)
  spikeballcorridorWall3 = MazeHorizontalWall(trialspikeballcorridor.rect.right-240,trialspikeballcorridor.rect.top+160,[trialspikeballcorridor],4)
  #maze walls
  mazeWallBottom1 = HorizontalWall(trialmaze.rect.left,trialmaze.rect.bottom-100,[trialmaze],7)
  mazeWallBottom2 = HorizontalWall(trialmaze.rect.left+900,trialmaze.rect.bottom-100,[trialmaze],29)
  mazeWallLeft = VerticalWall(trialmaze.rect.left,trialmaze.rect.top,[trialmaze],19)
  mazeWallRight = VerticalWall(trialmaze.rect.right-100,trialmaze.rect.top,[trialmaze],19)
  mazeWallTop1 = HorizontalWall(trialmaze.rect.left,trialmaze.rect.top,[trialmaze],18)
  mazeWallTop2 = HorizontalWall(trialmaze.rect.left+2000,trialmaze.rect.top,[trialmaze],18)
  #mazeWall1 = MazeVerticalWall(trialmaze.rect.left+640,trialmaze.rect.bottom-700,[trialmaze],10)

  #signs
  signMoving = Object(startmenu.x+700,startmenu.y+400,"data\startroomsign1.png",[startmenu],(startmenu.x+700,startmenu.y+476),(100,10))
  signShooting = Object(trialstart.x+800,trialstart.y+400,"data\startroomsign2.png",[trialstart],(trialstart.x+800,trialstart.y+476),(100,10))
  spacebarSign = Object(startmenu.x+850,startmenu.y+400,"data\\spacebarSign.png",[startmenu],(startmenu.x+850,startmenu.y+476),(100,10))
  turretSign = Object(trialstart2.x+800,trialstart2.y+400,"data\\turretSign.png",[trialstart2],(trialstart2.x+800,trialstart2.y+476),(100,10))
  ratSign = Object(trialstart3.x+800,trialstart3.y+400,"data\\ratSign.png",[trialstart3],(trialstart3.x+800,trialstart3.y+476),(100,10))
  volumeSign = Object(settingsmenu.x+850,settingsmenu.y+400,"data\\volumeSign.png",[settingsmenu],(settingsmenu.x+850,settingsmenu.y+476),(100,10))

  #bosspiano
  piano = Object(bossroom.x+500,bossroom.y+20,"data\\real piano.png",[bossroom],(bossroom.x+500,bossroom.y+67),(200,100))

  objects = [topWall,leftWall,rightWall,bottomWall,topWall2,bottomWall2,signMoving,signShooting,spacebarSign,turretSign,ratSign,volumeSign,mazeWallBottom1,mazeWallBottom2,mazeWallLeft,mazeWallRight,mazeWallTop1,mazeWallTop2,rock1,rock2,rock3,rock4,rock5,rock6,rock7,rock8,rock9,spikeballcorridorWall,spikeballcorridorWall2,spikeballcorridorWall3,piano]
  objectsOnScreen = []

  for j in range(0,2):
    for i in range(1,6):
      objects.append(Table(trialmaze.rect.left+500*i,trialmaze.rect.centery+400*j-300,[trialmaze]))
      enemies.append(FancyRat(trialmaze.rect.left+500*i+100,trialmaze.rect.centery+400*j-400,4,[trialmaze]))
      objects.append(Chair(trialmaze.rect.left+500*i-60,trialmaze.rect.centery+400*j-330,[trialmaze],1)) #left
      objects.append(Chair(trialmaze.rect.left+500*i+270,trialmaze.rect.centery+400*j-330,[trialmaze],0)) #right
      objects.append(Chair(trialmaze.rect.left+500*i+110,trialmaze.rect.centery+400*j-380,[trialmaze],3)) #top chair
      objects.append(Chair(trialmaze.rect.left+500*i+110,trialmaze.rect.centery+400*j-250,[trialmaze],2)) #bottom chair

  #create traps
  trap1 = Trap(trialspikerat.rect.left+250,trialspikerat.rect.top+500,[trialspikerat])
  trap2 = Trap(trialspikerat.rect.right-250,trialspikerat.rect.top+500,[trialspikerat])
  trap3 = Trap(trialspikerat.rect.left+300,trialspikerat.rect.bottom-600,[trialspikerat])
  trap4 = Trap(trialspikerat.rect.right-300,trialspikerat.rect.bottom-600,[trialspikerat])
  trap5 = Trap(trialspikeballcorridor.rect.right-300,trialspikeballcorridor.rect.bottom-100,[trialspikeballcorridor])
  trap6 = Trap(trialspikeballcorridor.rect.right-300,trialspikeballcorridor.rect.bottom-140,[trialspikeballcorridor])
  trap7 = Trap(trialspikeballcorridor.rect.right-300,trialspikeballcorridor.rect.bottom-180,[trialspikeballcorridor])

  traps = [trap1,trap2,trap3,trap4,trap5,trap6,trap7]
  for i in range(0,8):
    traps.append(Trap(trialspikeballcorridor.rect.left+300,trialspikeballcorridor.rect.bottom-1000+(i*40),[trialspikeballcorridor]))
    traps.append(Trap(trialspikeballcorridor.rect.left+360+(i*60),trialspikeballcorridor.rect.bottom-1000,[trialspikeballcorridor]))
    traps.append(Trap(trialspikeballcorridor.rect.left+360+(i*60),trialspikeballcorridor.rect.bottom-1040,[trialspikeballcorridor]))
    traps.append(Trap(trialspikeballcorridor.rect.left+400,trialspikeballcorridor.rect.top+60+(i*40),[trialspikeballcorridor]))
  for i in range(0,5):
    traps.append(Trap(trialspikeballcorridor.rect.left+576,trialspikeballcorridor.rect.top+100+(i*40),[trialspikeballcorridor]))
    traps.append(Trap(trialspikeballcorridor.rect.left+636+(i*60),trialspikeballcorridor.rect.top+300,[trialspikeballcorridor]))
    traps.append(Trap(trialspikeballcorridor.rect.left+(i*60),trialspikeballcorridor.rect.bottom-1200,[trialspikeballcorridor]))
  for i in range(0,4):
    traps.append(Trap(trialspikeballcorridor.rect.left+696+(i*60),trialspikeballcorridor.rect.top+260,[trialspikeballcorridor]))

  #create a list of lists which contains all the components on the screen
  components = [enemies,switches,doors,bullets,handles,objects,traps,deadEnemies]

  # set player moving variables to false
  movingup = False
  movingdown = False
  movingleft = False
  movingright = False

  # Create a main group for all the sprites to be rendered
  #renderSprites = pygame.sprite.Group()
  #player.add(renderSprites)
  movespeed = 4

  # -------- Main Program Loop -----------
  while not userQuit:

    # --- Event Processing
    for event in pygame.event.get():
      if event.type == pygame.QUIT:
        userQuit = True
      #check for player attack
      if player.weapon.reloadcount >= player.weapon.reloadtime:
        if event.type == pygame.MOUSEBUTTONDOWN:
          if event.button == 1:
            if not player.shooting:
              pygame.mixer.Sound.play(pistolshot)
              player.shooting = True
      #check for button presses
      if event.type == pygame.KEYDOWN:
        if event.key == pygame.K_w:
          movingup = True
        elif event.key == pygame.K_s:
          movingdown = True
        elif event.key == pygame.K_a:
          movingleft = True
        elif event.key == pygame.K_d:
          movingright = True
        elif event.key == pygame.K_j:
          player.setLocation(trialmaze)
        elif event.key == pygame.K_k:
          ratboss.lives = 1
        elif event.key == pygame.K_ESCAPE:
          player.setLocation(startmenu)
          player.resetRoom(startmenu,components)
          player.resetRoom(trialstart,components)
          playButton.image = playButton.images[0]
          settingsButton.image = settingsButton.images[0]
          if musicSwitch.getState():
            pygame.mixer.music.load("data\\titlemusic.wav")
            pygame.mixer.music.set_volume(volumeSwitch.getVolume())
            pygame.mixer.music.play(-1)
          score = 0
          player.reset()
          bullets = []
          for enemy in enemies:
            enemy.lives = enemy.startingLives
          for deadEnemy in deadEnemies:
            deadEnemy.lives = deadEnemy.startingLives
            deadEnemy.initialXY = deadEnemy.startingXY
            if deadEnemy.__class__.__name__ != "deadHat":
              enemies.append(deadEnemy)
          deadEnemies = []
        #check if open doors or flip switch
        elif event.key == pygame.K_SPACE:
          #play door
          if (player.getRect().colliderect(playButton.getRect()) and player.getLocation() in playButton.getLocation()):
            pygame.Rect.colliderect
            for bullet in bullets[:len(bullets) - 1]:
              bullets.remove(bullet)
              del bullet
            pygame.mixer.Sound.play(doorcreak)
            playDoorOpening = True
            if musicSwitch.getState():
              pygame.mixer.music.load("data\\sewer music.mp3")
              pygame.mixer.music.set_volume(volumeSwitch.getVolume())
              pygame.mixer.music.play(-1)
          #quit door
          elif (player.getRect().colliderect(quitButton.getRect()) and player.getLocation() in quitButton.getLocation()):
            pygame.mixer.Sound.play(doorcreak)
            quitDoorOpening = True
          #settings door
          elif (player.getRect().colliderect(settingsButton.getRect()) and player.getLocation() in settingsButton.getLocation()):
            pygame.mixer.Sound.play(doorcreak)
            settingsDoorOpening = True
          #settings switches
          for i in switches:
            if player.getLocation() in i.getLocation():
              if player.getRect().colliderect(i.getRect()):
                if i.__class__.__name__ != "Slideswitchframe":
                  i.flipSwitch()
                  if i == fullScreenSwitch:
                    restart = True
                    userQuit = True
        #settings slide switches
        if event.key == pygame.K_UP:
          for i in switches:
            if player.getLocation() in i.getLocation():
              if player.getRect().colliderect(i.getRect()):
                if i.__class__.__name__ == "Slideswitchframe":
                  i.slide(5)
        if event.key == pygame.K_DOWN:
          for i in switches:
            if player.getLocation() in i.getLocation():
              if player.getRect().colliderect(i.getRect()):
                if i.__class__.__name__ == "Slideswitchframe":
                  i.slide(-5)

      if event.type == pygame.KEYUP:
        if event.key in [pygame.K_w, pygame.K_s]:
          player.moveY(0)
          movingup = False
          movingdown = False
        if event.key in [pygame.K_a, pygame.K_d]:
          player.moveX(0)
          movingleft = False
          movingright = False

    #check what objects are on screen
    objectsOnScreen = []
    for object in objects:
      if player.getLocation() in object.getLocation():
        objectsOnScreen.append(object)

    components = [enemies,switches,doors,bullets,handles,objects,traps,deadEnemies]

    # player move animations and movement and also moving all the other components on the screen
    if movingdown == True:
      player.movingdown()
      if(player.getRect().bottom>screen_height-220 and player.location.getRect().bottom > screen_height):
        player.location.setY(player.location.y-movespeed)
        player.moveY(0)
        for c in components:
          for o in c:
            if o.__class__.__name__ == "Bullet" or Bullet in o.__class__.__bases__:
              o.setY(o.y-movespeed)
            elif player.getLocation() in o.getLocation():
              if o.__class__.__name__ == "Spikeball":
                o.changePoints(0,-movespeed)
              o.setY(o.y-movespeed)
      else:
        player.moveY(1)
    if movingup == True:
      player.movingup()
      if(player.getRect().top<220 and player.location.getRect().top < 0):
        player.location.setY(player.location.y+movespeed)
        player.moveY(0)
        for c in components:
          for o in c:
            if o.__class__.__name__ == "Bullet" or Bullet in o.__class__.__bases__:
              o.setY(o.y+movespeed)
            elif player.getLocation() in o.getLocation():
              if o.__class__.__name__ == "Spikeball":
                o.changePoints(0,movespeed)
              o.setY(o.y+movespeed)
      else:
        player.moveY(-1)
    if movingleft == True:
      player.movingleft()
      if(player.getRect().left<370 and player.location.getRect().left < 0):
        player.location.setX(player.location.x+movespeed)
        player.moveX(0)
        for c in components:
          for o in c:
            if o.__class__.__name__ == "Bullet" or Bullet in o.__class__.__bases__:
              o.setX(o.x+movespeed)
            elif player.getLocation() in o.getLocation():
              if o.__class__.__name__ == "Spikeball":
                o.changePoints(movespeed,0)
              o.setX(o.x+movespeed)
      else:
        player.moveX(-1)
    if movingright == True:
      player.movingright()
      if(player.getRect().right>screen_width-370 and player.location.getRect().right > screen_width):
        player.location.setX(player.location.x-movespeed)
        player.moveX(0)
        for c in components:
          for o in c:
            if o.__class__.__name__ == "Bullet" or Bullet in o.__class__.__bases__:
              o.setX(o.x-movespeed)
            elif player.getLocation() in o.getLocation():
              if o.__class__.__name__ == "Spikeball":
                o.changePoints(-movespeed,0)
              o.setX(o.x-movespeed)
      else:
        player.moveX(1)
    if movingright or movingdown or movingup or movingleft:
      player.moving()

    # --------------------  loop if game running ---------------------

    if player.location in gamerooms:
      if player.lives>0:
        
        #add score
        if score > highscore:
          highscore = score

        # move the sprites
        player.update(objectsOnScreen,enemies)

        #player shooting
        player.weapon.reloading()
        if player.shooting:
          if player.weapon.attacktimer():
            lastbullet = PistolBullet(player.shootingPoint[0],player.shootingPoint[1],180+player.weapon.angle,player.bulletspeed)
            bullets.append(lastbullet)
            player.weapon.attack(lastbullet)
            player.shooting = False

        #check enemies on screen
        enemiesOnScreen = []
        for enemy in enemies:
          if player.getLocation() in enemy.getLocation():
            enemiesOnScreen.append(enemy)

        #enemies
        for enemy in enemiesOnScreen:
          enemy.update(player.x,player.location,objectsOnScreen,player)
          enemy.move()
          #remove minion enemies
          if ratboss.lives > 30:
            if bossroom in enemy.location:
              if enemy.__class__.__name__ != "Boss" and enemy.__class__.__name__ != "WallGun":
                enemies.remove(enemy)
          #check for spikeball collision
          if enemy.__class__.__name__ == "Spikeball":
            if enemy.getHitbox().colliderect(player.getHitbox()):
              if (pow(pow(enemy.getHitbox().centerx-player.getHitbox().centerx,2)+pow(enemy.getHitbox().centery-player.getHitbox().centery,2), 0.5)< 70):
                player.lives -= 100
            for victim in enemiesOnScreen:
              if victim.__class__.__name__ == "Rat":
                if enemy.getHitbox().colliderect(victim.getHitbox()):
                  if (pow(pow(enemy.getHitbox().centerx-victim.getHitbox().centerx,2)+pow(enemy.getHitbox().centery-victim.getHitbox().centery,2), 0.5)< 70):
                    victim.lives -= 100
          # shoot bullets
          if not enemy.reloading():
            if enemy.__class__.__name__ == "Rat":
              lastbullet = RatBullet(enemy.shootingpoint[0],enemy.shootingpoint[1],0,enemy.bulletspeed)
              bullets.append(lastbullet)
              enemy.attack(lastbullet,player.rect.centerx,player.rect.centery)
            elif enemy.__class__.__name__ == "FancyRat":
              lastbullet = FancyBullet(enemy.shootingpoint[0],enemy.shootingpoint[1],0,enemy.bulletspeed)
              bullets.append(lastbullet)
              enemy.attack(lastbullet,player.rect.centerx,player.rect.centery)
              if enemy.lives <= 2:
                lastbullet = AngryBullet(enemy.angryshootingpoint[0],enemy.angryshootingpoint[1],0,4)
                bullets.append(lastbullet)
                enemy.attack(lastbullet,player.rect.centerx,player.rect.centery)
            elif enemy.__class__.__name__ == "WallGun":
              if ratboss.lives > 30 or (ratboss.lives <= 20 and ratboss.lives > 0):
                lastbullet = WallGunBullet(enemy.rect.centerx,enemy.rect.centery,enemy.shootingAngle,enemy.bulletspeed)
                bullets.append(lastbullet)
            elif enemy.__class__.__name__ == "Boss":
              if (ratboss.lives <= 30 and ratboss.lives > 20) or (ratboss.lives <= 10 and ratboss.lives > 0):
                for i in range(0,enemy.shotguncount):
                  lastbullet = RatBullet(enemy.shootingpoint[0],enemy.shootingpoint[1],0,enemy.bulletspeed)
                  bullets.append(lastbullet)
                  enemy.attack(lastbullet,player.rect.centerx,player.rect.centery)
              if ratboss.lives <= 20 and ratboss.minionspawned == False:
                for i in range(0,2):
                  enemies.append(Rat(bossroom.x+80,bossroom.y+100+100*i,2,[bossroom]))
                  enemies.append(FancyRat(bossroom.rect.right-128,bossroom.y+100+100*i,4,[bossroom]))
                ratboss.minionspawned = True
          elif enemy.__class__.__name__ == "Turret":
            if enemy.spritecount == 10 or enemy.spritecount == 40 or enemy.spritecount == 30 or enemy.spritecount == 20:
              lastbullet = TurretBullet(enemy.shootingpoint[0],enemy.shootingpoint[1],enemy.angle,enemy.bulletspeed)
              bullets.append(lastbullet)
          #check if hit by bullet
          for bullet in bullets:
            if bullet.getRect().colliderect(enemy.getRect()):
              if enemy.__class__.__name__ == "Spikeball" or enemy.__class__.__name__ == "Turret":
                if bullet.getRect().colliderect(enemy.getHitbox()):
                  enemy.lives -= 1
                  if enemy.lives>0:
                    pygame.mixer.Sound.play(spikeballimpact)
                  bullets.remove(bullet)
                  del bullet
              else:
                if bullet.friendly == True:
                  enemy.lives -= 1
                  if enemy.lives>0:
                    if enemy.__class__.__name__ == "Rat":
                      pygame.mixer.Sound.play(ratdamage)
                    elif enemy.__class__.__name__ == "FancyRat":
                      if enemy.lives == 2:
                        deadEnemies.append(deadHat(enemy.rect.x,enemy.rect.top,enemy.location,enemy.facingleft))
                    elif enemy.__class__.__name__ == "Boss":
                      if enemy.lives == 30:
                        pygame.mixer.music.stop()
                      elif enemy.lives == 20:
                        pygame.mixer.music.play(-1)
                  bullets.remove(bullet)
                  del bullet
          if enemy.lives <= 0:
            deadEnemies.append(enemy)
            enemies.remove(enemy)
            if enemy.__class__.__name__ == "Boss":
              bullets = []
              player.setLocation(victoryroom)
              pygame.mixer.Sound.play(bossdeath)
              pygame.mixer.music.load("data\\winning music.mp3")
              pygame.mixer.music.set_volume(volumeSwitch.getVolume())
              pygame.mixer.music.play(-1)
            score += 1
            if enemy.__class__.__name__ != "Boss":
              pygame.mixer.Sound.play(ratdeath)
        #move and remove the bullets
        for bullet in bullets:
          removeBullet = bullet.update(player.location)
          if player.getRect().colliderect(bullet.getRect()) and bullet.friendly == False:
            removeBullet = True
            player.lives -= 1
            pygame.mixer.Sound.play(playerdamage)
          elif bullet.__class__.__name__ == "WallGunBullet":
            if bullet.detonationTime == 0:
              removeBullet = True
              for i in range(0,4):
                bullets.append(TurretBullet(bullet.rect.left,bullet.rect.top,45+90*i,2))
          for object in objectsOnScreen:
            if object.getHitbox().colliderect(bullet.getRect()):
              removeBullet = True
          if removeBullet:
            bullets.remove(bullet)
            del bullet

        #enemydying
        for deadEnemy in deadEnemies:
          if player.location in deadEnemy.location:
            deadEnemy.update(player.x,player.location,objectsOnScreen,player)

        #check for trap activation
        for trap in traps:
          if player.getLocation() in trap.getLocation():
            if trap.update(player.getHitbox()):
              pygame.mixer.Sound.play(spiketrap)
            if trap.reloading:
              if pygame.Rect((trap.x,trap.y+5),(60,40)).colliderect(player.getHitbox()):
                if not trap.playerDamaged:
                  player.lives -= 1
                  pygame.mixer.Sound.play(playerdamage)
                  trap.playerDamaged = True

        #check for room change
        if player.location.moveRoom(player,components,screen_width,screen_height):
          bullets = []
          if player.location == bossroom:
            pygame.mixer.music.load("data\\piano music.mp3")
            pygame.mixer.music.set_volume(volumeSwitch.getVolume())
            pygame.mixer.music.play(-1)
          elif player.location == trialmaze:
            pygame.mixer.music.load("data\\gamemusic.mp3")
            pygame.mixer.music.set_volume(volumeSwitch.getVolume())
            pygame.mixer.music.play(-1)
          elif player.location == trialspikeballcorridor:
            pygame.mixer.music.load("data\\sewer music.mp3")
            pygame.mixer.music.set_volume(volumeSwitch.getVolume())
            pygame.mixer.music.play(-1)

        #start blitting everything
        screen.fill(DARK_BLUE)
        screen.blit(player.location.getSurface(),player.location.getRect())

        #load the dead screen music
        if player.lives < 1:
          if musicSwitch.getState():
            pygame.mixer.music.load("data\deadmusic.wav")
            pygame.mixer.music.set_volume(volumeSwitch.getVolume())
            pygame.mixer.music.play(-1)
          player.setLocation(deathroom)
          bullets = []
          for enemy in enemies:
            enemy.lives = enemy.startingLives
          for deadEnemy in deadEnemies:
            deadEnemy.lives = deadEnemy.startingLives
            deadEnemy.initialXY = deadEnemy.startingXY
            if deadEnemy.__class__.__name__ != "deadHat":
              enemies.append(deadEnemy)
          deadEnemies = []
          player.resetRoom(startmenu,components)
          for room in gamerooms:
            player.resetRoom(room,components)

    # game over screen
    if player.location == deathroom:
      screen.fill(BLACK)
      deadText = deadFont.render("You died",True,DARK_RED)
      highscoreText = titleFont.render("Highscore: "+str(highscore),True,DARK_RED)
      scoreText = titleFont.render("Enemies killed: "+str(score), True, DARK_RED)
      escapeText = escapeFont.render("Press ESCAPE to go back to menu",True,DARK_RED)
      screen.blit(deadText,(screen_width/2-115,250))
      screen.blit(scoreText,(screen_width/2-108,380))
      screen.blit(highscoreText,(screen_width/2-90,460))
      screen.blit(escapeText,(screen_width/2-150,600))
    # victory screen
    elif player.location == victoryroom:
      screen.fill(BLACK)
      victoryText = victoryFont.render("You Win!",True,GREEN)
      scoreText2 = victoryFont2.render("Enemies killed: "+str(score), True, GREEN)
      highscoreText2 = victoryFont2.render("Highscore: "+str(highscore),True,GREEN)
      escapeText2 = victoryFont3.render("Press ESCAPE to go back to menu",True,GREEN)
      screen.blit(victoryText,(screen_width/2-115,250))
      screen.blit(scoreText2,(screen_width/2-108,380))
      screen.blit(highscoreText2,(screen_width/2-90,460))
      screen.blit(escapeText2,(screen_width/2-135,600))
    #settings screen
    if player.location == settingsmenu:
      screen.fill(DARK_GREY)
      screen.blit(player.location.getSurface(), player.location.getRect())

      if musicSwitch.getState()==False:
        pygame.mixer.music.stop()

      if musicSwitch.getState() and pygame.mixer.music.get_busy()==False:
        pygame.mixer.music.play(-1)

      pygame.mixer.music.set_volume(volumeSwitch.getVolume())
      for s in sounds:
        pygame.mixer.Sound.set_volume(s,soundVolumeSwitch.getVolume())
      pygame.mixer.Sound.set_volume(pistolshot,soundVolumeSwitch.getVolume()/10)
      pygame.mixer.Sound.set_volume(spiketrap,soundVolumeSwitch.getVolume()/2)
      pygame.mixer.Sound.set_volume(ratdamage,soundVolumeSwitch.getVolume()/5)
      pygame.mixer.Sound.set_volume(ratdeath,soundVolumeSwitch.getVolume()/10)
      pygame.mixer.Sound.set_volume(spikeballimpact,soundVolumeSwitch.getVolume()/5)

      player.update(objectsOnScreen,enemies)

      #door animation
      if settingsDoorOpening:
        settingsDoorOpened = settingsButton.doorOpen()
        if settingsDoorOpened:
          player.location = startmenu
          player.resetRoom(startmenu,components)
          settingsDoorOpening = False
          settingsButton.imageToShow = 0
          settingsButton.counter = 0
          settingsButton.image = settingsButton.images[0]

      #blit the writing
      settingsButtonText = titleFont.render("Exit",True,DARK_RED)
      screen.blit(settingsButtonText, (settingsButton.x+15, settingsButton.rect.top-50))
      musicSwitchText = titleFont.render("Music",True,DARK_RED)
      screen.blit(musicSwitchText, (musicSwitch.x, musicSwitch.rect.top-50))
      volumeText = titleFont.render("Volume",True,DARK_RED)
      screen.blit(volumeText, (volumeSwitch.rect.left+30,volumeSwitch.rect.top-100))
      musicVolumeText = titleFont.render("Music",True,DARK_RED)
      screen.blit(musicVolumeText, (volumeSwitch.rect.left-15,volumeSwitch.rect.top-50))
      soundVolumeText = titleFont.render("Sounds",True,DARK_RED)
      screen.blit(soundVolumeText, (soundVolumeSwitch.rect.left-20,soundVolumeSwitch.rect.top-50))
      fullScreenSwitchText = titleFont.render("Fullscreen",True,DARK_RED)
      fullScreenSwitchText2 = titleFont.render("(will restart)",True,DARK_RED)
      screen.blit(fullScreenSwitchText, (fullScreenSwitch.rect.left-30,fullScreenSwitch.rect.top-100))
      screen.blit(fullScreenSwitchText2, (fullScreenSwitch.rect.left-30,fullScreenSwitch.rect.top-50))

    # menu screen when game not running
    if player.location == startmenu:
      screen.fill(DARK_GREY)
      screen.blit(player.location.getSurface(),player.location.getRect())

      player.update(objectsOnScreen,enemies)

      #door animations
      if playDoorOpening:
        playDoorOpened = playButton.doorOpen()
        if playDoorOpened:
          player.setLocation(trialstart)
          playDoorOpening = False
          playButton.imageToShow = 0
          playButton.counter = 0
      if quitDoorOpening:
        quitDoorOpened = quitButton.doorOpen()
        if quitDoorOpened:
          userQuit = True
      if settingsDoorOpening:
        settingsDoorOpened = settingsButton.doorOpen()
        if settingsDoorOpened:
          player.location = settingsmenu
          player.resetRoom(settingsmenu,components)
          settingsDoorOpening = False
          settingsButton.imageToShow = 0
          settingsButton.counter = 0
          settingsButton.image = settingsButton.images[0]

      # write the signs above the doors
      playButtonText = titleFont.render("Play",True,DARK_RED)
      quitButtonText = titleFont.render("Flee",True,DARK_RED)
      settingsButtonText = titleFont.render("Settings",True,DARK_RED)
      screen.blit(playButtonText, (playButton.x+15, playButton.y-50))
      screen.blit(quitButtonText, (quitButton.x+15, quitButton.y-50))
      screen.blit(settingsButtonText, (settingsButton.x-15, settingsButton.y-50))


    #                  ----------------------------------------------BLITTING----------------------------------------------------
    components = [enemies,switches,doors,bullets,objects]
    blitOrder = []
    for c in components:
      for o in c:
        if o.__class__.__name__ == "Bullet" or Bullet in o.__class__.__bases__:
          blitOrder.append(o)
        elif player.getLocation() in o.getLocation():
          blitOrder.append(o)
    if player.getLocation() != deathroom and player.getLocation() != victoryroom:
      blitOrder.append(player)
    
    #bubble sort
    blitOrder = bubblesort(blitOrder)
    deadEnemies = bubblesort(deadEnemies)
    traps = bubblesort(traps)
    deadEnemycount = 0
    trapcount = 0
    for deadEnemy in deadEnemies:
      if player.getLocation() in deadEnemy.getLocation():
        blitOrder.insert(deadEnemycount,deadEnemy)
        deadEnemycount += 1
    for trap in traps:
      if player.getLocation() in trap.getLocation():
        blitOrder.insert(trapcount,trap)
        trapcount += 1

    #blit all objects
    for object in blitOrder:
      if object.__class__.__name__ == "Bullet" or Bullet in object.__class__.__bases__:
        screen.blit(pygame.transform.rotate(object.getSurface(), -object.getAngle()),object.getRect())
      elif object.__class__.__name__ == "Slideswitchframe":
        screen.blit(object.getSurface(),object.getRect())
        screen.blit(object.handle.getSurface(),object.handle.getRect())
      elif object.__class__.__name__ == "Player":
        if object.imageToShow1 == 1:
          if object.weapon != "none":
            screen.blit(pygame.transform.rotate(object.weapon.getSurface(), -object.weapon.angle),object.weapon.getRect())
          screen.blit(object.getSurface(),object.getRect())
        else:
          screen.blit(object.getSurface(),object.getRect())
          if object.weapon != "none":
            screen.blit(pygame.transform.rotate(object.weapon.getSurface(), -object.weapon.angle),object.weapon.getRect())
      else:
        screen.blit(object.getSurface(),object.getRect())

    # blit the score text
    if player.getLocation() in gamerooms:
        livesText = titleFont.render("Lives: "+str(player.lives),True,DARK_RED)
        screen.blit(livesText,(20,20))

    # Limit to 60 frames per second
    clock.tick(60)

    # Render the screen as prepared with the blit commands
    pygame.display.flip()

  # Close everything down

  #save highscore
  highscorefile = open("data\highscore.txt","w")
  highscorefile.write(str(highscore))
  highscorefile.close()

  #save settings
  settingsfile = open("data\settings.txt","w")
  settingsfile.write(str(fullScreenSwitch.getState())+"\n"+str(musicSwitch.getState())+"\n"+str(volumeSwitch.getPosition())+"\n"+str(soundVolumeSwitch.getPosition()))
  settingsfile.close()

  pygame.quit()

  if restart:
    return True

if __name__ == "__main__":
  while main():
    pass