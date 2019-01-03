import items,util,sys
class Command:
    def __init__(self, name, description, aliases=None):
        self.DESCRIPTION = description
        self.NAME = name
        if aliases is None:
            aliases = []
        if len(name)>3 and not (name[:3]  in aliases):
            aliases.append(name[:3])
        aliases.insert(0,name)
        self.aliases = aliases
        self.alpha = False
        self.stateMustBe = None
        self.stateMustNotBe = None
        self.longDescription=description
        self.examples = ()

    def command(self, command, e):
        spli = command.split(" ")
        if len(spli)==0:
            return False
        if self.NAME.startswith(spli[0]) and  len(spli[0])>=3:
            return self.innerCommandTrue(command, spli, e)
        if spli[0] in self.aliases:
            return self.innerCommandTrue(command, spli, e)
        return False

    def innerCommandTrue(self, command, spli, e):
        return True

class CommandInfo(Command):
    def __init__(self):
        super().__init__("info", "Shows important info about the game")

    def innerCommandTrue(self, command, spli, e):
        e.player.buildInfo()
        e.player.showInfoPanel()
        return True

class CommandPlay(Command):
    def __init__(self):
        super().__init__("play", "play game",aliases=["p","pl"])
        self.stateMustBe=["intro"]
        self.longDescription="Starts the game.\n" \
                             " If you haven't played before, it will start fresh.\n " \
                             "If you have saved the game, it will load it."


    def innerCommandTrue(self, command, spli, e):
        if e.s.lastScreen=="intro":
            e.s.lastScreen="kitchen"

        e.s.setCurrent(e.s.lastScreen,e)
        tupl = e.getVar("animationFrame",("",-1))
        if tupl[0] != "":  # we have animation going
            e.a.playAnimation(tupl[0])
            e.a.cs().currentFrame=tupl[1]

        return True

class CommandLoad(Command):
    def __init__(self):
        super().__init__("load", "Loads the game")
        self.stateMustBe=["intro"]

    def command(self, command, e):
        if self.alpha:
            if command.lower().split(" ")[0] == "y":
                self.alpha = False
                if e.loadGame():
                    sys.exit(0)
                else:
                    e.player.buildHelpLine("Cannot load the game")
            else:
                e.player.showInfoPanel(False)
                self.alpha = False

            return True

        if command == "load":
            addin = "(You will loose current unsaved progress)"
            e.player.buildBoolQuery("Do you really want to load the game? (esc to exit)",addInfo=addin)
            e.player.showInfoPanel()
            self.alpha = True
            return True
        return False

class CommandSave(Command):
    def __init__(self):
        super().__init__("save", "Saves game",aliases=["s"])

    def innerCommandTrue(self, command, spli, e):
        suc = e.save()
        if suc:
            e.player.buildHelpLine("Game saved")
        elif not suc:
            e.player.buildHelpLine("Game can't be saved")
        return True

class CommandReset(Command):
    def __init__(self):
        super().__init__("reset", "Reset the whole game and quit")
        self.longDescription+=" (All data will be lost)"

    def command(self, command, e):
        if self.alpha:
            if command.lower().split(" ")[0] == "y":
                self.alpha = False
                e.exit(save=False,discard=True)
            else:
                self.alpha = False
                e.player.showInfoPanel(False)
            return True
        return super().command(command, e)

    def innerCommandTrue(self, command, spli, e):
        e.player.buildBoolQuery("Do you really want to reset the game? (all data will be discarded) (esc to exit)")
        e.player.showInfoPanel()
        self.alpha = True
        e.exit(save=False, discard=True)
        return True

class CommandExit(Command):
    def __init__(self):
        super().__init__("exit", " Saves and exits the game")
        self.longDescription="exit - save and exit the game\n exitd - discard current game state and exit"
        self.d=False

    def command(self, command, e):
        if self.alpha:
            if command.lower().split(" ")[0] == "y":
                self.alpha = False
                e.exit()
            else:
                e.player.showInfoPanel(False)
                self.alpha = False

            return True

        if command=="exit" or command=="exitd":
            self.d = command=="exitd"
            if self.d:
                e.player.buildBoolQuery("Do you really want to save and quit the game? (esc to exit)")
            else:
                e.player.buildBoolQuery("Do you really want to quit the game without saving? (esc to exit)",addInfo="(Any non saved data will be lost)")
            e.player.showInfoPanel()
            self.alpha = True
            return True
        return False

