import graphics, drawticks, saver
from items import Item


def makeInstances(manager):
    # print("Loaded Locations:")
    import sys, inspect
    clsmembers = inspect.getmembers(sys.modules[__name__], inspect.isclass)
    for i in clsmembers:
        if issubclass(i[1], Screen) and Screen != i[1]:
            # print(i)
            manager.register(i[1]())


class ScreenManager:
    def __init__(self, r):
        # type: (graphics.Renderer) -> None
        self.r = r
        self.screens = []
        self.currentScreenIndex = -1
        self.currentScreen = ""
        self.lastScreen = "kitchen"
        makeInstances(self)

    def register(self, screen):
        self.screens.append(screen)

    def cs(self):
        return self.screens[self.currentScreenIndex]

    def getScreen(self, screenid):
        for screen in self.screens:
            if screen.ID == screenid:
                return screen
        return None

    def setCurrent(self, currentID, e):
        if currentID=="":
            currentID="intro"
        if currentID == "intro":
            e.variables["state"] = "intro"
        else:
            e.variables["state"] = "location"


        if self.currentScreenIndex != -1:
            self.cs().onStop(self.r, e)
            if self.cs().ID!="intro":
                self.lastScreen = self.cs().ID
        self.r.clear()
        suc = False
        for i in range(len(self.screens)):
            screen = self.screens[i]
            if screen.ID == currentID:
                self.currentScreenIndex = i
                self.currentScreen=currentID
                self.cs().onStart(self.r, e)
                suc = True
        if not suc:
            print("Location ", currentID, " doesn't exist")
            self.setCurrent(self.lastScreen, e)

    def tick(self, e):
        self.cs().tick(self.r, e)


