import pythoncom
import win32api, win32gui, win32con
import win32com.client 
import numpy as np
from PIL import ImageGrab, Image
import time
import cv2
from config import *

# 获取游戏窗体位置左上角坐标
def getGameWindowPosition():
    window = win32gui.FindWindow(None, WINDOW_TITLE)

    while not window:
        print('定位游戏窗体失败, 1秒后尝试识别父窗口')
        time.sleep(1)
        return None

    pos = win32gui.GetWindowRect(window)
    # print('窗体位置：', pos[0], pos[1])
    return pos[0], pos[1]

# 获取游戏大厅的位置
def getFatherWindowPosition():
    window = win32gui.FindWindow('GRootViewClass', FATHER_WINDOW_TITLE)

    while not window:
        print('定位父游戏窗体失败，5秒后重试...')
        time.sleep(1)
        window = win32gui.FindWindow('GRootViewClass', FATHER_WINDOW_TITLE)

    pos = win32gui.GetWindowRect(window)
    print('父窗口识别成功')
    print('父窗体位置：', pos[0], pos[1])
    return pos[0], pos[1]

def setWindowForeground():
    window = win32gui.FindWindow(None, WINDOW_TITLE)
    pythoncom.CoInitialize()
    shell = win32com.client.Dispatch("WScript.Shell")
    shell.SendKeys('%')
    win32gui.SetForegroundWindow(window)

# 获取完整的屏幕截图
def getScreenImage():
    # print('图像识别中')
    scim = ImageGrab.grab()

    scim_array = np.array(scim)
    new_size = (int(scim.size[0]/ZOOM_PARAM), 
                int(scim.size[1]/ZOOM_PARAM))
    # if res:
    scim_array = cv2.resize(scim_array, dsize=(new_size))
    # np.save('scim_array.npy', scim_array)
    return scim_array

# 鼠标点击目标位置
def mouse_click(pos, time_interval=0.2, gamepos=(0, 0)):
    win32api.SetCursorPos((pos[0] + gamepos[0], pos[1]+gamepos[1]))
    win32api.mouse_event(win32con.MOUSEEVENTF_LEFTDOWN, pos[0] + gamepos[0], pos[1]+gamepos[1])
    win32api.mouse_event(win32con.MOUSEEVENTF_LEFTUP, pos[0] + gamepos[0], pos[1]+gamepos[1])
    time.sleep(time_interval)

def mouse_move(pos, gamepos=(0, 0)):
    win32api.SetCursorPos((pos[0]+gamepos[0], pos[1]+gamepos[1]))

def press_reshape(gamepos):
    # 点击重排
    pos_x = int((gamepos[0] + RESHAPE_X) )
    pos_y = int((gamepos[1] + RESHAPE_Y) )
    mouse_click( (pos_x, pos_y), 5)

def press_start():
    gamepos = getGameWindowPosition()
    pos_x = int((gamepos[0] + START_X) )
    pos_y = int((gamepos[1] + START_Y) )
    mouse_click( (pos_x, pos_y), 0)

def press_fstart(fgamepos):
    # 点击快速开始游戏
    pos_x = int((fgamepos[0] + FSTART_X) )
    pos_y = int((fgamepos[1] + FSTART_Y) )
    mouse_click( (pos_x, pos_y), 5)

def press_practice():
    gamepos = getGameWindowPosition()
    pos_x = int((gamepos[0] + PRAC_X) )
    pos_y = int((gamepos[1] + PRAC_Y) )
    mouse_click( (pos_x, pos_y), 0)

def press_iknow():
    gamepos = getGameWindowPosition()
    pos_x = int((gamepos[0] + IKNOW_X) )
    pos_y = int((gamepos[1] + IKNOW_Y) )
    mouse_click( (pos_x, pos_y), 0)