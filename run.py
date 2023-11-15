# 1. 找到游戏窗体，截取图片，数值处理转换为迷宫
# 2. 从左上角开始进行BFS，判断能否进行消除
# 3. 找到能消除的一对，坐标传递给

# Note
# 1. 横坐标、纵坐标的顺序

import numpy as np
import time
import cv2
from skimage.metrics import structural_similarity

import keyboard
from tqdm import tqdm
import sys

from config import *
from image_process import *
from tools import *
from solve import *


# 截图-识别窗体-返回迷宫
def recognize_window():
    gamepos = getGameWindowPosition() # 识别游戏窗体位置
    setWindowForeground()
    scim = getScreenImage() # 截取全屏图像
    image_list = get_image_list(scim, gamepos) # 切片为列表
    maze = get_maze(image_list) # 转换为二维数组标识的方块
    return gamepos, maze

def brute_solve(gamepos, maze):
    # 对所有剩余方块进行暴力点击
    # 适用于某些识别不出来的特殊情况
    # gamepos, maze = recognize_window()
    # setWindowForeground()
    for i in range(NUM_H):
        for j in range(NUM_W):
            for m in range(i + 1, NUM_H):
                for n in range(j + 1, NUM_W):

                    if maze[i, j] > 0 and maze[m, n] > 0:
                        st = (i, j)
                        ed = (m, n)
                        st_pos = (gamepos[0] + GAME_AREA_X + st[1] * SQUARE_W + 10, 
                                gamepos[1] + GAME_AREA_Y + st[0] * SQUARE_H + 10)
                        ed_pos = (gamepos[0] + GAME_AREA_X + ed[1] * SQUARE_W + 10, 
                                gamepos[1] + GAME_AREA_Y + ed[0] * SQUARE_H + 10)
                        mouse_click(st_pos, 0.01)
                        mouse_click(ed_pos, 0.01)
                        if not is_game_start():
                            return

def solve_single():
    gamepos, maze = recognize_window()
    res = search_pair(maze)
    if res:
        st, ed = res
        maze[st[0], st[1]] = -1
        maze[ed[0], ed[1]] = -1

        st_pos = (gamepos[0] + GAME_AREA_X + st[1] * SQUARE_W + 10, 
                  gamepos[1] + GAME_AREA_Y + st[0] * SQUARE_H + 10)
        ed_pos = (gamepos[0] + GAME_AREA_X + ed[1] * SQUARE_W + 10, 
                  gamepos[1] + GAME_AREA_Y + ed[0] * SQUARE_H + 10)
        mouse_click(st_pos, 0.01)
        mouse_click(ed_pos, 0.01)