class CommandHelp(Command):
    def __init__(self):
        super().__init__("help", "Type \"help (command)\" to check com.")
        self.longDescription="You had to try that, didn't you? :)\n Type \"help (command_name)\" to check command"

    def innerCommandTrue(self, command, spli, e):
        if len(spli)==2:
            arg = spli[1]
            for comm in e.c.list:
                if comm.NAME.lower()==arg.lower() or (comm.NAME.lower().startswith(arg.lower()) and len(arg)>=3):
                    ray = util.toArray(comm.longDescription,60)
                    if len(comm.examples)!=0:
                        ray.append("")
                        ray.append("Examples:")
                        for ex in comm.examples:
                            ray.append(ex)
                    ray.append("")
                    ray.append("Aliases:")
                    s = ""
                    for alias in comm.aliases:
                        s+=alias+", "
                    if len(s)!=0:
                        s=s[:-2]
                    ray.append(s)
                    e.player.buildHelp(ray,name="Description of command: \""+comm.NAME+"\"")
                    e.player.showInfoPanel()
                    return True

        e.player.buildHelp(e.c.getHelp())
        e.player.showInfoPanel()
        return True

class CommandEsc(Command):
    def __init__(self):
        super().__init__("esc", "Hides infoPanel", aliases=["escape"])
        self.longDescription+=", that's the one this text is currently in"
        self.longDescription+="\n Really, just type it now to see this window disappear!"

    def innerCommandTrue(self, command, spli, e):
        if len(spli) != 1:
            arg = spli[1]
            if arg == "l":
                e.player.switchLoc(False)
            elif arg == "i":
                e.player.switchItem(False)
        else:
            e.player.showInfoPanel(False)
        return True

class CommandGo(Command):
    def __init__(self):
        super().__init__("go", "Goes to a location",aliases=["g"])
        self.stateMustBe=["location"]
        self.longDescription="Usage:\n " \
                             "go - show/hide the panel with locations\n " \
                             "go (location_name/location_number) - it will get you to specified location"
        self.examples="go Cellar","go 0"

    def innerCommandTrue(self, command, spli, e):
        if len(spli) == 1:
            e.player.switchLoc(not e.player.locPanelActive)
        else:
            e.player.switchLoc(True)
            loc = spli[1]
            targetLoc = -1
            possibleOutcomes = e.s.cs().getExits(e)
            if toNumber(loc) in range(0, len(e.player.locList)):
                targetLoc = 0
                e.s.setCurrent(e.player.locList[toNumber(loc)][0],e)
            else:
                for i in possibleOutcomes:
                    if str(i[1]).lower() == loc.lower() or (str(i[1]).lower().startswith(loc.lower()) and len(loc.lower())>=3):
                        targetLoc = 0
                        e.s.setCurrent(i[0],e)
                        break
            if targetLoc == -1:
                e.player.buildHelpLine("This loc does not exist, choose from following.")
                e.player.switchLoc(True)
            else:
                e.player.buildHelpLine("You are in " + e.s.cs().NAME)
        return True

class CommandCheck(Command):
    def __init__(self):
        super().__init__("check", "Checks item",aliases=["c","ch"])
        self.stateMustBe=["location"]
        self.longDescription = "Shows additional info for item in inventory or in location.\n" \
                               "Usage:\n " \
                               "check - toggles check panel that shows items in location\n" \
                               "check (item)"
        self.examples="check chimney","check 0"

    def innerCommandTrue(self, command, spli, e):
        if len(spli) == 1:
            if not e.player.itemPanelActive:
                e.player.buildHelpLine("You looked for items in location")
            e.player.switchItem(not e.player.itemPanelActive)
        else:
            e.player.switchItem(True)
            itemName = spli[1]
            item = e.player.getItem(itemName)
            if item is not None:
                e.player.buildHelpLine("You have checked " + item.NAME)
                o =  item.onCheck(item, e)
                if o=="consume":
                    item.checked = True
                    return True
                elif o:
                    e.player.buildHelpLine(item.onCheckPhrase, addMode=True)
                e.player.buildItemInfo(item)
                e.player.showInfoPanel()
                item.checked=True
            else:
                e.player.buildHelpLine("This item is not here")
        return True

