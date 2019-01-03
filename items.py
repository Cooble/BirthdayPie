
def useBlank(item,item2,e):#item which calls it,other item(might be None), engine,
    pass
def checkBlank(item,e):#item which calls it, engine, ->return true if check phrase should be called
    return False
def pickBlank(item,e):#called when tried to pick up,item which calls it, engine, ->return true if can be picked up
    return False


class Item:
    def __init__(self,id,name,description="",pickable=False,pickPhrase="WTF?",visible=True,
                 creationPhrase="",onCheck=checkBlank,onCheckPhrase="",onUse=useBlank,onpick=None):#pickphrase used when try to pick up (pickable doesnt matter)
        self.onpick = onpick
        self.onCheckPhrase = onCheckPhrase
        self.onCheck = onCheck#returns true if oncheckphrase to be played
        self.onUse = onUse
        self.creationPhrase = creationPhrase
        self.visible = visible
        self.pickPhrase = pickPhrase
        self.pickable = pickable
        self.ID = id
        self.NAME=name
        self.DESCRIPTION=description
        self.checked=False

#if returns item it might mark source items as invisible to be removed
def crafter(item0,item1):#returns new item if combination was successful
    array = [item0,item1]
    if isThoseTwo(array,"branch","key"):
        getItem(array,"branch").visible=False
        getItem(array,"key").visible=False
        return Item("key_on_stick","Key on Stick","Key with extended range",creationPhrase="What an invention!")
    if isThoseTwo(array, "pole", "hook"):
        getItem(array, "pole").visible = False
        getItem(array, "hook").visible = False
        return Item("pole_hook", "Pole with hook", "Highly trained fisherman is worth high quality pole.", creationPhrase="Now I can reach for that key")


    return None
def isThoseTwo(array,name0,name1):
    return getItem(array,name0) is not None and getItem(array,name1) is not None

def getItem(array,name):
    for i in array:
        if i.ID.lower()==name.lower():
            return i
    return None