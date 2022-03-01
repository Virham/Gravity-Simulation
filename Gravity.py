import pygame
pygame.init()
import time
import json
import math
import random
import os


class SlideBar(object):
    def __init__(self, main, x, y, width, height, update_value, values, startingValue, color, sliderColor, ActiveColor, caption=None, captionSize=None, captionPos=None):
        """
        :param the main object
        :param x: x position of slider
        :param y: y position of slider
        :param width: width of slider
        :param height: height of slider
        :param: a function that can set another value
        :param value: tuple with the lowest value and the highest value
        :param startingValue: the value the slidebar starts with
        :param color: the color of the slidebar
        :param sliderColor: the color of the part you slide
        :param ActiveColor: the color of the slidebar when it is pressed down
        :param caption: describes what the sliderbar is used for
        :param captionSize: the size of the font used for the caption
        :param captionPos: the position of the caption on the screen

        """
        self.x = x
        self.y = y
        self.width = width
        self.height = height

        self.update_value = update_value
        self.valueRange = values
        self.value = startingValue
        self.name = caption
        self.caption = pygame.font.SysFont("Grf", captionSize or 1).render(caption or "", True, (255, 255, 255))

        self.rect = pygame.Rect(x, y, width, height)
        self.sliderWidth = round(width*0.05)
        self.offset = 0

        sliderX_scale = (self.value - self.valueRange[0]) / (self.valueRange[1] - self.valueRange[0])
        sliderX = ((self.value - self.valueRange[0]) / (self.valueRange[1] - self.valueRange[0])) * self.width - (self.sliderWidth / 2)
        self.sliderRect = pygame.Rect(self.x + round(sliderX), y - 10, self.sliderWidth, height + 20)
        self.font = pygame.font.SysFont('Great Attraction', 30)
        self.captionPos = captionPos

        self.main = main
        # self.LastState = 0
        self.state = None
        self.color = color
        self.sliderColor = sliderColor
        self.activeColor = ActiveColor
        self.currentColor = self.sliderColor

    def set_x(self, x):
        if self.x <= x < self.x + self.width:
            self.value = (((x - self.x) / self.width) * (self.valueRange[1]  - self.valueRange[0])) + self.valueRange[0]


        elif x < self.x:
            self.value = self.valueRange[0]

        elif x > self.x + self.valueRange[1]:
            self.value = self.valueRange[1]

        self.value = float("%.2f" % self.value)



    def update_rect(self, mouse_x):
        x = mouse_x
        x = x
        self.sliderRect.x = round(max(min(x, self.x + self.width), self.x) - (self.sliderWidth / 2))

    def draw(self, win):
        text = self.font.render( "%.2f" % self.value, False, (255, 255, 255))

        pygame.draw.rect(win, self.color, self.rect)

        pygame.draw.rect(win, self.currentColor, self.sliderRect)
        win.blit(text, (self.x + self.width + 8, round(self.y + self.height / 4)))

        if self.captionPos:
            win.blit(self.caption, self.captionPos)



    def collide(self):
        mouse_x, mouse_y = pygame.mouse.get_pos()
        morect = pygame.Rect(mouse_x, mouse_y, 2, 2)

        if self.state == "Active":
            if not pygame.mouse.get_pressed()[0]:
                self.state = None
                self.currentColor = self.sliderColor
                return

            self.update_rect(mouse_x)
            self.set_x(mouse_x)
            return

        elif pygame.mouse.get_pressed()[0]:
            if morect.colliderect(self.sliderRect):
                self.state = "Active"
                self.currentColor = self.activeColor

        self.LastState = pygame.mouse.get_pressed()[0]

    def all(self, win):
        self.draw(win)
        self.collide()


class Button:
    def __init__(self, rect, idleColor, pressedColor, func, args=None, caption=None, captionPos=None):
        self.rect = rect

        self.function = func
        self.arguments = args

        self.idleColor = idleColor
        self.pressedColor = pressedColor
        self.color = self.idleColor

        self.captionPos = captionPos
        self.caption = caption

        self.pressed = False
        self.lastState = 0


    def draw(self, win):
        pygame.draw.rect(win, self.color, self.rect)
        win.blit(self.caption, self.captionPos)


    def CheckPressed(self):
        mouse = pygame.mouse.get_pressed()[0]
        mouse_x, mouse_y = pygame.mouse.get_pos()

        if pygame.Rect(mouse_x, mouse_y, 1, 1).colliderect(self.rect):
            if mouse and not self.lastState:
                self.color = self.pressedColor

            if self.lastState and not mouse:
                self.color = self.idleColor
                self.OnPresed()

            self.lastState = mouse

    def OnPresed(self):
        if self.arguments:
            self.function(*self.arguments)

        else:
            self.function()


