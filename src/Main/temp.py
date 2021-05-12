# importing stuff
import pygame
import time

import numpy as np
 
# initializing pygame
 
pygame.init()
 
# defining variables
 
clock = pygame.time.Clock()
ver = "Beta 0.1.6.3"

miner_coins_per_tick = 0
coins = 0
display_width = 800
display_height = 600
white = np.array((255, 255, 255), dtype= np.uint8)
black = np.array((0, 0, 0), dtype= np.uint8)
grey = np.array((128, 128, 128), dtype= np.uint8)
light_grey = np.array((224, 224, 224), dtype= np.uint8)
light_blue = np.array((173, 216, 230), dtype= np.uint8)
grey = np.array((128, 128, 128), dtype= np.uint8)
blue = np.array((0, 100, 250), dtype= np.uint8)
 
 
# creating display and caption
 
gameDisplay = pygame.display.set_mode((display_width, display_height))
pygame.display.set_caption("clicky clicks")
 
# defining functions


 
def circle(display, color, x, y, radius):
    pygame.draw.circle(display, color, (x, y), radius)
 
def autominer():
    global coins
    global miner_coins_per_tick
    time.sleep(0.1)
    coins = coins + miner_coins_per_tick
 
 
def DrawText(text, Textcolor, Rectcolor, x, y, fsize):
    font = pygame.font.Font(r'D:\vscode workspace\cv project\src\Game\Freshman-POdx.ttf', fsize)
    text = font.render(text, True, Textcolor, Rectcolor)
    
    # the boundries of the text object
    textRect = text.get_rect()
    print(textRect[:])
    # setting the center of the text
    textRect.center = (x, y)
    gameDisplay.blit(text, textRect)
 
 
def rectangle(display, color, x, y, w, h):
    pygame.draw.rect(display, color, (x, y, w, h))
 
 
def main_loop():
    global clock
    global miner_coins_per_tick
    global ver
    
    
    coins_per_click = 6
    cost_for_upgrade = 500
    cost_for_miner = 50
    global coins
    game_running = True
    while game_running:
        if game_running: 
            autominer()
            
        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                game_running = False
 
            if event.type == pygame.MOUSEBUTTONDOWN:
                mouse_position = pygame.mouse.get_pos()
                if mouse_position >= (350, 0):
                    if mouse_position <= (450, 0):
                        coins += coins_per_click
 
                if mouse_position <= (800, 0):
                    if mouse_position >= (600, 0):
                        if coins >= cost_for_upgrade:
                            coins = coins - cost_for_upgrade
                            cost_for_upgrade = cost_for_upgrade * 1.5
                            coins_per_click = coins_per_click * 1.1
                            cost_for_upgrade = round(cost_for_upgrade, 0)
 
                if mouse_position >= (50, 0):
                    if mouse_position <= (245, 0):
                        if coins >= cost_for_miner:
                            coins = coins - cost_for_miner
                            cost_for_miner = cost_for_miner * 1.5
                            miner_coins_per_tick = miner_coins_per_tick + 0.5
                            cost_for_miner = round(cost_for_miner, 0)
 
                if coins == 2147483647:
                    print("You Beat the game")
                    game_running = False
 
 
 
        # drawing stuff
 
        gameDisplay.fill(light_blue)
        
        DrawText("Clicky Clicks", black, light_blue, 400, 100, 50)
        
        DrawText("you have " + str(f'{coins:.2f}') + " coins", black, light_blue, 100, 50, 20)
        
        DrawText("upgrade clicker " + str(cost_for_upgrade), black, light_blue, 700, 300, 20)
        
        DrawText("buy auto miner " + str(cost_for_miner), black, light_blue, 150, 370, 20)
        
        DrawText("Version: " + ver, black, light_blue, 650, 50, 20)
        
        rectangle(gameDisplay, blue, 50, 400, 200, 300)
        
        circle(gameDisplay, blue, 400, 260, 60)
        
        rectangle(gameDisplay, blue, 600, 317, 200, 300)
        
        pygame.display.update()
        clock.tick(60)
 
# ending the program
 
main_loop()
pygame.quit()
quit()