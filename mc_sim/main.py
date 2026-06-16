import numpy as np
import math
import random

import os
import glob
import argparse
import time as timer
from datetime import datetime
from tqdm import tqdm

from multiprocessing import Pool
from multiprocessing import cpu_count

import pandas as pd
import matplotlib.pyplot as plt
import matplotlib.cm as cm

import logging as lg
from src import brownian as GET

lg.basicConfig(level=lg.WARNING, format="%(levelname)s:%(message)s")

#モジュール数はMで与える

def trajectory(M,name,rate_forward=1,rate_backward=1):
    orbit = [] #軌跡のリスト,動作確認用
    current_state = 0b0 #回路の状態
    next_state = 0b0 #回路の次の状態
    dt = 0 #状態の滞在時間
    dt_list = [] #返す時間リスト,動作確認用
    time = 0 #返す時間
    jump = 0 #返す遷移総回数
    T=10000000 #経路の最大観測時間
    #初期状態の生成
    initial_state = GET.initialize(M,name) #初期状態
    current_state =initial_state
    initial_logic = GET.trans_logic(M,name,initial_state)
    orbit.append(current_state)
    #経路の生成
    while not GET.check_finish(M,name,next_state) and (time <= T):
        rand_t = random.random() #滞在時間を決定する乱数
        dt = 0
        q = 0
        q = rate_forward * GET.check_forward(M,name,current_state) + rate_backward * GET.check_backward(M,name,current_state)
        #次の遷移状態を決定する
        next_state = GET.gen_next(M,name,current_state,rate_forward,rate_backward)
        #現在の状態の滞在時間を決定する
        dt = 1/q * math.log(1/rand_t)
        dt_list.append(dt)
        time += dt
        #遷移を一回足す
        jump += 1
        current_state = next_state
        orbit.append(current_state)
    if time>T: lg.warning("transit time touched limit time")
    ending_logic = GET.trans_logic(M,name,next_state)
    return [initial_logic,ending_logic,time,jump]

def update_progress_bar(result):
    global pbar
    global results
    pbar.update()
    results.append(result)

def initialize_job_list():
    parser = argparse.ArgumentParser(
        description="Brownian circuit simulation"
    )
    parser.add_argument("--circuit",
                        type=str,
                        required=True,
                        help="Name of circuit"
                        )
    parser.add_argument("--module",
                        type=int,
                        nargs="+",
                        required=True,
                        help="Number of serially connected circuits")
    parser.add_argument("--gamma",
                        type=float,
                        nargs="+",
                        required=True,
                        help="List of forward transition rates"
                        )
    parser.add_argument("--trials",
                        type=int,
                        default=100,
                        help="Number of trials"
                        )
    args = parser.parse_args()
    return args

if __name__ == "__main__":
    job_args = initialize_job_list()
    test_num = job_args.trials
    name = job_args.circuit
    for M in job_args.module:
        for f_rate in job_args.gamma:
                #開始時刻を表示
                print(datetime.now())
                start=timer.time()
                #変数の処理
                input = (M,name,f_rate)
                print("test cases of "+name+"_mod-"+str(M)+"_rate-"+str(f_rate))
                #名前に使う変数の生成
                timename = str(timer.time_ns())
                b_rate = 1
                #プールのサイズをCPUコア数にする
                pool_size = cpu_count()
                results = []
                print(pool_size)
                #tqdmでプログレスバーを作成
                with tqdm(total=test_num) as pbar:
                    with Pool(pool_size) as pool:
                        for _ in range(test_num):
                            pool.apply_async(trajectory, args=(M,name,f_rate), callback=update_progress_bar)

                        pool.close()
                        pool.join()  #全てのタスクが終わるまで待機
                #データの変換
                data=np.array(results)
                data_frame = pd.DataFrame(data)
                data_frame.to_csv("../data/"+name+"/"+name+":mod-"+str(M)+"_test:"+str(test_num)+"rate:"+str(f_rate)+"-"+str(b_rate)+"_with"+timename+"_data.csv",header=False,index=False)
                print("test cases of "+name+"_mod-"+str(M)+"_rate-"+str(f_rate)+" were closed!")
                #終了時刻
                end=timer.time()
                print(end-start)