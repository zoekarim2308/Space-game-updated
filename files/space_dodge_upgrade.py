import pygame
import time
import random
import os
import csv
pygame.font.init()

WIDTH, HEIGHT= 600,600
win= pygame.display.set_mode((WIDTH, HEIGHT))
pygame.display.set_caption("SPACE DODGE UPGRADE")
PLAYERVEL=5
laservel=5.5

REDSHIP= pygame.image.load(os.path.join("assets","pixel_ship_red_small.png"))
GREENSHIP= pygame.image.load(os.path.join('assets','pixel_ship_green_small.png'))
BlUESHIP= pygame.image.load(os.path.join('assets','pixel_ship_blue_small.png'))
YELLOWSHIP= pygame.image.load(os.path.join('assets','pixel_ship_yellow.png'))

REDLAZER= pygame.image.load(os.path.join('assets','pixel_laser_red.png'))
BLUELAZER= pygame.image.load(os.path.join('assets','pixel_laser_blue.png'))
GREENLAZER= pygame.image.load(os.path.join('assets','pixel_laser_green.png'))
YELLOWLAZER= pygame.image.load(os.path.join('assets','pixel_laser_yellow.png'))

BG=pygame.transform.scale(pygame.image.load(os.path.join('assets','background-black.png')),(WIDTH, HEIGHT))

def save_record(name, level):
    with open('records.csv', "a", newline="") as f:
        writer = csv.writer(f)
        writer.writerow([name, level])

def load_records():
    records = []
    if os.path.exists('records.csv'):
        with open('records.csv', "r") as f:
            reader = csv.reader(f)
            for row in reader:
                if len(row) == 2:
                    records.append((row[0], row[1]))
    return records

def rewrite_records(records):
    with open('records.csv', "w", newline="") as f:
        writer = csv.writer(f)
        for r in records:
            writer.writerow(r)

def delete_records():
    if os.path.exists('records.csv'):
        os.remove('records.csv')
        print("All records deleted.")

def delete_one_record():
    records = load_records()
    if not records:
        print("No records to delete.")
        return
    print("\nRecords:")
    for i, r in enumerate(records, start=1):
        print(f"{i}. {r[0]} - Level {r[1]}")
    choice = input("\nEnter record number to delete: ")
    if choice.isdigit() and 1 <= int(choice) <= len(records):
        del records[int(choice)-1]
        rewrite_records(records)
        print("Record deleted successfully.")
    else:
        print("Invalid input.")

def modify_record_name():
    records = load_records()
    if not records:
        print("No records found.")
        return
    print("\nCurrent Records:")
    for i, r in enumerate(records, start=1):
        print(f"{i}. {r[0]} - Level {r[1]}")
    choice = input("\nEnter record number to modify name: ")
    if choice.isdigit() and 1 <= int(choice) <= len(records):
        new_name = input("Enter new name: ")
        records[int(choice)-1] = (new_name, records[int(choice)-1][1])
        rewrite_records(records)
        print("Name modified successfully.")
    else:
        print("Invalid input.")

class Laser:
    def __init__(self, x, y, img):
        self.x=x
        self.y=y
        self.img= img
        self.mask= pygame.mask.from_surface(self.img)

    def draw(self, window):
        window.blit(self.img, (self.x, self.y))

    def move(self, vel):
        self.y+=vel

    def offscreen(self,height):
        return not( self.y<= height and self.y>=0)

    def collision(self, obj):
        return collide(self, obj)

class Ship:
    COOLDOWN= 30
    def __init__(self, x, y, health=100):
        self.x=x
        self.y=y
        self.health= health
        self.ship_img= None
        self.laser_img= None
        self.laser=[]
        self.cooldowncounter= 0 
    def draw(self,window):
        window.blit(self.ship_img, (self.x, self.y))
        for laser in self.laser:
            laser.draw(window)

    def movelaser(self,vel,obj):
        self.cooldown()
        for laser in self.laser:
            laser.move(vel)
            if laser.offscreen(HEIGHT):
                self.laser.remove(laser)
            elif laser.collision(obj):
                obj.health-=10
                self.laser.remove(laser)

    def cooldown(self):
        if self.cooldowncounter>= self.COOLDOWN:
            self.cooldowncounter=0
        elif self.cooldowncounter>0:
            self.cooldowncounter+=1

    def get_width(self):
        return self.ship_img.get_width()
    def get_height(self):
        return self.ship_img.get_height()

    def shoot(self):
        if self.cooldowncounter==0:
            laser= Laser(self.x,self.y, self.laser_img)
            self.laser.append(laser)
            self.cooldowncounter= 1

