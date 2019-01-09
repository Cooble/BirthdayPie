from pickle import load,dump
import os
def loadImage(fileName):
    try:
        file = open("image/"+fileName+".txt", "r")
        out =  file.readlines()
        return out
    except FileNotFoundError:
        return "null"

def saveGame(engine):
    try:
        with open('game_file.bin', 'wb') as game_file:
            dump(engine, game_file)
            return True
    except OSError:
        return False

def loadGame():

    try:
        with open('game_file.bin', 'rb') as game_file:
            return  load(game_file)
    except OSError:
        return None

def clear():
    if os.path.exists("game_file.bin"):
        os.remove("game_file.bin")