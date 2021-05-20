import numpy as np
from numba import njit
import pygame


COLOR = np.array(object= [0, 0, 255], 
                 dtype= np.uint8)


def rgb2hsv(rgb: np.ndarray):
    """ convert RGB to HSV color space

    :param rgb: np.ndarray
    :return: np.ndarray
    """

    maxv = np.amax(rgb)
    maxc = np.argmax(rgb)
    minv = np.amin(rgb)
    minc = np.argmin(rgb)

    hsv = np.zeros(rgb.shape, dtype='float')
    hsv[maxc == minc, 0] = np.zeros(hsv[maxc == minc, 0].shape)
    hsv[maxc == 0, 0] = (((rgb[..., 1] - rgb[..., 2]) * 60.0 / (maxv - minv + np.spacing(1))) % 360.0)[maxc == 0]
    hsv[maxc == 1, 0] = (((rgb[..., 2] - rgb[..., 0]) * 60.0 / (maxv - minv + np.spacing(1))) + 120.0)[maxc == 1]
    hsv[maxc == 2, 0] = (((rgb[..., 0] - rgb[..., 1]) * 60.0 / (maxv - minv + np.spacing(1))) + 240.0)[maxc == 2]
    hsv[maxv == 0, 1] = np.zeros(hsv[maxv == 0, 1].shape)
    hsv[maxv != 0, 1] = (1 - minv / (maxv + np.spacing(1)))[maxv != 0]
    hsv[..., 2] = maxv
    return hsv


def hsv2rgb(hsv: np.ndarray):
    """ convert HSV to RGB color space

    :param hsv: np.ndarray
    :return: np.ndarray
    """

    hi = np.floor(hsv[..., 0] / 60.0) % 6
    hi = hi.astype('uint8')
    v = hsv[..., 2].astype('float')
    f = (hsv[..., 0] / 60.0) - np.floor(hsv[..., 0] / 60.0)
    p = v * (1.0 - hsv[..., 1])
    q = v * (1.0 - (f * hsv[..., 1]))
    t = v * (1.0 - ((1.0 - f) * hsv[..., 1]))

    rgb = np.zeros(hsv.shape)
    rgb[hi == 0] = np.array((v, t, p))[hi == 0, :]
    rgb[hi == 1, :] = np.array((q, v, p))[hi == 1, :]
    rgb[hi == 2, :] = np.array((p, v, t))[hi == 2, :]
    rgb[hi == 3, :] = np.array((p, q, v))[hi == 3, :]
    rgb[hi == 4, :] = np.array((t, p, v))[hi == 4, :]
    rgb[hi == 5, :] = np.array((v, p, q))[hi == 5, :]
    return rgb.astype(np.uint8)


@njit
def calcHue(score: np.float64):
    r'''
    # Calculate Hue
    this function takes a score and returns the next
    `hue` using the formula:

    `h` = new hue value  

    `s` = old hue value

    `h = 180sin(sqrt(s)) + 180`
    '''

    hue = 180 * np.sin(np.sqrt(score) * np.pi / 180.) + 180
    return hue

    
def getColor(score):
    rgb = COLOR
    hsv = rgb2hsv(rgb)

    hsv[0] = calcHue(score)

    rgb = hsv2rgb(hsv)

    return rgb