class Object:
    def __init__(self, size, mass, pos, vel):
        self.size = size
        self.mass = mass
        self.vel = vel
        self.pos = pos
        self.rect = pygame.Rect(self.pos[0], self.pos[1], self.size, self.size)
        self.color = (255, 200, 50)

        self.trail = []
        self.trail_range = 255
        self.activate_trail = False

    def update(self, GravVel, fs):
        self.vel = (self.vel[0] + GravVel[0] * fs, self.vel[1] + GravVel[1] * fs)

    def move(self, fs):
        self.pos = (self.pos[0] + self.vel[0] * fs, self.pos[1] + self.vel[1] * fs)
        self.trail.append(self.pos)
        if len(self.trail) > self.trail_range:
            self.trail.pop(0)
        self.rect = pygame.Rect(round(self.pos[0] * fs), round(self.pos[1] * fs), self.size, self.size)


class Main:
    def __init__(self):
        self.size = 1000
        self.win = pygame.display.set_mode((self.size+512, self.size))
        pygame.display.set_caption("Gravity")
        self.bg = self.CreateStars(self.size * 2)
        self.font = pygame.font.SysFont('Great Attraction', 50)

        self.currentSize = 10
        self.currentMass = 10
        self.currentVelocity = [0, 0]
        self.synced = True

        self.currentObject = None
        self.follow = False
        self.trail = True
        self.objects = []
        self.G = 1

        self.settings = []
        self.settings_setup()

        self.create = []
        self.create_setup()

        self.manage = []
        self.manage_setup()

        self.buttons = []
        self.button_setup()


        self.zoom = 1
        self.ZoomSpeed = 1
        self.paused = False
        self.menu = "settings"
        self.fps = 60

        self.offset = (10, 0)
        self.OffSpeed = 20
        self.input = {"w": False, "a": False, "s": False, "d":False}
        self.lastKeys = pygame.key.get_pressed()
        self.lastMouse = pygame.mouse.get_pressed()

    def settings_setup(self):
        def constant(value):
            self.G = value
        constant =      SlideBar(main=self, x=self.size + 64, y=150, width=375, height=64,
                                 update_value=constant,values=(-1, 5), startingValue=2,
                                 color=(255, 255, 255), sliderColor=(32, 32, 32), ActiveColor=(0, 0, 0),
                                 caption="Grativational constant", captionSize=40, captionPos=(self.size + 101, 100))

        self.settings.append(constant)

        def timeF(value):
            self.fps = value

        time_change = SlideBar(main=self, x=self.size + 64, y=270, width=375, height=64,
                                 update_value=timeF, values=(5, 500), startingValue=75,
                                 color=(255, 255, 255), sliderColor=(32, 32, 32), ActiveColor=(0, 0, 0),
                                 caption="Time speed", captionSize=40, captionPos=(self.size + 101, 230))

        self.settings.append(time_change)

        def offset_speedF(value):
            self.OffSpeed = value

        offset_speed = SlideBar(main=self, x=self.size + 64, y=390, width=375, height=64,
                                 update_value=offset_speedF, values=(1, 250), startingValue=35,
                                 color=(255, 255, 255), sliderColor=(32, 32, 32), ActiveColor=(0, 0, 0),
                                 caption="Offset speed", captionSize=40, captionPos=(self.size + 101, 350))


        self.settings.append(offset_speed)

        def zoom_speedF(value):
            self.ZoomSpeed = value


        zoom_speed = SlideBar(main=self, x=self.size + 64, y=520, width=375, height=64,
                                 update_value=zoom_speedF, values=(0.01, 5), startingValue=0.5,
                                 color=(255, 255, 255), sliderColor=(32, 32, 32), ActiveColor=(0, 0, 0),
                                 caption="Zoom speed", captionSize=40, captionPos=(self.size + 101, 480))

        self.settings.append(zoom_speed)


        def trailsF():
            self.trail = not self.trail

        trails = Button(rect=pygame.Rect(self.size + 64, 640, 384 , 64),
                        idleColor=(225, 225, 225), pressedColor=(125, 125, 125),
                        func=trailsF,
                        caption=pygame.font.SysFont("", 65).render("Show Trail", True, (150, 150, 150)),
                        captionPos=(self.size + 145, 650))

        self.settings.append(trails)

    def create_setup(self):
        def sizeF(value):
            self.currentSize = value
        size =        SlideBar(main=self, x=self.size + 100, y=125, width=350, height=64,
                               update_value=sizeF, values=(1, 500), startingValue=self.currentSize,
                               color=(255, 255, 255), sliderColor=(32, 32, 32), ActiveColor=(0, 0, 0),
                               caption="Size", captionSize=40, captionPos=(self.size + 20, 140))

        self.create.append(size)

        def massF(value):
            self.currentMass = value

        mass = SlideBar(main=self, x=self.size + 100, y=215, width=350, height=64,
                        update_value=massF, values=(1, 500), startingValue=self.currentMass,
                        color=(255, 255, 255), sliderColor=(32, 32, 32), ActiveColor=(0, 0, 0),
                        caption="Mass", captionSize=40, captionPos=(self.size + 20, 230))

        self.create.append(mass)

        def syncF(obj):
            self.synced = not self.synced
            if self.synced:
                obj.color = (50, 95, 240)

        synced = Button(rect=(self.size + 386, 305, 64, 64),
                        idleColor=(128, 128, 128), pressedColor=(64, 64, 64),
                        func=syncF,
                        caption=pygame.font.SysFont("", 40).render("Sync size and mass", True, (255, 255, 255)),
                        captionPos=(self.size + 100, 320))

        synced.arguments = [synced]
        synced.color = (50, 95, 240)

        self.create.append(synced)

        def vel_xF(value):
            self.currentVelocity[0] = value

        vel_x = SlideBar(main=self, x=self.size + 100, y =395, width=350, height=64,
                         update_value=vel_xF, values=(-50, 50), startingValue=0,
                         color=(255, 255, 255), sliderColor=(32, 32, 32), ActiveColor=(0, 0, 0),
                         caption="Vel X", captionSize=40, captionPos=(self.size + 20, 415))

        self.create.append(vel_x)

        def vel_yF(value):
            self.currentVelocity[1] = value

        vel_y = SlideBar(main=self, x=self.size + 100, y =485, width=350, height=64,
                         update_value=vel_yF, values=(-50, 50), startingValue=0,
                         color=(255, 255, 255), sliderColor=(32, 32, 32), ActiveColor=(0, 0, 0),
                         caption="Vel Y", captionSize=40, captionPos=(self.size + 20, 505))

        self.create.append(vel_y)

    def manage_setup(self):

        def followF():
            self.follow = not self.follow
            print(self.follow)


        button = Button(rect=pygame.Rect(self.size + 32, 796, 448, 64),
                        idleColor=(100, 100, 255), pressedColor=(50, 50, 255),
                        func=followF,
                        caption=pygame.font.SysFont("", 75).render("Follow", True, (250, 250, 250)), captionPos=(self.size + 175, 806))


        self.manage.append(button)

        def deleteF():
            self.objects.remove(self.currentObject)
            self.currentObject = None
            self.follow = False

        button = Button(rect=pygame.Rect(self.size + 32, 700, 448, 64),
                        idleColor=(255, 100, 100), pressedColor=(255, 50, 50),
                        func=deleteF,
                        caption=pygame.font.SysFont("", 75).render("Delete", True, (250, 250, 250)),
                        captionPos=(self.size + 175, 710))

        self.manage.append(button)

        def trailF():
            self.currentObject.activate_trail = not self.currentObject.activate_trail

        button = Button(rect=pygame.Rect(self.size + 32, 892, 448, 64),
                        idleColor=(225, 225, 225), pressedColor=(150, 150, 150),
                        func=trailF,
                        caption=pygame.font.SysFont("", 75).render("Show Trail", True, (150, 150, 150)),
                        captionPos=(self.size + 130, 902))

        self.manage.append(button)



    def button_setup(self):
        def settings(obj):
            self.menu = "settings"
            obj.color = (32, 32, 32)
            for i in self.buttons:
                if i != obj:
                    i.color = i.idleColor

        button =  Button(rect=pygame.Rect(self.size + 16, 16, 128, 40),
                         idleColor=(100, 100, 100), pressedColor=(64, 64, 64),
                         func=settings,
                         caption=pygame.font.SysFont("", 40).render("Settings", True, (255, 255, 255)), captionPos=(self.size + 22, 22))

        button.color = (32, 32, 32)
        button.arguments = [button]

        self.buttons.append(button)

        def create(obj):
            self.menu = "create"
            obj.color = (32, 32, 32)
            for i in self.buttons:
                if i != obj:
                    i.color = i.idleColor

        button = Button(rect=pygame.Rect(self.size + 160, 16, 128, 40),
                        idleColor=(100, 100, 100), pressedColor=(64, 64, 64),
                        func=create,
                        caption=pygame.font.SysFont("", 40).render("Create", True, (255, 255, 255)),
                        captionPos=(self.size + 180, 22))

        button.arguments = [button]

        self.buttons.append(button)

        def manage(obj):
            self.menu = "manage"
            obj.color = (32, 32, 32)
            for i in self.buttons:
                if i != obj:
                    i.color = i.idleColor


        button = Button(rect=pygame.Rect(self.size + 304, 16, 128, 40),
                        idleColor=(100, 100, 100), pressedColor=(64, 64, 64),
                        func=manage,
                        caption=pygame.font.SysFont("", 40).render("Manage", True, (255, 255, 255)),
                        captionPos=(self.size + 315, 22))

        button.arguments = [button]

        self.buttons.append(button)

    def HandleInput(self):
        keys = pygame.key.get_pressed()
        self.input["w"] = (0, -keys[pygame.K_w])
        self.input["a"] = (-keys[pygame.K_a], 0)
        self.input["s"] =(0, keys[pygame.K_s])
        self.input["d"] = (keys[pygame.K_d], 0)

        mx, my = pygame.mouse.get_pos()
        mr = pygame.Rect(mx, my, 1, 1)
        self.zoom += keys[pygame.K_SPACE] * self.ZoomSpeed * 0.1
        self.zoom += -keys[pygame.K_LSHIFT] * self.ZoomSpeed * 0.1
        self.zoom = max(0.1, self.zoom)

        if self.lastKeys[pygame.K_f] and not keys[pygame.K_f]:
            self.paused = not self.paused


        for i in self.input:
            v = self.input.get(i)
            self.offset = (self.offset[0] + v[0] * self.OffSpeed, self.offset[1] + v[1] * self.OffSpeed)

        if pygame.mouse.get_pressed()[0] and not self.lastMouse[0]:
            if mr.colliderect(pygame.Rect(0, 0, self.size, self.size)):
                pos = self.GetObjectPos((mx, my))
                self.objects.append(Object(self.currentSize, self.currentMass, pos, self.currentVelocity.copy()))

        if pygame.mouse.get_pressed()[2] and not self.lastMouse[2]:
            obj = self.ObjectClicked((mx, my))
            if obj:
                self.currentObject = obj

        if self.follow and self.currentObject:
            self.offset = (self.currentObject.pos[0], self.currentObject.pos[1])

        self.lastKeys = pygame.key.get_pressed()
        self.lastMouse = pygame.mouse.get_pressed()


    def CreateStars(self, amount):
        surf = pygame.Surface((self.size, self.size))
        for i in range(amount):
            x = random.randint(0, self.size)
            y = random.randint(0, self.size)
            s = random.randint(0, 200)

            pygame.draw.circle(surf, (s, s, s), (x, y), 1)

        pygame.image.save(surf, "stars.png")
        return pygame.image.load("stars.png")

    def GetGravity(self, o1, o2):
        offset = (o2.pos[0] - o1.pos[0], o2.pos[1] - o1.pos[1])
        dis = math.sqrt(pow(offset[0], 2) + pow(offset[1], 2))
        dis = max(0.1, dis)
        forceMagnitude = self.G * o2.mass / pow(dis, 1)
        direction = (offset[0] / dis, offset[1] / dis)

        force = (direction[0] * forceMagnitude, direction[1] * forceMagnitude)
        return force

    def updateVelocities(self):
        if not self.paused:
            for o in self.objects:
                for i in self.objects:
                    if o == i:
                        continue
                    grav = self.GetGravity(i, o)
                    i.update(grav, self.fps / 60)

                o.move(self.fps / 60)


    def GetScreenPos(self, pos):
        x = round((pos[0] - self.offset[0]) / self.zoom + self.size / 2)
        y = round((pos[1] - self.offset[1]) / self.zoom + self.size / 2)

        return (x, y)

    def GetObjectPos(self, pos):
        x = (pos[0] - self.size / 2) * self.zoom + self.offset[0]
        y = (pos[1] - self.size / 2) * self.zoom + self.offset[1]

        return(round(x), round(y))

    def ObjectClicked(self, screen_pos):
        mpos = self.GetObjectPos(screen_pos)
        for i in self.objects:
            p = i.pos
            if pow(mpos[0] - p[0], 2) + pow(mpos[1] - p[1], 2) <= pow(i.size, 2):
                return i

        return False



    def update_ui(self):

        for button in self.buttons:
            button.CheckPressed()

        if self.menu == "settings":
            for ui in self.settings:
                if isinstance(ui, SlideBar):
                    ui.collide()
                    ui.update_value(ui.value)

                if isinstance(ui, Button):
                    ui.CheckPressed()

        if self.menu == "create":
            for ui in self.create:
                if isinstance(ui, SlideBar):
                    ui.collide()
                    ui.update_value(ui.value)
                    if self.synced:
                        if ui.state:
                            if ui.name == "Size":
                                mass = self.create[1]
                                mx = pygame.mouse.get_pos()[0]
                                mass.update_rect(mx)
                                mass.set_x(mx)



                if isinstance(ui, Button):
                    ui.CheckPressed()

        if self.menu == "manage":
                if self.currentObject:
                    for i in self.manage:
                        i.CheckPressed()

    def display_text(self, text, pos):
        txt = self.font.render(text, True, (255, 255, 255))
        self.win.blit(txt, pos)

    def draw_menu(self):
        pygame.draw.rect(self.win, (200, 200, 200), (self.size, 0, 512, self.size))
        for button in self.buttons:
            button.draw(self.win)

        if self.menu == "settings":
            for i in self.settings:
                i.draw(self.win)

        if self.menu == "create":
            for i in self.create:
                i.draw(self.win)

        if self.menu == "manage":
            if self.currentObject:
                pygame.draw.circle(self.win, self.currentObject.color, (self.size + 256, 210), 125)
                self.display_text("Pos: %.2f, %.2f" % (self.currentObject.pos[0], self.currentObject.pos[1]), (self.size + 32, 400))
                self.display_text("Vel: %.2f, %.2f" % (self.currentObject.vel[0], self.currentObject.vel[1]), (self.size + 32, 450))
                self.display_text("Size: %d" % self.currentObject.size, (self.size + 32, 525))
                self.display_text("Mass: %d" % self.currentObject.mass, (self.size + 32, 575))
                for i in self.manage:
                    i.draw(self.win)



    def draw(self):
        self.win.fill((0, 0, 0))
        self.win.blit(self.bg, (0, 0))

        plist = [None]*len(self.objects)
        index = 0
        for o in self.objects:
            pos = self.GetScreenPos(o.pos)
            if o == self.currentObject:
                c = o.color
                color = (255 - c[0], 255 - c[1], 255 - c[2])
                pygame.draw.circle(self.win,  color, pos, round((5 + o.size * 1.1) / self.zoom))

                if o.activate_trail and not self.trail:
                    for i in range(len(o.trail) - 1):
                        pygame.draw.line(self.win, (i, i, i), self.GetScreenPos(o.trail[i]), self.GetScreenPos(o.trail[i + 1]))

            if self.trail:
                for i in range(len(o.trail) - 1):
                    pygame.draw.line(self.win, (i, i, i), self.GetScreenPos(o.trail[i]), self.GetScreenPos(o.trail[i + 1]), round(5 / self.zoom))

            pygame.draw.circle(self.win, o.color, pos, round(o.size / self.zoom))

            plist[index] = pos
            index += 1

        surf = pygame.Surface((self.size, self.size))
        surf.set_colorkey((0, 0, 0))
        surf.set_alpha(128)
        pygame.draw.circle(surf, (255, 255, 255, 0), pygame.mouse.get_pos(), round(self.currentSize / self.zoom))
        self.win.blit(surf, (0, 0))
        self.draw_menu()

        if self.paused:
            self.display_text("PAUSED", (20, 20))


    def loop(self):
        while True:
            self.HandleInput()
            self.updateVelocities()
            self.update_ui()
            self.draw()

            for event in pygame.event.get():
                if event.type == pygame.QUIT:
                    return

            keys = pygame.key.get_pressed()
            if keys[pygame.K_LALT] and keys[pygame.K_F4]:
                return

            pygame.display.update()


m = Main()

m.loop()



if os.path.exists(r"stars.png"):
    os.remove(r"stars.png")
