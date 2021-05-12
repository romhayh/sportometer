from concurrent.futures import ProcessPoolExecutor
from multiprocessing import process, shared_memory, Lock
from multiprocessing import Process, Array, Pool
import multiprocessing
import numpy as np

NP0 = np.zeros((3,), dtype= np.uint8)

lock = Lock()

movement: Array = Array('i', 3, lock=True)

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