class Player(Ship):
    def __init__(self, x, y, health=100):
        super().__init__(x, y, health)
        self.ship_img= YELLOWSHIP
        self.laser_img= YELLOWLAZER
        self.mask= pygame.mask.from_surface(self.ship_img)
        self.max_health = health

    def movelaser(self,vel,objs):
        self.cooldown()
        for laser in self.laser:
            laser.move(vel)
            if laser.offscreen(HEIGHT):
                self.laser.remove(laser)
            else:
                for obj in objs:
                    if laser.collision(obj):
                        objs.remove(obj)
                        self.laser.remove(laser)
    def draw(self, window):
        super().draw(window)
        self.healthbar(window)

    def healthbar(self,window):
        pygame.draw.rect(window, 'red', (self.x, self.y + self.ship_img.get_height() + 10, self.ship_img.get_width(), 10))
        pygame.draw.rect(window, 'green', (self.x, self.y + self.ship_img.get_height() + 10, self.ship_img.get_width()*(self.health/self.max_health), 10))

class Enemy(Ship):
        COLORMAP={
                "red": (REDSHIP,REDLAZER),
                "green": (GREENSHIP,GREENLAZER),
                "blue": (BlUESHIP,BLUELAZER)
                }
        def __init__(self, x, y, color, health=100):
            super().__init__(x,y, health)
            self.ship_img, self.laser_img= self.COLORMAP[color]
            self.mask= pygame.mask.from_surface(self.ship_img)

        def move(self, vel):
            self.y+=vel

        def shoot(self):
            if self.cooldowncounter==0:
                laser= Laser(self.x-15,self.y, self.laser_img)
                self.laser.append(laser)
                self.cooldowncounter= 1

def collide(obj1, obj2):
    offset_x= obj2.x - obj1.x
    offset_y=obj2.y - obj1.y
    return obj1.mask.overlap(obj2.mask, (offset_x,offset_y )) != None

def main():
    run=True
    FPS=60
    level=0
    lives=5
    FONT= pygame.font.SysFont('TimesNewRoman', 20)
    LOSTFONT= pygame.font.SysFont('TimesNewRoman', 40)

    enemies=[]
    wavelength=1
    enemyvel=1.5

    player= Player(200,430)
    laservel=4

    clock= pygame.time.Clock()
    lost= False
    lostcount= 0

    def redraw():
        win.blit(BG, (0,0))
        level_text= FONT.render(f'LEVEL: {level}', 1, 'pink')
        lives_text= FONT.render(f'LIVES: {lives}', 1, 'pink')

        win.blit(level_text, (10, 10))
        win.blit(lives_text, (WIDTH - lives_text.get_width() - 10, 10))

        for enemy in enemies:
            enemy.draw(win)
        player.draw(win)

        if lost:
            lost_lable= LOSTFONT.render('YOU A LOSER', 1, 'white')
            win.blit(lost_lable, (WIDTH/2 - lost_lable.get_width()/2, 250))   

        pygame.display.update()

    while run:
        clock.tick(FPS)
        redraw()

        if lives <= 0:
            lost = True
            lostcount += 1

        if lost:
            if lostcount> FPS * 3:
                run = False
            else:
                continue

        if len(enemies) == 0:
            level+=1
            wavelength+=3
            for i in range(wavelength):
                enemy= Enemy(random.randrange(50, WIDTH-50), random.randrange(-1500,-100), random.choice(['red', 'green', 'blue']))
                enemies.append(enemy)

        for event in pygame.event.get():
            if event.type== pygame.QUIT:
                quit()

        keys= pygame.key.get_pressed()
        if keys[pygame.K_LEFT] and player.x-PLAYERVEL >0:
            player.x-=PLAYERVEL
        if keys[pygame.K_RIGHT] and player.x+PLAYERVEL + player.get_width()< WIDTH:
            player.x+=PLAYERVEL
        if keys[pygame.K_UP] and player.y-PLAYERVEL >0:
            player.y-=PLAYERVEL
        if keys[pygame.K_DOWN]and player.y+PLAYERVEL+ player.get_height()+15< HEIGHT:
            player.y+=PLAYERVEL
        if keys[pygame.K_SPACE]:
            player.shoot()

        for enemy in enemies[:]:
            enemy.move(enemyvel)
            enemy.movelaser(laservel, player)
            if random.randrange(0, 2*60) == 1 :
                enemy.shoot()
            if collide(enemy, player):
                player.health-=10
                enemies.remove(enemy)
                if player.health <= 0:
                    lives -= 1
                    player.health = player.max_health
            elif enemy.y + enemy.get_height() > HEIGHT:
                lives -= 1
                enemies.remove(enemy)
        player.movelaser(-laservel, enemies)

def main_menu():
    while True:
        print("\n=== SPACE DODGE UPGRADE MENU ===")
        print("1. Play Game")
        print("2. View Records")
        print("3. Delete All Records")
        print("4. Delete One Record")
        print("5. Modify Name")
        print("6. Exit")

        choice = input("\nEnter your choice: ")
        if choice == "1":
            main()
        elif choice == "2":
            records = load_records()
            if not records:
                print("No records found.")
            else:
                print("\nSaved Records:")
                for name, lvl in records:
                    print(f"{name} - Level {lvl}")
        elif choice == "3":
            delete_records()
        elif choice == "4":
            delete_one_record()
        elif choice == "5":
            modify_record_name()
        elif choice == "6":
            print("Byebye")
            break
        else:
            print("Invalid choice.")

main_menu()