class CommandUse(Command):
    def __init__(self):
        super().__init__("use", "Uses an item (or even on different item)",aliases=["u","us"])
        self.stateMustBe=["location"]
        self.longDescription = "Performs an action with the item\n" \
                               "Usage:\n " \
                               "use (item)\n" \
                               "use (item0) (item1) - use item on another one\n"
        self.examples="use door - opens the door","use door key - unlocks the door","use key door - unlocks the door"

    def innerCommandTrue(self, command, spli, e):
        if len(spli) == 1:
            e.player.buildHelpLine("You need to specify at least one item!")
        else:
            item0 = e.player.getItem(spli[1])
            item1 = None
            if len(spli)==3:
                item1 = e.player.getItem(spli[2])

            if item0 is not None and not item0.onUse(item0,item1,e):
                if item1 is not None:
                    if not item1.onUse(item1, item0, e):
                        e.player.buildHelpLine("You cannot use "+item0.NAME+("" if item1 is None else" on "+item1.NAME))
                else:
                    e.player.buildHelpLine("You cannot use " + item0.NAME)

            if item0 is None or (len(spli)==3 and item1 is None):
                e.player.buildHelpLine("Invalid item(s)!")
        return True

class CommandInventory(Command):
    def __init__(self):
        super().__init__("inventory", "Opens players inventory",aliases=["i","inv","in"])
        self.stateMustBe=["location"]
        self.longDescription = "Toggles inventory panel that shows all items player currently has"

    def innerCommandTrue(self, command, spli, e):
        if e.s.currentScreen==0:
            e.player.buildHelpLine("You are not in play mode!")
            return True
        print("Inv open "+str(e.player.inventoryPanelActive))
        e.player.switchInventory(not e.player.inventoryPanelActive)
        return True

class CommandPick(Command):
    def __init__(self):
        super().__init__("pick", "Picks up item in location",aliases=["p","pi"])
        self.stateMustBe=["location"]
        self.longDescription = "Picks item from location and adds it to player inventory\n" \
                               "Note: you have to check item first\n\n" \
                               "Usage:\n " \
                               "pick (item)\n"
        self.examples="pick branch",""

    def innerCommandTrue(self, command, spli, e):
        if len(spli) == 1:
            e.player.buildHelpLine("You need to specify item to pick up!")
        else:
            itemName = spli[1]
            item = e.player.getLocItem(itemName)
            if item is not None:
                if not item.checked:
                    e.player.buildHelpLine("You need to check item first before you pick it!")
                elif item.onpick is not None:
                    if item.onpick(item,e):
                        e.player.inventory.append(item)
                        e.s.cs().items.remove(item)
                        if e.player.buildHelpLine=="":
                            e.player.buildHelpLine("You have picked " + item.NAME + " - " + item.pickPhrase)
                elif item.pickable:
                    e.player.inventory.append(item)
                    e.s.cs().items.remove(item)
                    e.player.buildHelpLine("You have picked " + item.NAME + " - " + item.pickPhrase)
                else:
                    e.player.buildHelpLine(item.pickPhrase)
            else:
                e.player.buildHelpLine("This item is not here")
        e.player.switchItem(True)
        return True

