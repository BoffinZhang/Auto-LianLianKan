import numpy as np
from config import *

vis = np.zeros((NUM_H, NUM_W), dtype=np.int32)

def dfs(maze, tgt, h, w, direct, depth):
    global vis
    if h < 0 or h >= NUM_H or w < 0 or w >= NUM_W:
        return None
    if depth > 2: # 最多拐弯两次
        return None
    if vis[h, w] != 0:
        return None
    if maze[h, w] == tgt:
        return h, w
    if maze[h, w] != -1:
        return None

    vis[h, w] = 1
    dhs = [-1, 0, 1, 0]
    dws = [0, 1, 0, -1]
    for dh, dw in zip(dhs, dws):
        new_h = h + dh
        new_w = w + dw
        if (dh, dw) != direct:
            res = dfs(maze, tgt, new_h, new_w, (dh, dw), depth+1)
        else:
            res = dfs(maze, tgt, new_h, new_w, direct, depth)
        if res is not None:
            return res
    vis[h, w] = 0
    return None            

# DFS寻找可行解
def search_pair(maze):
    for i in range(NUM_H):
        for j in range(NUM_W):
            if maze[i,j] > 0:
                global vis
                vis = np.zeros((NUM_H, NUM_W), dtype=np.int32)
                vis[i,j] = 1
                st = (i, j)
                for direct in [(-1, 0), (0, 1), (1, 0), (0, -1)]:
                    # print('start_search', i, j)
                    ed = dfs(maze, maze[i, j], i+direct[0], j+direct[1], direct=direct, depth=0)
                    
                    if ed is not None:
                        return st, ed
    return None

# 剩余方块数量
def get_square_left(maze):
    res = ((maze + 1) > 0).astype(np.int32).sum()
    return res