import numpy as np
import cv2
from skimage.metrics import structural_similarity

from config import *


# 计算结构相似分数
def calculate_ssim(image1, image2):
    # 将图片转换为灰度图像
    gray1 = cv2.cvtColor(image1, cv2.COLOR_BGR2GRAY)
    gray2 = cv2.cvtColor(image2, cv2.COLOR_BGR2GRAY)
    
    # 计算SSIM值
    score = structural_similarity(gray1, gray2)
    
    return score

# 对原始图像进行切片，获取11*19的方块列表
def get_image_list(scim, gamepos):
    image = scim[gamepos[1]:gamepos[1]+750, gamepos[0]:gamepos[0]+1000]
    image = image[GAME_AREA_Y:GAME_AREA_Y+NUM_H*SQUARE_H, 
                  GAME_AREA_X:GAME_AREA_X+NUM_W*SQUARE_W]
    image_list = []
    for i in range(NUM_H):
        row = []
        for j in range(NUM_W):
            img = image[i*(SQUARE_H):i*(SQUARE_H)+SQUARE_H, j*(SQUARE_W):j*(SQUARE_W)+SQUARE_W]
            row.append(img)
        image_list.append(row)
    return image_list

# 识别方块并转换为迷宫，修改传入的maze数组
def mark_id(image, image_list, cur_idx, maze):
    image1 = image[8:-8, 8:-8]
    for i in range(NUM_H):
        for j in range(NUM_W):
            if maze[i][j] == 0:
                image2 = image_list[i][j]
                image2 = image2[8:-8, 8:-8] 
                score1 = calculate_ssim(image1, image2)

                if (score1 > 0.93):
                    maze[i, j] = cur_idx

# 转换为矩阵形式的迷宫
def get_maze(image_list):
    # 0：未标记
    # -1: 空
    maze = np.zeros((NUM_H, NUM_W), dtype=int)
    cur_idx = 1
    # 标记空的图片
    empty_img = np.array(cv2.imread('./resource/empty.png'), dtype=np.uint8)
    empty_img = cv2.resize(empty_img, dsize=(SQUARE_W, SQUARE_H))
    mark_id(empty_img, image_list, -1, maze)

    for i in range(NUM_H):
        for j in range(NUM_W):
            if maze[i, j] == 0:
                maze[i, j] = cur_idx
                mark_id(image_list[i][j], image_list, cur_idx, maze)
                cur_idx += 1
    return maze

# 重构图片（测试用）
def reconstruct(image_list):
    image = np.zeros((NUM_H*SQUARE_H, NUM_W*SQUARE_W, 3), dtype=np.uint8)
    for i in range(NUM_H):
        for j in range(NUM_W):
            image[i*SQUARE_H:(i+1)*SQUARE_H,
                  j*SQUARE_W:(j+1)*SQUARE_W] = image_list[i][j]
    return image