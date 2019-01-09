import graphics
import drawticks
import screens
import saver
import command
import animation
from util import toArray

def startEngin():
    e.start()

def loadFuk():
    global e
    old= e
    loaded = saver.loadGame()
    if loaded is None:
        print("cannot load")
        return False
    else:
        old.running=False
        e=loaded
        e.player.switchInventory(False)
        e.player.switchItem(False)
        e.player.switchLoc(False)
        e.player.showInfoPanel(False)
        e.r.clear()
        print("Loading Saved game: ",e.id)
        e.start()
        return True


class Engine:
    def __init__(self):
        import datetime
        self.id=datetime.datetime.now().strftime("%Y-%m-%d %H:%M:%S")
        self.g = graphics.Graphics(53, 30)
        self.r = graphics.Renderer(self.g)
        self.s = screens.ScreenManager(self.r)
        self.c = command.CommandManager()
        self.a = animation.AnimationPlayer(self)
        self.variables = {}#state:(animation,location,intro)
        self.date=None

        self.player = None

        self.running = False

    def loadGame(self):
        return loadFuk()

    def getVar(self,key,defaultVal=""):
        try:
            return self.variables[key]
        except KeyError:
            self.variables[key]=defaultVal
            return self.variables[key]
    def start(self):
        self.r.clear()
        self.s.setCurrent("intro",self)
        self.running = True
        self.loop()

    def loop(self):
        while self.running:
            self.update()
            self.r.render()
            self.command(input())
            # time.sleep(1)

    def update(self):
        if self.variables["state"]=="animation":
            pass
        else:
            self.player.rebuild()
            self.s.tick(self)

    def load(self):
        self.running=False
        Engine.e = saver.loadGame()
        if e is not None:
            e.start()
            e.player.buildHelpLine("Game loaded!")
        else:
            self.running = True
            self.player.buildHelpLine("There is not anything to load!")
            Engine.e = self

    def save(self):
        import datetime
        self.variables["animationFrame"] = e.a.getCurrentAnimationFrame()
        self.s.getScreen("intro").saveIntro = "Last save: " + datetime.datetime.now().strftime("%Y-%m-%d %H:%M")
        print(str(datetime.datetime.now()))
        print("Saving game... ", end="")
        suc = saver.saveGame(self)
        print("Success" if suc else "Failure")
        return suc

    def exit(self,save=True,discard=False):
        self.running = False
        j = saver.loadImage("end")
        if j:
            self.g.clear()
            self.g.drawBounds()
            self.g.drawBitmap(1,1,j)
            self.g.render()
        if discard:
            saver.clear()
            print("Game state deleted")
        if save:
           self.save()
        print("Game quited")

    def command(self, command):
        self.c.command(command,self)

