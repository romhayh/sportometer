import cv2
import numpy as np

import os
from os.path import normpath
import shutil
import json

from termcolor import colored
from random import shuffle
 
from concurrent.futures import ProcessPoolExecutor
from multiprocessing import cpu_count, Lock, Manager
import multiprocessing as mp

 # opencv operations
EROSIONS = 3
DILATIONS = 5
FRAME_SIZE = (800, 800)
KERNEL = np.ones((3,3),np.uint8)
SAVE_SIZE = (100, 100)

ACTIONS =[normpath('/boost') + '\\', normpath('/click') + '\\', normpath('/upgrade') + '\\'] 
VID_PATH = normpath('D:\\vscode workspace\\cv project\\src\\Video\\Videos\\')
IMG_TRAIN_PATH = normpath('D:\\vscode workspace\\cv project\\src\\Video\\Images\\train')
IMG_TEST_PATH = normpath('D:\\vscode workspace\\cv project\\src\\Video\\Images\\test')

IMG_PATH = normpath('D:\\vscode workspace\\cv project\\src\\Video\\Images')

DIRECTORIES = ['train', 'test']
JACTIONS = ['boost', 'click', 'upgrade']

def insureAmountsJSON():
    data: dict = json.loads('''{
        "train" :
        {
            "boost" : 0,
            "click" : 0,
            "upgrade": 0
        },
        "test" :
        {
            "boost" : 0,
            "click" : 0,
            "upgrade": 0
        }
    }
    ''')
    
    # reseting the amounts
    for d in DIRECTORIES:
        for a in JACTIONS:
            data[d][a] = 0    
    # write
    with open('D:\\vscode workspace\\cv project\\src\\Video\\Images\\amounts.json', 'w') as f:
        json.dump(data, indent = 4, sort_keys=True, fp= f)
 

def updateAmounts():
    data: dict = None
    # read
    with open('D:\\vscode workspace\\cv project\\src\\Video\\Images\\amounts.json', 'r') as f:
        data: dict = json.load(fp= f)
    print(data)
    for d in DIRECTORIES:
        for a in JACTIONS:
            path_to_dir = normpath(IMG_PATH + '\\' + d + '\\' + a)
            
            amount = len(os.listdir(path_to_dir))
            
            print(f'{path_to_dir} has {amount} imgs in it')
            
            data[d][a] = amount
    # write
    with open('D:\\vscode workspace\\cv project\\src\\Video\\Images\\amounts.json', 'w') as f:               
        json.dump(data, indent = 4, sort_keys=True, fp= f)
    
       
        
    
    
def renameVideoFiles():
    FILE_PREFIXES = ['b', 'c', 'u']
    for a, action in enumerate(ACTIONS):
        for i, file in enumerate(os.listdir(normpath(VID_PATH + action))):
            try:
                os.rename(normpath(VID_PATH + action + '\\' + file),
                          normpath(VID_PATH + action + FILE_PREFIXES[a] + f'{i+1}.mp4'))
            except FileExistsError:
                continue
            
def cleanImagesDirectory():
    folders = (IMG_TRAIN_PATH, IMG_TEST_PATH)
    for folder in folders:
        for filename in os.listdir(folder): # train, test
            file_path = os.path.join(folder, filename)
            try:
                
                if os.path.isfile(file_path) or os.path.islink(file_path) and filename != 'amounts.json':
                    # this function removes unnecessary 
                    # files from the /Images/
                    # directory. there should be only
                    # the train and test directories
                    os.unlink(file_path)
                    
                elif os.path.isdir(file_path):
                    #! this function deletes the folders inside the file path
                    #! and recursively deletes all files and folders in them
                    shutil.rmtree(file_path)
                    
            except Exception as e:
                print(f'Failed to delete {file_path}. Reason: {e}')
    
        # use the cmdlet 'mkdir' to make the 
        # 'boost', 'click', 'upgrade' directories
        for a in ACTIONS:
            os.mkdir(normpath(folder + '/' + a))

