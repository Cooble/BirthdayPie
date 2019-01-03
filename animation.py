import drawticks
import saver
class Animation(drawticks.Drawable):
    def __init__(self,id):
        self.id = id
        self.frames = []
        self.currentFrame=0
        self.image = None
        self.lastImageName = None

    def start(self):
        self.currentFrame=0

    def sc(self):
        return self.frames[self.currentFrame]

    def next(self): #return true if its on last image
        self.currentFrame+=1
        if self.currentFrame==len(self.frames):#check if overflow
            self.currentFrame = 0
            return True
        return False

    def add(self,frame):
        self.frames.append(frame)

    def draw(self, g):
        nowImageName = self.sc()[0]
        if nowImageName!=self.lastImageName or self.image is None:
            self.image = saver.loadImage(nowImageName)
            self.lastImageName=nowImageName

        g.clear()
        g.drawBitmap(1,1,self.image)
        g.drawRectangle(0,0,g.WIDTH,g.HEIGHT,clearWithin=False)
        bubbles = self.sc()[1]
        for bubble in bubbles:
            inverse = False
            arra = bubble.copy()
            if len(bubble)==1:
                arra.append("")
                arra.append(1)
                arra.append(g.HEIGHT)
                arra.append(g.WIDTH-1)
                inverse =True
            elif len(bubble)==2:
                arra.append(1)
                arra.append(g.HEIGHT)
                arra.append(g.WIDTH-1)
                inverse =True
            if arra[1]!="":
                text = arra[1] + ":\n\n" + arra[0]
            else:
                text = arra[0]
            text="\n"+text+"\n"

            drawticks.TextArea(x=arra[2],y=arra[3],text=text,width=arra[4],yInverse=inverse).draw(g) #text,name,x,y,width


class AnimationPlayer:
    def __init__(self,e):
        self.e = e
        self.array = []
        self.currentAnimation = -1

        animation = Animation("intro")
        animation.add(["morning",[]])
        animation.add(["morning",[["It is one cold and dreary autumn morning on the farm.\n Old Farmer in his 60s is about to wake up. "]]])
        animation.add(["morning",[["I opened my eyes "
                                   "in a bedroom which seems to be quite empty after my wife passed away 15 years ago.","Farmer"]]])
        animation.add(["morning",[["But this day is somehow special:\n My Kitty cat has birthday.\n "
                                   "5th time this year but whatever.\n I have to get up and make him a Birthday Cake!","Farmer"]]])

        self.array.append(animation)

        animation = Animation("flour")
        animation.add(["flour_0", []])
        animation.add(["flour_0", [["It's nice bag of flour but......"]]])
        animation.add(["flour_1", []])
        animation.add(["flour_1", [["It's empty!!"]]])
        animation.add(["flour_1", [["Oh, that's unfortunate, we don't have flour. How am I supposed to make a birthday cake for "
                               "my cat when there is no flour :(\nMaybe I could buy it in the village!"]]])
        self.array.append(animation)

        animation = Animation("kitchen")
        animation.add(["kitchen_0", [["My Kitty Cat has birthday.\n "
                                   "5th time this year but whatever.\n I have to make him a Birthday Cake!\n I will need flour!","Farmer"]]])
        self.array.append(animation)


        animation = Animation("well_in_key")
        animation.add(["well_2_0",[]])
        animation.add(["well_2_0", [["I really wonder how did the key to the workshop get here. I can't reach it!"]]])
        animation.add(["well_2_0", [["Wish I have something long to get it out from down there."]]])
        self.array.append(animation)

        animation = Animation("well_no_key")
        animation.add(["well_2_1", []])
        animation.add(["well_2_1", [["It was lot of work but I finally got that key out of there!"]]])
        self.array.append(animation)

        animation = Animation("pole")
        animation.add(["pole", [["I found a pole in the attic!"]]])
        self.array.append(animation)

        animation = Animation("bull")
        animation.add(["bull_0", [["Now I will place that instrument!","Farmer"]]])
        animation.add(["bull_1", []])
        animation.add(["bull_1", [["Ladies and gentlemen, His Highness Mozart!","Farmer"]]])
        animation.add(["bull_1", [["Da ba de da ba dam Da ba de da ba dam Da ba de da ba dam Da ba de da ba dam","Gramophone"]]])
        animation.add(["bull_2", [["Dam ba de da ba dam Da ba de da ba dam Da ba de da ba dam Da ba de da ba","Gramophone"]]])
        animation.add(["bull_2", [["And it's done!","Farmer"]]])
        self.array.append(animation)

        animation = Animation("end")
        animation.add(["bicycle_item", [["Mending of a flat tire is as easy as pie...\n Even though the birthday pie is still  not done. :)", "Farmer"]]])
        animation.add(["trip", [["Let's get to a local village grocery shop"]]])
        animation.add(["flour_0", [["Buy a flour and candles"]]])
        animation.add(["trip", [["Let's get back"]]])
        animation.add(["kitchen_1", [["Make a batter.... And finally........... ..................."]]])
        animation.add(["pie", [["Happy Birthday my Kitty Cat"]]])
        animation.add(["morning", [["The Farmer managed to make a cake for his cat. Cat was happy and sunset was near.\n .\n "
                                   "This is the End of the game, thanks for playing and see ya later folks :),\n (Now you can do anything you want, or type \"reset\" to play again.)"]]])

        self.array.append(animation)

    def getCurrentAnimationFrame(self):
        if self.cs() is not None:
            return self.cs().id,self.cs().currentFrame
        return "",0

    def isRunning(self):
        return self.currentAnimation!=-1
    def getAnimation(self,name):
        for animation in self.array:
            if animation.id==name:
                return animation
        return None

    def playAnimation(self,name):
        if name=="":
            if self.currentAnimation!=-1:
                self.e.r.remove(self.cs())
                self.e.s.setCurrent(self.e.s.currentScreen,self.e)
            self.currentAnimation=-1
            return
        for i in range(len(self.array)):
            if self.array[i].id==name:
                self.currentAnimation=i
                self.e.variables["state"] = "animation"
                self.e.r.clear()
                self.e.r.add(self.cs())
                self.cs().start()
                return
        print("Invalid animation: ",name)


    def cs(self):
        if self.currentAnimation==-1:
            return None
        return self.array[self.currentAnimation]

    def next(self):
        if self.cs().next():
            self.playAnimation("")
            return True
        return False


