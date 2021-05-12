import pygame
from multiprocessing import Array

import time
import numpy as np
from numba import njit

# misc
import keyboard
from termcolor import colored

pygame.init()

# screen
WIDTH = 1080
HEIGHT = 800




# game
score = 0

# upgrade
UPGRADE_BASE = 1.1
UPGRADE_BIAS = 1

# click
pointsPerClick = 1.0

# boost
boostCoefficient = 1
BOOST_BASE = 5
BOOST_TIME = 5
boostStart = 0

def doAction(action: np.ndarray):
    global score
    global pointsPerClick
    global boostStart
    global boostCoefficient
    # action indecies list:
    # 0 boost
    # 1 click
    # 2 upgrade
      
    # the action is boost
    if np.argmax(action) == 0:
        boostStart = time.perf_counter()
        boostCoefficient *= BOOST_BASE
        print('boost')
        
    # the action is click
    elif np.argmax(action) == 1:
        score += boostCoefficient * pointsPerClick
        print(f'click, you will get extra {boostCoefficient * pointsPerClick} points.')
        print(f'boost timer = {time.perf_counter() - boostStart}, boost coefficient = {boostCoefficient}')
        
    # the action is upgrade
    elif np.argmax(action) == 2:
        pointsPerClick = UPGRADE_BASE * (pointsPerClick + UPGRADE_BIAS)
        print('upgrade')
      
      
def drawText(gameDisplay, text, Textcolor, Rectcolor, x, y, fsize):
    font = pygame.font.Font(r'D:\vscode workspace\cv project\src\Game\Freshman-POdx.ttf', fsize)
    text = font.render(text, True, Textcolor, Rectcolor)
    
    # the boundries of the text object
    # the canvas region of intrest
    canvasROI = text.get_rect()
    # setting the center of the text
    canvasROI.center = (x, y)
    gameDisplay.blit(text, canvasROI)      
    
      
def init():
    
    icon = pygame.image.load(r'D:\vscode workspace\cv project\src\Game\game_icon.ico')
    
    pygame.display.set_caption('Sportometer')  
    pygame.display.set_icon(icon)
    
    
@njit    
def getFontSize(x: np.uint16 = WIDTH, y: np.uint16 = HEIGHT, r: np.uint16 = 20):
    sqrt = np.sqrt(x*y)
    
    return r * np.uint16(sqrt / (x-y))


def draw(gameDisplay):
    drawText(gameDisplay,
    f'you have',
    (255,255, 255), (0, 0, 0),
    WIDTH / 2, HEIGHT / 3, getFontSize())
    
    drawText(gameDisplay,
    f'{np.round(score, 3)}',
    (255,255, 255), (0, 0, 0),
    WIDTH / 2, HEIGHT / 2, getFontSize())
    
    drawText(gameDisplay,
    f'sport points',
    (255,255, 255), (0, 0, 0),
    WIDTH / 2, 2 * HEIGHT / 3, getFontSize())
    
    if boostStart:
        drawText(gameDisplay,
            f'boost for: {np.round(BOOST_TIME - time.perf_counter() + boostStart, 3)}',
            (255,255, 255), (0, 0, 0),
            WIDTH / 4, 1 * HEIGHT / 8, getFontSize())
        
        drawText(gameDisplay,
            f'boost: {np.round(boostCoefficient)}',
            (255,255, 255), (0, 0, 0),
            WIDTH / 4, 7 * HEIGHT / 8, getFontSize())
    
    drawText(gameDisplay,
        f'sp per click: {np.round(pointsPerClick)}',
        (255,255, 255), (0, 0, 0),
        WIDTH / 4, 3 * HEIGHT / 4, getFontSize())
    

def runGame(_movement : Array):
    global boostCoefficient
    global boostStart
    gameDisplay = pygame.display.set_mode((WIDTH, HEIGHT))
    init()
    # start of movement
    # if set to True - there is an on going movement
    start = False
    running = True
    while running:
        # window section
        
        gameDisplay.fill(0)
        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                running = False
        movement: np.ndarray = np.array(_movement, dtype = np.uint8)
        
        draw(gameDisplay)
        
        pygame.display.flip()
        
        # movement
        
        for i in range(len(movement)):
            if movement[i] != 0:
                if not start:
                    start = True
                    t1 = time.perf_counter()
                    doAction(movement)
                    print(f'score = {score}')
                elif start:
                    t2 = time.perf_counter()
                    if t2-t1 > 0.2:
                        start = False
        
        if time.perf_counter() - boostStart > BOOST_TIME:
            if boostStart:
                print(colored(f'{time.perf_counter() - boostStart} is bigger than {BOOST_TIME}', 'red'))
            boostCoefficient = 1
            boostStart = 0
        
        if keyboard.is_pressed('q'):
            print(f'exiting')
            break
    pygame.quit()

if __name__ == '__main__':
    
    pass
    
                
        
   