class Player:
    def __init__(self, e):
        # type: (engine.Engine) -> None
        self.e = e
        self.infoPanel = drawticks.TextList(10, 4, [], False, 30, 20, "Help")
        self.locPanel = drawticks.TextList(self.e.g.WIDTH-8, 1, [], False, 8, 5, "Locations")
        self.itemPanel = drawticks.TextList(self.e.g.WIDTH-8, 8, [], False, 8, 10, "Loc Items")
        self.inventoryPanel = drawticks.TextList(1, 1, [], False, 8, 15, "Inventory")
        self.locItemList = []       # type: list
        self.locList = []           # type: list
        self.inventory = []         # type: list


        self.helpLine = drawticks.Text(1, e.g.HEIGHT - 2, "Type \"help\" to see all commands, or \"play\"")
        self.locPanelActive = False
        self.itemPanelActive = False
        self.inventoryPanelActive = False


        self.rebuild()

        self.state = ""

    def getInventoryItem(self,itemName):
        item = None
        if toNumber(itemName) in range(0, len(self.inventory)):
            item = self.inventory[toNumber(itemName)]
        else:
            for ite in self.inventory:
                if ite.NAME.lower() == itemName.lower() or (ite.NAME.lower().startswith(itemName.lower()) and len(itemName) >= 3):
                    item = ite
                    break
        return item

    def getLocItem(self, itemName):
        item = None
        if toNumber(itemName) in range(len(self.inventory), len(self.inventory)+len(self.locItemList)):
            item = self.locItemList[toNumber(itemName)-len(self.inventory)]
        else:
            for ite in self.locItemList:
                if ite.NAME.lower() == itemName.lower() or ( ite.NAME.lower().startswith(itemName.lower()) and len(itemName) >= 3):
                    item = ite
                    break
        return item

    def getItem(self,itemName):
        out = self.getLocItem(itemName)
        if out is None:
            out = self.getInventoryItem(itemName)
        return out
        item = None
        if toNumber(itemName) in range(0, len(self.inventory)):
            item = self.inventory[toNumber(itemName)]
        elif toNumber(itemName) in range(len(self.inventory),len(self.inventory)+len(self.locItemList)):
            item = self.locItemList[toNumber(itemName)-len(self.inventory)]
        else:
            for ite in e.player.inventory:
                if ite.NAME.lower()==itemName.lower() or (ite.NAME.lower().startswith(itemName.lower()) and len(itemName)>=3):
                    item = ite
                    break
            if item is None:
                for ite in e.player.locItemList:
                    if ite.NAME.lower() == itemName.lower() or (ite.NAME.lower().startswith(itemName.lower()) and len(itemName) >= 3):
                        item = ite
                        break
        return item

    def rebuild(self):
        self.e.r.add(self.helpLine)
        self.switchLoc(self.locPanelActive)
        self.switchItem(self.itemPanelActive)
        self.switchInventory(self.inventoryPanelActive)

    def newloc(self):
        self.switchItem(False)
        self.locItemList=[]
        self.locList = []

    def buildHelp(self,array,name="Help (esc to exit)"):
        self.infoPanel.textArray=array
        self.infoPanel.name = name

    def buildInventory(self):
        array = []

        index = 0
        for item in self.inventory:
            array.append(str(index)+" "+item.NAME)
            index+=1
        self.inventoryPanel.textArray=array

    def buildItemList(self):
        self.locItemList = []
        array = []
        index = len(self.inventory)
        for item in e.s.cs().getItems():
            if item.visible:
                self.locItemList.append(item)
                array.append(str(index) + " " + item.NAME)
                index += 1
        self.itemPanel.textArray = array

    def switchInventory(self,on):
        self.inventoryPanelActive = on
        if on:
            self.buildInventory()
            self.e.r.add(self.inventoryPanel)
        else:
            self.e.r.remove(self.inventoryPanel)

    def buildInfo(self):
        self.infoPanel.textArray = [
            "Birthday Cake The Game:",
            "-Minimalistic text adventure game with graphics!",
            "",
            "Author: Matej Cerny",
            "Development:",
            "   Start date: 27.12.",
            "   End date:   2.1.",
            "   Estimated time:   24hrs",
            "",
            "Copyright: CC BY-SA",
            "Year: 2018",
        ]
        self.infoPanel.name = "Game Info (esc to exit)"

    def showInfoPanel(self,on=True):
        if on:
            self.e.r.add(self.infoPanel)
        else:
            self.e.r.remove(self.infoPanel)

    def buildItemInfo(self,item):
        self.infoPanel.textArray = toArray(item.DESCRIPTION,40)
        self.infoPanel.name = "Item: "+ item.NAME

    def buildBoolQuery(self,question,addInfo=""):
        self.infoPanel.textArray = [
            "Y / N",
            "",
            addInfo
        ]
        self.infoPanel.name =question

    def buildHelpLine(self, string,addMode=False):
        if addMode and string!="":
            self.helpLine.text +=" | "+ string+" "
        else:
            self.helpLine.text = string+" "

    def switchLoc(self, on):
        self.locPanelActive = on
        if on:
            self.buildLoc()
            self.e.r.add(self.locPanel)
        else:
            self.e.r.remove(self.locPanel)

    def switchItem(self, on):
        self.itemPanelActive = on
        if not on:
            self.e.r.remove(self.itemPanel)
        else:
            self.buildItemList()
            self.e.r.add(self.itemPanel)

    def buildLoc(self):
        self.locList = []
        array = []
        index = 0
        for loc in e.s.cs().getExits(e):
            if loc[2] == 1:
                self.locList.append(loc)
                array.append(str(index) + " " + loc[1])
                index+=1
        self.locPanel.textArray = array

def toNumber(str):
    try:
        return int(str)
    except ValueError:
        return -1


e = Engine()
e.player = Player(e)
e.start()







