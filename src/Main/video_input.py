import multiprocessing
import cv2
import numpy as np

from os.path import normpath
from numba import njit
from termcolor import colored
from multiprocessing import Array, shared_memory


# opencv operations
EROSIONS = 3
DILATIONS = 5
FRAME_SIZE = (800, 800)
KERNEL = np.ones((3,3),np.uint8)

# model
SAVE_SIZE = (100, 100)
CLASSES = ['boost', 'click', 'upgrade']
SEQ_SIZES = {
    'boost': 5.8,
    'click': 6.8,
    'upgrade': 4
}

NO_MOVEMENT_MAX = 5
NP0 = np.zeros((3,), dtype=np.uint8)


@njit
def prepareImage(img: np.ndarray):
    
    # shift the values from [0, 255] to [0, 1]
    ans: np.ndarray = img / 255
    
    #*  make it a 4d tensor
    #*  with:
    #  ~~~~~~~~~~~~~~+ 1 img ~~~~~~~~
    #  ~~~~~~~~~~~~~~~~~+ size +~~~~~
    #  ~~~~~~~~~~~~~~~~one channel+~~
    return ans.reshape((1, SAVE_SIZE[0], SAVE_SIZE[1], 1))

def takeInput(movement : multiprocessing.Array):
    from tensorflow import keras
    
    print (f'type(movement) = {type(movement)}')
    model = keras.models.load_model(normpath('D:/vscode workspace/cv project/src/Video/Models/bigmodel.h5'))

    seq = {
        'boost': 0,
        'click': 0,
        'upgrad(e': 0
    }
    last_operation = ''
    timeWithoutMovement: np.uint16 = 0

    cap = cv2.VideoCapture(0)
    cap.set(cv2.CAP_PROP_FPS, 20)
    _, frame1 = cap.read()
    frame1 = cv2.resize(frame1, FRAME_SIZE)
    frame1 = cv2.flip(frame1, 1)

    # print(colored(f'{name}: from video input', 'green'))
    # existing_shm = shared_memory.SharedMemory(name= name)
    # movement = np.ndarray((3,), dtype= np.uint8, buffer= existing_shm.buf)
    
    while 'open':
        
        movement[:] = NP0[:]
        
        
        cv2.imshow('frame', frame1)
        
        _, frame2 = cap.read()
        
        frame2 = cv2.resize(frame2, FRAME_SIZE)
        frame2 = cv2.flip(frame2, 1)
        
        # taking the delta frame by absolute-subtraction 
        # of each pixel (x1, y1) in frame1
        # to its corresponding pixel (x1, y1)
        # in frame2
        img = cv2.absdiff(frame1, frame2)

        img = cv2.cvtColor(img, cv2.COLOR_BGR2GRAY)
        # perform opening
        
        img = cv2.erode(img, KERNEL, iterations= EROSIONS)

        img = cv2.dilate(img, None, iterations= DILATIONS)
        
        frame1 = frame2
        
        _, img = cv2.threshold(img, 20, 255, cv2.THRESH_BINARY)
        #        ~~~~~~~~~~~~~~~~~~~^^ the minimum value ~~~~~~
        #        ~ to become this value ^^^~~~~~~~~~~~~~~~~~~~~
        #        ~~~~~~~~~~~~~~ in this way ~^^^^^^^^^^^^^^^^^~
        
        cv2.imshow('delta frame', img)
        

        hist = cv2.calcHist([img], [0], None, [256], [0,256])
        #      ~~~~~~~~~~~~~^^^^^ an array of images ~~~~~~~~
        #      ~ calculate for the ^^^ only channel available
        #      ~~~~~~~~~~~~~~~~~~~~~~~~~^^^^~ apply no mask ~
        #      ~~~~~~~ the maximum value ~~~~~^^^^^~~~~~~~~~~
        #      ~~~~~~~~~~~~ the range of the values  ^^^^^^^~ 
        
        # invoke the model only if there is movement
        if hist[255] > 0: 

            # numba doesnt work with openCV
            # because it is written in C++
            img = prepareImage(cv2.resize(img, SAVE_SIZE))
            
            
            # prediction is an array of 3 
            # floats in it
            # the 0th index is the confidence for boost
            # the 1st index is the confidence for click
            # the 2nd index is the confidence for upgrade
            prediction = model.predict(img)
            
            if np.max(prediction) > 0.95:
    
                operation = CLASSES[np.argmax(prediction)]
                
                if last_operation != operation:
                    # reset
                    for c in CLASSES:
                        seq[c] = 0
                    timeWithoutMovement = 0
            
                else:
                    seq[operation] += np.max(prediction)
                    if seq[operation] >= SEQ_SIZES[operation]:
                        movement[np.argmax(prediction)] = 1
                        print(f'CLASSES[np.argmax(movement)] = {CLASSES[np.argmax(movement)]}, seq = {seq}')
                        
                        # reset
                        for c in CLASSES:
                            seq[c] = 0
                        timeWithoutMovement = 0
                    
                last_operation = operation
        else:
            timeWithoutMovement += 1
            
            if timeWithoutMovement >= NO_MOVEMENT_MAX:
                # reset
                for c in CLASSES:
                    seq[c] = 0
                timeWithoutMovement = 0
            
        wk = cv2.waitKey(1)
        if wk & 0xFF == ord('q') or wk & 0xFF == ord('Q') or wk & 0xFF == 27:
            break 



    cap.release()
    cv2.destroyAllWindows()

    


if __name__ == '__main__':
    movement = Array('i', 3)
    takeInput(movement)
    