def evenOut():
    # read the json file
    data: dict = None
    with open('D:\\vscode workspace\\cv project\\src\\Video\\Images\\amounts.json', 'r') as f:
       data = json.load(fp= f)
     
    # find out the min value for each directory 
    # (train or test)
    min_test  = min(data['test'].values())
    min_train = min(data['train'].values())
    i: np.uint32 = 0
    
    for action in ACTIONS:
        
        # take the lists and shuffle them. 
        # remember - all images are born equal for the model
        testls = os.listdir(normpath(IMG_TEST_PATH + action) + '\\')
        shuffle(testls)
        trainls = os.listdir(normpath(IMG_TRAIN_PATH + action) + '\\')
        shuffle(trainls)
        
        i = 0
        for file in trainls:
            i += 1
            # remove any unnecessary images
            if i > min_train:
                os.remove(normpath(IMG_TRAIN_PATH + action + file))
                print(i-min_train)
                print(colored(f'destroyed + {normpath(IMG_TRAIN_PATH + action + file)}', 'red'))
                
        i = 0
        for file in testls:
            i += 1
            if i > min_test:
                # remove any unnecessary images
                os.remove(normpath(IMG_TEST_PATH + action + file))
                print(i-min_test)
                print(colored(f'destroyed + {normpath(IMG_TEST_PATH + action + file)}', 'red'))