class CommandCombine(Command):
    def __init__(self):
        super().__init__("combine", "Combine 2 items in inventory",aliases=["com","cmb"])
        self.stateMustBe=["location"]
        self.longDescription = "Combines 2 inventory items to make third one\n" \
                               "Usage:\n " \
                               "combine (item0) (item1)\n"
        self.examples="combine hot_water cocoa - makes one good beverage :)",""

    def innerCommandTrue(self, command, spli, e):
        if e.s.currentScreen==0:
            e.player.buildHelpLine("You are not in play mode!")
            return True
        if len(spli) !=3:
            e.player.buildHelpLine("You need to specify two items from inventory to combine!")
        else:
            item0 = e.player.getInventoryItem(spli[1])
            item1 = e.player.getInventoryItem(spli[2])
            if item0 is None or item1 is None:
                e.player.buildHelpLine("Invalid inventory items")
                return True
            if item0==item1:
                e.player.buildHelpLine("You cannot combine item with itself!")
                return True
            outItem = items.crafter(item0,item1)
            if outItem is None:
                e.player.buildHelpLine("Cannot combine those items")
                return True
            if not item0.visible:
                e.player.inventory.remove(item0)
            if not item1.visible:
                e.player.inventory.remove(item1)
            e.player.inventory.append(outItem)
            e.player.buildHelpLine("You have combined "+item0.NAME+" and "+item1.NAME+" to make "+outItem.NAME)
            e.player.buildHelpLine(outItem.creationPhrase,addMode=True)

        e.player.switchInventory(True)
        return True
    def getItem(self,itemName,e):
        item = None
        if toNumber(itemName) in range(0, len(e.player.inventory)):
            item = e.player.inventory[toNumber(itemName)]
        else:
            for ite in e.player.inventory:
                if itemName.lower() == ite.NAME.lower():
                    item = ite
                    break
        return item

class CommandGuide(Command):
    def __init__(self):
        super().__init__("guide", "Shows how to play (no spoilers)",aliases=["guide2","g2","g1","návod"])


    def innerCommandTrue(self, command, spli, e):
        if command=="guide2" or command=="g2":
            ray = []
            ray.append("Locations:")
            ray.append("To see where you can go type \"go\"")
            ray.append("(to hide it type \"go\" again)")
            ray.append("You can \"go (location)\" to get there.")
            ray.append("")
            ray.append("That's it!")

            e.player.buildHelp(ray, name="How to play the game              (type \"g1\" to 1st list)")
            e.player.showInfoPanel()
        elif command!="guide2":
            ray = []
            ray.append("You have just started and then what.")
            ray.append("Well thanks God there is this guide.")
            ray.append("")
            ray.append("Checking:")
            ray.append("First you have to check location with command \"check\".")
            ray.append("Item Panel popped up in the right corner of the screen.")
            ray.append("(to hide it type \"check\" again)")
            ray.append("Here you can see all items which are available in this loc.")
            ray.append("Next to item names are numbers,")
            ray.append("you can use them in commands instead of their names.")
            ray.append("You can \"check (item)\" to see info about it.")
            ray.append("You can try \"pick (item)\" to put it into inventory.")
            ray.append("")
            ray.append("Inventory:")
            ray.append("To see inventory type \"i\"")
            ray.append("(to hide it type \"i\" again)")
            ray.append("There is another list of items,")
            ray.append("but these are with you no matter where you go.")
            ray.append("-> Type \"g2\" to see next list")
            e.player.buildHelp(ray, name="How to play the game              (type \"g2\" to next list)")
            e.player.showInfoPanel()
        return True

class CommandSpoilers(Command):
    def __init__(self):
        super().__init__("spoilers", "Complete walkthrough to beat this game",aliases=["spoilit","spoilit1","spoilit2"])


    def innerCommandTrue(self, command, spli, e):
        if command=="spoilit" or command=="spoilit1":
            ray = ["You found yourself in the kitchen",
                   "type \"check\" to see what can you pick",
                   "type \"check food\" to see whats in cabinet",
                   "check flour", "We have run out of flour",
                   "type \"go liv\" to get to the living room",
                   "check picture, go to the picture",
                   "check hook - he tells you that in the attic is a pole",
                   "go to hall, go to left garden, go to road",
                   "try to use bicycle to get to town and buy flour",
                   "go to workshop and check window,",
                   "There are mending tools to fix that bike",
                   "check door - its locked",
                   "go to the right garden, woodshed",
                   "check well - oh there's the key to unlock workshop",
                   "But how to get it?",
                   "in the living room picture there was fisherman!",
                   "go back to the picture",
                   "pick hook",
                   ]
            e.player.buildHelp(ray, name="Walk-through         (type \"spoilit2\" to next list)")
            e.player.showInfoPanel()
        elif command == "spoilit2":
            ray = [
                   "you can try to use it to get key out of the well,",
                   "but it won't work, we need fishing pole with hook!",
                   "go to workshop and check trapdoor",
                   "we can't get to it",
                   "go to land, there is a ladder",
                   "check the ladder and try to pick it",
                   "it won't work because there's a bull sleeping on it",
                   "check bull, we find out",
                    "that we need something laud to wake him up",
                   "oh that could be the gramophone in the hall",
                   "pick that gramophone and use it on bull",
                   "bull is gone and we can pick the ladder",
                   "use ladder on attic_door and use attic_door",
                   "we got the fishing pole",
                   "combine it with hook to produce pole with hook",
                   "use this pole to get the key from well",
                   "use the key to unlock the workshop door",
                   "go inside workshop and pick mending tools",
                   "use tools on bike to mend it.. The End!"
                   ]
            e.player.buildHelp(ray, name="Walk-through         (type \"spoilit1\" to 1st list)")
            e.player.showInfoPanel()
        else:
            ray = ["You find yourself struggling to move forward.",
                   "",
                   "To see walk-through type \"spoilit\":",
                   "",
                   "(Type \"esc\" to close this window)"
                   ]

            e.player.buildHelp(ray, name="Walk-through - how to beat the game")
            e.player.showInfoPanel()
        return True