class Screen:

    def __init__(self, id, name, otherName=""):
        if otherName == "":
            otherName = name
        self.ID = id
        self.time = 0
        self.NAME = name
        self.OTHER_NAME = otherName
        self.image = drawticks.Image(1, 1, [])
        self.nameLine = None
        self.items = []
        self.exits = []
        self.metaImagery = True  # image will be set according to e.getVar(self.ID+"_meta)
        self.metaImageryWorks = False
        self.lastImageMeta = -1

    def getItemByName(self, name):
        for item in self.items:
            if item.ID.lower() == name.lower():
                return item
        return None

    def onStart(self, r, e):
        ray = saver.loadImage(self.ID)
        width = r.g.WIDTH
        height = r.g.HEIGHT
        if ray != "null":
            self.image = drawticks.Image(1, 1, ray)
            r.add(self.image)
        elif self.metaImagery:
            ray = saver.loadImage(self.ID + "_" + str(e.getVar(self.ID + "_meta", 0)))
            if ray != "null":
                self.image = drawticks.Image(1, 1, ray)
                r.add(self.image)
                self.metaImageryWorks = True

        self.nameLine = drawticks.Text(r.g.WIDTH // 2, 0, " " + self.NAME + " ", centered=1, underline=False)
        rect = drawticks.Rectangle(0, 0, width, height, clearWithin=False)
        r.add(rect)
        r.add(self.nameLine)

    def setImageMeta(self, e):
        nowMeta = e.getVar(self.ID + "_meta", 0)
        if self.metaImageryWorks and self.lastImageMeta != nowMeta:
            self.image.array = saver.loadImage(self.ID + "_" + str(nowMeta))
            self.lastImageMeta = nowMeta

    def onStop(self, r, e):
        pass

    def tick(self, r, e):
        self.time += 1
        self.setImageMeta(e)

    def getItems(self):
        return self.items

    def getExits(self, e):  # 0-id,1-name,2-visible
        for exit in self.exits:
            loc = e.s.getScreen(exit[0])
            name = exit[0]
            if loc is not None:
                name = loc.OTHER_NAME

            if len(exit) != 3:
                if len(exit) == 1:
                    exit.append(name)
                    exit.append(1)
                else:
                    if exit[1] == 0 or exit[1] == 1:
                        exit.insert(1, name)
                    else:
                        exit.append(1)
        return self.exits


class ScreenIntro(Screen):
    def __init__(self):
        super().__init__("intro", "Intro")
        self.innerState = -1
        self.exits = []
        self.line0 = None
        self.line1 = None
        self.line2 = None
        self.saveIntro = ""

    def onStart(self, r, e):
        # type: (graphics.Renderer) -> None
        super().onStart(r, e)
        width = r.g.WIDTH
        height = r.g.HEIGHT
        self.line0 = drawticks.Text(width // 2, 2, "Birthday Cake Game", centered=1, underline=True)
        self.line1 = drawticks.Text(width // 2, 5, "Type \"help\" to see all commands, or \"play\"", centered=1,
                                    underline=False)
        self.line2 = drawticks.Text(width // 2, 7, self.saveIntro, centered=1, underline=False)
        r.add(self.line0)
        r.add(self.line1)
        r.add(self.line2)


def onFlourFound(item, e):
    flour = e.s.cs().getItemByName("flour")
    flour.visible = True
    e.player.inventory.append(flour)
    e.player.switchInventory(True)
    e.s.cs().items.remove(flour)
    return True


def onFlourCheck(item, e):
    # animation flour
    e.a.playAnimation("flour")
    e.variables["flour_checked"] = True
    return "consume"

def onTaskCheck(item, e):
    # animation flour
    e.a.playAnimation("kitchen")
    return "consume"

class ScreenKitchen(Screen):
    def __init__(self):
        super().__init__("kitchen", "Kitchen")
        self.innerState = -1
        self.exits = [["living_room"]]
        self.items = [Item("kitchen_window", "Window",
                           description="I can see my garden.\nIt doesn't protect the kitchen from wind as it used to :(\nI need to repair it before winter.",
                           ),
                      Item("cabinet", "Food Cabinet",
                           description="Place for food.",
                           onCheckPhrase="I found flour!",
                           onCheck=onFlourFound
                           ),
                      Item("flour", "Flour Bag",
                           description="It's empty! \nUnfortunately",
                           onCheckPhrase="",
                           onCheck=onFlourCheck,
                           visible=False
                           ),
                      Item("kitch", "Task",
                           onCheck=onTaskCheck,
                           )
                      ]

    def onStart(self, r, e):
        # type: (graphics.Renderer) -> None
        super().onStart(r, e)
        self.tick(r, e)
        r.addBack(self.image)

    def tick(self, r, e):
        super().tick(r, e)
        if e.getVar("fresh_kitchen", True):
            e.variables["fresh_kitchen"] = False
            e.a.playAnimation("intro")


def onPictureCheck(item, e):
    e.s.cs().exits[2][2] = 1
    return True


class ScreenLivingRoom(Screen):
    def __init__(self):
        super().__init__("living_room", "Living Room")
        self.exits = [["kitchen"], ["hall"], ["fisherman", 0]]
        self.items = [Item("picture_item", "Picture",
                           description="My photo when I was younger and on a fishing trip",
                           onCheck=onPictureCheck
                           ), ]


def onHookPick(item, e):
    out = e.getVar("well_check", False)
    if out:
        e.variables["fisherman_meta"] = 1
        e.player.buildHelpLine("This will help me!")
        return True
    else:
        e.player.buildHelpLine("I am not going fishing!")
        return False

def onHookCheck(item, e):
    e.variables["hook_checked"] = True

class ScreenFisherman(Screen):
    def __init__(self):
        super().__init__("fisherman", "Fisherman Picture", otherName="Picture")
        self.exits = [["living_room"]]
        self.items = [Item("hook", "Hook",
                           description="That's the hook of a pole with which I have beaten The Big Indonesian Trout."
                                       "\n Wonder where the pole is... I know! It's in the attic of a workshop! (If I recall correctly.) ",
                           onpick=onHookPick,
                           onCheck=onHookCheck
                           ), ]


def onGramophonePick(item, e):
    if e.s.cs().ID=="bull":
        e.player.buildHelpLine("It's right to educate the bull")
        return False
    if e.getVar("bull_checked", False):
        e.variables["hall_meta"] = 1
        e.variables["bull_checked"] = True
        e.player.buildHelpLine("This is gonna be useful.")
        return True
    else:
        e.player.buildHelpLine("I don't have time for this wonderful piece of art!")
        return False

def onGramUse(item, item2,e):
    print("use gram")
    if e.s.cs().ID=="bull":
        e.player.inventory.remove(item)
        e.s.cs().items.append(item)
        e.variables["bull_meta"] = 2
        e.a.playAnimation("bull")

class ScreenHall(Screen):
    def __init__(self):
        super().__init__("hall", "Hall")
        self.exits = [["living_room"], ["garden_left"]]
        self.items = [Item("gramophone", "Gramophone",
                           description="I have bought it in the...\n Well,I have no idea. So many years.., anyway, I don't have time to listen to it.",
                           onpick=onGramophonePick,
                           onUse=onGramUse
                           ), ]


class ScreenGardenLeft(Screen):
    def __init__(self):
        super().__init__("garden_left", "Left Garden")
        self.exits = [["bicycle"], ["workshop"], ["hall", "House"], ["garden_right"]]


class ScreenGardenRight(Screen):
    def __init__(self):
        super().__init__("garden_right", "Right Garden")
        self.exits = [["hall", "House"], ["garden_left"], ["well"], ["bull"]]



def onTrapdoorUse(item, item2, e):
    if e.getVar("workshop_meta",0)==1 and not e.getVar("pole_picked",False):
        e.variables["pole_picked"] = True
        # got fishing pole animation
        e.player.inventory.append(
            Item("pole", "Fishing pole",
                 description="Great pole but the hook is missing.",
                 ))
        e.a.playAnimation("pole")
        return True
    elif e.getVar("pole_picked",False):
        e.player.buildHelpLine("I have already got the fishing pole.")
        return True
    return False

def onDoorUse(item,item2,e):

    if item2 is not None and item2.ID=="key":
        e.player.inventory.remove(item2)
        e.s.cs().exits[2][2]=1
        e.player.buildHelpLine("Door unlocked!")
        return True
    else:
        e.player.buildHelpLine("Door is Locked!")
    return True

def onWinCheck(item,e):
    if e.getVar("flat_tire",False):
        item.DESCRIPTION="Oh, there is everything I need to fix that tire."
    else:
        item.DESCRIPTION="Oh, I can see a mouse on the table but I can't get in!"

def onTrapCheck(item,e):
    if e.getVar("hook_checked"):
        e.variables["trap_checked"] = True
        item.DESCRIPTION="And know that there is a pole in there but I can't reach it"
    else:
        item.DESCRIPTION="I can't reach it from here and what should I do in the attic?"


def onLadderUse(item,item2,e):
    if e.s.cs().ID=="workshop":
        e.player.inventory.remove(item)
        e.variables["workshop_meta"]=1
        e.player.buildHelpLine("Now I can get to the attic.")
        return True
    return False

class ScreenWorkshop(Screen):
    def __init__(self):
        super().__init__("workshop", "In front of the Workshop", otherName="Workshop")
        self.exits = [["bicycle"], ["garden_left"],["inside_workshop","To Workshop",0]]
        self.items = [Item("work_door", "Door",
                           description="The key is required to unlock it",
                           onUse=onDoorUse
                           ),
                      Item("work_window", "Window",
                           onCheck=onWinCheck
                           ),
                      Item("trapdoor", "Attic door",
                           onUse=onTrapdoorUse,
                           onCheck=onTrapCheck
                           ), ]


class ScreenWorkshopInside(Screen):
    def __init__(self):
        super().__init__("inside_workshop", "Workshop", otherName="Workshop")
        self.exits = [["workshop"]]
        self.items = [Item("tools", "Mending Tools",
                           description="I can repair everything with it",
                           pickable=True
                           ),
                     ]


def onBiUse(item,item2,e):
    if item2 is not None and item2.ID=="tools":
        e.a.playAnimation("end")
        e.exit(save=False,discard=True)
        #animation to go........
    else:
        if e.getVar("flour_checked"):
            e.player.buildHelpLine("Let's go get some flour... oh no, the tire is flat.")
            e.variables["flat_tire"]=True
        else:
            e.player.buildHelpLine("I don't need to go anywhere.")
    return True

class ScreenBicycle(Screen):
    def __init__(self):
        super().__init__("bicycle", "Road to town")
        self.exits = [["garden_left"], ["workshop"]]

        self.items = [Item("bicycle", "Bicycle",
                           description="My old bicycle, my only connection with th world.",
                           onUse=onBiUse
                           ),

                            ]

def onWellUse(item,item2,e):
    if item2 is None:
        return False
    if item2.ID=="pole_hook":
        e.player.inventory.append(
            Item("key", "Workshop key",
                 description="Opens the workshop.",
                 ))
        e.variables["well_in_key"]=False
        e.player.inventory.remove(item2)
        e.player.buildHelpLine("Yesss. I have the key!")
        return True
    elif item2.ID=="hook":
        e.player.buildHelpLine("This hook is too small.")
        return True
    elif item2.ID=="pole":
        e.player.buildHelpLine("I can reach it but it doesn't stick to the thread")
        return True
    return False

def onWellCheck(item,e):
    e.variables["well_check"]=True
    if e.getVar("well_in_key",True):
        e.a.playAnimation("well_in_key")
    else:
        e.a.playAnimation("well_no_key")
    return "consume"

class ScreenWell(Screen):
    def __init__(self):
        super().__init__("well", "Behind the Woodshed", otherName="Woodshed")
        self.exits = [["garden_right"], ["well_2", "Well", 0]]
        self.items = [Item("well", "Well",
                           description="It provides fresh water",
                           onCheck=onWellCheck,
                           onUse=onWellUse
                           ),
                    ]

def onBullCheck(item,e):
    if e.getVar("bull_meta",0)==0 and e.getVar("ladder_checked",False):
        e.variables["bull_checked"]=True
        item.DESCRIPTION="He is old and little deaf, I can't shout laud enough to make him leave that ladder"
    elif e.getVar("bull_meta",0)==0:
        item.DESCRIPTION="He is old and little deaf. and sleeping on a ladder"
    elif e.getVar("bull_meta",0)==1:
        item.DESCRIPTION="Now you (old bull) will enjoy the tones of Mozart"
    elif e.getVar("bull_meta", 0) == 2 or e.getVar("bull_meta", 0) == 3:
        item.DESCRIPTION = "He has run away. He doesn't seem to be enjoying Mozart"

def onLadderPick(item,e):
    if e.getVar("hook_checked",False) and e.getVar("trap_checked",False):
        e.variables["ladder_checked"]=True
        if  e.getVar("bull_meta",0)==2:
            e.variables["bull_meta"] = 3
            return True
        else:
            e.player.buildHelpLine("I can't pick it, because there is a bull sleeping on it!")
        return False
    else:
        e.player.buildHelpLine("I'm not going to repaint the house now.")

class ScreenBull(Screen):
    def __init__(self):
        super().__init__("bull", "Land")
        self.exits = [["garden_right"]]
        self.items = [Item("bull", "Bull",
                           onCheck=onBullCheck
                           ),
                      Item("ladder", "Ladder",
                           description="Ladder which will reach heavens. If there isn't of course a bull sleeping on it",
                           onpick=onLadderPick,
                           onUse=onLadderUse

                           ),
                     ]