def addToImageVector(path):
    print('hi guy')
    

    # NAME = file name with extension
    _, namext = os.path.split(normpath(path))
    NAME, extension = namext.split('.')
    SAVE_AS = '.png'

    cap = cv2.VideoCapture(normpath(path))

    # Prefix-To-Directory dictionary
    PTD = {'b' : ACTIONS[0],    # boost
        'c' : ACTIONS[1],    # click
        'u' : ACTIONS[2]}    # upgrade

    # take the video type from the name and get the extension from it
    # and end step 1
    ACTION = PTD[NAME[0]]
    
     
    # the blue line
    # for the histogram thresholding of the delta frame
    MIN_FACTORS = {ACTIONS[0] : 1.5,     # boost
                ACTIONS[1] : 1.6,     # click
                ACTIONS[2] : 1.45}     # upgrade
    
    MIN_FACTOR = MIN_FACTORS[ACTION]
    
    _, frame1 = cap.read()
    frame1 = cv2.resize(frame1, FRAME_SIZE)
    frame1 = cv2.flip(frame1, 1)

    # some videos might be currupted
    # in that case a manual skip
    # will be necessary
    while not cap.isOpened():
        print('not opened')
        wk = cv2.waitKey(1)
        if wk & 0xFF == ord('q') or wk & 0xFF == ord('Q') or wk & 0xFF == 27:
            break 

    n = 0
    sum = 0
    while cap.isOpened():        
        # the first parameter returned (ret)
        # is a boolean that is set True
        # if the read method succeeded
        # if not, it will be set to False
        # it will be False at the end of the video
        # think of it like a null terminator
        # at the end of a string
        ret, frame2 = cap.read()
        if not ret:
            break
        
        # the following lines are the same as the
        # image processing section for the movement
        # detection
        frame2 = cv2.resize(frame2, FRAME_SIZE)
        cv2.imshow('clip', frame2)
        frame2 = cv2.flip(frame2, 1)
        img = cv2.absdiff(frame1, frame2)
        img = cv2.cvtColor(img, cv2.COLOR_BGR2GRAY)
        # perform opening
        img = cv2.erode(img, KERNEL , iterations= EROSIONS)
        img = cv2.dilate(img, None, iterations= DILATIONS)
        frame1 = frame2
        _, img = cv2.threshold(img, 20, 255, cv2.THRESH_BINARY)
        cv2.imshow('difference', img)
        hist = cv2.calcHist([img], [0], None, [256], [0,256])
        if hist[255] != 0:
            # n is the number of frames in the 
            # video
            n += 1
            
            # if the frame detected is a movement frame
            # then it will have white pixels
            sum += hist[255]
        
        # manual stop
        # if the q or the 'esc' (escape) keys 
        # are pressed
        wk = cv2.waitKey(1)
        if wk & 0xFF == ord('q') or wk & 0xFF == ord('Q') or wk & 0xFF == 27:
            break 
    cap.release()
    cv2.destroyAllWindows()
    
    

    # take the average histogram of the video, 
    # for the delta frames
    # end of step 2, move on to the blue-line thresholding 
    avg = sum / n
    
    
    cap = cv2.VideoCapture(normpath(path))
    _, frame1 = cap.read()
    frame1 = cv2.resize(frame1, FRAME_SIZE)
    frame1 = cv2.flip(frame1, 1)

    while not cap.isOpened():
        print('not opened')
        wk = cv2.waitKey(1)
        if wk & 0xFF == ord('q') or wk & 0xFF == ord('Q') or wk & 0xFF == 27:
            break
    i = 0
    
    while cap.isOpened():
        
        ret, frame2 = cap.read()
        if not ret:
            break
        
        frame2 = cv2.resize(frame2, FRAME_SIZE)
        frame2 = cv2.flip(frame2, 1)
        img = cv2.absdiff(frame1, frame2)
        img = cv2.cvtColor(img, cv2.COLOR_BGR2GRAY)
        
        # perform opening
        img = cv2.erode(img, KERNEL, iterations= EROSIONS)
        img = cv2.dilate(img, None, iterations= DILATIONS)
        frame1 = frame2
        
        _, img = cv2.threshold(img, 20, 255, cv2.THRESH_BINARY)
        hist = cv2.calcHist([img], [0], None, [256], [0,256])
        
        # MIN_FACTOR * avg is the blue line (an)
        if hist[255] > MIN_FACTOR * avg:
            
            # a uniform distribution is a  
            # distribuiton in which each 
            # value has the same chance to be 
            # chosen
            num = np.random.uniform(0,100)
            
            img_path = IMG_TRAIN_PATH
            if num > 86:
                # the file will be added to test
                img_path = IMG_TEST_PATH
        
            # the file will be added to train
            # change the file size to (100, 100)
            img = cv2.resize(img, SAVE_SIZE)
            
            # print the path chosen
            print(normpath(img_path + ACTION) + '\\' + NAME + f'i{i}' +  SAVE_AS)
            print(normpath(img_path + ACTION) + '\\' + NAME + f'i{i+1}' +  SAVE_AS)
            
            # save the file
            cv2.imwrite(normpath(img_path + ACTION) + '\\' + NAME + f'i{i}' +  SAVE_AS, img)
            i += 1
            cv2.imwrite(normpath(img_path + ACTION) + '\\' + NAME + f'i{i}' +  SAVE_AS, cv2.flip(img, 1))
            i += 1
            
        
        wk = cv2.waitKey(1)
        if wk & 0xFF == ord('q') or wk & 0xFF == ord('Q') or wk & 0xFF == 27:
            break 

    cap.release()
    cv2.destroyAllWindows()
    # end of step 3
    
    
    
    

def generateVector():
    cleanImagesDirectory()
    insureAmountsJSON() # setup amounts.json
    renameVideoFiles()
    
    ls = []
    
    for a in ACTIONS:
        for file in os.listdir(normpath(VID_PATH + a)):
            ls.append(normpath(VID_PATH + a + file))
    print(len(ls))
    
    NUMBER_OF_CPUS = cpu_count()
    # use up to +++ of the cpu`s available 
    USE_UP_TO = 0.4
    MAX_WORKERS = np.uint16(NUMBER_OF_CPUS * USE_UP_TO)
    print(f'MAX_WORKERS = {MAX_WORKERS}')
    
    
    with ProcessPoolExecutor(max_workers= MAX_WORKERS) as executor:  
        for path in ls:
            print(colored(path, 'green'))
            executor.submit(addToImageVector, (path, ))

    updateAmounts() # count the images and update amounts.json
    
    evenOut()
    
    
if __name__ == '__main__':
    
    generateVector()

    