def solve(time_interval):
    print('求解速度: ', f'{time_interval:.2f}s')
    gamepos, maze = recognize_window()
    print(gamepos)
    print(maze)

    num_reshape = 0
    num_pairs = (maze > 0).astype(int).sum()
    print('砖块总数：', num_pairs)
    if num_pairs > 200:
        print('图像识别失败')
        return 

    i = 0
    for i in tqdm(range(num_pairs//2)):
        if (maze+1).sum() == 0:
            print('完成')
            break
        
        # 每隔5个方块检查当前游戏状态
        if i % 5 == 0:
            if not is_game_start():
                return

        # if (i+1) % 10 == 0:
            # gamepos, maze = recognize_window()
        res = search_pair(maze)  # 寻找配对

        if res is None:
            # 如果剩余方块小于10个
            if get_square_left(maze) < 10:
                # 首先尝试暴力
                print('暴力求解中')
                brute_solve(gamepos, maze)
                gamepos, maze = getGameWindowPosition()
                if not is_game_start():
                    break

            if get_square_left(maze) > 0 and num_reshape <= 2:
                print('无解，点击重排')
                # 点击重排
                press_reshape(gamepos)
                time.sleep(4)
                gamepos, maze = recognize_window()
                print('new maze:')
                print(maze)
                res = search_pair(maze)
                if res is None:
                    print('求解失败')
                    break
                num_reshape += 1
            else:
                break
        
        # 解析结果
        st, ed = res
        maze[st[0], st[1]] = -1
        maze[ed[0], ed[1]] = -1

        st_pos = (gamepos[0] + GAME_AREA_X + st[1] * SQUARE_W + 10, 
                  gamepos[1] + GAME_AREA_Y + st[0] * SQUARE_H + 10)
        ed_pos = (gamepos[0] + GAME_AREA_X + ed[1] * SQUARE_W + 10, 
                  gamepos[1] + GAME_AREA_Y + ed[0] * SQUARE_H + 10)

        mouse_click(st_pos, time_interval=time_interval*0.5 + time_interval*0.5*np.random.rand())
        mouse_click(ed_pos, time_interval=time_interval*0.5 + time_interval*0.5*np.random.rand())
        i += 1


def get_target_corp(image, lu_pos, rb_pos):
    tgt_area = image[lu_pos[1]:rb_pos[1], lu_pos[0]:rb_pos[0]]
    # print(lu_pos, rb_pos)
    # print(tgt_area.shape)
    return tgt_area

def is_game_start():
    gamepos = getGameWindowPosition()
    if gamepos is None:
        return False

    scim = getScreenImage()
    lu_pos = (gamepos[0]      , gamepos[1])
    rb_pos = (gamepos[0] + 150, gamepos[1] + 150)
    tgt_area = get_target_corp(scim, lu_pos, rb_pos)
    no_start = np.array(cv2.imread('./resource/no_start.png'), dtype=np.uint8)
    no_start = cv2.resize(no_start, dsize=(150, 150))
    score = calculate_ssim(tgt_area, no_start)
    if score > 0.8:
        return False
    else:
        return True


def auto_mode():
    print('进入自动模式')
    while(1):
        
        try:
            if not getGameWindowPosition():
                print('游戏窗口关闭，重新进入')
                fgamepos = getFatherWindowPosition()
                setFaterWindowForeground()
                press_fstart(fgamepos)
                time.sleep(2)
                press_iknow()
                time.sleep(0.5)
                press_iknow()
                # exit(0)
            press_start()
            time.sleep(0.5)
            press_start()
            while True:
                setWindowForeground()

                if not getGameWindowPosition():
                    break
                print('等待游戏开始...')
                if is_game_start():
                    time.sleep(3)
                    break
                time.sleep(3)
            press_iknow()
            if not getGameWindowPosition():
                continue
            solve(time_interval=CLICK_INTERVAL_AUTO)
            time.sleep(5)

        except Exception as e:
            print(type(e))
            print(e.args)
            print(e)

            # 游戏窗口未打开
            if not getGameWindowPosition():
                fgamepos = getFatherWindowPosition()
                setFaterWindowForeground()
                press_fstart(fgamepos)



def test():
    press_iknow()
    # fgamepos = getFatherWindowPosition()
    # press_fstart(fgamepos)
    # setWindowForeground()
    # print(is_game_start())

if __name__=='__main__':
    np.set_printoptions(threshold=np.inf, linewidth=np.inf)
    print('ENTER:   点击准备')
    print('P    :   点击练习')
    print('T    :   测试功能')
    print('A    :   消除一个')
    print('F4   :   自动模式')
    print('F6   :   极慢求解（1.00s）')
    print('F7   :   慢速求解（0.50s）')
    print('F8   :   标准求解（0.25s）')
    print('F9   :   快速求解（0.10s）')
    print('F10  :   极速求解（0.01s）')
    print('ESC  :   退出程序')

    keyboard.add_hotkey('f4', auto_mode)
    keyboard.add_hotkey('f6',  solve, args=(CLICK_INTERVAL_VERY_SLOW, ))
    keyboard.add_hotkey('f7',  solve, args=(CLICK_INTERVAL_SLOW, ))
    keyboard.add_hotkey('f8',  solve, args=(CLICK_INTERVAL, ))
    keyboard.add_hotkey('f9',  solve, args=(CLICK_INTERVAL_FAST, ))
    keyboard.add_hotkey('f10', solve, args=(CLICK_INTERVAL_VERY_FAST, ))
    keyboard.add_hotkey('p',   press_practice)
    keyboard.add_hotkey('enter', press_start)
    keyboard.add_hotkey('t', test)
    keyboard.add_hotkey('a', solve_single)
    keyboard.wait('esc')

    

  


