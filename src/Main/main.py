# multiprocessing
from concurrent.futures import ProcessPoolExecutor
from multiprocessing import process, shared_memory, Lock
from multiprocessing import Process, Array, Pool
import multiprocessing

from video_input import takeInput
from game import runGame


if __name__  == '__main__':
    from smglobals import movement
    p1 = Process(target=takeInput, args= (movement, ))
    p2 = Process(target=runGame, args=(movement, ))
    
    p1.name = 'video input'
    p2.name = 'game'
    
    p1.start()
    p2.start()
    
    p1.join()           
    p2.join()
    
    p1.close()
    p2.close()
    
    
    
    print('hi guy')