class CommandNext(Command):
    def __init__(self):
        super().__init__("next", "Moves to next slide in animation",aliases=["n","enter"])
        self.stateMustBe=["animation"]
        self.longDescription+="\n You can also just press enter to next slide"

    def command(self, command, e):
        if command=="" or command=="next" or command==" ":
            e.player.showInfoPanel(on=False)
            if e.a.next():
                e.s.setCurrent(e.s.currentScreen,e)
            return True
        return False

class CommandTest(Command):
    def __init__(self):
        super().__init__("test", "debug")
        self.longDescription="This is private"

    def command(self, command, e):
        if command=="test":
            print(e.id)

        return "test" in command

class CommandMenu(Command):
    def __init__(self):
        super().__init__("menu", "Gets to main menu")
    def innerCommandTrue(self, command, spli, e):
        e.player.showInfoPanel(False)
        e.player.switchInventory(False)
        e.player.switchLoc(False)
        last = e.s.lastScreen
        cur = e.s.currentScreen
        e.s.setCurrent("intro",e)
        if cur=="intro":
            e.s.lastScreen=last
        else:
            e.s.lastScreen=cur
        return True

class CommandManager:
    def __init__(self):
        self.list = []
        self.list.append(CommandHelp())
        self.list.append(CommandGuide())
        self.list.append(CommandPlay())
        self.list.append(CommandSave())
        self.list.append(CommandLoad())
        self.list.append(CommandReset())
        self.list.append(CommandExit())
        self.list.append(CommandInfo())
        self.list.append(CommandEsc())

        self.list.append(CommandGo())
        self.list.append(CommandCheck())
        self.list.append(CommandPick())
        self.list.append(CommandUse())
        self.list.append(CommandInventory())
        self.list.append(CommandCombine())

        self.list.append(CommandNext())
        self.list.append(CommandTest())
        self.list.append(CommandSpoilers())
        self.list.append(CommandMenu())

    def getHelp(self):
        out = []
        for command in self.list:
            out.append(extendToChar(command.NAME, 7) + " - " + command.DESCRIPTION)
        return out

    def command(self, command, e):
        e.player.buildHelpLine("")
        done = False
        for c in self.list:
            if c.alpha:
                c.command(command, e)
                done = True
                break
        command = command.replace("  "," ")
        command = command.replace("  "," ")
        if not done:
            for c in self.list:
                if c.stateMustBe is not None:
                    state = e.variables["state"]
                    if not (state in c.stateMustBe):
                        continue
                if c.stateMustNotBe is not None:
                    state = e.variables["state"]
                    if state in c.stateMustBe:
                        continue
                if c.command(command, e):
                    done = True
                    break
        if not done:

            if command=="" or command==" ":
                self.command("esc",e)
            else:
                e.player.buildHelpLine("This command doesn't exist, or you can't use it now. Type \"help\" to see all available commands.")

def toNumber(str):
    try:
        return int(str)
    except ValueError:
        return -1

def extendToChar(string, targetSize):
    if targetSize < len(string):
        return string
    for i in range(targetSize - len(string)):
        string += " "
    return string
#0-id,1-name,2-visible